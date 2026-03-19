
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import heapq
import matplotlib.pyplot as plt
import time

# ── A* for route inside simulator ────────────────────────
def heuristic(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    open_list = []
    heapq.heappush(open_list, (0, 0, start, [start]))
    visited = set()
    while open_list:
        f, g, current, path = heapq.heappop(open_list)
        if current in visited: continue
        visited.add(current)
        if current == goal: return path, g
        row, col = current
        for nr, nc in [(row-1,col),(row+1,col),(row,col-1),(row,col+1)]:
            if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]!=1 and (nr,nc) not in visited:
                ng = g + (1 if grid[nr][nc]==0 else 3)
                heapq.heappush(open_list,
                    (ng+heuristic((nr,nc),goal), ng, (nr,nc), path+[(nr,nc)]))
    return None, 0

# ── PREDICTION ENGINE ────────────────────────────────────
STATE_BASE = {
    "Assam":            {"flood":95,"wildfire":10,"landslide":60,"cyclone":20},
    "Bihar":            {"flood":92,"wildfire":5, "landslide":25,"cyclone":15},
    "Uttarakhand":      {"flood":70,"wildfire":90,"landslide":88,"cyclone":5},
    "Kerala":           {"flood":75,"wildfire":35,"landslide":88,"cyclone":45},
    "Odisha":           {"flood":80,"wildfire":40,"landslide":30,"cyclone":90},
    "Maharashtra":      {"flood":70,"wildfire":30,"landslide":50,"cyclone":55},
    "Tamil Nadu":       {"flood":65,"wildfire":20,"landslide":35,"cyclone":85},
    "West Bengal":      {"flood":85,"wildfire":10,"landslide":30,"cyclone":75},
    "Karnataka":        {"flood":55,"wildfire":65,"landslide":50,"cyclone":30},
    "Himachal Pradesh": {"flood":55,"wildfire":60,"landslide":85,"cyclone":5},
    "Sikkim":           {"flood":50,"wildfire":20,"landslide":92,"cyclone":5},
    "Rajasthan":        {"flood":20,"wildfire":15,"landslide":5, "cyclone":10},
    "Gujarat":          {"flood":50,"wildfire":20,"landslide":15,"cyclone":60},
    "Uttar Pradesh":    {"flood":75,"wildfire":10,"landslide":15,"cyclone":10},
    "Madhya Pradesh":   {"flood":45,"wildfire":35,"landslide":20,"cyclone":10},
}

DISASTER_ICONS = {
    "flood":"🌊", "wildfire":"🔥",
    "landslide":"⛰️", "cyclone":"🌀"
}

def predict_disaster(rainfall, wind, temp, humidity, slope, pop, state):
    base = STATE_BASE.get(state, STATE_BASE["Assam"])

    # Each disaster gets a dynamic score based on sliders
    flood_score = min(100, int(
        base["flood"] * 0.4 +
        rainfall * 0.35 +
        humidity * 0.15 +
        (100 - temp) * 0.1
    ))
    wildfire_score = min(100, int(
        base["wildfire"] * 0.4 +
        temp * 0.3 +
        (100 - humidity) * 0.2 +
        wind * 0.1
    ))
    landslide_score = min(100, int(
        base["landslide"] * 0.4 +
        rainfall * 0.25 +
        slope * 0.25 +
        humidity * 0.1
    ))
    cyclone_score = min(100, int(
        base["cyclone"] * 0.4 +
        wind * 0.35 +
        humidity * 0.15 +
        rainfall * 0.1
    ))

    scores = {
        "flood":     flood_score,
        "wildfire":  wildfire_score,
        "landslide": landslide_score,
        "cyclone":   cyclone_score,
    }

    top = max(scores, key=scores.get)
    top_score = scores[top]

    # Decision Tree alert logic
    if top_score >= 75 and pop > 60:
        alert, alert_css = "RED",    "alert-red"
    elif top_score >= 55 or pop > 80:
        alert, alert_css = "ORANGE", "alert-orange"
    elif top_score >= 35:
        alert, alert_css = "YELLOW", "alert-yellow"
    else:
        alert, alert_css = "GREEN",  "alert-green"

    # KNN-style confidence (how many disasters agree)
    high_risk = sum(1 for v in scores.values() if v >= 50)
    knn_conf  = min(100, int(top_score * 0.6 + high_risk * 10))

    return scores, top, top_score, alert, alert_css, knn_conf

def make_grid(disaster):
    grids = {
        "flood":    [[0,0,0,0,0,0,0,0,0,0],[0,1,1,0,0,0,1,0,0,0],[0,0,1,0,1,0,1,0,1,0],[0,0,0,0,1,0,0,0,1,0],[2,2,0,0,0,0,0,0,0,0],[2,2,2,0,0,1,1,0,0,0],[0,2,2,0,0,1,0,0,0,0],[0,0,0,0,0,0,0,1,1,0],[0,1,0,0,0,0,0,1,0,0],[0,0,0,0,0,0,0,0,0,0]],
        "wildfire": [[0,0,0,0,0,0,0,0,0,0],[0,1,0,0,0,0,0,1,0,0],[0,1,0,1,0,0,0,1,0,0],[0,0,0,1,2,2,0,0,0,0],[0,0,0,0,2,2,2,0,0,0],[0,0,1,0,2,2,2,0,1,0],[0,0,1,0,0,2,0,0,1,0],[0,0,0,0,0,0,0,0,0,0],[0,1,1,0,0,0,0,1,0,0],[0,0,0,0,0,0,0,0,0,0]],
        "landslide":[[0,0,0,0,0,0,0,0,0,0],[0,1,1,0,0,0,0,1,0,0],[0,0,1,0,0,1,0,1,0,0],[0,0,0,0,0,1,0,0,0,0],[0,0,0,1,0,0,0,0,0,0],[0,0,0,1,0,0,1,0,0,0],[0,2,0,0,0,0,1,0,0,0],[0,2,2,0,0,0,0,0,1,0],[0,0,2,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,0,0,0]],
        "cyclone":  [[0,0,0,0,0,0,0,0,0,0],[0,1,0,0,2,0,0,1,0,0],[0,1,0,0,2,0,0,1,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,1,0,0,1,0,0,0],[0,0,0,1,0,0,1,0,0,0],[0,2,0,0,0,0,0,0,0,0],[0,2,0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,0,0,0]],
    }
    return grids.get(disaster, grids["flood"])

def draw_route(grid, path):
    fig, ax = plt.subplots(figsize=(3.5, 3.5))
    vis  = np.array(grid, dtype=float)
    cmap = plt.cm.colors.ListedColormap(["#F5F5F0","#2C2C2A","#FAEEDA"])
    ax.imshow(vis, cmap=cmap, vmin=0, vmax=2)
    for x in range(11): ax.axvline(x-0.5, color="#B4B2A9", lw=0.4)
    for y in range(11): ax.axhline(y-0.5, color="#B4B2A9", lw=0.4)
    if path:
        pr = [p[0] for p in path]
        pc = [p[1] for p in path]
        ax.plot(pc, pr, color="#185FA5", lw=2.5, zorder=3)
        ax.scatter(pc[1:-1], pr[1:-1], color="#378ADD", s=15, zorder=4)
    ax.scatter(0, 0, color="#3B6D11", s=150, marker="*", zorder=5)
    ax.scatter(9, 9, color="#E24B4A", s=150, marker="*", zorder=5)
    ax.axis("off")
    plt.tight_layout(pad=0.1)
    return fig

def radar_chart(scores):
    categories = [f"{DISASTER_ICONS[k]} {k.title()}" for k in scores]
    values     = list(scores.values())
    values_closed = values + [values[0]]
    cats_closed   = categories + [categories[0]]

    fig = go.Figure(go.Scatterpolar(
        r=values_closed,
        theta=cats_closed,
        fill="toself",
        fillcolor="rgba(226,75,74,0.15)",
        line=dict(color="#E24B4A", width=2),
        marker=dict(size=6, color="#E24B4A"),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0,100],
                           tickfont=dict(size=9), gridcolor="#E8E8E8"),
            angularaxis=dict(tickfont=dict(size=11)),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=40, r=40, t=30, b=30),
        height=280,
    )
    return fig

# ── MAIN RENDER ───────────────────────────────────────────
def render():
    st.subheader("🎮 What-If Disaster Scenario Simulator")
    st.markdown("Adjust the environmental conditions below and watch the AI predict the disaster type, alert level, and evacuation route **in real time.**")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── SLIDERS ───────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🌍 Location**")
        state = st.selectbox("State", sorted(STATE_BASE.keys()), index=0,
                             key="sim_state")
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("**🌧 Rainfall intensity**")
        rainfall = st.slider("Rainfall (mm/day)", 0, 100, 40, key="sim_rain")

        st.markdown("**💨 Wind speed**")
        wind = st.slider("Wind speed (km/h)", 0, 100, 30, key="sim_wind")

        st.markdown("**🌡 Temperature**")
        temp = st.slider("Temperature (°C scale 0–100)", 0, 100, 35, key="sim_temp")

    with col2:
        st.markdown("**📊 Conditions**")
        humidity = st.slider("Humidity (%)", 0, 100, 60, key="sim_hum")

        st.markdown("**⛰ Terrain slope**")
        slope = st.slider("Slope steepness (0=flat, 100=steep)", 0, 100, 30,
                          key="sim_slope")

        st.markdown("**👥 Population density**")
        pop = st.slider("Population density (0=rural, 100=dense city)",
                        0, 100, 50, key="sim_pop")

        st.markdown("<br>", unsafe_allow_html=True)

    # ── PRESET SCENARIOS ──────────────────────────────────
    st.markdown("**⚡ Quick presets**")
    p1, p2, p3, p4, p5 = st.columns(5)

    def set_preset(r, w, t, h, sl, p):
        st.session_state.sim_rain  = r
        st.session_state.sim_wind  = w
        st.session_state.sim_temp  = t
        st.session_state.sim_hum   = h
        st.session_state.sim_slope = sl
        st.session_state.sim_pop   = p

    with p1:
        if st.button("🌊 Kerala Flood", use_container_width=True):
            set_preset(95, 25, 28, 95, 20, 65)
            st.rerun()
    with p2:
        if st.button("🔥 Uttarakhand Fire", use_container_width=True):
            set_preset(5, 40, 88, 15, 60, 30)
            st.rerun()
    with p3:
        if st.button("🌀 Odisha Cyclone", use_container_width=True):
            set_preset(80, 95, 35, 90, 10, 55)
            st.rerun()
    with p4:
        if st.button("⛰ Sikkim Landslide", use_container_width=True):
            set_preset(85, 20, 20, 90, 95, 25)
            st.rerun()
    with p5:
        if st.button("✅ Normal day", use_container_width=True):
            set_preset(10, 15, 30, 45, 15, 40)
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── RUN PREDICTION ────────────────────────────────────
    scores, top, top_score, alert, alert_css, knn_conf = predict_disaster(
        rainfall, wind, temp, humidity, slope, pop, state
    )

    alert_colors = {
        "RED":    "#E24B4A",
        "ORANGE": "#D85A30",
        "YELLOW": "#BA7517",
        "GREEN":  "#3B6D11",
    }
    alert_bg = {
        "RED":    "#FCEBEB",
        "ORANGE": "#FAECE7",
        "YELLOW": "#FAEEDA",
        "GREEN":  "#EAF3DE",
    }
    alert_emoji = {
        "RED":"🚨","ORANGE":"🔶","YELLOW":"⚠️","GREEN":"✅"
    }
    shake_style = """
        animation: shake 0.6s ease infinite, pulse-red 1.2s ease infinite;
    """ if alert == "RED" else ""

    acolor = alert_colors[alert]
    abg    = alert_bg[alert]

    # ── RESULTS HEADER ────────────────────────────────────
    st.markdown("### 🤖 AI Prediction Results")

    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown(
            f'''<div style="background:{acolor}18;border:2px solid {acolor};
            border-radius:12px;padding:16px;text-align:center;{shake_style}">
            <div style="font-size:0.8rem;color:{acolor};font-weight:500">CNN DETECTED</div>
            <div style="font-size:1.8rem">{DISASTER_ICONS[top]}</div>
            <div style="font-size:1rem;font-weight:700;color:{acolor}">{top.upper()}</div>
            <div style="font-size:0.8rem;color:{acolor}">Score: {top_score}/100</div>
            </div>''', unsafe_allow_html=True)
    with r2:
        st.markdown(
            f'''<div style="background:{acolor}18;border:2px solid {acolor};
            border-radius:12px;padding:16px;text-align:center">
            <div style="font-size:0.8rem;color:{acolor};font-weight:500">DECISION TREE ALERT</div>
            <div style="font-size:1.8rem">{alert_emoji[alert]}</div>
            <div style="font-size:1.1rem;font-weight:700;color:{acolor}">{alert}</div>
            <div style="font-size:0.8rem;color:{acolor}">Alert level</div>
            </div>''', unsafe_allow_html=True)
    with r3:
        st.markdown(
            f'''<div style="background:#1A5276 18;border:2px solid #1A5276;
            border-radius:12px;padding:16px;text-align:center">
            <div style="font-size:0.8rem;color:#1A5276;font-weight:500">KNN CONFIDENCE</div>
            <div style="font-size:1.8rem">🔍</div>
            <div style="font-size:1.1rem;font-weight:700;color:#1A5276">{knn_conf}%</div>
            <div style="font-size:0.8rem;color:#1A5276">Historical match</div>
            </div>''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CHARTS + ROUTE ────────────────────────────────────
    ch1, ch2, ch3 = st.columns(3)

    with ch1:
        st.markdown("**Disaster risk radar**")
        st.plotly_chart(radar_chart(scores),
                        use_container_width=True)

    with ch2:
        st.markdown("**Risk scores**")
        bars = go.Figure(go.Bar(
            x=[f"{DISASTER_ICONS[k]} {k.title()}" for k in scores],
            y=list(scores.values()),
            marker_color=[alert_colors.get(
                "RED" if v>=75 else "ORANGE" if v>=55 else "YELLOW" if v>=35 else "GREEN","#3B6D11"
            ) for v in scores.values()],
            text=[str(v) for v in scores.values()],
            textposition="outside",
        ))
        bars.update_layout(
            yaxis=dict(range=[0,115],gridcolor="#F1EFE8"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=5,r=5,t=10,b=5),
            height=260,
            showlegend=False,
        )
        st.plotly_chart(bars, use_container_width=True)

    with ch3:
        st.markdown("**A* evacuation route**")
        grid = make_grid(top)
        path, cost = astar(grid, (0,0), (9,9))
        fig = draw_route(grid, path)
        st.pyplot(fig, use_container_width=False)
        plt.close()
        if path:
            st.caption(f"Steps: {len(path)} · Cost: {cost}")

    # ── ACTION RECOMMENDATIONS ────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**📋 Recommended actions**")

    actions = {
        "RED": [
            f"🚨 Issue immediate evacuation order for {state}",
            "📞 Alert NDRF — National Helpline: 011-24363260",
            "🚁 Deploy aerial rescue teams to dense zones",
            "🏥 Activate all district hospitals on emergency mode",
            f"📻 Broadcast emergency alert on All India Radio",
            "🛣 Open designated relief camps immediately",
        ],
        "ORANGE": [
            f"⚠️ Put {state} SDRF on high alert",
            "📢 Issue public warning via loudspeakers",
            "🏗 Inspect bridges and weak infrastructure",
            "🚒 Pre-position fire and rescue teams",
            "📦 Stock relief camps with food and medicine",
        ],
        "YELLOW": [
            f"👁 Monitor {state} situation every 2 hours",
            "📱 Send advisory SMS to residents",
            "🌧 Track IMD weather bulletin closely",
            "🏘 Identify vulnerable households for quick evac",
        ],
        "GREEN": [
            f"✅ Routine monitoring for {state}",
            "📊 Continue data collection from sensors",
            "🗂 Update disaster preparedness plans",
        ],
    }

    for action in actions[alert]:
        st.markdown(f"- {action}")

    # ── INPUT SUMMARY ─────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📊 View input parameters used for prediction"):
        params = pd.DataFrame([{
            "Parameter": "State",             "Value": state,          "Impact": "Base risk profile"},
            {"Parameter": "Rainfall (mm/day)","Value": str(rainfall),  "Impact": "Drives flood + landslide"},
            {"Parameter": "Wind speed (km/h)","Value": str(wind),      "Impact": "Drives cyclone risk"},
            {"Parameter": "Temperature",      "Value": str(temp),      "Impact": "Drives wildfire risk"},
            {"Parameter": "Humidity (%)",     "Value": str(humidity),  "Impact": "Affects all disasters"},
            {"Parameter": "Slope steepness",  "Value": str(slope),     "Impact": "Drives landslide risk"},
            {"Parameter": "Population density","Value": str(pop),      "Impact": "Determines alert level"},
        ])
        st.dataframe(params, use_container_width=True, hide_index=True)
