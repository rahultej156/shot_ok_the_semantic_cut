from pydantic import BaseModel
from typing import List, Optional, Any

class Dialogue(BaseModel):
    timestamp_start_sec: float
    timestamp_end_sec: float
    actor: str
    text: str

class ClipDescription(BaseModel):
    # Depending on format, text can be list or string. 
    # Example file has string list. We will handle joining in logic or model.
    pass 

class Clip(BaseModel):
    clip_id: str
    clip_description: List[str]
    actors_involved: List[str]
    dialogue: List[Dialogue] = []

class SceneDescription(BaseModel):
    int_ext: str
    location: str
    time_of_day: str
    actors_involved: List[str]

class Scene(BaseModel):
    scene_id: str
    scene_description: SceneDescription
    clips: List[Clip]

class SearchRequest(BaseModel):
    query: str
    limit: int = 10

class SearchResult(BaseModel):
    clip_id: str
    video_id: Optional[str] = None # Keeping for compatibility if needed, though clip_id is primary
    start: float
    end: float
    text: str
    score: float
    confidence: Optional[str] = None
    metadata: Optional[Any] = None

class IndexRequest(BaseModel):
    scenes: List[Scene]
    recreate_collection: bool = False
