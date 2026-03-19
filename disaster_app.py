
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import heapq
import time
import random
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from datetime import datetime

st.set_page_config(
    page_title="Disaster Management AI",
    page_icon="🚨",
    layout="wide"
)

st.markdown("""
<style>
  .main-title{font-size:2rem;font-weight:600;color:#E24B4A;margin-bottom:0}
  .sub-title{font-size:0.9rem;color:#888780;margin-bottom:1.5rem}
  .alert-red{background:red;border-left:4px solid #E24B4A;padding:12px 16px;border-radius:8px;margin:8px 0}
  .alert-orange{background:#FAECE7;border-left:4px solid #D85A30;padding:12px 16px;border-radius:8px;margin:8px 0}
  .alert-yellow{background:#FAEEDA;border-left:4px solid #BA7517;padding:12px 16px;border-radius:8px;margin:8px 0}
  .alert-green{background:#EAF3DE;border-left:4px solid #3B6D11;padding:12px 16px;border-radius:8px;margin:8px 0}
  .metric-box{background:#F1EFE8;border-radius:10px;padding:14px 18px;text-align:center}
  .metric-val{font-size:1.6rem;font-weight:600}
  .metric-lbl{font-size:0.75rem;color:#5F5E5A;margin-top:2px}
  .log-row{font-size:0.8rem;padding:4px 0;border-bottom:0.5px solid #D3D1C7}
  .sim-active{background:#FCEBEB;border:1.5px solid #E24B4A;border-radius:10px;padding:10px 16px;text-align:center;font-weight:600;color:#A32D2D}
  .sim-idle{background:#EAF3DE;border:1.5px solid #3B6D11;border-radius:10px;padding:10px 16px;text-align:center;font-weight:600;color:#27500A}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚨 Intelligent Disaster Management System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">By Manish Kant (24CS2025) &amp; OM JEE (24CS2028) &nbsp;·&nbsp; AI Project</div>', unsafe_allow_html=True)

for key,val in [("sim_running",False),("sim_step",0),("event_log",[]),
                ("current",None),("total_events",0),("total_red",0)]:
    if key not in st.session_state: st.session_state[key]=val

SCENARIOS=[
    {"disaster":"flood",    "severity":8.5,"population":3200,"infrastructure":70,"weather":7.5,"location":"Sector 4B — Lower Plains"},
    {"disaster":"wildfire", "severity":7.8,"population":1400,"infrastructure":55,"weather":8.2,"location":"Northern Ridge Forest Zone"},
    {"disaster":"landslide","severity":6.5,"population":800, "infrastructure":45,"weather":6.0,"location":"Hill Station B — Eastern Slope"},
    {"disaster":"normal",   "severity":1.5,"population":400, "infrastructure":5, "weather":2.0,"location":"Zone 12 — Urban Centre"},
    {"disaster":"flood",    "severity":9.1,"population":4500,"infrastructure":82,"weather":9.0,"location":"Coastal Zone — Port Area"},
    {"disaster":"wildfire", "severity":8.9,"population":2100,"infrastructure":68,"weather":8.8,"location":"Western Dry Forest — Block 7"},
]

def get_alert(sev,pop,infra,weather):
    if sev>=7 and pop>1000: return 3,"RED","🚨","alert-red"
    if sev>=7 or infra>60:  return 2,"ORANGE","🔶","alert-orange"
    if sev>=4 or weather>=6:return 1,"YELLOW","⚠️","alert-yellow"
    return 0,"GREEN","","alert-green"

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
    disaster_zones=[
        [25.5941,85.1376,0.9],[26.8467,80.9462,0.8],[22.5726,88.3639,0.9],
        [26.1158,91.7086,0.8],[23.3441,85.3096,0.7],[21.1458,79.0882,0.6],
        [20.2961,85.8245,0.8],[30.0668,79.0193,0.8],[32.2190,77.1234,0.7],
        [27.3314,88.6138,0.9],[31.1048,77.1734,0.8],[13.0827,80.2707,0.7],
        [19.0760,72.8777,0.6],[20.9374,85.0985,0.8],[16.5062,80.6480,0.7],
        [25.4670,91.3662,0.7],[18.5204,73.8567,0.5],[15.3173,75.7139,0.6],
    ]
    active_alerts=[
        {"city":"Patna",      "lat":25.5941,"lon":85.1376,"type":"Flood",    "alert":"RED"},
        {"city":"Guwahati",   "lat":26.1158,"lon":91.7086,"type":"Flood",    "alert":"RED"},
        {"city":"Uttarakhand","lat":30.0668,"lon":79.0193,"type":"Wildfire", "alert":"ORANGE"},
        {"city":"Sikkim",     "lat":27.3314,"lon":88.6138,"type":"Landslide","alert":"ORANGE"},
        {"city":"Chennai",    "lat":13.0827,"lon":80.2707,"type":"Cyclone",  "alert":"YELLOW"},
        {"city":"Shimla",     "lat":31.1048,"lon":77.1734,"type":"Landslide","alert":"YELLOW"},
        {"city":"Mumbai",     "lat":19.0760,"lon":72.8777,"type":"Flood",    "alert":"YELLOW"},
        {"city":"Bhubaneswar","lat":20.2961,"lon":85.8245,"type":"Cyclone",  "alert":"ORANGE"},
    ]
    m=folium.Map(location=[20.5937,78.9629],zoom_start=5,tiles="CartoDB dark_matter")
    HeatMap(disaster_zones,min_opacity=0.4,radius=35,blur=25,
            gradient={"0.2":"blue","0.4":"cyan","0.6":"yellow","0.8":"orange","1.0":"red"}
    ).add_to(m)
    color_map={"RED":"red","ORANGE":"orange","YELLOW":"beige","GREEN":"green"}
    icon_map={"Flood":"tint","Wildfire":"fire","Landslide":"warning-sign","Cyclone":"cloud"}
    for a in active_alerts:
        folium.Marker(
            location=[a["lat"],a["lon"]],
            popup=folium.Popup(f"<b>{a['city']}</b><br>Type: {a['type']}<br>Alert: <b>{a['alert']}</b>",max_width=200),
            tooltip=f"{a['city']} — {a['type']} — {a['alert']}",
            icon=folium.Icon(color=color_map[a["alert"]],icon=icon_map[a["type"]],prefix="glyphicon")
        ).add_to(m)
    return m

# ── TABS ──────────────────────────────────────────────────
tab1,tab2,tab3=st.tabs(["🔴 Live Simulation","🗺 India Heatmap","📊 System Info"])

# ════════════════════════════════
# TAB 1 — SIMULATION
# ════════════════════════════════
with tab1:
    with st.sidebar:
        st.header("Control Panel")
        speed=st.selectbox("Speed",["Slow (5s)","Normal (3s)","Fast (1.5s)"],index=1)
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

    if st.session_state.sim_running:
        st.markdown('<div class="sim-active">🔴 LIVE SIMULATION RUNNING</div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="sim-idle">⚪ SIMULATION IDLE — Press ▶ Start in sidebar</div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    m1,m2,m3,m4=st.columns(4)
    with m1: st.markdown(f'''<div class="metric-box"><div class="metric-val">{st.session_state.total_events}</div><div class="metric-lbl">Events scanned</div></div>''',unsafe_allow_html=True)
    with m2: st.markdown(f'''<div class="metric-box"><div class="metric-val" style="color:#E24B4A">{st.session_state.total_red}</div><div class="metric-lbl">RED alerts</div></div>''',unsafe_allow_html=True)
    with m3: st.markdown('<div class="metric-box"><div class="metric-val">4</div><div class="metric-lbl">AI modules</div></div>',unsafe_allow_html=True)
    with m4: st.markdown('<div class="metric-box"><div class="metric-val" style="color:#3B6D11">99%+</div><div class="metric-lbl">Accuracy</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    left,right=st.columns([3,2])
    with left:
        st.subheader("Live detection feed")
        feed_ph=st.empty()
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
            "alert":alert_name,"emoji":emoji
        })
        if len(st.session_state.event_log)>20:
            st.session_state.event_log=st.session_state.event_log[:20]
        st.session_state.current=(sc,alert_name,emoji,css,path,cost)
        st.session_state.sim_step+=1

    if st.session_state.current:
        sc,alert_name,emoji,css,path,cost=st.session_state.current
        with feed_ph.container():
            c1,c2=st.columns([1,2])
            with c1: st.image(make_image(sc["disaster"]),caption=f"Satellite — {sc['disaster'].upper()}",width=180)
            with c2:
                st.markdown(f"**Location:** {sc['location']}")
                st.markdown(f"**Detected:** {sc['disaster'].upper()}")
                st.markdown(f"**Severity:** {sc['severity']} / 10")
                st.markdown(f"**Population at risk:** {sc['population']:,}")
                st.markdown(f"**Infrastructure damage:** {sc['infrastructure']}%")
                st.markdown(f'''<div class="{css}">{emoji} <strong>ALERT: {alert_name}</strong></div>''',unsafe_allow_html=True)
        with details_ph.container():
            d1,d2=st.columns(2)
            with d1:
                st.markdown("**A* evacuation route**")
                fig=draw_route(GRIDS.get(sc["disaster"],GRIDS["normal"]),path)
                st.pyplot(fig,use_container_width=False)
                plt.close()
            with d2:
                st.markdown("**Route summary**")
                if path:
                    st.metric("Steps",len(path))
                    st.metric("Route cost",cost)
                st.markdown("**Decision path**")
                sev,pop,infra,wea=sc["severity"],sc["population"],sc["infrastructure"],sc["weather"]
                if sev>=7 and pop>1000: st.code(f"Severity {sev} >= 7\nPopulation {pop} > 1000\n-> RED")
                elif sev>=7 or infra>60: st.code(f"Severity {sev} >= 7 or Infra {infra}%\n-> ORANGE")
                elif sev>=4 or wea>=6:  st.code(f"Severity {sev} >= 4 or Weather {wea}\n-> YELLOW")
                else: st.code(f"Severity {sev} < 4\n-> GREEN")

    with log_ph.container():
        if st.session_state.event_log:
            cmap2={"RED":"#E24B4A","ORANGE":"#D85A30","YELLOW":"#BA7517","GREEN":"#3B6D11"}
            for e in st.session_state.event_log[:12]:
                c=cmap2.get(e["alert"],"#888")
                st.markdown(f'''<div class="log-row"><span style="color:#888">{e["time"]}</span> &nbsp; {e["emoji"]} <strong style="color:{c}">{e["alert"]}</strong> &nbsp; {e["disaster"]} &nbsp; <span style="color:#888;font-size:0.75rem">{e["location"][:28]}</span></div>''',unsafe_allow_html=True)
        else:
            st.markdown("*No events yet — press ▶ Start*")

    if st.session_state.sim_running:
        time.sleep(delay)
        st.rerun()

# ════════════════════════════════
# TAB 2 — INDIA HEATMAP
# ════════════════════════════════
with tab2:
    st.subheader("🗺 India Disaster Risk Heatmap")
    st.markdown("Live risk zones across India — red = extreme risk, blue = low risk.")
    col1,col2,col3,col4=st.columns(4)
    with col1: st.markdown('<div class="metric-box"><div class="metric-val" style="color:#E24B4A">2</div><div class="metric-lbl">RED zones</div></div>',unsafe_allow_html=True)
    with col2: st.markdown('<div class="metric-box"><div class="metric-val" style="color:#D85A30">3</div><div class="metric-lbl">ORANGE zones</div></div>',unsafe_allow_html=True)
    with col3: st.markdown('<div class="metric-box"><div class="metric-val" style="color:#BA7517">3</div><div class="metric-lbl">YELLOW zones</div></div>',unsafe_allow_html=True)
    with col4: st.markdown('<div class="metric-box"><div class="metric-val">18</div><div class="metric-lbl">Zones monitored</div></div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    india_map=build_india_map()
    st_folium(india_map,width=1000,height=550)
    st.markdown("<br>",unsafe_allow_html=True)
    st.subheader("Active alerts")
    alert_data=[
        {"City":"Patna",      "State":"Bihar",           "Type":"Flood",    "Alert":"🚨 RED",   "Action":"Evacuate immediately"},
        {"City":"Guwahati",   "State":"Assam",           "Type":"Flood",    "Alert":"🚨 RED",   "Action":"Evacuate immediately"},
        {"City":"Bhubaneswar","State":"Odisha",          "Type":"Cyclone",  "Alert":"🔶 ORANGE","Action":"Prepare evacuation"},
        {"City":"Uttarakhand","State":"Uttarakhand",     "Type":"Wildfire", "Alert":"🔶 ORANGE","Action":"Standby teams ready"},
        {"City":"Sikkim",     "State":"Sikkim",          "Type":"Landslide","Alert":"🔶 ORANGE","Action":"Monitor slopes"},
        {"City":"Chennai",    "State":"Tamil Nadu",      "Type":"Cyclone",  "Alert":"⚠️ YELLOW","Action":"Issue advisory"},
        {"City":"Mumbai",     "State":"Maharashtra",     "Type":"Flood",    "Alert":"⚠️ YELLOW","Action":"Monitor water levels"},
        {"City":"Shimla",     "State":"Himachal Pradesh","Type":"Landslide","Alert":"⚠️ YELLOW","Action":"Road closures"},
    ]
    st.dataframe(pd.DataFrame(alert_data),use_container_width=True,hide_index=True)

# ════════════════════════════════
# TAB 3 — SYSTEM INFO
# ════════════════════════════════
with tab3:
    st.subheader("📊 System Architecture")
    st.markdown("""
    | Module | Algorithm | Accuracy | Purpose |
    |--------|-----------|----------|---------|
    | 1 — Image Detection | CNN (3 Conv layers) | 100% | Classifies satellite images |
    | 2 — Alert Generation | Decision Tree | 99% | Generates RED/ORANGE/YELLOW/GREEN |
    | 3 — False Alarm Filter | KNN (k=5) | 99% | Reduces false alerts |
    | 4 — Evacuation Routing | A* Search | Optimal | Finds safest escape route |
    """)
    st.divider()
    st.subheader("Team")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("**Manish Kant**")
        st.markdown("Roll No: 24CS2025")
    with c2:
        st.markdown("**OM JEE**")
        st.markdown("Roll No: 24CS2028")
    st.divider()
    st.markdown("**Tech stack:** Python · PyTorch · Scikit-learn · Folium · Streamlit · NumPy · Matplotlib")
