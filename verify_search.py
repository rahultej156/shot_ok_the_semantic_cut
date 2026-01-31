import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def verify_system():
    # Search Queries
    queries = [
        "Michael explaining his family",
        "tense conversation about business",
        "Kay asking about the men outside"
    ]

    print("\n--- Searching ---")
    for q in queries:
        print(f"\nQuery: '{q}'")
        try:
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/explain", json={"query": q, "limit": 3})
            
            if response.status_code == 200:
                result = response.json()
                print(f"Time: {time.time() - start_time:.4f}s")
                print("Top Result:")
                if result["results"]:
                    top = result["results"][0]
                    # Handle new metadata structure
                    meta = top.get('metadata', {})
                    video_id = top.get('video_id', 'N/A')
                    print(f"  Scene/Video: {video_id}")
                    print(f"  Clip ID: {top.get('clip_id', 'N/A')}")
                    print(f"  Location: {meta.get('location', 'N/A')}")
                    print(f"  Actors: {meta.get('actors', [])}")
                    print(f"  Score: {top['score']:.4f}")
                    print(f"  Confidence: {top['confidence']}")
                else:
                    print("  No results found.")
                
                print(f"LLM Explanation: {result.get('explanation', 'N/A')}")
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Search failed: {e}")

if __name__ == "__main__":
    verify_system()
