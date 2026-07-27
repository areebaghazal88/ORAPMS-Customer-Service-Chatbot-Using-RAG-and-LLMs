```markdown
# 🤖 Business-Customized Chatbot (Flask + Qdrant + HuggingFace)

This is a domain-specific chatbot that can be customized to any business (hotel, clinic, mart, etc.) simply by uploading a `.txt` file with relevant information. It uses vector similarity for context retrieval and Mistral-7B (via Hugging Face Inference API) for response generation. Optionally, it supports references for specific datasets (e.g., ORAPMS).

---

## 📁 Folder Structure

```

CHATBOT2/
├── data/                      # Upload business-specific .txt files here
│   ├── mini dataset.txt
│   └── trivelles\_dataset.txt
│
├── qdrant\_data/              # Auto-generated vector store (delete before switching datasets)
│   ├── collection/
│   ├── .lock
│   └── meta.json
│
├── static/                   # Frontend styling
│   ├── script.js
│   └── style.css
│
├── templates/                # Frontend HTML template
│   └── index.html
│
├── venv/                     # Python virtual environment
│
├── .env                      # API keys and model config
├── app.py                    # Main chatbot backend (Flask)
├── delete.py                 # Optional cleanup script
├── reference\_matcher.py      # Reference handler (for ORAPMS dataset only)
├── references.json           # Reference metadata for ORAPMS
├── requirements.txt          # Python dependencies
├── setup\_vectorstore.py      # Embeds and stores your .txt file in Qdrant
├── text\_loader.py            # Utility to load and format chunks
├── web.config                # For deployment (e.g., IIS/Azure)
└── README.md                 # This file

````

---

## ⚙️ Setup Instructions

### 🔹 Step 1: Create Environment

```bash
cd your-repo
python -m venv venv
venv\Scripts\activate   # or source venv/bin/activate
pip install -r requirements.txt
````

---

### 🔹 Step 2: Configure `.env`

Create a `.env` file in the root directory and add:

```
HF_TOKEN=your_huggingface_token
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
MODEL=mistralai/Mistral-7B-Instruct-v0.1
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key_if_any
COLLECTION_NAME=your_collection_name
```

---

### 🔹 Step 3: Upload Your `.txt` File

Place your desired business knowledge file in the `data/` folder.

> 📌 For example: `trivelles_dataset.txt` for a hotel.

---

### 🔹 Step 4: Delete Existing Vector DB

Before switching datasets, **delete the existing Qdrant DB folder**:

```bash
rm -rf qdrant_data/
```

---

### 🔹 Step 5: Run `setup_vectorstore.py`

Update the script with your file name and collection name inside:

```python
# Inside setup_vectorstore.py
FILE_PATH = "data/trivelles_dataset.txt"
COLLECTION_NAME = "trivelles"
```

Then run:

```bash
python setup_vectorstore.py
```

This loads, chunks, embeds, and stores your text into Qdrant.

---

### 🔹 Step 6: Run `text_loader.py`

This script formats and loads the chunks for retrieval.

```bash
python text_loader.py
```

---

### 🔹 Step 7: Run the Chatbot

```bash
python app.py
```

The chatbot runs at `http://localhost:5000` and can be accessed via frontend or API.

---

## 🧠 Dataset-Specific Reference Matching (ORAPMS only)

* The `reference_matcher.py` and `references.json` are only used for datasets that include **structured references** (like **mini dataset / ORAPMS**).
* If you're using a new `.txt` file without references, you **must remove or comment out** the reference matcher section in `app.py`.

#### To enable references:

* Make a `references.json` matching the structure of your custom dataset
* Keep the matcher logic in `app.py` uncommented
* It will automatically append reference notes in responses

---

## 🌐 Frontend Usage

The project includes a basic frontend:

* `/templates/index.html`: HTML form for sending queries
* `/static/style.css`: Styling
* `/static/script.js`: Fetch-based AJAX for API requests

To use it:

1. Run `app.py`
2. Open `http://localhost:5000/` in browser

---

## 📤 API Usage

You can also interact via API:

```bash
curl -X POST http://localhost:5000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Do you have free WiFi?"}'
```

---

## 🧪 Test & Evaluate

You can build a test suite to evaluate chatbot answers against expected outputs (not included by default).

---

## 🚫 Common Mistakes

* ❗ **Forgetting to delete `qdrant_data/` when changing datasets**
* ❗ **Leaving `reference_matcher.py` active for datasets that don’t need it**
* ❗ **Not updating `FILE_PATH` and `COLLECTION_NAME` in `setup_vectorstore.py`**

---

## 👩‍💻 Maintainer

Areeba Ghazal
Email: [yourname@example.com](mailto:areebaghazal88@gmail.com)

```
