import os
from crewai import Agent, Task, Crew, Process, LLM
from src.tools.supabase_tool import fetch_inactive_customers
from src.tools.email_tool import send_email_tool
from dotenv import load_dotenv

load_dotenv()

# CrewAI 1.x nativer LLM Wrapper fuer Ollama (Kein LangChain mehr noetig!)
local_llm = LLM(model="ollama/llama3.2", base_url="http://localhost:11434")

data_agent = Agent(
    role="E-Commerce Data Analyst",
    goal="Identifiziere inaktive Kunden und analysiere ihre Praeferenzen.",
    backstory="Du bist ein Experte im Querying von Datenbanken und verstehst Kundenverhalten.",
    tools=[fetch_inactive_customers],
    llm=local_llm,
    verbose=True
)

copywriter_agent = Agent(
    role="E-Commerce Copywriter",
    goal="Schreibe eine personalisierte E-Mail. VERBOTEN: Verwende KEINE Platzhalter wie [Name], [Produkt] oder [Rabatt]. Nutze AUSSCHLIESSLICH die echten Daten des Kunden (Name, Kategorie, Datum).",
    backstory="Du bist ein preisgekrönter Copywriter. Du hasst generische Templates. Du schreibst immer 100% personalisierte Texte mit den echten Daten, die dir gegeben wurden.",
    llm=local_llm,
    verbose=True
)

qa_agent = Agent(
    role="Quality Assurance Reviewer",
    goal="Stelle sicher, dass die E-Mail professionell, fehlerfrei und persuasiv ist.",
    backstory="Du bist ein strenger QA-Manager. Du akzeptierst nur perfekte Texte und verbesserst sie.",
    llm=local_llm,
    verbose=True
)

sender_agent = Agent(
    role="Email Dispatcher",
    goal="Sende die finale, freigegebene E-Mail sicher an den Kunden.",
    backstory="Du bist der technische Operator, der den Versand ueber SMTP zuverlaessig sicherstellt.",
    tools=[send_email_tool],
    llm=local_llm,
    verbose=True
)

def create_crew():
    task1 = Task(
        description="Hole die Liste der inaktiven Kunden. Waehle den ersten Kunden aus der Liste fuer die weitere Bearbeitung.",
        agent=data_agent,
        expected_output="JSON-aehnliche Darstellung des ausgewaehlten Kunden mit Name, E-Mail und letztem Kauf."
    )
    
    task2 = Task(
        description="Schreibe eine personalisierte Re-Engagement E-Mail an diesen spezifischen Kunden.",
        agent=copywriter_agent,
        expected_output="Der komplette E-Mail-Entwurf mit Betreff und Textkoerper."
    )
    
    task3 = Task(
        description="Reviewe und optimiere den E-Mail-Entwurf. Mache ihn ueberzeugender und fehlerfrei.",
        agent=qa_agent,
        expected_output="Der final freigegebene E-Mail-Text."
    )
    
    task4 = Task(
        description="Sende die finale E-Mail an die E-Mail-Adresse des Kunden.",
        agent=sender_agent,
        expected_output="Bestaetigung des erfolgreichen Versands oder eine detaillierte Fehlermeldung."
    )

    return Crew(
        agents=[data_agent, copywriter_agent, qa_agent, sender_agent],
        tasks=[task1, task2, task3, task4],
        process=Process.sequential,
        verbose=True
    )
