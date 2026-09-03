from typing import TypedDict, List, Any, Optional
from langgraph.graph import StateGraph, END
from src.agents.crew import create_crew

class AgentState(TypedDict):
    messages: List[str]
    current_step: str
    final_email_sent: bool
    error: Optional[str]

def run_crew_node(state: AgentState):
    """Führt die CrewAI Agenten sequenziell aus und fängt Fehler ab."""
    print("🚀 Starte CrewAI Ausführung...")
    try:
        crew = create_crew()
        result = crew.kickoff()
        
        # Ergebnis extrahieren (CrewAI gibt ein CrewOutput Objekt zurück)
        result_text = str(result)
        
        return {
            "messages": state["messages"] + [result_text],
            "current_step": "crew_finished",
            "final_email_sent": True,
            "error": None
        }
    except Exception as e:
        return {
            "messages": state["messages"] + [f"Fehler: {str(e)}"],
            "current_step": "error",
            "final_email_sent": False,
            "error": str(e)
        }

def build_graph():
    """Baut und kompiliert den LangGraph Workflow."""
    workflow = StateGraph(AgentState)
    
    # Node hinzufügen
    workflow.add_node("execute_crew", run_crew_node)
    
    # Entry Point und Edges definieren
    workflow.set_entry_point("execute_crew")
    workflow.add_edge("execute_crew", END)
    
    return workflow.compile()
