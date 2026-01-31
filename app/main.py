from fastapi import FastAPI, HTTPException
from app.models.schemas import IndexRequest, SearchRequest, SearchResult
from app.services.models import model_service
from app.services.vector_db import vector_db
from app.services.llm import llm_service
from app.core.config import settings
import uuid
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Semantic Footage Search Engine API"}

@app.post(f"{settings.API_V1_STR}/index")
async def index_scenes(request: IndexRequest):
    """
    Index a list of Scenes with advanced metadata.
    """
    start_time = time.time()
    try:
        if request.recreate_collection:
            vector_db.recreate_collection()

        segments_to_add = []
        texts_to_embed = []
        
        for scene in request.scenes:
            for clip in scene.clips:
                # 1. Construct text for embedding
                scene_desc_str = f"Location: {scene.scene_description.location} ({scene.scene_description.int_ext}, {scene.scene_description.time_of_day})"
                clip_desc_str = " ".join(clip.clip_description)
                dialogue_texts = [d.text for d in clip.dialogue]
                dialogue_str = " ".join(dialogue_texts)
                actors_str = ", ".join(clip.actors_involved)

                text_to_embed = f"""
Scene: {scene_desc_str}
Clip Description: {clip_desc_str}
Dialogue: {dialogue_str}
Actors: {actors_str}
""".strip()
                
                # 2. Prepare Payload
                # Calculate start/end time from dialogue or default to 0 if no dialogue
                if clip.dialogue:
                    start_sec = clip.dialogue[0].timestamp_start_sec
                    end_sec = clip.dialogue[-1].timestamp_end_sec
                else:
                    start_sec = 0.0
                    end_sec = 0.0

                # Convert dialogue objects to dicts for payload
                dialogue_payload = [d.model_dump() for d in clip.dialogue]

                # Convert string ID to UUID for Qdrant compatibility
                clip_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, clip.clip_id))

                segment_data = {
                    "id": clip_uuid, # Qdrant requires UUID or int
                    "clip_id": clip.clip_id, # Store original ID in payload
                    "scene_id": scene.scene_id,
                    "location": scene.scene_description.location,
                    "int_ext": scene.scene_description.int_ext,
                    "time_of_day": scene.scene_description.time_of_day,
                    "actors": clip.actors_involved,
                    "clip_description": clip.clip_description,
                    "dialogue": dialogue_payload,
                    "start": start_sec,
                    "end": end_sec,
                    # We store the combined text in payload too, or just the raw text components
                    "text": text_to_embed 
                }
                
                segments_to_add.append(segment_data)
                texts_to_embed.append(text_to_embed)

        if not segments_to_add:
            return {"message": "No clips to index."}

        # Generate embeddings
        embeddings = model_service.get_embedding(texts_to_embed)
        
        # Add to Vector DB
        vector_db.add_segments(segments_to_add, embeddings)
        
        duration = time.time() - start_time
        return {"message": f"Successfully indexed {len(segments_to_add)} clips in {duration:.2f} seconds."}

    except Exception as e:
        logger.error(f"Indexing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post(f"{settings.API_V1_STR}/search", response_model=list[SearchResult])
async def search_footage(request: SearchRequest):
    """
    Search for footage segments using natural language query.
    """
    try:
        # 1. Embed Query
        query_embedding = model_service.get_embedding(request.query)
        
        # 2. Vector Search (Get more results than needed for reranking)
        initial_k = request.limit * 3
        search_results = vector_db.search(query_embedding, n_results=initial_k)
        
        if not search_results:
            return []

        # Flatten results for reranking
        candidates = []
        
        for point in search_results:
            # point is a ScoredPoint object with id, version, score, payload, vector
            candidates.append({
                "id": point.id,
                "text": point.payload.get("text"),
                "metadata": point.payload
            })

        # 3. Rerank
        candidate_texts = [c["text"] for c in candidates]
        rerank_scores = model_service.rerank(request.query, candidate_texts)
        
        # 4. Format Results
        final_results = []
        for idx, score in rerank_scores[:request.limit]:
            candidate = candidates[idx]
            meta = candidate["metadata"]
            
            # Label confidence
            confidence = "Low"
            if score > 0.7: confidence = "High"
            elif score > 0.4: confidence = "Medium"

            final_results.append(SearchResult(
                clip_id=meta.get("clip_id", "unknown"), # Correctly map from metadata payload
                video_id=meta.get("scene_id", "unknown"), # Mapping scene_id to video_id for now
                start=meta.get("start", 0.0),
                end=meta.get("end", 0.0),
                text=candidate["text"], # This is the full embedded text block
                score=float(score),
                confidence=confidence,
                metadata=meta # Pass full metadata if needed by frontend
            ))
            
        return final_results

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post(f"{settings.API_V1_STR}/explain")
async def explain_search(request: SearchRequest):
    """
    Search and provide an LLM explanation of the results.
    """
    results = await search_footage(request)
    
    context = "\n".join([f"- [{r.video_id} {r.start}-{r.end}] {r.text}" for r in results])
    explanation = llm_service.generate_response(request.query, context)
    
    return {
        "results": results,
        "explanation": explanation
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
