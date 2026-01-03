# Hackathon Presentation Guide: Delhi Water-Logging Platform

This guide will help you present the platform to the judges effectively.

## 1. Preparation (Run these before the judges arrive)

### Terminal 1: Backend
```bash
cd backend
# Database should be running (docker-compose up -d)
python main.py
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

### Browser
Open [http://localhost:3000](http://localhost:3000)

---

## 2. Presentation Flow (The "Judge's Journey")

### Step 1: The Vision (Landing Page/Map)
*   **Show**: The main Map view.
*   **Pitch**: "Judges, this is the Delhi Water-Logging Hotspot Platform. We've combined crowdsourced civic reporting with GIS predictive analytics to help the city prepare for monsoons."
*   **Highlight**: Point out the different markers (reports) and the Ward Heatmap (ML-generated risk zones).

### Step 2: Citizen Empowerment (Add a Report)
*   **Action**: Go to "Report Incident".
*   **Talk**: "Anyone can report an incident. Our app automatically captures GPS coordinates. We'll add a title, severity (High), and even a photo."
*   **Action**: Submit the report.
*   **Talk**: "The report is now live, visible to authorities and other citizens who can upvote it to verify its urgency."

### Step 3: Predictive Analytics (Analytics Tab)
*   **Action**: Navigate to "Ward Analytics".
*   **Talk**: "We don't just wait for reports. Our ML model processes SRTM elevation data and terrain slope. Wards in low-lying areas or with poor drainage get higher risk scores automatically."
*   **Highlight**: Click a high-risk ward to show the specific recommendation (e.g., "Critical: Deploy emergency units").

### Step 4: Authority Action (Authority Dashboard)
*   **Action**: Login as Authority (`authority@example.com` / `password123`).
*   **Talk**: "Authorities have a command center. They can see the incoming reports, assign them to agencies like PWD or MCD, and update the status in real-time."
*   **Action**: Select a report, change status to "In Progress" or "Resolved".
*   **Talk**: "This creates a full audit trail of the city's response."

---

## 3. Technical Talking Points (Key Buzzwords)
*   **Spatial Intelligence**: "We use **PostGIS** for high-performance spatial queries, indexing millions of coordinates."
*   **Modern Stack**: "**FastAPI** for an async, high-performance backend and **React** for a premium, responsive UI."
*   **Explainable AI**: "Our risk model isn't a black box; it's based on physical geography—**elevation** and **slope**—making it actionable for engineers."
*   **Civic Engagement**: "Crowdsourced verification ensures the most critical issues rise to the top."

## 4. Troubleshooting
*   If the map doesn't load markers: Check if the Backend terminal shows any errors.
*   If login fails: Ensure you ran `python scripts/seed_data.py`.
