# 🛡️ InsiderThreat-AI: Hybrid Threat Detection System

## 🌟 Overview
**InsiderThreat-AI** is a state-of-the-art security platform designed to detect malicious, negligent, or compromised user activity within a corporate environment. By leveraging a **Hybrid AI Architecture**, the system bridges the gap between mathematical anomaly detection and human-like contextual reasoning.

Traditional SIEMs often fail because they lack "intent" analysis. This system solves that by utilizing **Hybrid AI** to map behavior to two primary threat categories:
- 🔴 **Type 1: Password-Based Insider Threat** (Credential Leakage, Password Sharing, VPN Keys).
- 🟠 **Type 2: Configuration / Governance Threat** (Ex-Employee active accounts, Admin privilege misuse, Role mismatches).

---

## 🏗️ System Architecture

The project is built on a modular pipeline designed for scalability and explainability.

*   **Data Loader (`data_loader.py`):** Ingests diverse datasets including Email logs, Psychometric profiles (OCEAN model), File access logs, and the **Employee Status Database** (Current/Ex).
*   **Synthetic Engine (`generate_synthetic_data.py`):** Generates high-fidelity logs with specific scenarios:
    - **Credential Leakage**: Sharing "Admin@123" via email.
    - **Governance Failure**: Ex-employee logging in from an "Unknown Location".

### 2. 🧠 Behavioral ML Engine (`ml_engine.py`)
This layer handles the numerical heavy lifting. It establishes a "Baseline of Normalcy" for every user.
*   **Feature Engineering:** Extracts behavioral vectors (e.g., after-hours activity frequency, attachment volumes, unusual process executions).
*   **Isolation Forest:** Uses unsupervised learning to detect outliers that don't fit the standard user profile.
*   **Risk Scoring:** Assigns a 0-100 mathematical anomaly score.

### 3. ✍️ Semantic Summarization Layer (`summarizer.py`)
The "Bridge" between raw data and the LLM. 
*   It transforms cold CSV rows and ML scores into structured **Natural Language Narratives**.
*   This allows the LLM to "read" the user's behavior as if it were a story, providing context that raw numbers cannot convey.

### 4. 🤖 LLM Intent Classification (`llm_engine.py`)
The "Brain" of the system. It acts as a Virtual SOC Analyst.
*   **Structured Reasoning:** Processes the behavior summary through an advanced prompt engineering chain.
*   **Categorization:** Classifies intent into `Malicious`, `Negligent`, or `Normal`.
*   **MITRE ATT&CK Mapping:** Automatically maps detected behaviors to MITRE framework concepts (e.g., T1071 - Application Layer Protocol).
*   **Explainable AI (XAI):** Generates a detailed justification for every flag, reducing the "Black Box" problem in security.
*   **Agnostic Backend:** Supports high-tier models (GPT-4), local LLaMA-3, or a high-speed heuristic mock for development (**Simulation Mode**).

### 5. 📡 Live System Monitor (`network_monitor.py`)
A real-time component that monitors the local environment:
*   **Network Analysis:** Tracks active connections and scans for suspicious ports (e.g., 4444 for Meterpreter).
*   **Deep Network Scan:** Performs an ARP sweep and ping sweep to discover hidden devices on the local subnet.
*   **Service Monitoring:** Tracks running Windows services to detect persistence mechanisms.
*   **Live AI Assessment:** Allows the LLM to analyze the "Current State" of the local machine to detect ongoing attacks.

---

### 6. 🖥️ SOC Analyst Dashboard (`streamlit_app.py`)
The primary interface for security professionals, organized into two specialized workspaces:
*   **Historical Log Analysis Tab:** Visualize ML-ranked risk scores, drill down into user summaries, and trigger LLM reasoning for deep forensics.
*   **Live System Monitor Tab:** Real-time visibility into local services, connections, and hardware interfaces. 
*   **Interactive Timelines & MITRE Details:** View the AI's reasoning directly alongside the raw data and framework mappings.
*   **Simulation Mode Toggle:** High-speed development mode to test UI and pipeline flow without API overhead.

---

## 🛠️ Technology Stack
| Category | Tools & Frameworks |
| :--- | :--- |
| **Core Logic** | Python 3.10+, Pandas, NumPy |
| **Machine Learning** | Scikit-Learn (Isolation Forest, StandardScaler) |
| **Large Language Models** | OpenAI GPT-4 / local LLaMA-3 / Structured Mock Interface |
| **Dashboard** | Streamlit |
| **System Interaction** | Psutil, Subprocess (netsh, arp) |

---

## 🚀 Getting Started

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate Threat Data:**
   ```bash
   python generate_synthetic_data.py
   ```

3. **Launch the Dashboard:**
   ```bash
   streamlit run streamlit_app.py
   ```

---

## 🎯 Project Goals
- **Reduce Alert Fatigue:** By filtering "noisy" anomalies through an LLM.
- **Provide Context:** Moving from "User X did Y" to "User X's behavior suggests deliberate data exfiltration."
- **Proactive Hunting:** Using live monitors to catch threats as they emerge.
