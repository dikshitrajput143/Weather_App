# Weather App (Python + Streamlit)

A simple, no-API-key weather app built with **Python**, **Streamlit**, and the free **Open‑Meteo** services.

## Features
- Search any city (uses Open‑Meteo Geocoding, no key required)
- Current conditions
- 7‑day daily forecast
- Hourly temperature chart (next 24 hours)
- Metric/Imperial units toggle

## How to Run
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the app**
   ```bash
   streamlit run app.py
   ```


   <img width="1466" height="671" alt="image" src="https://github.com/user-attachments/assets/4a12eda6-2507-4311-8a2a-3244b173dec6" />


3. Open the URL shown in the terminal (usually http://localhost:8501).

## Project Structure
```
weather_app/
├── app.py            # Streamlit UI
├── weather.py        # Core logic (geocoding + forecast)
├── requirements.txt  # Libraries
└── README.md
```

## Notes
- Data source: [Open‑Meteo](https://open-meteo.com/) (forecast + geocoding).
- Timezone is auto-detected from API; charts display your local hour labels.
- This app makes live web requests; ensure you have an active internet connection when running it locally.
