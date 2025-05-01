import requests, datetime, json
from typing import Dict, List, Any
from langchain.tools import StructuredTool

# NOAA / NWS CAP endpoint – filters alerts that cover a single point
ENDPOINT_TEMPLATE = "https://api.weather.gov/alerts/active?point={lat},{lon}"

def fetch_live_disaster_info(
    lat: float,
    lon: float,
    max_alerts: int = 5
) -> Dict[str, Any]:
    """
    Retrieve up-to-date disaster alerts for a specific lat/lon.

    Returns JSON:
        {
            "alerts": [
              {
                "event": "Wildfire Warning",
                "severity": "Severe",
                "headline": "Wildfire Warning issued July 30 at 3:42 PM MDT",
                "instruction": "Evacuate immediately …",
                "effective": "2025-07-30T21:42:00Z",
                "expires":   "2025-07-31T03:00:00Z",
                "areas":     "Coconino County; Yavapai County"
              },
              …
            ],
            "source": "NOAA/NWS api.weather.gov"
        }
    """
    url = ENDPOINT_TEMPLATE.format(lat=lat, lon=lon)
    headers = { "User-Agent": "VitaGuardian/1.0 (github.com/your-repo)" }

    try:
        resp = requests.get(url, headers=headers, timeout=7)
        resp.raise_for_status()
    except requests.RequestException as e:
        print('Error')
        return {
            "alerts": [],
            "error": f"Failed to reach NOAA API ({e})",
            "source": "NOAA/NWS api.weather.gov"
        }

    features: List[Dict[str, Any]] = resp.json().get("features", [])
    if not features:
        return { "alerts": [], "source": "NOAA/NWS api.weather.gov" }

    # Normalise & trim
    cleaned: List[Dict[str, Any]] = []
    for feat in features[:max_alerts]:
        prop = feat["properties"]
        cleaned.append({
            "event":      prop.get("event"),
            "severity":   prop.get("severity"),
            "headline":   prop.get("headline"),
            "instruction":prop.get("instruction"),
            "effective":  prop.get("effective"),
            "expires":    prop.get("expires"),
            "areas":      prop.get("areaDesc")
        })

    return { "alerts": cleaned, "source": "NOAA/NWS api.weather.gov" }


# Wrap as a LangChain StructuredTool
disaster_live_tool = StructuredTool.from_function(
    name        = "live_disaster_alerts",
    description = (
        "Fetch real-time NOAA/NWS alerts that cover the user’s coordinates. "
        "Returns up to `max_alerts` structured alert objects."
    ),
    func        = fetch_live_disaster_info
)

# Example usage:
# alerts_info = fetch_live_disaster_info(25.7617, -80.1918)
# print(alerts_info)