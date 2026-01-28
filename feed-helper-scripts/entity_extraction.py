"""
Entity extraction helper for article import scripts.
"""

from collections import Counter


try:
    import spacy
    import pytextrank
    nlp = spacy.load("en_core_web_sm")
    if not any(pipe_name == "textrank" for pipe_name, _ in nlp.pipeline):
        nlp.add_pipe("textrank")
    SPACY_AVAILABLE = True
    PYTEXTRANK_AVAILABLE = True
except (ImportError, OSError, ValueError):
    SPACY_AVAILABLE = False
    PYTEXTRANK_AVAILABLE = False
    print("⚠ spaCy or PyTextRank not available. Install with: pip install spacy pytextrank && python -m spacy download en_core_web_sm")
    print("  Entity extraction will be skipped.\n")

def extract_entities(text, top_n=5):
    """
    Extract top N named entities from text using spaCy.
    Returns comma-separated string of entities.
    """
    if not SPACY_AVAILABLE or not text:
        return keyword_fallback(text, top_n)
    try:
        doc = nlp(text[:10000])
        # 1. Top PERSON entity (by order of appearance)
        person_entity = None
        stopwords = set(nlp.Defaults.stop_words)
        for ent in doc.ents:
            norm = ent.text.strip().lower()
            if len(norm) > 2 and norm not in stopwords and any(c.isalnum() for c in norm):
                if ent.label_ == 'PERSON':
                    person_entity = norm
                    break
        # 2. Up to 3 PyTextRank phrases or non-PERSON entities (ORG, EVENT, GPE, PRODUCT, LAW)
        phrase_candidates = []
        # PyTextRank phrases first (in order)
        if PYTEXTRANK_AVAILABLE and hasattr(doc._, 'phrases'):
            for phrase in doc._.phrases:
                pnorm = phrase.text.strip().lower()
                if len(pnorm) > 2 and pnorm not in stopwords and any(c.isalnum() for c in pnorm):
                    if pnorm != person_entity and pnorm not in phrase_candidates:
                        phrase_candidates.append(pnorm)
        # Then non-PERSON entities (in order of appearance)
        for ent in doc.ents:
            norm = ent.text.strip().lower()
            if len(norm) > 2 and norm not in stopwords and any(c.isalnum() for c in norm):
                if ent.label_ in {'ORG', 'EVENT', 'GPE', 'PRODUCT', 'LAW'}:
                    if norm != person_entity and norm not in phrase_candidates:
                        phrase_candidates.append(norm)
        tags = []
        if person_entity:
            tags.append(person_entity)
        tags.extend(phrase_candidates[:3])
        if not tags:
            return keyword_fallback(text, top_n)
        return ', '.join(tags)
    except Exception as e:
        print(f"    ⚠ Entity extraction failed: {e}")
        return keyword_fallback(text, top_n)

# Simple keyword extraction fallback
import re
def keyword_fallback(text, top_n=5):
    # Lowercase and tokenize
    words = re.findall(r'\b\w+\b', text.lower())
    # Remove stopwords and short words
    try:
        import spacy
        stopwords = set(spacy.lang.en.stop_words.STOP_WORDS)
    except ImportError:
        stopwords = set()
    keywords = [w for w in words if w not in stopwords and len(w) > 2]
    counts = Counter(keywords)
    # Only include keywords that occur more than once
    top_keywords = [kw for kw, c in counts.most_common() if c > 1][:top_n]
    return ', '.join(top_keywords[:5])