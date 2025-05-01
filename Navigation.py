# tools/live_disaster_context.py
import requests, datetime, json
from langchain.tools import StructuredTool
from typing import Dict, List, Any
from live_updates import fetch_live_disaster_info
from langchain.tools import StructuredTool
import os
from dotenv import load_dotenv
load_dotenv()

NWS_ALERT_POINT   = "https://api.weather.gov/alerts/active?point={lat},{lon}"
NWS_POINT_FORECAST= "https://api.weather.gov/points/{lat},{lon}"
AZURE_MAP_REVERSE = "https://atlas.microsoft.com/search/address/reverse/json"

AZ_KEY  = os.getenv('AZURE_MAP_KEY')

def get_alerts(lat, lon):
    j = requests.get(NWS_ALERT_POINT.format(lat=lat, lon=lon),
                     headers={"User-Agent":"VitaGuardian/1.0"}).json()
    return [{
        "event":p["properties"]["event"],
        "severity":p["properties"]["severity"],
        "headline":p["properties"]["headline"],
        "instruction":p["properties"]["instruction"]
    } for p in j.get("features", [])[:3]]

def get_env(lat, lon):
    # Wind / temp via NWS forecast grid-point metadata
    meta = requests.get(NWS_POINT_FORECAST.format(lat=lat, lon=lon),
                        headers={"User-Agent":"VitaGuardian/1.0"}).json()
    print(meta)
    station_url = meta["properties"]["observationStations"]
    print(station_url)
    obs         = requests.get(station_url, headers={"User-Agent":"VitaGuardian/1.0"}).json()
    props       = obs["features"][0]["properties"]
    if "temperature" in props:
      temp_c      = props["temperature"]["value"]
    else:
      temp_c      = None
    if "windDirection" in props:
      wind_dir    = props["windDirection"]["value"]
    else:
      wind_dir    = None
    if "windSpeed" in props:
      wind_spd    = props["windSpeed"]["value"]
    else:
      wind_spd    = None
    return dict(wind_dir=wind_dir, wind_kph=wind_spd, temp_c=temp_c)

def haversine(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2
    R=6371; dlat=radians(lat2-lat1); dlon=radians(lon2-lon1)
    a=sin(dlat/2)**2+cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return R*2*atan2(sqrt(a), sqrt(1-a))

import requests

def search_azure_shelters(lat, lon, radius=25000, limit=5, query="community center emergency shelter "):
    AZURE_KEY = AZ_KEY 
    base_url = "https://atlas.microsoft.com/search/poi/json"
    params = {
        "api-version": "1.0",
        "subscription-key": AZURE_KEY,
        "query": query,
        "lat": lat,
        "lon": lon,
        "radius": radius,
        "limit": limit
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()

    results = []
    for item in data.get("results", []):
        results.append({
            "name": item["poi"]["name"],
            "address": item["address"]["freeformAddress"],
            "dist_km": round(item.get("dist", 0) / 1000, 2),
            "lat": item["position"]["lat"],
            "lon": item["position"]["lon"],
        })

    return results

def live_disaster_context(lat:float, lon:float)->dict:
    return {
        "alerts"  : fetch_live_disaster_info(lat, lon),
        "env"     : get_env(lat, lon),
        "community spaces": search_azure_shelters(lat, lon),
        "updated" : datetime.datetime.utcnow().isoformat()+"Z"
    }

live_disaster_context_tool = StructuredTool.from_function(
    name="live_disaster_context",
    description=("Return a JSON block containing live NOAA alerts, "
                 "current wind/temperature, and the three closest open "
                 "Red Cross shelters (with distance & capacity ratio)."),
    func=live_disaster_context
)


# print(live_disaster_context(25.7617 ,-80.1918))