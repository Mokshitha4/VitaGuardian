from FEMA_NOAA_data import fema_search, noaa_search
from typing import Dict, Any
from call_llm import call_gpt_chat
from live_updates import fetch_live_disaster_info

def first_response_agent(state: str, county_name: str,
                         lat: float, lon: float,
                         personal_profile: Dict[str, Any],
                         ) -> Dict[str, Any]:
    
    llm = call_gpt_chat
    fetch_alert_fn = fetch_live_disaster_info
    # 1. Fetch live alert from api.weather.gov or other source
#     fake_alert = {
#     "event": "Severe Thunderstorm Warning",
#     "headline": "Severe Thunderstorm Warning issued April 30 at 7:20 PM EDT until 8:00 PM EDT",
#     "description": "Wind gusts up to 60 mph and hail are expected. Seek shelter immediately.",
#     "instruction": "Take cover now. Stay away from windows."
# }
    # live_alert= fake_alert
    
    live_alert = fetch_alert_fn(lat, lon)
    alert_summary = live_alert.get("headline", "No active alert found.")
    hazard_type = live_alert.get("event", "Unknown Event")

    # 2. Historical context
    fema_info = fema_search(state, county_name)
    noaa_info = noaa_search(state, county_name)

    # 3. Expanded profile description for GPT
    profile_desc = (
        f"User profile:\n"
        f"- Age: {personal_profile.get('age')}\n"
        f"- Has asthma: {personal_profile.get('has_asthma')}\n"
        f"- Can walk long distance: {personal_profile.get('can_walk_long')}\n"
        f"- House type: {personal_profile.get('house_type')}\n"
        f"- Dependents: {', '.join(personal_profile.get('dependents', [])) or 'None'}\n"
        f"- Medical dependencies: {', '.join(personal_profile.get('medical_dependencies', [])) or 'None'}\n"
        f"- Home exit difficulty: {personal_profile.get('exit_difficulty', 'None')}\n"
        f"- Communication access: {personal_profile.get('communication_access', 'Normal')}\n"
        f"- Power dependency: {personal_profile.get('power_dependency', 'None')}\n"
    )

    # 4. Prompt content
    prompt_content = f"""
A disaster alert is currently active in {county_name.title()} County, {state.upper()}.
The alert reads: "{alert_summary}"
Hazard type: {hazard_type}

Here is the user’s profile:
{profile_desc}

Historical data for this county:
- FEMA reports (past 15 years): {fema_info['top_incidents']}
- NOAA reports (last 10 years): {noaa_info['top_events']}
- Hazards with past fatalities: {noaa_info['fatal_event_counts']}

Generate a 3-part **IMMEDIATE ACTION PLAN** for this user:
1. What is happening and what risks it poses based on the alert and history
2. Immediate next steps for the user (evacuation or staying in the same place, supplies, shelter)
3. Additional safety instructions considering their medical, mobility, and power needs
"""

    if llm:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a real-time emergency assistant. Your task is to help people during disasters by providing "
                    "accurate, customized, and life-saving instructions based on their medical needs, mobility, and living conditions. "
                    "Be clear, concise, and specific in all instructions. Avoid general advice."
                )
            },
            {"role": "user", "content": prompt_content.strip()}
        ]
        response = llm(messages)
        return {
            "live_alert": live_alert,
            "fema_summary": fema_info,
            "noaa_summary": noaa_info,
            "personal_profile": personal_profile,
            "first_response_plan": response
        }
    else:
        return {
            "live_alert": live_alert,
            "fema_summary": fema_info,
            "noaa_summary": noaa_info,
            "personal_profile": personal_profile,
            "first_response_plan": prompt_content.strip()
        }


# Example usage:
# response = first_response_agent(
#     state="PA",
#     county_name="Allegheny",
#     county_fips="003",
#     lat=40.4406,
#     lon=-79.9959,
#     personal_profile={
#         "age": 68,
#         "has_asthma": False,
#         "can_walk_long": False,
#         "house_type": "apartment",
#         "dependents": [],
#         "medical_dependencies": ["blood thinner"],
#         "exit_difficulty": "elevator only",
#         "communication_access": "hearing impaired",
#         "power_dependency": "CPAP machine"
#     }
# )

# print(response)