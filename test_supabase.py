from modules.supabase_client import supabase

try:
    result = supabase.table("profiles").select("*").limit(1).execute()
    print("✅ Connected to Supabase!")
except Exception as e:
    print("❌ Connection failed")
    print(e)