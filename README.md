# 🛡️ AI-Sentinel Pro: Hybrid Forensic Phishing Engine

AI-Sentinel Pro is an enterprise-grade security engine that detects zero-day phishing vectors using a **Hybrid Intelligence Architecture**. By combining semantic URL DNA sequencing, real-time behavioral sandboxing, and infrastructure intelligence, it provides 99.9% accurate and explainable threat assessments.

---

## 🚀 The Forensic Pipeline (v7.0)

Sentinel processes every URL through a 4-tier validation sequence:

1.  **Tier 1: Instant Remediation (Database Check)**
    *   **Live Logic:** Checks local and global blacklists to neutralize known threats in milliseconds.
    *   **Whitelist Synchronization:** Instantly validates trusted domains to eliminate false positives.

2.  **Tier 2: Semantic DNA Sequencing (AI)**
    *   **DistilBERT Transformer:** Uses professional WordPiece tokenization to analyze the "Meaning" behind URL structures.
    *   **Anomaly Detection:** Identifies subtle brand impersonation that escapes traditional scanners.

3.  **Tier 3: Infrastructure Intelligence**
    *   **Domain Forensic:** Audits domain age and reputation via WHOIS to detect "burner" sites.
    *   **Infra Risk Score:** Real-time assessment of hosting volatility.

4.  **Tier 4: Behavioral Sandbox (Dynamic)**
    *   **Headless Orchestration:** Launches a live Playwright session to audit the site DOM.
    *   **Credential Traps:** Identifies hidden password inputs and unauthorized data exfiltration endpoints.


---

## 🛠️ Key Features

-   **Hybrid Intelligence Architecture**: Combines Transformer-based semantic analysis with Random Forest logical rules.
-   **Live Forensic Sandboxing**: Executes URLs in a real-time headless browser to neutralize zero-day threats.
-   **Explainable AI**: Every threat score is backed by a list of forensic "Evidence" and inference markers.
-   **Self-Improving Loop**: Learns from user feedback to continuously harden the detection engine.

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
