import json
from sentence_transformers import SentenceTransformer, util
import logging

class ReferenceMatcher:
    def __init__(self, reference_file="references.json"):
        self.references = []
        self.embeddings = []
        try:
            self.model = SentenceTransformer("BAAI/bge-small-en-v1.5")
            with open(reference_file, "r") as f:
                self.references = json.load(f)
            self.embeddings = self.model.encode(
                [ref["content"] for ref in self.references],
                convert_to_tensor=True
            )
        except Exception as e:
            logging.exception("Error loading references or model")

    def match(self, query, threshold=0.6):
        try:
            if not query.strip() or self.embeddings is None or len(self.embeddings) == 0:
                return None
            query_embedding = self.model.encode(query, convert_to_tensor=True)
            scores = util.pytorch_cos_sim(query_embedding, self.embeddings)[0]
            best_idx = scores.argmax().item()
            best_score = scores[best_idx].item()
            if best_score >= threshold:
                return self.references[best_idx]
        except Exception as e:
            logging.exception("Error during reference matching")
        return None

    def format_reference(self, reference):
        try:
            if reference and "link" in reference:
                return f"🔗 For more, see: {reference['link']}"
        except:
            pass
        return ""



from spellchecker import SpellChecker

spell = SpellChecker()

def correct_spelling(text):
    try:
        corrected = []
        for word in text.split():
            corrected_word = spell.correction(word)
            corrected.append(corrected_word or word)
        return " ".join(corrected)
    except Exception as e:
        logging.exception("Spelling correction failed")
        return text  # Fallback to original text
