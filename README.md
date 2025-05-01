# VitaGuardian: AI-Driven Disaster Preparedness and Response Assistant

## 🧩 Overview
VitaGuardian is a multi-agent AI system that empowers individuals during disasters by offering real-time, location-aware, and personalized support through a conversational interface. It handles both pre-disaster readiness and emergency response using geospatial data, AI insights, and structured workflows.
It’s a real-time, life-aware assistant that adapts to  —  user health,  mobility,  location.

Whether it’s helping to prepare in advance or act fast in chaos, disaster response should be personal, instant, and reliable.
---

## 💡 Key Features
- **Conversational Chat UI:** Seamless interaction for both preparedness and emergency scenarios
- **Personalized Readiness:** Based on health, mobility, medical dependencies, and more
- **Live Response and historical data analysis:** Informed by FEMA disaster data, NOAA weather alerts, and uploaded images
- **Location-Aware Navigation:** Suggests nearest shelters using Azure Maps and FEMA data
- **Image Understanding:** Accepts photos of user environment to interpret smoke, fire, or hazards
- **Profile Customization:** Dynamic profile editing supported within the session, suggestions based on health conditions, mobility and responsibilities.

---

## 🧠 Architecture Summary

![image](https://github.com/user-attachments/assets/835a507f-cc2c-462b-9092-f6b0c633f940)

### 👤 Input Preparer Agent
- Enriches user query with geolocation, county, and state metadata
- Initializes personal profile and image bytes

### 🧠 Level 2 Agents (Run in Parallel)
- **Readiness Agent**: Offers tips and checklists tailored to profile before disasters
- **First Response Agent**: Crafts real-time safety plan using FEMA and NOAA data
- **Navigation Agent**: Uses Azure Maps, shelter databases to suggest safe locations and directions
- **Visual Agent**: Analyzes uploaded images (e.g., smoke or flooding)

### 🤖 Supervisor Agent
- Aggregates responses from all agents
- Synthesizes a final user-facing message with structured JSON output

---

## 🌍 Data Sources and APIs
- **NOAA Alerts API**: [https://api.weather.gov/alerts/active?point](https://api.weather.gov/alerts/active?point) - disaster and weather event tracking by geolocation
- **FEMA Disaster Recovery Centers**: Location and status of disaster support centers
- **Red Cross Shelter Feeds**: (When available) for shelter info
- **Azure Maps**: Reverse geocoding and location-aware search
- **OpenAI GPT-4o (via Azure)**: Used to power decision making and outputs

---

## 💬 User Interface
Built using pure HTML, CSS, and JavaScript:
- **Stage 1:** Profile Form for input (age, health, dependencies)
- **Stage 2:** Chat interface to talk with VitaGuardian
- **Extras:** Upload image, edit profile anytime, receive Google Maps links

---


---



## 🧪 Future Enhancements
- Indoor Navigation Support
Use building blueprints and BLE beacons for guiding users within complex structures (e.g., hospitals, malls, shelters).

- Community Network Layer
Enable real-time peer-to-peer coordination (e.g., help from nearby individuals, safe meetups, updates from locals).

- Multilingual Support
Expand accessibility by supporting regional and international languages in both UI and response generation.

- Offline Fallback Mode
Cache critical safety steps and maps locally so the app remains helpful even without connectivity.

---



##  Setup & Execution

###  1. Clone the Repository
```bash
git clone https://github.com/your-username/vita-guardian.git
cd vita-guardian
```

###  2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate     # For Windows
```

###  3. Install Dependencies
```bash
pip install -r requirements.txt
```

###  4. Set Environment Variables
Create a `.env` file in the root with the following:
```
OPENAI_API_KEY=your_openai_key
AZURE_MAPS_KEY=your_azure_maps_key
```

###  5. Start the Backend (FastAPI)
```bash
uvicorn main:app --reload
```

###  6. Run Frontend
Open `index.html` in a browser  
**OR** serve locally with:
```bash
python -m http.server 8080
```

Then visit: [http://localhost:8080](http://localhost:8080) 


