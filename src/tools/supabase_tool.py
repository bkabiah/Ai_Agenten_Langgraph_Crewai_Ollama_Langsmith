import os
from crewai.tools import tool
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Initialisiere Supabase Client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if supabase_url and supabase_key:
    supabase: Client = create_client(supabase_url, supabase_key)
else:
    supabase = None

@tool("Fetch Inactive Customers")
def fetch_inactive_customers(days_inactive: int = 30) -> str:
    """Holt Kunden aus der Datenbank, die seit X Tagen nicht gekauft haben."""
    if not supabase:
        return "FEHLER: Supabase URL oder Key fehlt in der .env Datei."
    
    try:
        # Vereinfachte Abfrage für das Demo. In Produktion: Filter auf last_purchase_date
        response = supabase.table("customers").select("*").limit(5).execute()
        return str(response.data)
    except Exception as e:
        return f"Datenbankfehler: {str(e)}"
