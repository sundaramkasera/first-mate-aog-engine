# ✈️ First Mate: Enterprise AOG Mitigation Engine

> **AI-powered logistics routing, cascading network simulation, and FAA compliance engine built for aviation command centers.**

[![Built with Streamlit](https://img.shields.io/badge/Built_with-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Powered by Cohere](https://img.shields.io/badge/Powered_by-Cohere_Command_R+-39594D.svg)](https://cohere.com/)
[![Database](https://img.shields.io/badge/Database-Coral_Cross--Source_SQL-0081F1.svg)](#)

## 🚨 The Problem: The $150,000/Hour Bottleneck
When a commercial aircraft breaks down (AOG - Aircraft on Ground), the airline loses between $25,000 to $150,000 per hour. Current mitigation requires commercial dispatchers to manually cross-reference siloed databases: maintenance manuals, inventory warehouses, tarmac fleet status, weather data, and crew scheduling. This manual friction leads to massive downstream network delays and displaced passengers.

## 💡 The Solution: First Mate
First Mate is a multi-agent orchestration dashboard that acts as a digital dispatcher. It synthesizes mechanical requirements, global inventory, fleet availability, and human safety regulations in real-time to generate instant, actionable Recovery Directives.

### 🌟 Core Enterprise Features

* **Multi-Database AI Routing:** Utilizes **Cohere Command R+** to autonomously write and execute SQL queries against 5 distinct data tables via the **Coral SQL engine**.
* **Decoupled Architecture:** The LLM handles complex relational routing (finding parts and planes), while a deterministic Python background engine handles strict FAA mathematical constraints (Crew Fatigue).
* **Cascading Network Impact Simulator:** Dynamically queries downstream flight schedules to accurately predict the ripple effect of gate blockages and displaced passengers.
* **Human FTL Compliance Engine:** Automatically calculates Flight Time Limitations (FTL) for backup crews, seamlessly scrambling reserve pilots if the repair delay forces an FAA hours-on-duty violation.
* **Real-Time Streaming UX:** Built with Streamlit `@st.fragment` for isolated UI state management, real-time token streaming, and viewport-scaled interactive supply chain graphs.

---

## 🏗️ System Architecture

First Mate utilizes a strict Separation of Concerns. The AI does not guess mathematical outcomes; it queries them.

1. **Codex DB:** Maps distress fault codes (e.g., ERR-808 Engine Fire) to required replacement parts and estimated repair hours.
2. **Inventory DB:** Scans localized hub warehouses for component availability.
3. **Fleet DB:** Scans the localized tarmac for `IDLE` backup airframes.
4. **Crew Registry DB:** Tracks live hours-on-duty for assigned captains.
5. **Flight Schedule DB:** Tracks downstream connecting passengers.

---

## ⚙️ Installation & Deployment

### Prerequisites
* Python 3.9+
* A valid [Cohere API Key](https://dashboard.cohere.com/api-keys)

### Local Setup
1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR-USERNAME/first-mate-aog-engine.git](https://github.com/YOUR-USERNAME/first-mate-aog-engine.git)
   cd first-mate-aog-engine