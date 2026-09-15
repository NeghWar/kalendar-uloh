import streamlit as st
from datetime import date
from supabase import create_client, Client

# --- NASTAVENIE PRIPOJENIA NA SUPABASE ---
# SEM VLOŽTE SVOJE ÚDAJE ZO SUPABASE (Project Settings -> API)
SUPABASE_URL = "https://fdfsifvklwsdgeskgadc.supabase.co"
SUPABASE_KEY = "sb_publishable_rJ815qf4quLjznGgEPT7Tw_UeP3lITQ"

# Inicializácia Supabase klienta
@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# Nastavenie vzhľadu stránky
st.set_page_config(page_title="Môj Cloud Kalendár", page_icon="📅", layout="centered")
st.title("📅 Môj Cloud Kalendár Úloh")

# --- FORMULÁR NA PRIDANIE ÚLOHY ---
st.subheader("Pridať novú úlohu")
with st.form(key="nova_uloha_form", clear_on_submit=True):
    nazov_ulohy = st.text_input("Názov úlohy:", placeholder="Napr. Kúpiť mlieko...")
    datum_splnenia = st.date_input("Termín splnenia:", date.today())
    
    tlacidlo_pridat = st.form_submit_button(label="Pridať úlohu")

if tlacidlo_pridat and nazov_ulohy:
    # Odoslanie údajov do online databázy Supabase
    data = {
        "nazov": nazov_ulohy,
        "datum": datum_splnenia.isoformat()  # Prevod dátumu na text, ktorý SQL pozná
    }
    try:
        supabase.table("ulohy").insert(data).execute()
        st.success(f"Úloha '{nazov_ulohy}' bola uložená do cloudu! 🚀")
    except Exception as e:
        st.error(f"Chyba pri ukladaní: {e}")

# --- NAČÍTANIE A ZOBRAZENIE ÚLOH Z DATABÁZY ---
st.subheader("Moje aktuálne úlohy z cloudu")

try:
    # Vytiahneme úlohy z databázy a zoradíme ich podľa dátumu splnenia
    odpoved = supabase.table("ulohy").select("*").order("datum", desc=False).execute()
    zoznam_uloh = odpoved.data

    if not zoznam_uloh:
        st.info("Nemáš žiadne cloudové úlohy. Uži si voľný čas! 🎉")
    else:
        for uloha in zoznam_uloh:
            # Oprava formátu dátumu pre pekné zobrazenie (RRRR-MM-DD -> DD.MM.RRRR)
            r, m, d = uloha['datum'].split('-')
            pekny_datum = f"{d}.{m}.{r}"
            
            # Zobrazenie úlohy v boxe
            st.info(f"**{uloha['nazov']}** \n\n 📅 Termín: {pekny_datum}")

except Exception as e:
    st.error(f"Nepodarilo sa načítať úlohy: {e}")
