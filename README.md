---
title: AI Sentinel Pro
emoji: 🛡️
colorFrom: blue
colorTo: gray
sdk: docker
pinned: false
app_port: 7860
---

# 🛡️ Sentinel Forensic: High-Efficiency Phishing Analyst

Sentinel Forensic is a professional-grade security tool that detects phishing URLs using a **Rule-Based Heuristic Engine**. By focusing on forensic evidence rather than black-box AI, it provides transparent, explainable, and lightning-fast threat assessments.

---

## 🚀 The Forensic Pipeline

Sentinel processes every URL through a 3-stage validation process:

1.  **Tier 1: Global & Local Intelligence**
    *   **Live Feeds:** Syncs with online threat databases to identify known malicious patterns instantly.
    *   **Verified List:** Instantly validates trusted services (Google, Microsoft) to eliminate false positives.

2.  **Tier 2: DNA Pattern Matching (Heuristics)**
    *   Analyzes the URL structure for "Genetic Red Flags" (long strings, excessive dots, sensitive keywords like 'login' or 'verify').
    *   Detects typosquatting and suspicious domain obfuscation.

3.  **Tier 3: Deep Behavioral Scan**
    *   **Credential Harvesting:** Scans HTML for unauthorized password input fields.
    *   **External Routing:** Detects if data forms are sending information to third-party domains.
    *   **Authority Check:** Audits domain age via WHOIS (recently registered domains are flagged).

---

## 🛠️ Key Features

-   **Zero-Model Architecture:** No training required. Works out of the box with zero "guesswork."
-   **Explainable Verdicts:** Every risk score comes with a list of forensic "Evidence" found on the site.
-   **Continuous Data Logging:** Automatically builds your local threat database as you scan.
-   **High Performance:** Uses multi-threaded scanning to deliver results in under 3 seconds.

---

## 📂 Project Structure

```text
phishing-detector/
├── app.py                # Sentinel Forensic Dashboard
├── src/
│   └── features.py       # Rule-Based Heuristic Engine
├── data/
│   ├── phishing_dataset.csv # Local Threat Intelligence
│   └── whitelist.txt        # Trusted Domain Registry
└── requirements.txt      # Dependency Manifest
```

---

## ⚙️ Installation & Usage

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Dashboard**
   ```bash
   streamlit run app.py
   ```

---

## 📊 Risk Calculation Matrix

| Indicator | Risk Weight | Significance |
| :--- | :--- | :--- |
| **Password Field** | 40% | Direct indicator of credential harvesting attempts. |
| **External Form** | 30% | Detects data being exfiltrated to non-matching domains. |
| **URL DNA** | 25% | Flags structural anomalies and brand spoofing. |
| **Recent Domain** | 20% | Most phishing sites use domains less than 365 days old. |

---

**Disclaimer**: *Sentinel Forensic is a tool for security professionals. Always verify results manually before taking critical actions.*
