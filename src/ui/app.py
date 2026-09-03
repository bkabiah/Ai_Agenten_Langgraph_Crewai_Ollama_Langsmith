import sys
import os

# Füge das Projekt-Root-Verzeichnis absolut sicher zum Python-Pfad hinzu
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
from src.graph.langgraph_orchestrator import build_graph

st.set_page_config(page_title="E-Commerce AI Agents", layout="wide", page_icon="🛒")

st.title("🛒 E-Commerce Re-Engagement AI System")
st.markdown("**Tech Stack:** Orchestriert mit **LangGraph**, ausgeführt von **CrewAI**, Datenbank via **Supabase**, 100% lokal via **Ollama**.")
st.divider()

if st.button("🚀 KI-Kampagne starten", type="primary", use_container_width=True):
    with st.spinner("Agenten arbeiten... (kann 30-60 Sek. dauern)"):
        try:
            graph = build_graph()
            initial_state = {
                "messages": [], 
                "current_step": "start", 
                "final_email_sent": False,
                "error": None
            }
            
            final_state = graph.invoke(initial_state)
            
            if final_state.get("final_email_sent"):
                st.success("✅ Kampagne erfolgreich abgeschlossen!")
            else:
                st.error("❌ Fehler bei der Ausführung aufgetreten.")
                
            st.subheader("📜 Agenten Log & Output:")
            messages = final_state.get("messages", [])
            for i, msg in enumerate(messages):
                with st.expander(f"Schritt {i+1} Output", expanded=(i == len(messages)-1)):
                    st.text(msg)
                    
            st.info("💡 Dieses System läuft 100% lokal auf deinem VPS mit Ollama – keine API-Kosten!")
            
        except Exception as e:
            st.error(f"Kritischer Fehler: {str(e)}")
            st.exception(e)
