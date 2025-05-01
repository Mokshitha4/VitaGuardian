from FEMA_NOAA_data import fema_search, noaa_search
from typing import Dict, Any
from call_llm import call_gpt_chat

def readiness_planner_agent(state: str, county_name: str,
                            personal_profile: Dict[str, Any]) -> Dict[str, Any]:
    llm = call_gpt_chat
    fema_info = fema_search(state, county_name)
    noaa_info = noaa_search(state, county_name)

    # Format personal profile as string
    profile_desc = (
        f"User profile:\n"
        f"- Age: {personal_profile.get('age')}\n"
        f"- Has asthma: {personal_profile.get('has_asthma')}\n"
        f"- Can walk long distance: {personal_profile.get('can_walk_long')}\n"
        f"- House type: {personal_profile.get('house_type')}\n"
        f"- Dependents: {', '.join(personal_profile.get('dependents', [])) or 'None'}\n"
    )

    # Compose prompt content
    prompt_content = f"""
    The user lives in {county_name.title()} County, {state.upper()}.
    Here is their profile:
    {profile_desc}

    Based on historical data:
    - FEMA reports (past 15 years): {fema_info['top_incidents']}
    - NOAA reports (last 10 years): {noaa_info['top_events']}
    - Hazards with past fatalities: {noaa_info['fatal_event_counts']}

    Generate a 3-part readiness checklist for this user:
    1. Most likely hazards they should prepare for
    2. Customized emergency supplies and medicine based on their condition
    3. Shelter or evacuation recommendations based on age, mobility, and dependents
    """
    system_message = {
        "role": "system",
        "content": (
            "You are a highly reliable and detail-oriented disaster preparedness expert. "
            "Your job is to analyze historical disaster data, understand individual user needs, "
            "and generate personalized emergency readiness checklists.\n\n"
            "Consider the user's location, medical conditions, age, mobility, and housing situation. "
            "You must prioritize hazards based on both frequency and severity (including fatalities). "
            "Make your checklist concise, specific, and life-saving.\n\n"
            "Structure your response clearly into 3 sections:\n"
            "1. Most likely hazards to prepare for\n"
            "2. Emergency supplies and medications based on user profile\n"
            "3. Evacuation or shelter tips appropriate to the user's situation"
            "Make sure to use pronouns instead of using 'user' and sound friendly.\n\n"
        )
    }

    if llm:
        messages = [
            system_message,
            {"role": "user", "content": prompt_content.strip()}
        ]
        response = llm(messages)
        return {
            "fema_summary": fema_info,
            "noaa_summary": noaa_info,
            "personal_profile": personal_profile,
            "readiness_plan": response
        }
    else:
        return {
            "fema_summary": fema_info,
            "noaa_summary": noaa_info,
            "personal_profile": personal_profile,
            "readiness_plan": prompt_content.strip()
        }

# example usage:
# response = readiness_planner_agent(
#     state="CA",
#     county_name="Butte",
#     personal_profile={
#         "age": 65,
#         "has_asthma": True,
#         "can_walk_long": False,
#         "house_type": "mobile home",
#         "dependents": ["grandchild"]
#     }
# )

# print(response)