# ExpoCheck 🛡️
> **The Local-First Git History Scanner for the Modern Developer.**

ExpoCheck is a powerful, user-friendly security tool designed to detect exposed API keys and secrets hidden deep within your local Git history. Built for "Vibe Coders" who want premium security without the command-line headache.

## 🚀 Why ExpoCheck?
Deleting a file from GitHub **does not** delete it from your history. Hackers scrape public commits in seconds.
ExpoCheck performs a **Deep Time Scan** on your local repository, checking every commit `diff` to find secrets you deleted months ago but forgot to scrub.

### Features
-   **🕵️ Deep History Scan:** Iterates through every commit in your `.git` database.
-   **🔐 Local-First Security:** Runs 100% locally on `localhost`. Your keys never leave your machine.
-   **🧠 Smart Detection:** Uses advanced Regex to detect:
    -   AWS Access/Secret Keys
    -   Google/Gemini API Keys
    -   OpenAI (sk-...) Keys
    -   Stripe, Slack, Twilio, and Generic High-Entropy Tokens
-   **✨ Premium UI:** A beautiful, dark-mode Web Dashboard. No more boring terminal logs.

## 🛠️ Technology Stack
-   **Backend:** Python 3.13 + FastAPI
-   **Engine:** GitPython (Direct object database access)
-   **Frontend:** HTML5, Vanilla JS, CSS3 (Glassmorphism & Neon Design)

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/Smik022/EXPO_CHECKER.git
cd EXPO_CHECKER

# Install dependencies
pip install -r requirements.txt
```

## ⚡ Usage

1.  **Start the Engine:**
    ```bash
    python server.py
    ```
2.  **Open Dashboard:**
    The tool will automatically launch your default browser to `http://127.0.0.1:8000`.
    _(If it doesn't, just click the link above)._

3.  **Scan a Repo:**
    -   Paste the **absolute path** to any local project (e.g., `C:\Users\You\Desktop\MyProject`).
    -   Click **START SCAN**.
    -   Watch the progress bar as it travels through time! 🕰️

## ⚠️ Disclaimer
ExpoCheck is a security tool intended for **defensive use only**. Scan your own repositories to protect yourself. The authors are not responsible for misuse.

---
