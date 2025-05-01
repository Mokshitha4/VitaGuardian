image_prompt = """
You are an expert visual disaster analyst helping people in emergencies.

The user has uploaded an image of their current surroundings during a potential disaster situation. Analyze the image to identify visible risks and suggest immediate safety actions.

Consider:
- What hazard (fire, flood, building collapse, etc.) may be happening?
- Is evacuation necessary? What type of shelter or help might be needed?
- What are the most urgent steps the user should take?
- What items or information should they gather immediately?

Respond with a short, empathetic, and clear set of next steps tailored to what you visually detect.
"""
from call_llm import call_gpt_chat
import base64

def analyze_disaster_image(image_path):
        if image_path is None:
            return "No image provided for analysis."
        encoded_image = base64.b64encode(open(image_path, 'rb').read()).decode('ascii')
        messages=[
            {"role": "system", "content": image_prompt},
            {"role": "user",  "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}"
                }
            }]}
        ]
        response = call_gpt_chat(messages=messages)
        return response

# Example usage:
# print(analyze_disaster_image("images/fire.png"))
