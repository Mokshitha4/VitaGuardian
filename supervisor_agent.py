from typing import Dict, Any
from call_llm import call_gpt_chat
from langchain_core.runnables import RunnableLambda

SUPERVISOR_PROMPT = """
You are VitaGuardian, a smart AI assistant designed to protect and guide users during disasters.

You have received results from 3 to 4 specialist agents:

1. Readiness Agent: Uses historical FEMA/NOAA data and personal profile to generate a pre-disaster checklist.
2. First Response Agent: Analyzes live alerts and user needs to give urgent safety instructions.
3. Navigation Agent: Identifies shelters and gives a walking route considering weather and environmental hazards.
4. Visual Agent (optional only when image input is given): Analyzes the uploaded image of surroundings to detect dangers and guide response.

Your task is to synthesize these into **one coherent message** that is:
- Calm and empathetic
- Prioritized and structured
- Personalized to the user

Respond in this JSON structure:
{
"Current Situation": "<current situation summary>",
"Safety Instructions": "<safety instructions>",
"Where to Go": "<where to go as a {'information':, 'location':<lat, lon>}">",
"Additional Tips": "<additional tips>"
}
"""

def supervisor_agent(state: dict) -> dict:
    print(state)
    readiness = state.readiness_result
    first_response = state.first_response_result
    navigation = state.navigation_result
    visual = state.visual_result

    full_context = f"""
The user has requested disaster-related help. Below is a summary of what each agent provided:

👤 **User Query**:
{state.user_query}

---

**Readiness Agent**:
{readiness}

**First Response Agent**:
{first_response}

**Navigation Agent**:
{navigation}

**Visual Agent**:
{visual}
"""

    messages = [
        {"role": "system", "content": SUPERVISOR_PROMPT},
        {"role": "user", "content": full_context}
    ]

    response = call_gpt_chat(messages)  # your custom function
    print("Supervisor response:", response)
    return {
        "supervisor_summary": response,
    }
