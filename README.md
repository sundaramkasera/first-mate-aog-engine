# ✈️ First Mate: Enterprise AOG Mitigation Engine

> **AI-powered logistics routing, cascading network simulation, and FAA compliance engine built for aviation command centers.**

[![Built with Streamlit](https://img.shields.io/badge/Built_with-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Powered by Cohere](https://img.shields.io/badge/Powered_by-Cohere_Command_R+-39594D.svg)](https://cohere.com/)
[![Database](https://img.shields.io/badge/Database-Coral_Cross--Source_SQL-0081F1.svg)](#)

---

## 🚨 The Problem: The $150,000/Hour Bottleneck
When a commercial aircraft breaks down (AOG - Aircraft on Ground), the airline loses between $25,000 to $150,000 per hour. 

Airlines possess all the data needed to fix the problem, but it is heavily siloed. Current mitigation requires commercial dispatchers to manually cross-reference disconnected systems: maintenance manuals, inventory warehouses, tarmac fleet status, live weather, and crew scheduling. This manual friction takes hours, leading to massive downstream network delays, displaced passengers, and spiraling operational costs.

## 💡 What We Built: First Mate
First Mate is a multi-agent orchestration dashboard that acts as an autonomous digital dispatcher. It synthesizes mechanical requirements, global inventory, fleet availability, and human safety regulations in real-time to generate instant, legally compliant **Recovery Directives**.

**Core Enterprise Features:**
* **Decoupled Architecture:** The LLM handles complex relational routing (finding parts and planes), while a deterministic Python background engine handles strict FAA mathematical constraints (Crew Fatigue) to save API tokens and guarantee mathematical accuracy.
* **Cascading Network Impact Simulator:** Dynamically queries downstream flight schedules to accurately predict the ripple effect of gate blockages and displaced passengers.
* **Human FTL Compliance Engine:** Automatically calculates Flight Time Limitations (FTL) for backup crews, seamlessly scrambling reserve pilots if the repair delay forces an FAA hours-on-duty violation.
* **Real-Time Streaming UX:** Built with Streamlit `@st.fragment` for isolated UI state management, real-time token streaming, and viewport-scaled interactive supply chain graphs.

## 🛠️ How We Used Coral (The Unified Data Layer)
To solve the data silo problem, we integrated **Coral** as our unified cross-source SQL engine. 

Instead of forcing our LLM (Cohere Command R+) to navigate complex APIs or multiple disparate JSON files, we used Coral to bridge 5 distinct datasets via a unified `aog_data.yaml` schema. This allowed our AI Agent to write standard, cross-source SQL queries against localized data as if it were a single Enterprise Data Warehouse. By abstracting the data-joining process, Coral completely eliminated LLM hallucination and drastically reduced routing latency.

## 📊 Connected Data Sources & The Logical "Join"
Our architecture relies on 5 distinct data tables. When an AOG is triggered, the system executes a cascading logical join across these sources:

1.  **Codex DB:** Maps the distress flare (e.g., `ERR-808 Engine Fire`) to the required part and estimated repair hours.
2.  **Inventory DB:** Scans localized hub warehouses to check if that specific part is in stock.
3.  **Fleet DB:** If stock is zero, it scans the localized tarmac for `IDLE` backup airframes.
4.  **Crew Registry DB:** Identifies the captain assigned to the backup tail and adds the repair delay to their live hours-on-duty to ensure they do not violate FAA safety limits.
5.  **Flight Schedule DB:** Tracks downstream connecting passengers departing from the AOG hub to calculate localized network bottlenecks.

---

## 🚀 Demo, Repo, and Setup

### Prerequisites
* Python 3.9+
* A valid [Cohere API Key](https://dashboard.cohere.com/api-keys)

### Local Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR-USERNAME/first-mate-aog-engine.git](https://github.com/YOUR-USERNAME/first-mate-aog-engine.git)
   cd first-mate-aog-engine

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   
3. Configure your API Keys:
   ```bash
   Create a .streamlit/secrets.toml file in the root directory.
   Add your Cohere key exactly like this:
   ```
   Ini, TOML
   
   COHERE_API_KEY = "your_actual_key_here"
   ```
4. Run the Command Center:
   ```bash
   python -m streamlit run app.py


(Note: The app is configured with an automated startup script to download and install the Coral Linux binary natively upon cloud deployment).

🔮 What's Next: Future Scalability
Currently, First Mate utilizes bounded .jsonl mock datasets to demonstrate Coral's SQL engine capabilities and ensure deterministic routing during offline presentations.

Our immediate roadmap focuses on replacing these static files with live production infrastructure:

Live API Integration: Hooking Coral directly into global commercial flight APIs (e.g., Sabre, Amadeus) and live ADS-B telemetry for real-time fleet positioning.

Dynamic Weather Re-Routing: Expanding the Open-Meteo integration to actively block runway swaps if localized crosswinds exceed airframe limits.

Write-Back Capabilities: Transitioning First Mate from a "read-only advisor" to an active dispatcher capable of executing POST requests to automatically rebook displaced passengers and file updated FAA flight plans.