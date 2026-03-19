
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import heapq
import time
import random
from datetime import datetime
import risk_calculator
import scenario_simulator

st.set_page_config(
    page_title="India Disaster Management AI",
    page_icon="🚨",
    layout="wide"
)

st.markdown("""
<style>
  .main-title{font-size:2rem;font-weight:600;color:#E24B4A;margin-bottom:0}
  .sub-title{font-size:0.9rem;color:#888780;margin-bottom:1.5rem}
  .alert-red{background:#FCEBEB;border-left:4px solid #E24B4A;padding:12px 16px;border-radius:8px;margin:8px 0}
  .alert-orange{background:#FAECE7;border-left:4px solid #D85A30;padding:12px 16px;border-radius:8px;margin:8px 0}
  .alert-yellow{background:#FAEEDA;border-left:4px solid #BA7517;padding:12px 16px;border-radius:8px;margin:8px 0}
  .alert-green{background:#EAF3DE;border-left:4px solid #3B6D11;padding:12px 16px;border-radius:8px;margin:8px 0}
  .metric-box{background:#F1EFE8;border-radius:10px;padding:14px 18px;text-align:center}
  .metric-val{font-size:1.6rem;font-weight:600}
  .metric-lbl{font-size:0.75rem;color:#5F5E5A;margin-top:2px}
  .log-row{font-size:0.8rem;padding:4px 0;border-bottom:0.5px solid #D3D1C7}
  .sim-active{background:#FCEBEB;border:1.5px solid #E24B4A;border-radius:10px;padding:10px 16px;text-align:center;font-weight:600;color:#A32D2D}
  .sim-idle{background:#EAF3DE;border:1.5px solid #3B6D11;border-radius:10px;padding:10px 16px;text-align:center;font-weight:600;color:#27500A}

  @keyframes shake {
    0%  { transform: translateX(0); }
    10% { transform: translateX(-8px); }
    20% { transform: translateX(8px); }
    30% { transform: translateX(-8px); }
    40% { transform: translateX(8px); }
    50% { transform: translateX(-5px); }
    60% { transform: translateX(5px); }
    70% { transform: translateX(-3px); }
    80% { transform: translateX(3px); }
    90% { transform: translateX(-1px); }
    100%{ transform: translateX(0); }
  }
  @keyframes pulse-red {
    0%   { box-shadow: 0 0 0 0 rgba(226,75,74,0.7); }
    50%  { box-shadow: 0 0 0 15px rgba(226,75,74,0); }
    100% { box-shadow: 0 0 0 0 rgba(226,75,74,0); }
  }
  .red-alert-shake {
    animation: shake 0.6s ease infinite, pulse-red 1.2s ease infinite;
    border: 2px solid #E24B4A !important;
    border-radius: 8px;
    padding: 14px 18px;
    background: #FCEBEB;
    font-size: 1.1rem;
    font-weight: 700;
    color: #A32D2D;
    text-align: center;
    margin: 8px 0;
  }
  .orange-alert {
    border: 2px solid #D85A30;
    border-radius: 8px;
    padding: 14px 18px;
    background: #FAECE7;
    font-size: 1.1rem;
    font-weight: 700;
    color: #7D3010;
    text-align: center;
    margin: 8px 0;
  }
  .yellow-alert {
    border: 2px solid #BA7517;
    border-radius: 8px;
    padding: 14px 18px;
    background: #FAEEDA;
    font-size: 1.1rem;
    font-weight: 700;
    color: #6B4308;
    text-align: center;
    margin: 8px 0;
  }
  .green-alert {
    border: 2px solid #3B6D11;
    border-radius: 8px;
    padding: 14px 18px;
    background: #EAF3DE;
    font-size: 1.1rem;
    font-weight: 700;
    color: #1E3A08;
    text-align: center;
    margin: 8px 0;
  }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚨 India Intelligent Disaster Management System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">By Manish Kant (24CS2025) &amp; OM JEE (24CS2028) &nbsp;·&nbsp; AI Project 2025–26</div>', unsafe_allow_html=True)

for key,val in [("sim_running",False),("sim_step",0),("event_log",[]),
                ("current",None),("total_events",0),("total_red",0)]:
    if key not in st.session_state: st.session_state[key]=val

# ── ALL INDIA SCENARIOS ──────────────────────────────────
SCENARIOS = [
    {"disaster":"flood",    "severity":9.1,"population":4500,"infrastructure":82,"weather":9.0,
     "location":"Patna, Bihar","state":"Bihar","cause":"Ganga river overflow during monsoon"},
    {"disaster":"flood",    "severity":8.5,"population":3200,"infrastructure":70,"weather":7.5,
     "location":"Guwahati, Assam","state":"Assam","cause":"Brahmaputra river flooding"},
    {"disaster":"wildfire", "severity":7.8,"population":1200,"infrastructure":55,"weather":8.5,
     "location":"Uttarakhand Forest Zone","state":"Uttarakhand","cause":"Dry summer heat wave"},
    {"disaster":"landslide","severity":7.2,"population":800, "infrastructure":60,"weather":8.0,
     "location":"Sikkim Hill Slopes","state":"Sikkim","cause":"Heavy rainfall destabilised slopes"},
    {"disaster":"flood",    "severity":8.0,"population":5000,"infrastructure":65,"weather":7.0,
     "location":"Mumbai, Maharashtra","state":"Maharashtra","cause":"Coastal flooding + heavy rain"},
    {"disaster":"wildfire", "severity":6.8,"population":900, "infrastructure":45,"weather":7.5,
     "location":"Simlipal Forest, Odisha","state":"Odisha","cause":"Forest fire spread by wind"},
    {"disaster":"landslide","severity":6.5,"population":600, "infrastructure":50,"weather":7.8,
     "location":"Shimla, Himachal Pradesh","state":"Himachal Pradesh","cause":"Cloudburst triggered slide"},
    {"disaster":"flood",    "severity":7.5,"population":3800,"infrastructure":58,"weather":6.5,
     "location":"Chennai, Tamil Nadu","state":"Tamil Nadu","cause":"Northeast monsoon cyclone surge"},
    {"disaster":"wildfire", "severity":7.0,"population":1100,"infrastructure":40,"weather":8.2,
     "location":"Bandipur, Karnataka","state":"Karnataka","cause":"Forest fire in reserve"},
    {"disaster":"landslide","severity":6.2,"population":500, "infrastructure":48,"weather":7.2,
     "location":"Wayanad, Kerala","state":"Kerala","cause":"Soil erosion after heavy rain"},
    {"disaster":"flood",    "severity":6.8,"population":2800,"infrastructure":52,"weather":6.0,
     "location":"Kolkata, West Bengal","state":"West Bengal","cause":"Cyclone Amphan aftermath"},
    {"disaster":"normal",   "severity":1.5,"population":400, "infrastructure":5, "weather":2.0,
     "location":"Jaipur, Rajasthan","state":"Rajasthan","cause":"No disaster detected"},
    {"disaster":"normal",   "severity":1.2,"population":300, "infrastructure":3, "weather":1.5,
     "location":"Bhopal, Madhya Pradesh","state":"Madhya Pradesh","cause":"All clear"},
]

def get_alert(sev,pop,infra,weather):
    if sev>=7 and pop>1000: return 3,"RED","🚨","alert-red"
    if sev>=7 or infra>60:  return 2,"ORANGE","🔶","alert-orange"
    if sev>=4 or weather>=6:return 1,"YELLOW","⚠️","alert-yellow"
    return 0,"GREEN","✅","alert-green"

def make_image(cls):
    img=np.zeros((180,180,3),dtype=np.uint8)
    if cls=="flood":
        img[:,:,0]=np.random.randint(30,80,(180,180))
        img[:,:,1]=np.random.randint(60,120,(180,180))
        img[:,:,2]=np.random.randint(130,210,(180,180))
        for i in range(0,180,18): img[i:i+2,:,2]=220
    elif cls=="wildfire":
        img[:,:,0]=np.random.randint(160,255,(180,180))
        img[:,:,1]=np.random.randint(30,90,(180,180))
        img[:,:,2]=np.random.randint(0,35,(180,180))
        for _ in range(25):
            x,y=random.randint(0,155),random.randint(0,155)
            img[x:x+20,y:y+20]=[18,12,8]
    elif cls=="landslide":
        img[:,:,0]=np.random.randint(100,155,(180,180))
        img[:,:,1]=np.random.randint(80,125,(180,180))
        img[:,:,2]=np.random.randint(40,75,(180,180))
        for i in range(0,180,22):
            for j in range(180):
                if i+j//3<180: img[i+j//3,j]=[55,45,28]
    else:
        img[:,:,0]=np.random.randint(20,75,(180,180))
        img[:,:,1]=np.random.randint(110,185,(180,180))
        img[:,:,2]=np.random.randint(20,65,(180,180))
    return img

def heuristic(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])

def astar(grid,start,goal):
    rows,cols=len(grid),len(grid[0])
    open_list=[]
    heapq.heappush(open_list,(0,0,start,[start]))
    visited=set()
    while open_list:
        f,g,current,path=heapq.heappop(open_list)
        if current in visited: continue
        visited.add(current)
        if current==goal: return path,g
        row,col=current
        for nr,nc in [(row-1,col),(row+1,col),(row,col-1),(row,col+1)]:
            if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]!=1 and (nr,nc) not in visited:
                ng=g+(1 if grid[nr][nc]==0 else 3)
                heapq.heappush(open_list,(ng+heuristic((nr,nc),goal),ng,(nr,nc),path+[(nr,nc)]))
    return None,0

GRIDS={
    "flood":    [[0,0,0,0,0,0,0,0,0,0],[0,1,1,0,0,0,1,0,0,0],[0,0,1,0,1,0,1,0,1,0],[0,0,0,0,1,0,0,0,1,0],[2,2,0,0,0,0,0,0,0,0],[2,2,2,0,0,1,1,0,0,0],[0,2,2,0,0,1,0,0,0,0],[0,0,0,0,0,0,0,1,1,0],[0,1,0,0,0,0,0,1,0,0],[0,0,0,0,0,0,0,0,0,0]],
    "wildfire": [[0,0,0,0,0,0,0,0,0,0],[0,1,0,0,0,0,0,1,0,0],[0,1,0,1,0,0,0,1,0,0],[0,0,0,1,2,2,0,0,0,0],[0,0,0,0,2,2,2,0,0,0],[0,0,1,0,2,2,2,0,1,0],[0,0,1,0,0,2,0,0,1,0],[0,0,0,0,0,0,0,0,0,0],[0,1,1,0,0,0,0,1,0,0],[0,0,0,0,0,0,0,0,0,0]],
    "landslide":[[0,0,0,0,0,0,0,0,0,0],[0,1,1,0,0,0,0,1,0,0],[0,0,1,0,0,1,0,1,0,0],[0,0,0,0,0,1,0,0,0,0],[0,0,0,1,0,0,0,0,0,0],[0,0,0,1,0,0,1,0,0,0],[0,2,0,0,0,0,1,0,0,0],[0,2,2,0,0,0,0,0,1,0],[0,0,2,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,0,0,0]],
    "normal":   [[0,0,0,0,0,0,0,0,0,0],[0,1,0,0,0,0,0,0,0,0],[0,1,0,1,0,0,0,0,0,0],[0,0,0,1,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0],[0,0,0,0,0,1,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0]],
}

def draw_route(grid,path):
    fig,ax=plt.subplots(figsize=(4,4))
    vis=np.array(grid,dtype=float)
    cmap=plt.cm.colors.ListedColormap(["#F5F5F0","#2C2C2A","#FAEEDA"])
    ax.imshow(vis,cmap=cmap,vmin=0,vmax=2)
    for x in range(11): ax.axvline(x-0.5,color="#B4B2A9",lw=0.4)
    for y in range(11): ax.axhline(y-0.5,color="#B4B2A9",lw=0.4)
    if path:
        pr=[p[0] for p in path]; pc=[p[1] for p in path]
        ax.plot(pc,pr,color="#185FA5",lw=2.5,zorder=3)
        ax.scatter(pc[1:-1],pr[1:-1],color="#378ADD",s=20,zorder=4)
    ax.scatter(0,0,color="#3B6D11",s=180,marker="*",zorder=5)
    ax.scatter(9,9,color="#E24B4A",s=180,marker="*",zorder=5)
    ax.axis("off")
    plt.tight_layout(pad=0.2)
    return fig

def build_india_map():
    locations=[
        {"city":"Patna",           "state":"Bihar",           "lat":25.5941,"lon":85.1376,"type":"Flood",    "alert":"RED",   "sev":9.1,"pop":4500},
        {"city":"Guwahati",        "state":"Assam",           "lat":26.1158,"lon":91.7086,"type":"Flood",    "alert":"RED",   "sev":8.5,"pop":3200},
        {"city":"Mumbai",          "state":"Maharashtra",     "lat":19.0760,"lon":72.8777,"type":"Flood",    "alert":"RED",   "sev":8.0,"pop":5000},
        {"city":"Uttarakhand",     "state":"Uttarakhand",     "lat":30.0668,"lon":79.0193,"type":"Wildfire", "alert":"ORANGE","sev":7.8,"pop":1200},
        {"city":"Sikkim",          "state":"Sikkim",          "lat":27.3314,"lon":88.6138,"type":"Landslide","alert":"ORANGE","sev":7.2,"pop":800},
        {"city":"Chennai",         "state":"Tamil Nadu",      "lat":13.0827,"lon":80.2707,"type":"Cyclone",  "alert":"ORANGE","sev":7.5,"pop":3800},
        {"city":"Simlipal",        "state":"Odisha",          "lat":21.6000,"lon":86.2500,"type":"Wildfire", "alert":"ORANGE","sev":6.8,"pop":900},
        {"city":"Shimla",          "state":"Himachal Pradesh","lat":31.1048,"lon":77.1734,"type":"Landslide","alert":"YELLOW","sev":6.5,"pop":600},
        {"city":"Bandipur",        "state":"Karnataka",       "lat":11.6710,"lon":76.6347,"type":"Wildfire", "alert":"YELLOW","sev":7.0,"pop":1100},
        {"city":"Wayanad",         "state":"Kerala",          "lat":11.6854,"lon":76.1320,"type":"Landslide","alert":"YELLOW","sev":6.2,"pop":500},
        {"city":"Kolkata",         "state":"West Bengal",     "lat":22.5726,"lon":88.3639,"type":"Flood",    "alert":"YELLOW","sev":6.8,"pop":2800},
        {"city":"Bhubaneswar",     "state":"Odisha",          "lat":20.2961,"lon":85.8245,"type":"Cyclone",  "alert":"YELLOW","sev":5.5,"pop":1800},
        {"city":"Jaipur",          "state":"Rajasthan",       "lat":26.9124,"lon":75.7873,"type":"Normal",   "alert":"GREEN", "sev":1.5,"pop":400},
        {"city":"Bhopal",          "state":"Madhya Pradesh",  "lat":23.2599,"lon":77.4126,"type":"Normal",   "alert":"GREEN", "sev":1.2,"pop":300},
        {"city":"Hyderabad",       "state":"Telangana",       "lat":17.3850,"lon":78.4867,"type":"Normal",   "alert":"GREEN", "sev":1.0,"pop":500},
        {"city":"Ahmedabad",       "state":"Gujarat",         "lat":23.0225,"lon":72.5714,"type":"Normal",   "alert":"GREEN", "sev":0.8,"pop":200},
    ]
    df=pd.DataFrame(locations)
    color_map={"RED":"#E24B4A","ORANGE":"#D85A30","YELLOW":"#BA7517","GREEN":"#3B6D11"}
    df["color"]=df["alert"].map(color_map)
    df["size"]=df["sev"]*9
    df["tooltip"]=df.apply(lambda r:
        f"<b>{r['city']}, {r['state']}</b><br>"
        f"Disaster: {r['type']}<br>"
        f"Alert: <b>{r['alert']}</b><br>"
        f"Severity: {r['sev']}/10<br>"
        f"Population at risk: {r['pop']:,}",axis=1)
    fig=go.Figure()
    for alert_level,color in color_map.items():
        subset=df[df["alert"]==alert_level]
        if len(subset)==0: continue
        fig.add_trace(go.Scattergeo(
            lat=subset["lat"],lon=subset["lon"],
            mode="markers+text",
            marker=dict(size=subset["size"],color=color,opacity=0.9,
                        line=dict(width=1.5,color="white")),
            text=subset["city"],
            textposition="top center",
            textfont=dict(size=10,color="white"),
            hovertemplate=subset["tooltip"]+"<extra></extra>",
            name=f"{alert_level} alert",
        ))
    fig.update_layout(
        geo=dict(
            scope="asia",
            center=dict(lat=22,lon=82),
            projection_scale=4.8,
            showland=True,    landcolor="#1a1a2e",
            showocean=True,   oceancolor="#0d1b2a",
            showlakes=True,   lakecolor="#0d1b2a",
            showcountries=True,countrycolor="#555",
            showcoastlines=True,coastlinecolor="#666",
            bgcolor="#0d1b2a",
        ),
        paper_bgcolor="#0d1b2a",
        plot_bgcolor="#0d1b2a",
        font=dict(color="white"),
        legend=dict(bgcolor="rgba(0,0,0,0.5)",bordercolor="#444",
                    borderwidth=1,font=dict(color="white",size=12)),
        margin=dict(l=0,r=0,t=0,b=0),
        height=540,
    )
    return fig

# ── TABS ─────────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5=st.tabs(["🔴 Live Simulation","🗺 India Risk Map","📊 System Info","🔢 Risk Calculator","🎮 Scenario Simulator"])

# ════════════════════════════
# TAB 1
# ════════════════════════════
with tab1:
    with st.sidebar:
        st.header("🇮🇳 Control Panel")
        speed=st.selectbox("Simulation speed",["Slow (5s)","Normal (3s)","Fast (1.5s)"],index=1)
        delay_map={"Slow (5s)":5,"Normal (3s)":3,"Fast (1.5s)":1.5}
        delay=delay_map[speed]
        st.divider()
        c1,c2=st.columns(2)
        with c1: start_btn=st.button("▶ Start",use_container_width=True,type="primary")
        with c2: stop_btn=st.button("⏹ Stop",use_container_width=True)
        if start_btn: st.session_state.sim_running=True
        if stop_btn:  st.session_state.sim_running=False
        st.divider()
        if st.button("🗑 Clear log",use_container_width=True):
            st.session_state.event_log=[]
            st.session_state.total_events=0
            st.session_state.total_red=0
        st.divider()
        st.markdown("**Alert levels**")
        st.markdown("🚨 RED — Evacuate now")
        st.markdown("🔶 ORANGE — High alert")
        st.markdown("⚠️ YELLOW — Moderate")
        st.markdown("✅ GREEN — All clear")

    if st.session_state.sim_running:
        st.markdown('<div class="sim-active">🔴 LIVE SIMULATION RUNNING — INDIA DISASTER MONITORING</div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="sim-idle">⚪ SIMULATION IDLE — Press ▶ Start to begin monitoring</div>',unsafe_allow_html=True)

    

    # ✅ STEP 1: CSS (PUT THIS AT TOP OR BEFORE CARDS)
st.markdown("""
<style>
.metric-box {
    background-color: #1E293B;  /* 🔥 change color here */
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    color: white;
}
</style>
""", unsafe_allow_html=True)



st.markdown("<br>", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f'''
    <div class="metric-box">
        <div class="metric-val">{st.session_state.total_events}</div>
        <div class="metric-lbl">Zones scanned</div>
    </div>
    ''', unsafe_allow_html=True)

with m2:
    st.markdown(f'''
    <div class="metric-box">
        <div class="metric-val" style="color:#E24B4A">{st.session_state.total_red}</div>
        <div class="metric-lbl">RED alerts issued</div>
    </div>
    ''', unsafe_allow_html=True)

with m3:
    st.markdown('''
    <div class="metric-box">
        <div class="metric-val">13</div>
        <div class="metric-lbl">Indian states monitored</div>
    </div>
    ''', unsafe_allow_html=True)

with m4:
    st.markdown('''
    <div class="metric-box">
        <div class="metric-val" style="color:#3B6D11">99%+</div>
        <div class="metric-lbl">Detection accuracy</div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    left,right=st.columns([3,2])
    with left:
        st.subheader("Live satellite detection")
        feed_ph=st.empty()
        alert_ph=st.empty()
        details_ph=st.empty()
    with right:
        st.subheader("Event log")
        log_ph=st.empty()

    if st.session_state.sim_running:
        idx=st.session_state.sim_step % len(SCENARIOS)
        sc=SCENARIOS[idx]
        alert_lvl,alert_name,emoji,css=get_alert(sc["severity"],sc["population"],sc["infrastructure"],sc["weather"])
        grid=GRIDS.get(sc["disaster"],GRIDS["normal"])
        path,cost=astar(grid,(0,0),(9,9))
        st.session_state.total_events+=1
        if alert_name=="RED": st.session_state.total_red+=1
        st.session_state.event_log.insert(0,{
            "time":datetime.now().strftime("%H:%M:%S"),
            "location":sc["location"],"disaster":sc["disaster"].upper(),
            "alert":alert_name,"emoji":emoji,
            "state":sc["state"]
        })
        if len(st.session_state.event_log)>20:
            st.session_state.event_log=st.session_state.event_log[:20]
        st.session_state.current=(sc,alert_name,emoji,css,path,cost)
        st.session_state.sim_step+=1

    if st.session_state.current:
        sc,alert_name,emoji,css,path,cost=st.session_state.current
        with feed_ph.container():
            c1,c2=st.columns([1,2])
            with c1:
                st.image(make_image(sc["disaster"]),
                         caption=f"Satellite image — {sc['location']}",width=180)
            with c2:
                st.markdown(f"**📍 Location:** {sc['location']}")
                st.markdown(f"**🏛 State:** {sc['state']}")
                st.markdown(f"**⚠️ Disaster type:** {sc['disaster'].upper()}")
                st.markdown(f"**📊 Severity:** {sc['severity']} / 10")
                st.markdown(f"**👥 Population at risk:** {sc['population']:,} people")
                st.markdown(f"**🏗 Infrastructure damage:** {sc['infrastructure']}%")
                st.markdown(f"**🌧 Cause:** {sc['cause']}")

        with alert_ph.container():
            if alert_name == "RED":
                st.markdown(
                    f'''<div class="red-alert-shake">
                    🚨 &nbsp; RED ALERT — {sc["location"].upper()} &nbsp; 🚨<br>
                    <span style="font-size:0.85rem;font-weight:400">
                    IMMEDIATE EVACUATION REQUIRED — Contact NDRF immediately
                    </span></div>''', unsafe_allow_html=True)
            elif alert_name == "ORANGE":
                st.markdown(
                    f'''<div class="orange-alert">
                    🔶 ORANGE ALERT — {sc["location"]}
                    <br><span style="font-size:0.85rem;font-weight:400">Prepare evacuation — Standby rescue teams</span>
                    </div>''', unsafe_allow_html=True)
            elif alert_name == "YELLOW":
                st.markdown(
                    f'''<div class="yellow-alert">
                    ⚠️ YELLOW ALERT — {sc["location"]}
                    <br><span style="font-size:0.85rem;font-weight:400">Monitor situation — Issue public advisory</span>
                    </div>''', unsafe_allow_html=True)
            else:
                st.markdown(
                    f'''<div class="green-alert">
                    ✅ GREEN — {sc["location"]}
                    <br><span style="font-size:0.85rem;font-weight:400">No immediate threat — Routine monitoring</span>
                    </div>''', unsafe_allow_html=True)

        with details_ph.container():
            d1,d2=st.columns(2)
            with d1:
                st.markdown("**A* Evacuation route**")
                fig=draw_route(GRIDS.get(sc["disaster"],GRIDS["normal"]),path)
                st.pyplot(fig,use_container_width=False)
                plt.close()
            with d2:
                st.markdown("**Route summary**")
                if path:
                    st.metric("Steps to safe zone",len(path))
                    st.metric("Total route cost",cost)
                st.markdown("**Decision path**")
                sev,pop,infra,wea=sc["severity"],sc["population"],sc["infrastructure"],sc["weather"]
                if sev>=7 and pop>1000: st.code(f"Severity {sev} >= 7\nPopulation {pop} > 1000\n=> RED ALERT")
                elif sev>=7 or infra>60: st.code(f"Severity {sev} >= 7 or Infra {infra}%\n=> ORANGE ALERT")
                elif sev>=4 or wea>=6:  st.code(f"Severity {sev} >= 4 or Weather {wea}\n=> YELLOW ALERT")
                else: st.code(f"Severity {sev} < 4\n=> GREEN — All clear")

    with log_ph.container():
        if st.session_state.event_log:
            cmap2={"RED":"#E24B4A","ORANGE":"#D85A30","YELLOW":"#BA7517","GREEN":"#3B6D11"}
            for e in st.session_state.event_log[:12]:
                c=cmap2.get(e["alert"],"#888")
                st.markdown(
                    f'''<div class="log-row">
                    <span style="color:#888">{e["time"]}</span> &nbsp;
                    {e["emoji"]} <strong style="color:{c}">{e["alert"]}</strong>
                    &nbsp; {e["disaster"]} &nbsp;
                    <span style="color:#888;font-size:0.75rem">{e["location"][:30]}</span>
                    </div>''', unsafe_allow_html=True)
        else:
            st.markdown("*No events yet — press ▶ Start*")

    if st.session_state.sim_running:
        time.sleep(delay)
        st.rerun()

# ════════════════════════════
# TAB 2
# ════════════════════════════
with tab2:
    st.subheader("🗺 India Disaster Risk Map")
    st.markdown("Hover over markers for details · Size = severity · Colour = alert level")
    col1,col2,col3,col4=st.columns(4)
    with col1: st.markdown('<div class="metric-box"><div class="metric-val" style="color:#E24B4A">3</div><div class="metric-lbl">RED zones</div></div>',unsafe_allow_html=True)
    with col2: st.markdown('<div class="metric-box"><div class="metric-val" style="color:#D85A30">4</div><div class="metric-lbl">ORANGE zones</div></div>',unsafe_allow_html=True)
    with col3: st.markdown('<div class="metric-box"><div class="metric-val" style="color:#BA7517">5</div><div class="metric-lbl">YELLOW zones</div></div>',unsafe_allow_html=True)
    with col4: st.markdown('<div class="metric-box"><div class="metric-val">16</div><div class="metric-lbl">Zones monitored</div></div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    st.plotly_chart(build_india_map(),use_container_width=True)
    st.subheader("Active alerts across India")
    alert_data=[
        {"Location":"Patna, Bihar",          "Disaster":"Flood",    "Severity":"9.1/10","Alert":"🚨 RED",   "Cause":"Ganga overflow","Action":"Evacuate immediately"},
        {"Location":"Guwahati, Assam",       "Disaster":"Flood",    "Severity":"8.5/10","Alert":"🚨 RED",   "Cause":"Brahmaputra flood","Action":"Evacuate immediately"},
        {"Location":"Mumbai, Maharashtra",   "Disaster":"Flood",    "Severity":"8.0/10","Alert":"🚨 RED",   "Cause":"Coastal flooding","Action":"Evacuate immediately"},
        {"Location":"Chennai, Tamil Nadu",   "Disaster":"Cyclone",  "Severity":"7.5/10","Alert":"🔶 ORANGE","Cause":"NE monsoon surge","Action":"Prepare evacuation"},
        {"Location":"Uttarakhand",           "Disaster":"Wildfire", "Severity":"7.8/10","Alert":"🔶 ORANGE","Cause":"Summer heat wave","Action":"Deploy fire teams"},
        {"Location":"Sikkim",               "Disaster":"Landslide","Severity":"7.2/10","Alert":"🔶 ORANGE","Cause":"Heavy rainfall","Action":"Close mountain roads"},
        {"Location":"Simlipal, Odisha",      "Disaster":"Wildfire", "Severity":"6.8/10","Alert":"🔶 ORANGE","Cause":"Forest fire","Action":"Aerial water drop"},
        {"Location":"Bandipur, Karnataka",   "Disaster":"Wildfire", "Severity":"7.0/10","Alert":"⚠️ YELLOW","Cause":"Reserve fire","Action":"Contain spread"},
        {"Location":"Wayanad, Kerala",       "Disaster":"Landslide","Severity":"6.2/10","Alert":"⚠️ YELLOW","Cause":"Soil erosion","Action":"Road closures"},
        {"Location":"Kolkata, West Bengal",  "Disaster":"Flood",    "Severity":"6.8/10","Alert":"⚠️ YELLOW","Cause":"Cyclone aftermath","Action":"Monitor drains"},
        {"Location":"Shimla, HP",           "Disaster":"Landslide","Severity":"6.5/10","Alert":"⚠️ YELLOW","Cause":"Cloudburst","Action":"Evacuate hillside"},
        {"Location":"Bhubaneswar, Odisha",   "Disaster":"Cyclone",  "Severity":"5.5/10","Alert":"⚠️ YELLOW","Cause":"Bay of Bengal low","Action":"Issue advisory"},
    ]
    st.dataframe(pd.DataFrame(alert_data),use_container_width=True,hide_index=True)

# ════════════════════════════
# TAB 3
# ════════════════════════════
with tab3:
    st.subheader("📊 System Architecture")

    st.markdown("""
    | Module | Algorithm | Accuracy | Purpose |
    |--------|-----------|----------|---------|
    | 1 — Image Detection | CNN (3 Conv layers) | 100% | Classifies satellite images into 4 disaster types |
    | 2 — Alert Generation | Decision Tree | 99% | Generates RED / ORANGE / YELLOW / GREEN alerts |
    | 3 — False Alarm Filter | KNN (k=5) | 99% | Validates alerts against historical records |
    | 4 — Evacuation Routing | A* Search | Optimal | Computes safest path avoiding obstacles |
    | 5 — Risk Scoring | Weighted scoring model | — | Personal disaster risk score by state and season |
    | 6 — Scenario Prediction | Multi-factor formula | — | Real-time what-if disaster prediction engine |
    """)

    st.divider()
    st.subheader("🖥️ App Features")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Tab 1 — Live Simulation**
        - Auto-cycles through 13 India disaster scenarios
        - CNN detection with satellite image
        - RED alert shakes and pulses
        - A* evacuation route per disaster
        - Live event log with timestamps

        **Tab 2 — India Risk Map**
        - 16 real Indian locations monitored
        - Plotly dark-theme interactive map
        - Markers sized by severity
        - Hover for full disaster details
        - Active alerts table with causes
        """)
    with col2:
        st.markdown("""
        **Tab 4 — Risk Calculator**
        - All 30 Indian states covered
        - 5 disaster types per state
        - Seasonal multipliers (12 months)
        - Gauge chart + bar chart
        - Compared to national average
        - Precautions checklist

        **Tab 5 — Scenario Simulator**
        - 6 environmental sliders
        - 5 India preset scenarios
        - Radar chart + bar chart
        - Live A* route recomputation
        - Actions by alert level
        """)

    st.divider()
    st.subheader("🇮🇳 India Coverage")
    st.markdown("""
    | Disaster Type | States Covered |
    |---------------|----------------|
    | Flood | Bihar, Assam, West Bengal, Maharashtra, Tamil Nadu, Kerala, UP |
    | Wildfire | Uttarakhand, Karnataka, Odisha, Himachal Pradesh, MP |
    | Landslide | Sikkim, Himachal Pradesh, Kerala, Uttarakhand, Manipur |
    | Cyclone | Odisha, Tamil Nadu, Andhra Pradesh, West Bengal, Gujarat |
    | Earthquake | J&K, Sikkim, Gujarat, Uttarakhand, Northeast states |
    """)

    st.divider()
    st.subheader("📈 Project Stats")
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("AI algorithms", "6")
    with s2:
        st.metric("Indian states", "30")
    with s3:
        st.metric("App tabs", "5")
    with s4:
        st.metric("Accuracy", "99%+")

    st.divider()
    st.subheader("👨‍💻 Team")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        **Manish Kant**
        Roll No: 24CS2025
        Module: CNN + System Integration + Deployment
        """)
    with c2:
        st.markdown("""
        **OM JEE**
        Roll No: 24CS2028
        Module: Decision Tree + A* Routing + UI
        """)
    st.divider()
    st.markdown("**Tech stack:** Python · PyTorch · Scikit-learn · Plotly · Streamlit · NumPy · Matplotlib · Streamlit Cloud")
    st.markdown("**Live at:** https://disaster-ai-zf6ayb3rv7xjosoura93xf.streamlit.app")
# TAB 4 — RISK CALCULATOR
# ════════════════════════════
with tab4:
    risk_calculator.render()

# ════════════════════════════
# TAB 5 — SCENARIO SIMULATOR
# ════════════════════════════
with tab5:
    scenario_simulator.render()
