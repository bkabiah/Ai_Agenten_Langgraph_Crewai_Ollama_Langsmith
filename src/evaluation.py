import requests
import re

class OllamaEvaluator:
    """Custom Evaluator der Ollama direkt ueber die HTTP-API anspricht."""

    def __init__(self, model="llama3.2", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def _call_ollama(self, prompt):
        """Ruft das lokale Ollama-Modell auf."""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            return response.json().get("response", "")
        except Exception as e:
            return f"FEHLER: {e}"

    def _extract_score(self, text):
        """Extrahiert eine Zahl zwischen 0 und 1 aus dem Text."""
        match = re.search(r'(0\.\d+|1\.0|1|0)', text.strip())
        if match:
            score = float(match.group(1))
            return min(max(score, 0.0), 1.0)
        return 0.5

    def evaluate_relevance(self, customer_data, email_text):
        """Bewertet die Relevanz der E-Mail fuer den Kunden."""
        prompt = f"""Bewerte auf einer Skala von 0.0 bis 1.0 wie relevant diese E-Mail fuer den Kunden ist.
0.0 = Gar nicht relevant, generischer Text
1.0 = Perfekt auf den Kunden und seine Interessen zugeschnitten

Kundendaten: {customer_data}
E-Mail: {email_text}

Antworte NUR mit der Zahl (z.B. 0.85):"""
        response = self._call_ollama(prompt)
        return self._extract_score(response)

    def evaluate_coherence(self, email_text):
        """Bewertet die sprachliche Qualitaet der E-Mail."""
        prompt = f"""Bewerte auf einer Skala von 0.0 bis 1.0 die sprachliche Qualitaet dieses deutschen E-Mail-Textes.
0.0 = Viele Fehler, Halluzinationen, unverstaendlich
1.0 = Perfektes, professionelles Deutsch

E-Mail: {email_text}

Antworte NUR mit der Zahl (z.B. 0.75):"""
        response = self._call_ollama(prompt)
        return self._extract_score(response)

    def evaluate_persuasiveness(self, email_text):
        """Bewertet die Ueberzeugungskraft der E-Mail."""
        prompt = f"""Bewerte auf einer Skala von 0.0 bis 1.0 wie ueberzeugend diese Marketing-E-Mail ist.
0.0 = Langweilig, kein Kaufanreiz
1.0 = Extrem ueberzeugend, starker Call-to-Action

E-Mail: {email_text}

Antworte NUR mit der Zahl (z.B. 0.80):"""
        response = self._call_ollama(prompt)
        return self._extract_score(response)


def evaluate_email(subject, body, customer_name="Unbekannt", customer_category="Allgemein"):
    """Hauptfunktion zur Bewertung einer generierten E-Mail."""
    evaluator = OllamaEvaluator()

    customer_data = f"Name: {customer_name}, Kategorie: {customer_category}"
    full_email = f"Betreff: {subject}\n\n{body}"

    print("\n" + "=" * 60)
    print("📊 TRULENS-STYLE EVALUATION (via Ollama LLM-as-Judge)")
    print("=" * 60)
    print("⏳ Bewertung laeuft... (3 lokale LLM-Calls, ca. 30-60 Sek.)\n")

    try:
        print("  [1/3] Relevanz wird bewertet...")
        relevance = evaluator.evaluate_relevance(customer_data, full_email)

        print("  [2/3] Kohaerenz wird bewertet...")
        coherence = evaluator.evaluate_coherence(full_email)

        print("  [3/3] Ueberzeugungskraft wird bewertet...")
        persuasiveness = evaluator.evaluate_persuasiveness(full_email)

        avg_score = (relevance + coherence + persuasiveness) / 3

        print("\n" + "-" * 60)
        print(f"  📌 Relevanz (Kundenbezug):      {relevance:.2f} / 1.00")
        print(f"  📌 Kohaerenz (Sprachqualitaet):  {coherence:.2f} / 1.00")
        print(f"  📌 Ueberzeugungskraft:           {persuasiveness:.2f} / 1.00")
        print("-" * 60)
        print(f"  🏆 GESAMTSCORE:                  {avg_score:.2f} / 1.00")

        if avg_score >= 0.7:
            print("  ✅ QUALITAET BESTANDEN - E-Mail bereit zum Versand!")
        else:
            print("  ⚠️ WARNUNG - Niedriger Score! Manuelle Pruefung empfohlen.")

        print("=" * 60)

        return {
            "relevance": relevance,
            "coherence": coherence,
            "persuasiveness": persuasiveness,
            "overall": avg_score,
            "status": "success"
        }

    except Exception as e:
        print(f"\n  ❌ Evaluations-Fehler: {e}")
        return {"status": "error", "error": str(e)}
