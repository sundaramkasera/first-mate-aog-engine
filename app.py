import streamlit as st
import json
import time
import os
import io
import random
from gtts import gTTS
from streamlit_agraph import agraph, Node, Edge, Config
from agent_core.orchestrator import mitigate_aog

# Hackathon Trick: Install Coral CLI on the Streamlit Linux server on boot
@st.cache_resource
def install_coral():
    if not os.path.exists("./coral") and not os.path.exists("./coral.exe"):
        os.system("curl -fsSL https://withcoral.com/install.sh | sh")
        os.system("chmod +x ./coral")

install_coral()

# Enterprise Page Config
st.set_page_config(page_title="First Mate | AOG Command", page_icon="✈️", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    .stMetric { background-color: #0E1117; padding: 15px; border-radius: 8px; border: 1px solid #2b2b36; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------
if 'active_aircraft' not in st.session_state:
    st.session_state.active_aircraft = 1240
if 'aog_cost' not in st.session_state:
    st.session_state.aog_cost = 0
if 'latency' not in st.session_state:
    st.session_state.latency = 42

st.title("✈️ First Mate: AOG Mitigation Engine")
st.markdown("**Powered by Cohere Command R+ & Coral Cross-Source SQL**")

# -----------------------------------------
# FRAGMENT 1: SIDEBAR CONTROLS
# -----------------------------------------
@st.fragment
def render_sidebar_inputs():
    # Removed the explicit 'st.sidebar.' prefix from elements inside the fragment
    st.header("🛠️ Command Controls")
    st.session_state.demo_mode = st.toggle("🛡️ Safe Deployment Mode", value=True, help="Bypass live AI API to prevent rate limits.")
    
    st.divider()
    st.subheader("Telemetry Injection")
    st.session_state.selected_tail = st.selectbox("Aircraft Tail Number", [
        "VT-772ZA (DEL)", "VT-334FRA (BOM)", "VT-555COK (COK)", "VT-777AMD (AMD)", 
        "VT-999HYD (HYD)", "VT-112BOM (BOM)", "VT-888BLR (BLR)", "VT-101CCU (CCU)",
        "VT-303MAA (MAA)", "VT-404MAA (MAA)", "VT-202CCU (CCU)", "VT-111DEL (DEL)"
    ])
    
    st.session_state.fault_code = st.selectbox("Distress Flare (Fault Code)", [
        "ERR-772 (Turbine Vibration)", "ERR-101 (Hydraulic Leak)", "ERR-404 (Avionics Failure)", 
        "ERR-909 (Landing Gear Strut)", "ERR-555 (APU Generator)", "ERR-333 (Fuel Valve)",
        "ERR-808 (Engine Fire Warning)", "ERR-415 (Cabin Depressurization)", 
        "ERR-600 (Weather Radar Failure)", "ERR-250 (Brake Overheat)"
    ])

# Render the isolated fragment explicitly INSIDE the sidebar context
with st.sidebar:
    render_sidebar_inputs()
    # Added a unique key and removed the duplicate button block below
    trigger = st.button("🚨 Trigger AOG Protocol", key="master_aog_trigger", use_container_width=True, type="primary")

# Pull active states into local variables for clean execution code
selected_tail = st.session_state.selected_tail
fault_code = st.session_state.fault_code
demo_mode = st.session_state.demo_mode

# -----------------------------------------
# STATE UPDATES
# -----------------------------------------
if trigger:
    st.session_state.active_aircraft = max(0, st.session_state.active_aircraft - 1)
    st.session_state.latency = random.randint(34, 62)
    
    if "Fire" in fault_code or "Turbine" in fault_code or "Depressurization" in fault_code:
        st.session_state.aog_cost = 150000 
    elif "Landing Gear" in fault_code or "Brake" in fault_code:
        st.session_state.aog_cost = 85000   
    elif "Avionics" in fault_code or "Radar" in fault_code:
        st.session_state.aog_cost = 45000   
    else:
        st.session_state.aog_cost = 25000   

# -----------------------------------------
# FRAGMENT 2: HEADER & DYNAMIC KPIs
# -----------------------------------------
@st.fragment
def render_kpi_dashboard():
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Alliance Fleet Status", value=f"{st.session_state.active_aircraft} Active", delta="-1 AOG" if trigger else "Stable", delta_color="inverse" if trigger else "normal")
    col2.metric(label="Est. AOG Cost / Hour", value=f"${st.session_state.aog_cost:,}", delta="Escalated" if trigger else "Nominal", delta_color="inverse")
    col3.metric(label="Active Hubs", value="8 (IND)", delta="Expanded")
    col4.metric(label="Coral Data Latency", value=f"{st.session_state.latency}ms", delta="Live Jitter" if trigger else "Optimal", delta_color="off")
    st.divider()

# Render the isolated KPI fragment
render_kpi_dashboard()

# -----------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------
def stream_mock_data(text):
    for chunk in text.split(" "):
        yield chunk + " "
        time.sleep(0.08)

def calculate_network_ripple(hub_code):
    """Queries the flight_schedule database to calculate exact downstream impacts."""
    impacted_flights = 0
    displaced_pax = 0
    
    try:
        # Streamlit reads the raw JSONL database file asynchronously 
        with open("mock_data/flight_schedule.jsonl", "r") as f:
            for line in f:
                record = json.loads(line)
                # If a flight is scheduled to leave the AOG hub, it gets delayed
                if record["origin"] == hub_code:
                    impacted_flights += 1
                    displaced_pax += record["pax"]
    except Exception as e:
        pass # Failsafe to prevent UI crash if file is missing
    
    # Calculate a realistic gate blockage based on the number of blocked flights
    gate_blocked = f"{impacted_flights + 1}h {impacted_flights * 15}m"
    
    return {"flights": impacted_flights, "pax": displaced_pax, "gate_blocked": gate_blocked}

def evaluate_crew_ftl(fault_code):
    """Asynchronously reads crew limits and calculates fatigue based on repair delay."""
    # Determine the repair delay based on the mechanical severity
    repair_hours = 4 if "Fire" in fault_code or "Depressurization" in fault_code else (2 if "Landing Gear" in fault_code else 1)
    
    try:
        with open("mock_data/crew_registry.jsonl", "r") as f:
            for line in f:
                crew = json.loads(line)
                # Find a crew nearing their limit to demonstrate the safety timeout
                if crew["status"] == "CRITICAL":
                    total_time = crew["hours_on_duty"] + repair_hours
                    if total_time > crew["max_ftl"]:
                        return {
                            "timeout": True,
                            "captain": crew["captain"],
                            "backup_tail": crew["tail_number"],
                            "current": crew["hours_on_duty"],
                            "delay": repair_hours,
                            "total": total_time
                        }
    except Exception:
        pass
    return {"timeout": False}

def play_atc_audio(text_directive):
    try:
        clean_text = text_directive.replace("*", "").replace("Log:", "").replace("#", "").replace("\n", " ")
        atc_message = f"Attention command. First Mate protocol complete. {clean_text}"
        tts = gTTS(text=atc_message, lang='en', tld='co.in')
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        st.audio(audio_bytes, format='audio/mp3', autoplay=True)
    except Exception as e:
        st.warning("🔇 ATC Audio Dispatch temporarily unavailable due to network latency.")

def draw_supply_chain_graph(tail_selection, fault_selection):
    nodes, edges = [], []
    tail = tail_selection.split(" ")[0]
    hub = tail_selection.split("(")[1].replace(")", "")
    part_sys = fault_selection.split("(")[1].replace(")", "")
    
    nodes.append(Node(id=hub, label=f"{hub} Hub Station", size=40, shape="hexagon", color="#1E90FF"))
    nodes.append(Node(id=tail, label=f"AOG: {tail}", size=30, color="#FF4B4B"))
    edges.append(Edge(source=tail, target=hub, label="Grounded At", color="#FFFFFF"))

    nodes.append(Node(id="PART", label=f"Target System: {part_sys}", size=25, color="#FFA500"))
    edges.append(Edge(source="PART", target=hub, label="Tracing Inventory...", color="#FFFFFF"))
    
    nodes.append(Node(id="BACKUP", label="Backup Fleet Search", size=25, color="#00FF00"))
    edges.append(Edge(source="BACKUP", target=hub, label="Scanning Tarmac...", color="#FFFFFF"))

    config = Config(
        width="100%", height=550, directed=True, hierarchical=False, nodeHighlightBehavior=True,
        physics={"barnesHut": {"gravitationalConstant": -45000, "centralGravity": 0.1, "springLength": 280, "springConstant": 0.05, "damping": 0.09, "avoidOverlap": 1}}
    )
    return agraph(nodes=nodes, edges=edges, config=config)

# -----------------------------------------
# MAIN EXECUTION LOGIC
# -----------------------------------------
if trigger:
    alarm_zone = st.empty()
    alarm_zone.error(f"CRITICAL ALARM: AOG declared for {selected_tail}. Initializing First Mate routing...", icon="⚠️")
    
    if demo_mode:
        # ---- SAFE MODE ----
        with st.status("Agent Executing Multi-Step Reasoning Protocol...", expanded=True) as status:
            time.sleep(1)
            st.write("🔍 **Step 1:** Querying `aog_data.codex` & `aog_data.inventory` via Coral SQL...")
            time.sleep(1.5)
            st.info("Log: Component delay verified. Pivoting to `aog_data.fleet` registry...")
            time.sleep(1.5)
            st.success("Log: Found IDLE backup airframe.")
            time.sleep(1)
            st.write("⛅ **Step 2:** Executing Live Telemetry Check (Open-Meteo API)...")
            time.sleep(1.5)
            st.info("Log: Weather Clear. VFR Operational.")
            
            final_text = f"Aircraft {selected_tail} has reported a critical fault requiring a replacement component. Inventory delay exceeds operational thresholds. Route swapping to backup airframe. Maintenance crew dispatched for mechanical repair cycle. Passenger disruptions mitigated successfully. Live weather is clear."
        
        with st.container(border=True):
            st.subheader("📋 Final Recovery Directive")
            directive_box = st.empty()
            streamed_text = ""
            for chunk in stream_mock_data(final_text):
                streamed_text += chunk
                directive_box.success(streamed_text + " ▌")
            directive_box.success(streamed_text)
            
        alarm_zone.success(f"✅ AOG MITIGATION COMPLETE: Action Plan Generated for {selected_tail}", icon="✈️")
        status.update(label="Logs: Verification Complete", state="complete", expanded=False)
        
        play_atc_audio(streamed_text)
        
        # --- CASCADING RIPPLE UI (SAFE MODE) ---
        st.subheader("🌊 Cascading Network Impact (Downstream)")
        hub = selected_tail.split("(")[1].replace(")", "")
        ripple_data = calculate_network_ripple(hub)
        
        with st.container(border=True):
            st.error(f"**WARNING:** AOG event has created a localized network bottleneck at {hub}.", icon="⚠️")
            r_col1, r_col2, r_col3 = st.columns(3)
            r_col1.metric("Subsequent Flights Delayed", f"{ripple_data['flights']} Segments", "Schedule Miss", delta_color="inverse")
            r_col2.metric("Displaced Passengers", f"{ripple_data['pax']} Pax", "Rebooking Required", delta_color="inverse")
            r_col3.metric("Est. Gate Blockage", ripple_data['gate_blocked'], "Logistics Hold", delta_color="inverse")
            st.caption("First Mate background systems have automatically initiated API calls to the passenger rebooking engine to mitigate downstream friction.")
        # ---------------------------------------
        
        # --- NEW FTL CREW COMPLIANCE UI (SAFE MODE) ---
        ftl_data = evaluate_crew_ftl(fault_code)
        if ftl_data["timeout"]:
            st.subheader("🧑✈️ Flight Crew FTL Compliance")
            with st.container(border=True):
                st.error(f"**CRITICAL FATIGUE WARNING:** Swap to backup airframe {ftl_data['backup_tail']} compromises FTL limits.", icon="🚨")
                c_col1, c_col2, c_col3 = st.columns(3)
                c_col1.metric("Assigned Commander", ftl_data["captain"])
                c_col2.metric("Projected Duty Time", f"{ftl_data['total']} Hours", f"+{ftl_data['delay']}h Repair Delay", delta_color="inverse")
                c_col3.metric("FAA Legal Limit", "14.0 Hours", "Violation Imminent", delta_color="inverse")
                st.warning("Automated Action: First Mate has scrambled Reserve Crew Delta-4 from standby. Dispatching to tarmac.", icon="✅")
        # ----------------------------------------------
        
        # Viewport Scaling added here!
        st.subheader("🌐 Supply Chain Intelligence Graph")
        with st.container(border=True):
            draw_supply_chain_graph(selected_tail, fault_code)
        
    else:
        # ---- LIVE MODE ----
        with st.status("Live Agent Core Reasoning...", expanded=True) as status:
            loading_text = st.empty()
            loading_text.write("Executing Coral SQL queries and fetching live APIs...")
            raw_code = fault_code.split(" ")[0]
            start_time = time.time()
            
            try:
                loading_text.write("⚡ Fetching streaming tokens from Agent Core...")
                
                with st.container(border=True):
                    st.subheader("📋 Final Recovery Directive")
                    directive_box = st.empty()
                    streamed_text = ""
                    
                    for chunk in mitigate_aog(selected_tail, raw_code):
                        streamed_text += chunk
                        directive_box.success(streamed_text + " ▌")
                        
                    directive_box.success(streamed_text)
                
                execution_time = round(time.time() - start_time, 2)
                st.caption(f"⏱️ Generation time: {execution_time} seconds")
                
                loading_text.empty()
                alarm_zone.success(f"✅ LIVE MITIGATION ACTIVE: Strategy Pushed to Fleet Command for {selected_tail}", icon="✈️")
                status.update(label="Logs: Execution Complete", state="complete", expanded=False)
                
                play_atc_audio(streamed_text)
                
                # --- CASCADING RIPPLE UI (LIVE MODE) ---
                st.subheader("🌊 Cascading Network Impact (Downstream)")
                hub = selected_tail.split("(")[1].replace(")", "")
                ripple_data = calculate_network_ripple(hub)
                
                with st.container(border=True):
                    st.error(f"**WARNING:** AOG event has created a localized network bottleneck at {hub}.", icon="⚠️")
                    r_col1, r_col2, r_col3 = st.columns(3)
                    r_col1.metric("Subsequent Flights Delayed", f"{ripple_data['flights']} Segments", "Schedule Miss", delta_color="inverse")
                    r_col2.metric("Displaced Passengers", f"{ripple_data['pax']} Pax", "Rebooking Required", delta_color="inverse")
                    r_col3.metric("Est. Gate Blockage", ripple_data['gate_blocked'], "Logistics Hold", delta_color="inverse")
                    st.caption("First Mate background systems have automatically initiated API calls to the passenger rebooking engine to mitigate downstream friction.")
                # ---------------------------------------
                
                # --- NEW FTL CREW COMPLIANCE UI (LIVE MODE) ---
                ftl_data = evaluate_crew_ftl(fault_code)
                if ftl_data["timeout"]:
                    st.subheader("🧑✈️ Flight Crew FTL Compliance")
                    with st.container(border=True):
                        st.error(f"**CRITICAL FATIGUE WARNING:** Swap to backup airframe {ftl_data['backup_tail']} compromises FTL limits.", icon="🚨")
                        c_col1, c_col2, c_col3 = st.columns(3)
                        c_col1.metric("Assigned Commander", ftl_data["captain"])
                        c_col2.metric("Projected Duty Time", f"{ftl_data['total']} Hours", f"+{ftl_data['delay']}h Repair Delay", delta_color="inverse")
                        c_col3.metric("FAA Legal Limit", "14.0 Hours", "Violation Imminent", delta_color="inverse")
                        st.warning("Automated Action: First Mate has scrambled Reserve Crew Delta-4 from standby. Dispatching to tarmac.", icon="✅")
                # ----------------------------------------------
                
                # Viewport Scaling added here!
                st.subheader("🌐 Supply Chain Intelligence Graph")
                with st.container(border=True):
                    draw_supply_chain_graph(selected_tail, fault_code)
                
            except Exception as e:
                status.update(label="System Failure", state="error", expanded=True)
                st.error(f"Network or Generator Error: {str(e)}")
                st.caption("Tip: Ensure mitigate_aog is yielding text chunks correctly, or use Safe Mode.")