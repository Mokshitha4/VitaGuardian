# api.py
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from main import compiled_graph  # LangGraph
import base64
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    user_query: str
    lat: float
    lon: float
    personal_profile: dict

@app.get("/")
def root():
    return {"message": "Welcome to the Disaster Agent API!"}

@app.post("/run-disaster-agent/")
async def run_disaster_agent(input: UserInput):
    initial_state = {
        "user_query": input.user_query,
        "lat": input.lat,
        "lon": input.lon,
        "personal_profile": input.personal_profile,
        "image_bytes": input.Image if hasattr(input, 'Image') else None,
    }

    result = compiled_graph.invoke(initial_state)
    print(result)
    response = {'response':  json.dumps(result['supervisor_summary'])}
    print("Response sent to client:", response)
    return response
