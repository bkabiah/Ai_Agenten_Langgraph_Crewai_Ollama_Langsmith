import sys
import os
import re
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.graph.langgraph_orchestrator import build_graph
from src.tools.email_tool import send_email_tool
from src.evaluation import evaluate_email

def main():
    print("=" * 60)
    print("🛒 E-Commerce AI Pipeline + LLM-as-Judge Evaluation")
    print("=" * 60)

    graph = build_graph()
    initial_state = {
        "messages": [],
        "current_step": "start",
        "final_email_sent": False,
        "error": None
    }

    print("⏳ Phase 1: KI-Agenten generieren E-Mail...")
    result = graph.invoke(initial_state)

    full_history = "\n".join(str(msg) for msg in result["messages"])

    recipient = None
    subject = "Wichtige Nachricht"
    raw_body = ""
    customer_name = "Kunde"

    # SENIOR FIX: Exaktes JSON extrahieren und sicher parsen
    # Wir suchen nach dem JSON-Block, der mit { beginnt und bei } endet
    json_match = re.search(r'\{\s*"name"\s*:\s*"send_email_to_customer".*?\}', full_history, re.DOTALL)
    
    if json_match:
        try:
            # json.loads verarbeitet \u00FC automatisch korrekt zu 'ü'!
            data = json.loads(json_match.group(0))
            params = data.get("parameters", {})
            recipient = params.get("recipient_email")
            subject = params.get("subject", "Wichtige Nachricht")
            raw_body = params.get("body", "")
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON Parsing Fehler: {e}")

    # Fallback: Name aus früherem Schritt holen, falls im JSON nicht vorhanden
    name_match = re.search(r'"name":\s*"([^"]+)"', full_history)
    if name_match and name_match.group(1) not in ["send_email_to_customer", "fetch_inactive_customers"]:
        customer_name = name_match.group(1)

    # Validierung
    if recipient and raw_body and len(raw_body.strip()) > 50:
        print(f"\n📧 E-Mail generiert fuer: {recipient} ({customer_name})")
        print(f"📌 Betreff: {subject}")
        print("-" * 60)
        # Nur Vorschau anzeigen, um Terminal nicht zu fluten
        preview = raw_body[:300].replace('\\n', '\n') 
        print(preview + "..." if len(raw_body) > 300 else preview)
        print("-" * 60)

        # Phase 2: Evaluation
        print("\n⏳ Phase 2: Bewertung der Qualität (dauert ca. 20 Sek.)...")
        try:
            eval_result = evaluate_email(subject, raw_body, customer_name, "Elektronik")
            
            # Phase 3: Versand (Schwellenwert 0.3, da lokales LLM streng ist)
            if eval_result["status"] == "success" and eval_result["overall"] >= 0.3:
                print("\n🚀 Phase 3: E-Mail wird versendet...")
                send_result = send_email_tool(recipient, subject, raw_body)
                print(f"📬 {send_result}")
            else:
                print("\n⛔ Versand blockiert aufgrund niedriger Qualität (LLM-as-Judge).")
                print(f"Score: {eval_result.get('overall', 'N/A')}")
        except Exception as e:
            print(f"\n❌ Fehler bei der Evaluation: {e}")
    else:
        print("\n⚠️ Konnte E-Mail-Daten nicht extrahieren oder Inhalt zu kurz.")
        print(f"DEBUG: recipient={recipient}, body_len={len(raw_body) if raw_body else 0}")

if __name__ == "__main__":
    main()
