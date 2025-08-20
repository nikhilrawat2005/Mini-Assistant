# 🤖 Mini Assistant

Mini Assistant is a **personal AI-powered desktop assistant** built in Python.  
It can listen, understand, and respond to user queries, perform offline & online tasks, search the web, maintain memory, and assist in daily workflows.  

---

## ✨ Features
- 🎤 **Voice & Text Mode** – Interact with the assistant via voice or text.  
- 🧠 **Core Brain & NLU** – Natural Language Understanding (`brain.py`, `nlu.py`) to process commands.  
- 🔎 **Search Engine** – Custom search crawler, indexer, and query classifier.  
- 📚 **Dictionary & Tools** – Offline utilities (maths, system info, time, etc.).  
- 📝 **Memory & Learning** – Stores knowledge in `mini_learning.db` & `memory.json`.  
- 📂 **Data Persistence** – Logs & notes saved locally.  
- 🔐 **Secure** – Credentials & sensitive data kept private.  

---

## 📂 Project Structure
```
MiniAssistant/
│── main.py                # Entry point
│── mini.py                # Mini Assistant interface
│── requirements.txt       # Python dependencies
│── core/                  # Brain & language understanding
│   ├── brain.py
│   ├── nlu.py
│── tools/                 # Utilities & modules
│   ├── dictionary.py
│   ├── offline_tools.py
│   ├── search_engine_2.py
│   ├── search_engine/     # Custom search engine system
│       ├── crawler.py
│       ├── parser.py
│       ├── query_classifier.py
│       ├── search_index.py
│       ├── mini_integration.py
│       ├── seed_loader.py
│── data/                  # Local databases
│   ├── memory.json
│   ├── mini_learning.db
│   ├── sources.json
│── utils/                 # Helper utilities
│── .gitignore             # Ignore sensitive/log files
```

---

## ⚙️ Installation
### 1. Clone the repository
```bash
git clone https://github.com/nikhilrawat2005/Mini-Assistant.git
cd Mini-Assistant
```

### 2. Create & activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate   # Linux/Mac
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Usage
### Run Mini Assistant
```bash
python main.py
```

- By default, Mini will start in **text mode**.  
- To use **voice mode**, enable microphone in `mini.py`.  

---

## 🔧 Tools & Modules
- **Dictionary (`dictionary.py`)** – word meanings, synonyms, usage.  
- **Offline Tools (`offline_tools.py`)** – calculations, system info, date/time utilities.  
- **Search Engine (`search_engine/`)** – crawler, parser, indexing, query classification.  
- **Learning (`data/mini_learning.db`)** – stores knowledge over time.  

---

## 🛡️ Security & Privacy
- All sensitive files (like `credentials.json`, `.db`, `.sqlite`, `chromedriver.exe`, logs) are **ignored** in Git.  
- Only safe, reusable code is uploaded to GitHub.  

---

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss.  

---

## 📜 License
This project is licensed under the **MIT License** – free to use and modify.  
