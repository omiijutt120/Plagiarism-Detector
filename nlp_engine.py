"""
nlp_engine.py – Academic Plagiarism Detection NLP Engine
ACP Project

Techniques Used (Pure Python — no heavy libraries):
  1. Text Preprocessing  → tokenize, remove stopwords, clean
  2. TF-IDF Vectors      → term frequency × inverse document frequency
  3. Cosine Similarity   → angular similarity between TF-IDF vectors
  4. Jaccard Similarity  → word set overlap ratio
  5. N-gram Fingerprint  → detect copied phrases (bigrams, trigrams)
  6. Sentence Matching   → difflib SequenceMatcher per sentence pair
  7. Risk Classification → weighted score → Low / Medium / High / Critical
"""

import re, math, difflib
from collections import Counter

# ── Stopwords (compact English set) ────────────────────────────────────────
STOPWORDS = {
    'the','a','an','and','or','but','in','on','at','to','for','of','with',
    'by','from','is','are','was','were','be','been','have','has','had',
    'do','does','did','will','would','could','should','may','might',
    'this','that','these','those','it','its','he','she','they','we','i',
    'my','your','his','her','their','our','which','who','what','when',
    'where','how','if','as','not','no','so','up','out','about','into',
    'than','then','there','here','can','just','also','all','more','some',
    'such','each','both','only','same','other','any','most','very',
}


# ════════════════════════════════════════════════════════════════════════════
#  TextPreprocessor
# ════════════════════════════════════════════════════════════════════════════
class TextPreprocessor:
    """Encapsulates all text-cleaning operations."""

    def clean(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,!?]', '', text)
        return text.strip()

    def tokenize(self, text: str) -> list[str]:
        """Lowercase words only, excluding stopwords and short tokens."""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        return [w for w in words if w not in STOPWORDS]

    def get_sentences(self, text: str) -> list[str]:
        """Split text into sentences (min 15 chars)."""
        parts = re.split(r'(?<=[.!?])\s+', text.strip())
        return [p.strip() for p in parts if len(p.strip()) >= 15]

    def get_ngrams(self, tokens: list[str], n: int) -> list[str]:
        return [' '.join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]


# ════════════════════════════════════════════════════════════════════════════
#  TF-IDF Cosine Similarity
# ════════════════════════════════════════════════════════════════════════════
class TFIDFEngine:
    """
    Implements TF-IDF from scratch using only Python math.
    No sklearn or external libraries required.
    """

    def _tf(self, tokens: list[str]) -> dict:
        total = len(tokens) or 1
        return {w: c / total for w, c in Counter(tokens).items()}

    def _idf(self, word: str, docs: list[set]) -> float:
        containing = sum(1 for d in docs if word in d)
        return math.log((len(docs) + 1) / (containing + 1)) + 1  # smoothed

    def cosine(self, text1: str, text2: str, prep: TextPreprocessor) -> float:
        t1 = prep.tokenize(text1)
        t2 = prep.tokenize(text2)
        if not t1 or not t2:
            return 0.0

        docs = [set(t1), set(t2)]
        vocab = set(t1) | set(t2)

        tf1, tf2 = self._tf(t1), self._tf(t2)
        idf = {w: self._idf(w, docs) for w in vocab}

        v1 = [tf1.get(w, 0) * idf[w] for w in vocab]
        v2 = [tf2.get(w, 0) * idf[w] for w in vocab]

        dot  = sum(a * b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a * a for a in v1)) or 1
        mag2 = math.sqrt(sum(b * b for b in v2)) or 1

        return round(dot / (mag1 * mag2), 4)


# ════════════════════════════════════════════════════════════════════════════
#  Similarity Metrics
# ════════════════════════════════════════════════════════════════════════════
class SimilarityMetrics:
    """Collection of similarity algorithms — demonstrates OOP utility classes."""

    def jaccard(self, tokens1: list, tokens2: list) -> float:
        s1, s2 = set(tokens1), set(tokens2)
        if not s1 or not s2:
            return 0.0
        return round(len(s1 & s2) / len(s1 | s2), 4)

    def ngram_similarity(self, tokens1: list, tokens2: list,
                         prep: TextPreprocessor, n: int = 3):
        ng1 = set(prep.get_ngrams(tokens1, n))
        ng2 = set(prep.get_ngrams(tokens2, n))
        if not ng1 or not ng2:
            return 0.0, []
        common = ng1 & ng2
        score  = round(len(common) / max(len(ng1), len(ng2)), 4)
        # Sort by length for display (longer = more damning)
        phrases = sorted(common, key=len, reverse=True)[:15]
        return score, list(phrases)

    def sentence_matches(self, text1: str, text2: str,
                         prep: TextPreprocessor, threshold: float = 0.60):
        s1 = prep.get_sentences(text1)
        s2 = prep.get_sentences(text2)
        results = []
        for sent1 in s1:
            for sent2 in s2:
                r = difflib.SequenceMatcher(None,
                                            sent1.lower(),
                                            sent2.lower()).ratio()
                if r >= threshold:
                    results.append({
                        'sent1': sent1,
                        'sent2': sent2,
                        'ratio': round(r * 100, 1),
                    })
        results.sort(key=lambda x: x['ratio'], reverse=True)
        return results[:12]

    def highlight_sentences(self, target: str, reference: str,
                            prep: TextPreprocessor, threshold: float = 0.55):
        """Returns sentences in `target` tagged as flagged/clean vs `reference`."""
        ref_sents = [s.lower() for s in prep.get_sentences(reference)]
        result = []
        for sent in prep.get_sentences(target):
            best = 0.0
            if ref_sents:
                best = max(
                    difflib.SequenceMatcher(None, sent.lower(), rs).ratio()
                    for rs in ref_sents
                )
            result.append({
                'text':    sent,
                'flagged': best >= threshold,
                'score':   round(best * 100, 1),
            })
        return result


# ════════════════════════════════════════════════════════════════════════════
#  Main Analyzer
# ════════════════════════════════════════════════════════════════════════════
class PlagiarismAnalyzer:
    """
    Orchestrator class — combines all NLP modules into one analysis pipeline.

    OOP Concepts:
        Composition  — owns Preprocessor, TFIDFEngine, SimilarityMetrics
        Encapsulation — internal methods hidden behind public analyze()
        Abstraction   — caller only sees one method: analyze(text1, text2)
    """

    def __init__(self):
        self.prep    = TextPreprocessor()
        self.tfidf   = TFIDFEngine()
        self.metrics = SimilarityMetrics()

    def _risk(self, score: float) -> tuple[str, str]:
        if score >= 0.70: return 'CRITICAL', 'critical'
        if score >= 0.45: return 'HIGH',     'high'
        if score >= 0.20: return 'MEDIUM',   'medium'
        return 'LOW', 'low'

    def analyze(self, text1: str, text2: str,
                title1: str = 'Document A',
                title2: str = 'Document B') -> dict:
        """
        Run full plagiarism analysis and return a structured report dict.
        """
        t1 = self.prep.clean(text1)
        t2 = self.prep.clean(text2)

        tok1 = self.prep.tokenize(t1)
        tok2 = self.prep.tokenize(t2)

        # ── Run all metrics ──
        cosine  = self.tfidf.cosine(t1, t2, self.prep)
        jaccard = self.metrics.jaccard(tok1, tok2)
        ng3, matched_phrases = self.metrics.ngram_similarity(tok1, tok2, self.prep, n=3)
        ng2, _               = self.metrics.ngram_similarity(tok1, tok2, self.prep, n=2)

        # ── Weighted overall score ──
        overall = round(cosine * 0.40 + jaccard * 0.25 + ng3 * 0.20 + ng2 * 0.15, 4)

        risk_label, risk_key = self._risk(overall)

        # ── Sentence-level analysis ──
        sent_matches = self.metrics.sentence_matches(t1, t2, self.prep)
        highlighted1 = self.metrics.highlight_sentences(t1, t2, self.prep)
        highlighted2 = self.metrics.highlight_sentences(t2, t1, self.prep)

        flagged1 = sum(1 for s in highlighted1 if s['flagged'])
        flagged2 = sum(1 for s in highlighted2 if s['flagged'])

        return {
            # Scores (0–1 floats)
            'overall':      overall,
            'cosine':       cosine,
            'jaccard':      jaccard,
            'ngram3':       ng3,
            'ngram2':       ng2,

            # Percentages for display
            'overall_pct':  round(overall  * 100, 1),
            'cosine_pct':   round(cosine   * 100, 1),
            'jaccard_pct':  round(jaccard  * 100, 1),
            'ngram3_pct':   round(ng3      * 100, 1),
            'ngram2_pct':   round(ng2      * 100, 1),

            # Risk
            'risk_label':   risk_label,
            'risk_key':     risk_key,

            # Text metadata
            'title1':       title1,
            'title2':       title2,
            'words1':       len(text1.split()),
            'words2':       len(text2.split()),
            'sents1':       len(self.prep.get_sentences(t1)),
            'sents2':       len(self.prep.get_sentences(t2)),

            # Evidence
            'matched_phrases':   matched_phrases,
            'sentence_matches':  sent_matches,
            'highlighted1':      highlighted1,
            'highlighted2':      highlighted2,
            'flagged1':          flagged1,
            'flagged2':          flagged2,
            'matched_count':     len(sent_matches),
        }
