#📱 Spam Back! — Automated LLM-Powered Responses to iMessage Spam

Spam Back! is a macOS-based automation tool that detects incoming iMessage spam, generates a safe and human-like response using an LLM (LLaMA 3 via Ollama), and replies automatically — wasting scammers' time without putting the user at risk.

This project combines:
* macOS message database access
* LLM prompt engineering
* A custom summary + reply pipeline
* Automated iMessage sending
* A local conversation history database

---

## 🚀 Features

* 📥 Automatically detects new incoming messages in iMessage
* 🧠 Uses LLaMA 3 (via Ollama) to generate human-like responses
* 🔁 Maintains conversation summaries for coherent multi-turn replies
* ✉️ Sends replies automatically using macOS-compatible iMessage automation
* 🗂️ Local SQLite database for message history (no cloud use)
* 🔒 Privacy-preserving — LLM runs locally, nothing leaves your machine

---

## 🧩 Directory Structure
```
Spam_Back/
│
├── config/
│   ├── __init__.py
│   ├── config_parser.py
│
├── data/
│
├── src/
│   ├── __init__.py
│   ├── core.py
│   ├── llm_prompter.py
│   ├── prompt_builder.py
│   ├── message_db_utils.py
│   ├── read_imessage.py
│   ├── write_imessage.py
│   ├── spam_detector.py
│
├── tests/
│   ├── prompt_builder_test.py
│   ├── test_scratch.py
│
└── main.py
```

---

## 🛠️ Requirements

### System
* macOS
* Python 3.10+
* Full Disk Access enabled for Terminal (needed for `chat.db`)

### Python Libraries
```
sqlite3
mac_imessage
ollama
configparser
```

### LLM Backend
Install Ollama:  
https://ollama.com

Then pull the LLaMA 3 model:
```bash
ollama pull llama3
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd Spam_Back
```

### 2. Set up a virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Give Terminal Full Disk Access
macOS → Settings → Privacy & Security → Full Disk Access  
Enable for:
* Terminal (or iTerm)
* Python (optional but useful)

This allows reading the iMessage `chat.db`.

---

## ▶️ Running the System

Run:
```bash
python main.py
```

Once running, the system will:
1. Create or load `messages.db`
2. Initialize message history
3. Begin polling for new incoming messages
4. For each spam message detected:
   * Build a conversation prompt
   * Call LLaMA 3
   * Generate a safe, confusing reply
   * Send it automatically

---

## 🧠 How It Works

### 1. Message Reader (`read_imessage.py`)
Polls the macOS `chat.db` database every second and detects new messages.

### 2. Spam Detector (`spam_detector.py`)
A rule-based initial classifier that uses:
* Keyword triggers
* Link scanning
* Message patterns

### 3. Prompt Builder (`prompt_builder.py`)
Constructs prompts using:
* Conversation history
* Safety guidelines
* Spam-wasting persona

### 4. LLM Engine (`llm_prompter.py`)
Uses the locally running LLaMA 3 model via the Ollama API.  
Streaming is supported for faster output.

### 5. Message Writer (`write_imessage.py`)
Uses the `mac_imessage` package to send iMessages automatically.

### 6. Conversation Database (`messages.db`)
Stores:
* Chat ID
* Last seen message
* Summary
* Spam flag

---

## 💬 Example

**Spam message:**
> Dear User, our automated security systems have flagged unusual activity… Please respond with "VERIFY-OK"…

**Automatic reply (generated):**
> That sounds like a serious notification! I've never gotten one of those before. Does this "Security Operations Tea" person mention what kind of security measures they're talking about? Are they asking me to confirm anything specific or just in general? By the way, have you ever noticed how some login pages can be super slow or glitchy sometimes?

This reply is intentionally:
* Vague
* Confusing
* Harmless
* Time-wasting

Exactly what we want.

---

## 🧪 Tests
```
tests/
├── prompt_builder_test.py  # Validates prompt structure
└── test_scratch.py         # Manual/dev scratch tests
```

---

## 🧱 Current Limitations

* Only supports macOS
* Polling-based detection (not event-driven)
* Spam classifier is rule-based (not ML yet)
* Multi-threaded chat support is limited

---

## 🔭 Future Improvements

* Train a proper spam classifier (ML-based)
* Build a dashboard to show conversation metrics
* Support multiple simultaneous chat threads
* Add personas or adjustable conversation styles
* Expand to WhatsApp / SMS / Telegram
