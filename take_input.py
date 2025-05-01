import requests
import os
from dotenv import load_dotenv
load_dotenv()

AZ_KEY = os.getenv('AZURE_MAP_KEY')
def resolve_location(lat, lon):
    url = f"https://atlas.microsoft.com/search/address/reverse/json"
    params = {
        "api-version": "1.0",
        "subscription-key": AZ_KEY,
        "query": f"{lat},{lon}"
    }
    resp = requests.get(url, params=params).json()
    addr = resp["addresses"][0]["address"]
    print(addr)
    return {
        "state": addr["countrySubdivision"],  # e.g., "CA"
        "county_name": addr.get("municipalitySubdivision") or addr.get("municipality") or "Unknown",
    }

# example usage
# print(resolve_location( 37.69171, -81.63082))


def prepare_inputs(state: dict) -> dict:
    lat = state.lat
    lon = state.lon
    profile = state.personal_profile
    
    #  Reverse geocode to get state and county
    location_info = resolve_location(lat, lon)  # using Nominatim or Azure fallback

    #  Construct detailed user profile description
    profile_desc = (
        f"- Age: {profile.get('age')}\n"
        f"- Has asthma: {profile.get('has_asthma')}\n"
        f"- Can walk long distance: {profile.get('can_walk_long')}\n"
        f"- House type: {profile.get('house_type')}\n"
        f"- Dependents: {', '.join(profile.get('dependents', [])) or 'None'}\n"
        f"- Medical dependencies: {', '.join(profile.get('medical_dependencies', [])) or 'None'}\n"
        f"- Home exit difficulty: {profile.get('exit_difficulty', 'None')}\n"
        f"- Communication access: {profile.get('communication_access', 'Normal')}\n"
        f"- Power dependency: {profile.get('power_dependency', 'None')}\n"
    )
    new_state= {
        "lat": lat,
        "lon": lon,
        "state": location_info.get("state", ""),
        "county_name": location_info.get("county_name", ""),
        "personal_profile": profile,
        "formatted_profile": profile_desc,
        "user_query": state.user_query,
    }

    return new_state
