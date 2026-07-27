import os
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
from qdrant_client import QdrantClient
from text_loader import retrieve_similar_chunks, generate_response
from reference_matcher import ReferenceMatcher
from reference_matcher import correct_spelling
from collections import Counter
import re
from flask_cors import CORS

# ========== 🔐 Load Environment Variables ==========
load_dotenv()
mistral_token = os.getenv("HF_API_TOKEN")
embedding_model = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

# ========== 🌐 Init Flask ==========
app = Flask(__name__)
CORS(app) 

# ========== 🧠 Get Vectorstore ==========
def get_vectorstore(embedding_model):
    model = SentenceTransformer(embedding_model)
    client = QdrantClient(path="qdrant_data")
    return client, model

# ========== 📁 Load Collection ==========
collection_name = os.getenv("COLLECTION_NAME", "customer_service_static")
client, model = get_vectorstore(embedding_model)

# ========== 📘 Reference Matcher ==========
matcher = ReferenceMatcher(reference_file="references.json")

conversation_history = []

# ========== 🧠 Semantic Validation ==========
def is_semantically_similar(reply, context_chunks, model, threshold=0.65):
    if not context_chunks:
        return False
    reply_embedding = model.encode(reply, convert_to_tensor=True)
    top_context = context_chunks[0]
    context_embedding = model.encode(top_context, convert_to_tensor=True)
    similarity = util.cos_sim(reply_embedding, context_embedding).item()
    print(f"🔎 Semantic similarity score: {similarity:.3f}")
    return similarity >= threshold


# ========== ✅ Intent Match Validator ==========
def is_intent_matched(user_input, bot_reply, model, threshold=0.6):
    """Check whether the bot reply shares the same intent/topic as the user question."""
    if not user_input or not bot_reply:
        return False
    input_embedding = model.encode(user_input, convert_to_tensor=True)
    reply_embedding = model.encode(bot_reply, convert_to_tensor=True)
    similarity = util.cos_sim(input_embedding, reply_embedding).item()
    print(f"🧭 Intent similarity score: {similarity:.3f}")
    return similarity >= threshold

def is_answer_entailed(reply, supporting_chunks, model, threshold=0.55):
    # Check if reply is "contained" in one of the chunks semantically
    reply_vec = model.encode(reply, convert_to_tensor=True)
    for chunk in supporting_chunks:
        chunk_vec = model.encode(chunk, convert_to_tensor=True)
        score = util.cos_sim(reply_vec, chunk_vec).item()
        if score >= threshold:
            return True
    return False


def detect_repetition(response: str, n: int = 3, threshold: int = 2) -> bool:
    """
    Detects repetition using regex and n-gram overlap.

    Parameters:
        response (str): The model's output string.
        n (int): N-gram size (default is 3).
        threshold (int): How many times a phrase must repeat to be flagged.

    Returns:
        bool: True if repetition is detected, else False.
    """

    # 1. Regex: Simple repeated phrase like "thanks thanks" or "yes yes yes"
    regex_repeat = re.findall(r'\b(\w+)( \1\b)+', response.lower())
    if regex_repeat:
        return True

    # 2. N-gram based repetition
    words = response.lower().split()
    if len(words) < n:
        return False

    ngrams = [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
    ngram_counts = Counter(ngrams)

    # Flag if any n-gram appears more than `threshold` times
    for phrase, count in ngram_counts.items():
        if count >= threshold:
            return True

    return False



# ========== 💬 Home ==========
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global conversation_history

    try:
        user_input = request.json.get("message", "").strip()
        print(f"\n🔵 User input: {user_input}")

        if not user_input:
            return jsonify({"response": "Please ask something."})

        # Step 1: Retrieve context
        try:
            context_chunks = retrieve_similar_chunks(user_input, model, client, collection_name)
        except Exception as e:
            print(f"[❌] Context retrieval error: {e}")
            context_chunks = []

        # Step 2: Retry loop on validation failure
        MAX_RETRIES = 1
        for attempt in range(MAX_RETRIES + 1):
            print(f"\n⚙️ Attempt {attempt + 1} to generate response...")
            try:
                reply = generate_response(user_input, context_chunks, mistral_token, conversation_history)
            except Exception as e:
                print(f"[💥] Model generation failed: {e}")
                reply = "I'm having trouble understanding that. Could you try rephrasing?"

            try:
                if not is_semantically_similar(reply, context_chunks, model):
                    print("❌ Semantic mismatch.")
                    continue
                if not is_intent_matched(user_input, reply, model):
                    print("⚠️ Intent mismatch.")
                    continue
                if not is_answer_entailed(reply, context_chunks, model):
                    print("🚫 Not entailed.")
                    continue
                # if detect_repetition(reply):
                #     print("🔁 Repetition detected.")
                #     continue
                # ✅ Passed all filters
                break

            except Exception as e:
                print(f"[⚠️] Filter chain error: {e}")
                reply = "I'm here to help with questions about our services. Let me try to answer again."
                break
        else:
            return jsonify({
                "response": "Sorry, I couldn't get the right answer from ORA PMS at the moment. Could you rephrase or ask another question?"
            })

        # Step 3: Add reference note (optional)
        try:
            corrected_input = correct_spelling(user_input)
            ref = matcher.match(corrected_input)
            ref_note = matcher.format_reference(ref)
        except Exception as e:
            print(f"[📘] Reference matcher failed: {e}")
            ref_note = ""

        # Step 4: Maintain history
        conversation_history.extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": reply}
        ])
        conversation_history = conversation_history[-6:]

        # Step 5: Final Response
        final_reply = f"{reply}\n\n{ref_note}" if ref_note else reply
        return jsonify({"response": final_reply})

    except Exception as e:
        # Absolute fallback if anything crashes at top level
        print(f"[❗] Fatal /chat error: {e}")
        return jsonify({"response": "Something went wrong. Please try again later."})



# ========== 🚀 Run ==========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)