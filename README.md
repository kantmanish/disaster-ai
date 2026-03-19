# 🚨 Intelligent Disaster Management System

> An Integrated AI Framework for Real-Time Disaster Detection and Response Optimization

**By Manish Kant (24CS2025) 
B.Tech Computer Science — AI Project | 2025–2026

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://disaster-ai-zf6ayb3rv7xjosoura93xf.streamlit.app)

---

## 🌐 Live Demo

**👉 [https://disaster-ai-zf6ayb3rv7xjosoura93xf.streamlit.app](https://disaster-ai-zf6ayb3rv7xjosoura93xf.streamlit.app)**

Open the link → go to **Tab 1** → press **▶ Start** in the sidebar to see the live simulation.

---

## 📌 About the Project

Natural disasters like floods, wildfires, and landslides cause massive loss of life every year. Many regions lack a unified platform that can detect disasters early and coordinate an automated response.

This project builds a complete end-to-end AI pipeline that:
- **Detects** disasters from satellite images using a CNN
- **Generates alerts** using a Decision Tree (RED / ORANGE / YELLOW / GREEN)
- **Filters false alarms** using KNN by comparing to historical events
- **Computes evacuation routes** using the A* search algorithm
- **Displays risk zones** on an interactive India disaster heatmap

---

## 🤖 AI Modules

| Module | Algorithm | Accuracy | Purpose |
|--------|-----------|----------|---------|
| 1 | Convolutional Neural Network (CNN) | 100% | Classifies satellite images into flood / wildfire / landslide / normal |
| 2 | Decision Tree | 99% | Generates RED / ORANGE / YELLOW / GREEN alert levels |
| 3 | K-Nearest Neighbours (KNN, k=5) | 99% | Validates alerts against historical records to reduce false alarms |
| 4 | A* Search Algorithm | Optimal | Computes safest evacuation route avoiding obstacles and danger zones |

---

## 🖥️ App Features

### Tab 1 — 🔴 Live Simulation
- Auto-cycles through disaster scenarios every 1.5 / 3 / 5 seconds
- Shows satellite image, CNN prediction, alert level, A* evacuation route
- Live event log with timestamps and locations
- Counters for total events scanned and RED alerts issued
- Speed control and Stop/Start buttons in sidebar

### Tab 2 — 🗺 India Heatmap
- Interactive dark-theme map of India built with Folium
- 18 disaster-prone zones visualised with heat intensity
- Clickable city markers showing disaster type and alert level
- Active alert table with city, state, type, and recommended action

### Tab 3 — 📊 System Info
- Full architecture table with accuracy metrics
- Team details and roll numbers
- Complete technology stack

---

## 🔧 Tech Stack

| Category | Tools |
|----------|-------|
| Deep Learning | PyTorch, torchvision |
| Machine Learning | scikit-learn |
| Data | NumPy, Pandas |
| Visualisation | Matplotlib, Folium, streamlit-folium |
| Web App | Streamlit |
| Development | Google Colab (GPU) |
| Deployment | Streamlit Cloud |

---

## 📁 Project Structure

```
disaster-ai/
├── disaster_app.py       ← Main Streamlit application
├── requirements.txt      ← Python dependencies
└── README.md             ← This file
```

---

## 🚀 Run Locally

**Step 1 — Clone the repository**
```bash
git clone https://github.com/kantmanish/disaster-ai.git
cd disaster-ai
```

**Step 2 — Create a virtual environment**
```bash
conda create -n disasterai python=3.10
conda activate disasterai
```

**Step 3 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 4 — Run the app**
```bash
streamlit run disaster_app.py
```

**Step 5 — Open in browser**
```
http://localhost:8501
```

---

## 📊 Results

| Metric | Value |
|--------|-------|
| CNN classification accuracy | 100% |
| Decision Tree alert accuracy | 99% |
| KNN false alarm filter accuracy | 99% |
| A* route optimality | Guaranteed optimal |
| Pipeline execution time | < 2 seconds per event |
| Disaster classes detected | 4 (flood, wildfire, landslide, normal) |
| Alert levels | 4 (RED, ORANGE, YELLOW, GREEN) |
| India zones monitored | 18 |

---

## 🗺️ How the Pipeline Works

```
Satellite Image
      │
      ▼
┌─────────────┐
│  CNN Model  │  →  Detects: Flood / Wildfire / Landslide / Normal
└─────────────┘
      │
      ▼
┌──────────────────┐
│  Decision Tree   │  →  Generates: RED / ORANGE / YELLOW / GREEN
└──────────────────┘
      │
      ▼
┌─────────────┐
│  KNN Filter │  →  Validates alert using 5 nearest historical events
└─────────────┘
      │
      ▼
┌──────────────┐
│  A* Router   │  →  Computes optimal evacuation path on grid map
└──────────────┘
      │
      ▼
   Alert + Route sent to rescue teams
```

---

## 🔮 Future Work

- Train CNN on real satellite data (Sentinel-2, NASA FIRMS)
- Integrate live weather API (OpenWeatherMap / IMD)
- Replace grid map with real road network (OpenStreetMap + Dijkstra)
- Add SMS/push alerts via Twilio when RED alert fires
- Extend to detect cyclones and earthquakes
- Fine-tune pretrained ResNet-50 for higher accuracy on real imagery

---

## 📚 References

1. LeCun et al. (1998) — Gradient-based learning applied to document recognition
2. Breiman et al. (1984) — Classification and Regression Trees
3. Cover & Hart (1967) — Nearest Neighbor Pattern Classification
4. Hart, Nilsson & Raphael (1968) — A Formal Basis for the A* Algorithm
5. Paszke et al. (2019) — PyTorch: An imperative style deep learning library
6. Pedregosa et al. (2011) — Scikit-learn: Machine learning in Python

---



## 📄 License

This project was developed for academic purposes as part of the B.Tech Computer Science AI curriculum.

---

*Built with ❤️ using Python, PyTorch, and Streamlit*
