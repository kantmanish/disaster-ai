
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ── INDIA DISASTER RISK DATABASE ─────────────────────────
# Based on NDMA historical disaster records
RISK_DATA = {
    "Assam":             {"flood":95,"wildfire":10,"landslide":60,"cyclone":20,"earthquake":30},
    "Bihar":             {"flood":92,"wildfire":5, "landslide":25,"cyclone":15,"earthquake":40},
    "West Bengal":       {"flood":85,"wildfire":10,"landslide":30,"cyclone":75,"earthquake":20},
    "Odisha":            {"flood":80,"wildfire":40,"landslide":30,"cyclone":90,"earthquake":20},
    "Uttarakhand":       {"flood":70,"wildfire":90,"landslide":88,"cyclone":5, "earthquake":75},
    "Himachal Pradesh":  {"flood":55,"wildfire":60,"landslide":85,"cyclone":5, "earthquake":65},
    "Sikkim":            {"flood":50,"wildfire":20,"landslide":92,"cyclone":5, "earthquake":80},
    "Kerala":            {"flood":75,"wildfire":35,"landslide":88,"cyclone":45,"earthquake":15},
    "Maharashtra":       {"flood":70,"wildfire":30,"landslide":50,"cyclone":55,"earthquake":35},
    "Tamil Nadu":        {"flood":65,"wildfire":20,"landslide":35,"cyclone":85,"earthquake":10},
    "Andhra Pradesh":    {"flood":60,"wildfire":25,"landslide":30,"cyclone":80,"earthquake":15},
    "Karnataka":         {"flood":55,"wildfire":65,"landslide":50,"cyclone":30,"earthquake":20},
    "Gujarat":           {"flood":50,"wildfire":20,"landslide":15,"cyclone":60,"earthquake":70},
    "Rajasthan":         {"flood":20,"wildfire":15,"landslide":5, "cyclone":10,"earthquake":25},
    "Madhya Pradesh":    {"flood":45,"wildfire":35,"landslide":20,"cyclone":10,"earthquake":20},
    "Uttar Pradesh":     {"flood":75,"wildfire":10,"landslide":15,"cyclone":10,"earthquake":45},
    "Jammu & Kashmir":   {"flood":60,"wildfire":30,"landslide":80,"cyclone":5, "earthquake":85},
    "Manipur":           {"flood":65,"wildfire":30,"landslide":75,"cyclone":15,"earthquake":70},
    "Meghalaya":         {"flood":70,"wildfire":20,"landslide":80,"cyclone":15,"earthquake":40},
    "Arunachal Pradesh": {"flood":65,"wildfire":25,"landslide":78,"cyclone":10,"earthquake":75},
    "Nagaland":          {"flood":55,"wildfire":30,"landslide":70,"cyclone":10,"earthquake":60},
    "Tripura":           {"flood":70,"wildfire":20,"landslide":65,"cyclone":30,"earthquake":50},
    "Mizoram":           {"flood":60,"wildfire":25,"landslide":82,"cyclone":15,"earthquake":55},
    "Telangana":         {"flood":50,"wildfire":30,"landslide":20,"cyclone":40,"earthquake":15},
    "Jharkhand":         {"flood":55,"wildfire":40,"landslide":45,"cyclone":15,"earthquake":35},
    "Chhattisgarh":      {"flood":50,"wildfire":45,"landslide":25,"cyclone":15,"earthquake":20},
    "Punjab":            {"flood":40,"wildfire":10,"landslide":10,"cyclone":5, "earthquake":35},
    "Haryana":           {"flood":35,"wildfire":10,"landslide":5, "cyclone":5, "earthquake":30},
    "Delhi":             {"flood":40,"wildfire":10,"landslide":5, "cyclone":5, "earthquake":45},
    "Goa":               {"flood":55,"wildfire":20,"landslide":40,"cyclone":50,"earthquake":10},
}

# Seasonal risk multipliers (month -> multiplier per disaster)
SEASONAL = {
    1:  {"flood":0.2,"wildfire":0.5,"landslide":0.2,"cyclone":0.3,"earthquake":1.0},  # Jan
    2:  {"flood":0.2,"wildfire":0.6,"landslide":0.2,"cyclone":0.2,"earthquake":1.0},  # Feb
    3:  {"flood":0.2,"wildfire":0.8,"landslide":0.3,"cyclone":0.3,"earthquake":1.0},  # Mar
    4:  {"flood":0.3,"wildfire":0.9,"landslide":0.4,"cyclone":0.5,"earthquake":1.0},  # Apr
    5:  {"flood":0.4,"wildfire":0.8,"landslide":0.5,"cyclone":0.7,"earthquake":1.0},  # May
    6:  {"flood":0.9,"wildfire":0.4,"landslide":0.9,"cyclone":0.6,"earthquake":1.0},  # Jun
    7:  {"flood":1.0,"wildfire":0.2,"landslide":1.0,"cyclone":0.5,"earthquake":1.0},  # Jul
    8:  {"flood":1.0,"wildfire":0.2,"landslide":1.0,"cyclone":0.6,"earthquake":1.0},  # Aug
    9:  {"flood":0.9,"wildfire":0.3,"landslide":0.9,"cyclone":0.8,"earthquake":1.0},  # Sep
    10: {"flood":0.6,"wildfire":0.4,"landslide":0.6,"cyclone":1.0,"earthquake":1.0},  # Oct
    11: {"flood":0.3,"wildfire":0.5,"landslide":0.3,"cyclone":0.9,"earthquake":1.0},  # Nov
    12: {"flood":0.2,"wildfire":0.5,"landslide":0.2,"cyclone":0.4,"earthquake":1.0},  # Dec
}

MONTH_NAMES = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
               7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}

DISASTER_ICONS = {
    "flood":"🌊","wildfire":"🔥","landslide":"⛰️","cyclone":"🌀","earthquake":"🌍"
}

PRECAUTIONS = {
    "flood": [
        "Move to higher ground immediately",
        "Store drinking water and dry food for 3 days",
        "Keep documents in waterproof bags",
        "Avoid walking in moving water",
        "Call NDRF: 011-24363260",
        "Follow State Disaster Management Authority alerts",
    ],
    "wildfire": [
        "Evacuate if authorities order it",
        "Close all windows and doors",
        "Remove dry leaves and debris near home",
        "Keep buckets of water ready",
        "Cover nose and mouth with wet cloth",
        "Call Forest Department helpline: 1926",
    ],
    "landslide": [
        "Stay away from slopes and hillsides",
        "Watch for cracks or bulges in roads",
        "Avoid river valleys during heavy rain",
        "Evacuate to designated relief camps",
        "Keep emergency kit ready",
        "Call SDRF helpline in your state",
    ],
    "cyclone": [
        "Move away from coastal areas",
        "Reinforce your home doors and windows",
        "Store 3 days of food and water",
        "Unplug electrical appliances",
        "Follow IMD cyclone warnings closely",
        "Call IMD helpline: 1800-180-1717",
    ],
    "earthquake": [
        "Drop, cover, and hold on during shaking",
        "Stay away from windows and heavy furniture",
        "After shaking stops, exit building carefully",
        "Check for gas leaks before switching lights",
        "Expect aftershocks",
        "Call emergency services: 112",
    ],
}

def calculate_risk(state, month):
    if state not in RISK_DATA:
        return None
    base  = RISK_DATA[state]
    multi = SEASONAL[month]
    scores = {d: min(100, int(base[d] * multi[d])) for d in base}
    overall = min(100, int(sum(scores.values()) / len(scores) * 1.4))
    return scores, overall

def risk_color(score):
    if score >= 70: return "#E24B4A", "HIGH RISK"
    if score >= 40: return "#D85A30", "MODERATE RISK"
    if score >= 20: return "#BA7517", "LOW-MODERATE"
    return "#3B6D11", "LOW RISK"

def gauge_chart(overall, state):
    color, label = risk_color(overall)
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=overall,
        title={"text": f"Overall Risk Score<br><span style='font-size:0.85em;color:{color}'>{label}</span>",
               "font": {"size": 16}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1,
                     "tickcolor": "#888", "tickfont": {"size": 11}},
            "bar":  {"color": color, "thickness": 0.3},
            "bgcolor": "white",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  20], "color": "#EAF3DE"},
                {"range": [20, 40], "color": "#FAEEDA"},
                {"range": [40, 70], "color": "#FAECE7"},
                {"range": [70,100], "color": "#FCEBEB"},
            ],
            "threshold": {
                "line": {"color": color, "width": 4},
                "thickness": 0.8,
                "value": overall
            }
        },
        number={"suffix": "/100", "font": {"size": 28, "color": color}},
    ))
    fig.update_layout(
        height=280,
        margin=dict(l=20,r=20,t=40,b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#2C2C2A"},
    )
    return fig

def bar_chart(scores):
    disasters = list(scores.keys())
    values    = list(scores.values())
    colors    = [risk_color(v)[0] for v in values]
    labels    = [f"{DISASTER_ICONS[d]} {d.title()}" for d in disasters]

    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=colors,
        text=[f"{v}" for v in values],
        textposition="outside",
        textfont=dict(size=12),
    ))
    fig.update_layout(
        yaxis=dict(range=[0,115], title="Risk score",
                   gridcolor="#F1EFE8", tickfont=dict(size=11)),
        xaxis=dict(tickfont=dict(size=12)),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10,r=10,t=20,b=10),
        height=280,
        showlegend=False,
    )
    return fig

def render():
    st.subheader("🔢 Personal Disaster Risk Score Calculator")
    st.markdown("Enter your location and current month to see your personalised disaster risk score across all hazard types.")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        state = st.selectbox("Select your state", sorted(RISK_DATA.keys()), index=0)
    with c2:
        month = st.selectbox("Select current month",
                             list(MONTH_NAMES.values()),
                             index=2)
        month_num = list(MONTH_NAMES.values()).index(month) + 1

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔍 Calculate My Risk Score", type="primary", use_container_width=True):
        scores, overall = calculate_risk(state, month_num)
        color, label    = risk_color(overall)

        # ── Overall score header ─────────────────────────
        st.markdown(
            f"""<div style="background:{color}18;border:2px solid {color};
            border-radius:12px;padding:16px 20px;text-align:center;margin:8px 0">
            <div style="font-size:0.85rem;color:{color};font-weight:500">
            {state} &nbsp;·&nbsp; {month}</div>
            <div style="font-size:2rem;font-weight:700;color:{color}">{overall}/100</div>
            <div style="font-size:1rem;font-weight:600;color:{color}">{label}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Gauge + Bar charts ───────────────────────────
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("**Overall risk gauge**")
            st.plotly_chart(gauge_chart(overall, state),
                            use_container_width=True)
        with g2:
            st.markdown("**Risk by disaster type**")
            st.plotly_chart(bar_chart(scores),
                            use_container_width=True)

        # ── Highest risk disaster ────────────────────────
        top_disaster = max(scores, key=scores.get)
        top_score    = scores[top_disaster]
        top_color, _ = risk_color(top_score)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""<div style="background:{top_color}15;border-left:4px solid {top_color};
            border-radius:8px;padding:14px 18px;margin:8px 0">
            <strong style="color:{top_color}">
            {DISASTER_ICONS[top_disaster]} Highest risk: {top_disaster.upper()} ({top_score}/100)
            </strong><br>
            <span style="font-size:0.85rem;color:#5F5E5A">
            {state} is most vulnerable to {top_disaster}s in {month}.
            This is based on historical disaster records and seasonal patterns.
            </span></div>""", unsafe_allow_html=True)

        # ── Scores table ─────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Detailed risk breakdown**")
        rows = []
        for d, v in sorted(scores.items(), key=lambda x: -x[1]):
            c, lbl = risk_color(v)
            rows.append({
                "Disaster": f"{DISASTER_ICONS[d]} {d.title()}",
                "Score": f"{v}/100",
                "Level": lbl,
                "Season peak": "Monsoon (Jun–Sep)" if d in ["flood","landslide"]
                               else "Summer (Mar–Jun)" if d == "wildfire"
                               else "Oct–Nov" if d == "cyclone"
                               else "Any time",
            })
        st.dataframe(pd.DataFrame(rows),
                     use_container_width=True, hide_index=True)

        # ── Precautions ──────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"**{DISASTER_ICONS[top_disaster]} Precautions for {top_disaster}**")
        for p in PRECAUTIONS[top_disaster]:
            st.markdown(f"- {p}")

        # ── Compared to national average ─────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        all_overalls = []
        for s in RISK_DATA:
            _, ov = calculate_risk(s, month_num)
            all_overalls.append(ov)
        national_avg = int(sum(all_overalls) / len(all_overalls))
        diff = overall - national_avg
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        diff_color = "#E24B4A" if diff > 0 else "#3B6D11"
        st.markdown(
            f"""<div style="background:var(--color-background-secondary);
            border-radius:10px;padding:14px 18px;display:flex;
            justify-content:space-between;align-items:center">
            <span style="font-size:0.9rem;color:#5F5E5A">
            National average risk score ({month})</span>
            <span style="font-size:1.1rem;font-weight:600">
            {national_avg}/100 &nbsp;
            <span style="color:{diff_color};font-size:0.9rem">
            ({diff_str} vs your state)</span></span>
            </div>""", unsafe_allow_html=True)
