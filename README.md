# 🤖 ORAPMS Customer Service Chatbot using RAG and LLMs

A Retrieval-Augmented Generation (RAG) chatbot designed to answer business-specific customer service queries using a custom knowledge base.

The chatbot allows businesses to upload their own knowledge base as a plain text file, which is automatically processed, embedded, indexed into a Qdrant vector database, and retrieved during inference. Retrieved context is then provided to **Mistral-7B-Instruct** through the Hugging Face Inference API to generate accurate, context-aware responses.

The architecture is generic and can be adapted to various domains such as hotels, hospitals, restaurants, universities, or customer support systems by simply replacing the dataset.

---

# ✨ Features

- 🔍 Retrieval-Augmented Generation (RAG)
- 📄 Business-specific knowledge base from TXT files
- ✂️ Automatic document preprocessing and chunking
- 🧠 Semantic embeddings using **BAAI/bge-small-en-v1.5**
- 🗂️ Vector similarity search with **Qdrant**
- 🤖 Response generation using **Mistral-7B-Instruct**
- ✅ Semantic response validation
- 🎯 Intent matching
- 📚 Optional reference matching for structured datasets
- 💬 Conversation history support
- 🌐 Flask-based REST API
- 🎨 Simple web interface

---

# 🏗️ System Architecture

> Replace the image below with your architecture diagram.

<p align="center">
  <img src="assets/rag_pipeline.png" width="900">
</p>

---

# 🧠 RAG Pipeline

The chatbot follows a Retrieval-Augmented Generation (RAG) workflow to generate reliable responses grounded in the uploaded business knowledge.

## Step 1 — Knowledge Base

Business information is provided as a plain text document.

Example:

```
Reservation Policy
Room Categories
Cancellation Policy
Check-in Rules
Payment Methods
```

The chatbot can work with any business dataset by replacing this file.

---

## Step 2 — Text Preprocessing

Before indexing, the dataset is cleaned by:

- Removing unnecessary whitespace
- Normalizing line breaks
- Formatting text consistently

This ensures higher-quality embeddings and better retrieval.

---

## Step 3 — Document Chunking

Large documents are divided into overlapping chunks.

```
Chunk 1
Chunk 2
Chunk 3
...
```

Chunk overlap preserves context across neighboring sections and improves retrieval accuracy.

---

## Step 4 — Embedding Generation

Each chunk is converted into a dense semantic vector using

**BAAI/bge-small-en-v1.5**

Rather than relying on keyword matching, embeddings capture the semantic meaning of the text.

---

## Step 5 — Vector Storage

The generated embeddings are stored inside a local **Qdrant** vector database.

Each stored record contains:

- Vector embedding
- Original text chunk
- Metadata

This enables fast semantic similarity search during inference.

---

## Step 6 — User Query Embedding

When a user asks a question, the same embedding model converts the query into a semantic vector.

Example:

```
How do I create a reservation?
```

---

## Step 7 — Semantic Retrieval

The embedded query is compared against the stored vectors using cosine similarity.

The chatbot retrieves the **Top-K** most relevant knowledge chunks from Qdrant.

---

## Step 8 — Prompt Construction

The retrieved context is inserted into the system prompt before sending it to the language model.

```
System Prompt

Context:
Retrieved Chunk 1
Retrieved Chunk 2
Retrieved Chunk 3

User:
How do I create a reservation?
```

This grounds the language model on business-specific information instead of relying solely on its pre-trained knowledge.

---

## Step 9 — Response Generation

The prompt is sent to

**Mistral-7B-Instruct**

through the Hugging Face Inference API.

The model generates a context-aware response using only the retrieved information.

---

## Step 10 — Response Validation

Before returning the answer, several validation steps are performed.

### Semantic Similarity

Checks whether the generated answer matches the retrieved context.

### Intent Matching

Ensures the response aligns with the user's question.

### Context Entailment

Verifies that the answer is supported by the retrieved knowledge.

If validation fails, the chatbot attempts regeneration or returns a safe fallback response.

---

# 💬 Chatbot Demo

<p align="center">
  <img src="assets/chatbot_demo.png" width="500">
</p>

Example interaction showing the chatbot answering customer queries using information retrieved from the indexed business knowledge base.

---

# 📁 Project Structure

```
chatbot/
│
├── data/
│   ├── mini dataset.txt
│   └── trivelles_dataset.txt
│
├── qdrant_data/
│
├── static/
│   ├── script.js
│   └── style.css
│
├── templates/
│   └── index.html
│
├── app.py
├── text_loader.py
├── setup_vectorstore.py
├── reference_matcher.py
├── references.json
├── requirements.txt
├── .env
└── README.md
```

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/yourusername/ORAPMS-Customer-Service-Chatbot-Using-RAG-and-LLMs.git

cd ORAPMS-Customer-Service-Chatbot-Using-RAG-and-LLMs
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root.

```env
HF_API_TOKEN=your_huggingface_token

EMBEDDING_MODEL=BAAI/bge-small-en-v1.5

COLLECTION_NAME=customer_service_static
```

---

# 📄 Preparing Your Dataset

Place your business knowledge file inside

```
data/
```

Example

```
data/mini dataset.txt
```

or

```
data/hotel_dataset.txt
```

---

# 🗂️ Build the Vector Database

Run

```bash
python setup_vectorstore.py
```

The script will

- preprocess the document
- split it into chunks
- generate embeddings
- store vectors inside Qdrant

---

# ▶️ Run the Chatbot

```bash
python app.py
```

The application starts on

```
http://localhost:8080
```

---

# 🌐 API

POST request

```
POST /chat
```

Example

```json
{
    "message":"How do I create a reservation?"
}
```

Response

```json
{
    "response":"To create a reservation, navigate to the Reservation module and click Add Reservation..."
}
```

---

# 🛠️ Technologies Used

- Python
- Flask
- Hugging Face Inference API
- Mistral-7B-Instruct
- Sentence Transformers
- BAAI/bge-small-en-v1.5
- LangChain
- Qdrant
- HTML
- CSS
- JavaScript

---

# 🚀 Future Improvements

- Multi-document knowledge base
- PDF and DOCX ingestion
- Hybrid keyword + semantic search
- Streaming LLM responses
- Docker support
- Cloud deployment
- User authentication
- Admin dashboard for dataset management

---

# 👩‍💻 Author

**Areeba Ghazal**

GitHub: https://github.com/areebaghazal88
