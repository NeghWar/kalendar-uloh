import streamlit as st
from datetime import date, timedelta
from supabase import create_client, Client

# --- AUTOMATICKÉ NAČÍTANIE ZO SECRETS ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
MOJE_TAJNE_HESLO = st.secrets["MOJE_TAJNE_HESLO"]

@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

st.set_page_config(page_title="Revízny Systém Strojov", page_icon="⚙️", layout="wide")

# ==========================================
# 🔒 BEZPEČNOSTNÝ ZÁMOK
# ==========================================
if "overeny" not in st.session_state:
    st.session_state.overeny = False

if not st.session_state.overeny:
    st.title("🔒 Chránený revízny systém")
    st.subheader("Vstup len pre oprávnené osoby")
    
    zadane_heslo = st.text_input("Zadajte prístupové heslo:", type="password")
    tlacidlo_prihlasit = st.button("Prihlásiť sa")
    
    if tlacidlo_prihlasit:
        if zadane_heslo == MOJE_TAJNE_HESLO:
            st.session_state.overeny = True
            st.rerun()
        else:
            st.error("Nesprávne heslo! Prístup odmietnutý.")
            
    st.stop()

# ... ZVYŠOK KÓDU (ZÁLOŽKY, FORMULÁRE) OSTÁVA ÚPLNE ROVNAKÝ ...


if "overeny" not in st.session_state:
    st.session_state.overeny = False

if not st.session_state.overeny:
    st.title("🔒 Chránený revízny systém")
    st.subheader("Vstup len pre oprávnené osoby")
    
    zadane_heslo = st.text_input("Zadajte prístupové heslo:", type="password")
    tlacidlo_prihlasit = st.button("Prihlásiť sa")
    
    if tlacidlo_prihlasit:
        if zadane_heslo == MOJE_TAJNE_HESLO:
            st.session_state.overeny = True
            st.rerun()
        else:
            st.error("Nesprávne heslo! Prístup odmietnutý.")
            
    # Zastavíme vykonávanie zvyšku kódu, kým nie je používateľ overený
    st.stop()

# ==========================================
# HLAVNÝ PROGRAM (Spustí sa len po správnom hesle)
# ==========================================
st.title("⚙️ Profesionálny Systém Revízií a Prehliadok")

# --- POMOCNÁ FUNKCIA NA VÝPOČET TERMÍNU ---
def vypocitaj_nasledujuci(posledny_datum, roky):
    if posledny_datum is None:
        return None
    dni = (roky * 365) - 1
    return posledny_datum + timedelta(days=dni)

# Tlačidlo na odhlásenie v hornom rohu
if st.sidebar.button("🔒 Odhlásiť sa"):
    st.session_state.overeny = False
    st.rerun()

# --- ROZDELENIE STRÁNKY NA ZÁLOŽKY ---
tab_prehlad, tab_kalendar, tab_pridat = st.tabs([
    "🔔 Prehľad a Upozornenia", 
    "📅 Mesačný Kalendár", 
    "➕ Pridať / Evidovať Stroj"
])

# ==========================================
# ZÁLOŽKA 3: PRIDANIE / EVIDENCIA STROJA
# ==========================================
with tab_pridat:
    st.header("Evidencia nového stroja do systému")
    
    with st.form(key="novy_stroj_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nazov = st.text_input("Názov stroja / zariadenia:", placeholder="Napr. Mostový žeriav 5t")
        with col2:
            umiestnenie = st.text_input("Umiestnenie (Hala / Stanovište):", placeholder="Napr. Hala A - expedícia")
            
        st.markdown("---")
        st.subheader("Zadajte dátumy posledných vykonaných kontrol:")
        
        c1, c2 = st.columns(2)
        with c1:
            p_revizia = st.date_input("Posledná Revízia (opakuje sa ročne):", None)
            
            p_revizna_sk = st.date_input("Posledná Revízna skúška:", None)
            perioda_reviznej = st.selectbox("Perióda Revíznej skúšky (roky):", [2, 3])
            
            p_podrobna_ok = st.date_input("Posledná Podrobná prehliadka OK (opakuje sa 5-ročne):", None)
        
        with c2:
            p_uradna = st.date_input("Posledná Úradná skúška:", None)
            perioda_uradnej = st.selectbox("Perióda Úradnej skúšky (roky):", [5, 6, 10])
            
            p_odborna_pr = st.date_input("Posledná Odborná prehliadka (opakuje sa ročne):", None)
            p_odborna_sk = st.date_input("Posledná Odborná skúška (opakuje sa ročne):", None)
            
        st.markdown("---")
        ma_geometriu = st.checkbox("Vykonáva sa na tomto stroji Geometrické zameranie žeriavovej dráhy? (10 rokov)")
        p_geometria = None
        if ma_geometriu:
            p_geometria = st.date_input("Posledné Geometrické zameranie dráhy:", None)
            
        tlacidlo_ulozit = st.form_submit_button("Uložiť stroj a vypočítať revízie")

    if tlacidlo_ulozit and nazov:
        n_revizia = vypocitaj_nasledujuci(p_revizia, 1)
        n_revizna_sk = vypocitaj_nasledujuci(p_revizna_sk, perioda_reviznej)
        n_podrobna_ok = vypocitaj_nasledujuci(p_podrobna_ok, 5)
        n_uradna = vypocitaj_nasledujuci(p_uradna, perioda_uradnej)
        n_odborna_pr = vypocitaj_nasledujuci(p_odborna_pr, 1)
        n_odborna_sk = vypocitaj_nasledujuci(p_odborna_sk, 1)
        n_geometria = vypocitaj_nasledujuci(p_geometria, 10) if ma_geometriu else None

        novy_stroj_data = {
            "nazov": nazov, "umiestnenie": umiestnenie,
            "posledna_revizia": p_revizia.isoformat() if p_revizia else None,
            "nasledujuca_revizia": n_revizia.isoformat() if n_revizia else None,
            "posledna_revizna_skuska": p_revizna_sk.isoformat() if p_revizna_sk else None,
            "perioda_reviznej_skusky": perioda_reviznej,
            "nasledujuca_revizna_skuska": n_revizna_sk.isoformat() if n_revizna_sk else None,
            "posledna_podrobna_prehliadka_ok": p_podrobna_ok.isoformat() if p_podrobna_ok else None,
            "nasledujuca_podrobna_prehliadka_ok": n_podrobna_ok.isoformat() if n_podrobna_ok else None,
            "posledna_uradna_skuska": p_uradna.isoformat() if p_uradna else None,
            "perioda_uradnej_skusky": perioda_uradnej,
            "nasledujuca_uradna_skuska": n_uradna.isoformat() if n_uradna else None,
            "posledna_odborna_prehliadka": p_odborna_pr.isoformat() if p_odborna_pr else None,
            "nasledujuca_odborna_prehliadka": n_odborna_pr.isoformat() if n_odborna_pr else None,
            "posledna_odborna_skuska": p_odborna_sk.isoformat() if p_odborna_sk else None,
            "nasledujuca_odborna_skuska": n_odborna_sk.isoformat() if n_odborna_sk else None,
            "vykonava_sa_geometria": ma_geometriu,
            "posledna_geometria": p_geometria.isoformat() if p_geometria else None,
            "nasledujuca_geometria": n_geometria.isoformat() if n_geometria else None,
        }
        
        try:
            supabase.table("stroje").insert(novy_stroj_data).execute()
            st.success(f"Stroj '{nazov}' bol úspešne zaevidovaný!")
            st.rerun()
        except Exception as e:
            st.error(f"Chyba pri ukladaní stroja: {e}")

# ==========================================
# NAČÍTANIE DÁT PRE PREHĽAD A KALENDÁR
# ==========================================
try:
    odpoved = supabase.table("stroje").select("*").execute()
    vsetky_stroje = odpoved.data
except Exception as e:
    st.error(f"Chyba pri načítaní dát: {e}")
    vsetky_stroje = []

# ==========================================
# ZÁLOŽKA 1: PREHĽAD A UPOZORNENIA
# ==========================================
with tab_prehlad:
    st.header("🔔 Blížiace sa termíny revízií (Nasledujúcich 30 dní)")
    
    dnes = date.today()
    hranica_upozornenia = dnes + timedelta(days=30)
    naslo_sa_upozornenie = False
    
    definicia_kontrol = {
        "nasledujuca_revizia": "Revízia",
        "nasledujuca_revizna_skuska": "Revízna skúška",
        "nasledujuca_podrobna_prehliadka_ok": "Podrobná prehliadka OK",
        "nasledujuca_uradna_skuska": "Úradná skúška",
        "nasledujuca_odborna_prehliadka": "Odborná prehliadka",
        "nasledujuca_odborna_skuska": "Odborná skúška",
        "nasledujuca_geometria": "Geometrické zameranie dráhy"
    }

    for stroj in vsetky_stroje:
        for stlpec, nazov_kontroly in definicia_kontrol.items():
            if stroj[stlpec]:
                termin = date.fromisoformat(stroj[stlpec])
                if dnes <= termin <= hranica_upozornenia:
                    naslo_sa_upozornenie = True
                    dni_do = (termin - dnes).days
                    st.warning(f"⚠️ **{stroj['nazov']}** ({stroj['umiestnenie']}) -> **{nazov_kontroly}** vyprší dňa **{termin.strftime('%d.%m.%Y')}** (o {dni_do} dní!)")
                elif termin < dnes:
                    naslo_sa_upozornenie = True
                    st.error(f"🚨 **{stroj['nazov']}** ({stroj['umiestnenie']}) -> **{nazov_kontroly}** je **PO TERMÍNE** od {termin.strftime('%d.%m.%Y')}!")

    if not naslo_sa_upozornenie:
        st.success("V najbližších 30 dňoch vás nečakajú žiadne naliehavé revízie. Všetko je v poriadku! ✅")

# ==========================================
# ZÁLOŽKA 2: MESAČNÝ KALENDÁR
# ==========================================
with tab_kalendar:
    st.header("📅 Prehľad podľa mesiacov")
    
    c_rok, c_mes = st.columns(2)
    with c_rok:
        izvoleny_rok = st.selectbox("Rok:", [2026, 2027, 2028, 2029, 2030], index=0)
    with c_mes:
        mesiace_sk = ["Január", "Február", "Marec", "Apríl", "Máj", "Jún", "Júl", "August", "September", "Október", "November", "December"]
        izvoleny_mesiac_nazov = st.selectbox("Mesiac:", mesiace_sk, index=date.today().month - 1)
        izvoleny_mesiac_num = mesiace_sk.index(izvoleny_mesiac_nazov) + 1

    st.subheader(f"Plán revízií na: {izvoleny_mesiac_nazov} {izvoleny_rok}")
    nasli_sa_v_mesiaci = False
    
    for stroj in vsetky_stroje:
        for stlpec, nazov_kontroly in definicia_kontrol.items():
            if stroj[stlpec]:
                termin = date.fromisoformat(stroj[stlpec])
                if termin.year == izvoleny_rok and termin.month == izvoleny_mesiac_num:
                    nasli_sa_v_mesiaci = True
                    st.info(f"📅 **{termin.strftime('%d.%m.%Y')}** - **{stroj['nazov']}** ({stroj['umiestnenie']}) -> Vykonať: *{nazov_kontroly}*")
                    
    if not nasli_sa_v_mesiaci:
        st.text("Pre tento mesiac nie sú naplánované žiadne revízie.")
