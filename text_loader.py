import os
import re
import math
import json
from langchain.schema import Document
from typing import List
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

# ---------- 🔍 Vector Retrieval ----------
def retrieve_similar_chunks(query, model, client, collection_name, top_k=5):
    try:
        vector = model.encode(f"query: {query}").tolist()
        results = client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=top_k,
            with_payload=True,
            with_vectors=False
        )
        chunks = [hit.payload.get("text", "").strip() for hit in results if hit.payload.get("text")]
        for idx, chunk in enumerate(chunks):
            print(f"    ➤ Chunk {idx+1}: {chunk[:100]}...")
        return chunks
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[❌] Retrieval failed: {e}")
        return []  # Silent fail — empty list triggers fallback response


# ---------- 🧠 Mistral Response ----------
def estimate_token_count(text):
    return max(1, math.ceil(len(text) / 3.5))

def get_dynamic_token_limit(prompt_text, max_total=4096, buffer=200):
    prompt_tokens = estimate_token_count(prompt_text)
    return max(100, min(1000, max_total - prompt_tokens - buffer))

# ---------- 🧠 Mistral Response ----------
def generate_response(user_input, context_chunks, mistral_token, conversation_history=None, model_id="mistralai/Mistral-7B-Instruct-v0.3"):
    print(f"\n[🧠] Generating response for: {user_input}")
    
    if not mistral_token:
        print("❌ Mistral HF_API_TOKEN is missing.")
        return "I'm here to help with questions about our services. Just let me know what you'd like to know!"
    
    # 🛑 Clean up context chunks — remove any rules/instructions accidentally stored in DB
    filtered_chunks = []
    for chunk in context_chunks:
        if "RULES:" in chunk or "You are a professional" in chunk or "Passage:" in chunk:
            continue
        filtered_chunks.append(chunk.strip())
    
    if not filtered_chunks:
        print("[⚠️] No relevant context chunks found — triggering fallback message.")
        return "I'm here to help with questions about our services. Just let me know what you'd like to know!"
    
    client = InferenceClient(model=model_id, token=mistral_token)
    context = "\n\n".join(filtered_chunks)

    # ✅ Separate rules from content clearly
    system_prompt = f"""
You are a professional and strict customer service assistant.

Follow these rules exactly:
1. ONLY answer using the information inside CONTEXT.
2. If the user's question is NOT clearly answerable from CONTEXT, respond with:
   "I'm here to help with questions about our services. Just let me know what you'd like to know!"
3. NEVER summarize, explain, greet, add extra info, or provide links.
4. DO NOT thank the user, repeat their question, or speculate.
5. DO NOT answer general knowledge questions.
6. Ignore compliments, thank yous, greetings, jokes, unknowns, empty or general chat. Respond with the same default message.

---
CONTEXT START
{context}
CONTEXT END
""".strip()

    messages = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        messages.extend(conversation_history[-6:])
    messages.append({"role": "user", "content": user_input})

    dynamic_max_tokens = get_dynamic_token_limit(system_prompt + "\nUser: " + user_input)

    try:
        result = client.chat_completion(
            messages=messages,
            max_tokens=dynamic_max_tokens,
            temperature=0.0
        )
        reply = result.choices[0].message["content"]
        cleaned_reply = re.sub(r"[^\x00-\x7F]+", "", reply).strip()
        print(f"[✅] Model reply: {cleaned_reply}")
        return cleaned_reply

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[💥] Mistral API error: {e}")
        return "I'm having a bit of trouble processing that. Please try again shortly."



# ---------- 💬 CLI Chat Loop ----------
def chat_with_bot(client, model, collection_name, mistral_token):
    print("\n🤖 Chatbot is ready! Type 'exit' to quit.\n")
    print("Bot: Hello, how can I help you?")
    conversation_history = []

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Ending chat. Goodbye!")
            break

        print(f"\n[👤] User asked: {user_input}")
        chunks = retrieve_similar_chunks(user_input, model, client, collection_name)

        bot_response = generate_response(
            user_input=user_input,
            context_chunks=chunks,
            mistral_token=mistral_token,
            conversation_history=conversation_history
        )

        print(f"Bot: {bot_response}\n")

        conversation_history.extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": bot_response}
        ])
        conversation_history = conversation_history[-6:]

# ---------- 🔁 Main ----------
if __name__ == "__main__":
    mistral_token = os.getenv("HF_API_TOKEN")  # Or replace with actual token
    collection_name = "customer_service_static"
    embedding_model = "BAAI/bge-small-en-v1.5"

    print("[🚀] Starting chatbot script...")
    client = QdrantClient(path="qdrant_data")
    model = SentenceTransformer(embedding_model)
    print("[✅] Models and Qdrant client loaded.")

    if not client.collection_exists(collection_name):
        print(f"❌ Collection '{collection_name}' not found. Run the setup script first.")
    else:
        print(f"[📦] Using collection: {collection_name}")
        chat_with_bot(client, model, collection_name, mistral_token)
