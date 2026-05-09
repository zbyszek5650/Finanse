import streamlit as st
import pandas as pd
import datetime
import time

# --- CONFIGURATION ---
st.set_page_config(
    page_title="CyberBank - Enterprise Crisis Control",
    layout="wide",
    page_icon="🏦",
    initial_sidebar_state="collapsed"
)

# --- CSS (Wersja Oryginalna + Dodatki) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    :root {
        --bg-color: #0f172a; --panel-bg: #1e293b; --border-color: #334155;
        --text-primary: #f8fafc; --text-secondary: #94a3b8;
        --accent-cyan: #06b6d4; --accent-red: #ef4444;
        --accent-green: #22c55e; --accent-yellow: #f59e0b;
        --font-sans: 'Inter', sans-serif; --font-mono: 'JetBrains Mono', monospace;
    }
    .stApp { background-color: var(--bg-color) !important; color: var(--text-primary); font-family: var(--font-sans); }
    #MainMenu, footer, header { visibility: hidden; }
    .command-header {
        height: 64px; background: rgba(15, 23, 42, 0.8); border-bottom: 1px solid var(--border-color);
        padding: 0 24px; display: flex; justify-content: space-between; align-items: center;
        margin-top: -75px; margin-bottom: 24px; position: sticky; top: 0; z-index: 1000;
    }
    .brand-title { font-family: var(--font-mono); font-weight: 700; font-size: 1.2rem; color: var(--accent-cyan); text-transform: uppercase; }
    .panel { background: var(--panel-bg); border: 1px solid var(--border-color); border-radius: 6px; padding: 16px; height: 100%; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .panel-label { font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; margin-bottom: 12px; display: block; }
    .kpi-header { display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 6px; }
    .progress-bar-bg { background: var(--bg-color); height: 4px; border-radius: 2px; overflow: hidden; }
    .progress-bar-fill { height: 100%; transition: width 1s; background: var(--accent-cyan); }
    .scenario-header { background: linear-gradient(135deg, var(--panel-bg) 0%, var(--bg-color) 100%); border-left: 4px solid var(--accent-cyan); padding: 20px; margin-bottom: 20px; }
    .danger-zone { border: 1px solid var(--accent-red); padding: 15px; border-radius: 6px; margin-top: 20px; background: rgba(239, 68, 68, 0.05); }
    </style>
""", unsafe_allow_html=True)

# --- SCENARIOS SETUP ---
FIN_SCENARIOS = [
    {"name": "I: Atak Ransomware", "rounds": 5},
    {"name": "II: Insider Threat", "rounds": 5},
    {"name": "III: Supply Chain Sabotage", "rounds": 5},
    {"name": "IV: Phishing Masowy", "rounds": 5},
    {"name": "V: Atak na SWIFT", "rounds": 5},
    {"name": "VI: Deepfake & Social Engineering", "rounds": 5}
]

# --- NARRATIVE DESCRIPTIONS FOR EVERY ROUND ---
SCENARIO_DESCRIPTIONS = {
    0: { # I: Atak Ransomware
        1: "Wykryto nietypowe, drastyczne obciążenie procesorów na stacjach roboczych w dziale obsługi klienta. Pojawiają się pierwsze zgłoszenia o samoczynnym zmianie rozszerzeń plików. Rozpoczyna się proces szyfrowania.",
        2: "Ekrany pracowników banku zostają zablokowane czerwoną planszą. Wyświetla się komunikat z żądaniem okupu w wysokości 15 milionów dolarów w kryptowalutach w zamian za klucz deszyfrujący.",
        3: "Złośliwe oprogramowanie (robak) usiłuje przenieść się ze stacji roboczych na główne serwery bazodanowe oraz magazyny kopii zapasowych (backup storage). Wśród personelu wybucha panika.",
        4: "Przez opóźnienia w systemach, klienci nie mogą wykonywać przelewów ani wypłacać gotówki z bankomatów sieci. Media społecznościowe zalewa fala spekulacji. Atakujący grożą upublicznieniem danych na Dark Webie.",
        5: "Krytyczny moment. Okno negocjacyjne dobiega końca. Bank musi podjąć decyzję o strategii odbudowy z izolowanych taśm (cold backup) i długotrwałym przestoju, lub innym sposobie rozwiązania kryzysu."
    },
    1: { # II: Insider Threat
        1: "Systemy DLP (Data Loss Prevention) odnotowują masowe pobieranie danych analitycznych i portfeli klientów VIP na zewnętrzny, nieszyfrowany nośnik USB w godzinach nocnych.",
        2: "Śledztwo wewnętrzne wykazuje, że logowania pochodzą z konta zwolnionego w ubiegłym tygodniu architekta baz danych. Nikt z IT nie zablokował jego wirtualnego profilu VPN.",
        3: "Były pracownik kontaktuje się z zarządem anonimowym kanałem. Szantażuje bank, że przekaże bazę klientów do konkurencyjnej instytucji finansowej lub na czarny rynek, jeśli nie otrzyma gigantycznej odprawy.",
        4: "Dziennikarz śledczy z dużego portalu kontaktuje się z rzecznikiem banku prosząc o komentarz. Twierdzi, że otrzymał „próbkę” plików bankowych wykazujących nieprawidłowości inwestycyjne zarządu.",
        5: "Sytuacja eskaluje prawnie. Prokuratura oraz Urząd Ochrony Danych Osobowych żądają wydania nośników serwerowych jako dowodów w sprawie, co grozi zawieszeniem usług operacyjnych banku."
    },
    2: { # III: Supply Chain Sabotage
        1: "Popularny dostawca oprogramowania finansowego (Zewnętrzny Vendor) wdraża rutynową, zautomatyzowaną aktualizację systemów księgowych w Waszym banku. SOC wykrywa nietypowe zapytania wychodzące z serwera aplikacji.",
        2: "Okazuje się, że infrastruktura dostawcy została przejęta przez zaawansowaną grupę APT. Przez zaufany kanał do banku wpuszczono złośliwego backdoora, który mapuje wewnętrzną sieć.",
        3: "Hakerzy, wykorzystując lukę, uzyskują uprawnienia do manipulacji rejestrem księgi głównej. Klienci korporacyjni zgłaszają, że salda na ich kontach nie zgadzają się z rzeczywistością.",
        4: "Vendor oficjalnie ogłasza, że jego środowisko jest całkowicie skompromitowane i traci kontrolę. Bank traci kluczowe oprogramowanie analityczne i musi zarządzać awarią we własnym zakresie.",
        5: "Czas na inwentaryzację szkód. Audytorzy zewnętrzni sprawdzają, czy zainfekowany kod nie dokonał ukrytych przesunięć środków na konta zagraniczne. Należy zbudować plan migracji na nową infrastrukturę."
    },
    3: { # IV: Phishing Masowy
        1: "Pół tysiąca pracowników banku otrzymuje spersonalizowane maile przypominające wewnętrzne powiadomienia HR z linkiem do „Tabeli podwyżek inflacyjnych”. Znaczny procent personelu klika w link.",
        2: "Złośliwa witryna przechwytuje dziesiątki loginów i haseł pracowników. W ciągu kilkunastu minut intruzi zaczynają logować się do wewnętrznego systemu intranetu banku.",
        3: "Atakujący, używając skradzionych kont pracowników szczebla operacyjnego, próbują autoryzować masowe, drobnokwotowe przelewy, które uchodzą uwadze algorytmów zabezpieczających.",
        4: "Z przejętych skrzynek e-mailowych wysyłane są sfałszowane dyspozycje do kluczowych klientów biznesowych banku (tzw. Business Email Compromise) z prośbą o zmianę numeru rachunku do rozliczeń bieżących.",
        5: "Do banku napływają roszczenia od oburzonych klientów, którzy wykonali przelewy na konta oszustów i żądają zwrotu skradzionych środków z powodu luk w bezpieczeństwie banku."
    },
    4: { # V: Atak na SWIFT
        1: "Monitor operacji zagranicznych alarmuje: w ciągu ostatniej godziny autoryzowano trzy wielomilionowe transfery środków przez system SWIFT do banków w egzotycznych rajach podatkowych, pomimo braku takich dyspozycji zlecających.",
        2: "Złośliwy kod wewnątrz stacji obsługującej SWIFT nadpisuje logi w bazie danych Oracle, zacierając ślady wyprowadzania gotówki. Raporty dla dyrekcji generują sztuczne, fałszywie dodatnie salda.",
        3: "Atak trwa, a środki w obcych walutach wyciekają z rezerw bankowych. Wykryto złośliwe procesy w pamięci operacyjnej, operacja jest sterowana z adresów IP w Azji Południowo-Wschodniej.",
        4: "Krajowy regulator nadzoru finansowego zauważa potężną utratę rezerw walutowych Waszego banku. Do sztabu kryzysowego dołączają agenci międzynarodowych organów ścigania.",
        5: "Operacje zagraniczne banku zostają formalnie zamrożone na globalnym rynku. Trwa weryfikacja logów przez niezależnych analityków oraz gorączkowe próby cofnięcia zagranicznych przelewów."
    },
    5: { # VI: Deepfake & Social Engineering
        1: "Dyrektor Finansowy (CFO) odbiera pilny, bezpośredni telefon. Osoba brzmiąca identycznie jak Prezes Zarządu zleca natychmiastowy, poufny przelew na 30 mln euro w związku ze strategicznym i tajnym przejęciem spółki za granicą.",
        2: "Przelew zostaje wykonany z ominięciem standardowych procedur („na prośbę prezesa”). Kilka godzin później prawdziwy Prezes informuje, że nie dzwonił – wykorzystano zaawansowaną technologię klonowania głosu (Audio Deepfake).",
        3: "To dopiero początek. W serwisie YouTube i Twitter pojawia się wygenerowane przez AI wideo, na którym „Prezes banku” informuje, że bank jest niewypłacalny. Film zyskuje tysiące udostępnień w godzinę.",
        4: "Rozpoczyna się klasyczny „Bank Run”. Spanikowani deponenci ustawiają się w gigantycznych kolejkach przed oddziałami banku, a serwery bankowości internetowej padają pod lawiną logowań i prób zerwania lokat.",
        5: "Panika zagraża utrzymaniu płynności całego banku. Rząd oraz fundusze gwarancyjne bacznie obserwują, jak Sztab poradzi sobie z dementowaniem kłamstw, ustabilizowaniem histerii rynku i odzyskaniem utraconych milionów."
    }
}

def get_round_data(s_idx, r_num):
    # Pobieranie opisu dla danego scenariusza i rundy (lub opisu zapasowego)
    scen_description = SCENARIO_DESCRIPTIONS.get(s_idx, {}).get(r_num, f"Sytuacja w scenariuszu {FIN_SCENARIOS[s_idx]['name']} rozwija się dynamicznie.")
    
    # Stabilna struktura danych dla rund
    return {
        "title": f"FAZA {r_num}: KRYZYS W TOKU",
        "desc": scen_description,
        "questions": {
            "IT": {
                "label": "CYBER-SECURITY", 
                "correct_option": "Zewnętrzny audyt śledczy i izolacja DC",
                "options": {
                    "Zewnętrzny audyt śledczy i izolacja DC": {"trust": +5, "liq": -10, "cap": -10, "comp": +25},
                    "Pełna izolacja systemów (Blackout)": {"trust": 0, "liq": -40, "cap": 0, "comp": +10},
                    "Próba neutralizacji bez wyłączania": {"trust": -10, "liq": 0, "cap": 0, "comp": -10},
                    "Ignorowanie (fałszywy alarm)": {"trust": -30, "liq": 0, "cap": 0, "comp": -50}
                }
            },
            "Ops": {
                "label": "OPERACJE / RYZYKO", 
                "correct_option": "Weryfikacja manualna transakcji krytycznych",
                "options": {
                    "Weryfikacja manualna transakcji krytycznych": {"trust": +15, "liq": -25, "cap": 0, "comp": +10},
                    "Blokada wypłat powyżej limitu": {"trust": -30, "liq": +20, "cap": 0, "comp": 0},
                    "Uruchomienie rezerw płynności": {"trust": 0, "liq": +50, "cap": -30, "comp": 0},
                    "Brak ograniczeń operacyjnych": {"trust": +5, "liq": -20, "cap": 0, "comp": -15}
                }
            },
            "Dir": {
                "label": "ZARZĄD / PR", 
                "correct_option": "Zgłoszenie do organów nadzoru i komunikat PR",
                "options": {
                    "Zgłoszenie do organów nadzoru i komunikat PR": {"trust": +10, "liq": 0, "cap": 0, "comp": +40},
                    "Pełna transparentność medialna": {"trust": +25, "liq": 0, "cap": 0, "comp": +5},
                    "Utrzymanie ciszy informacyjnej": {"trust": -40, "liq": 0, "cap": 0, "comp": -25},
                    "Kampania dezinformacyjna": {"trust": -10, "liq": 0, "cap": 0, "comp": -60}
                }
            }
        }
    }

# --- ENGINE ---
@st.cache_resource
def get_engine():
    return {"scenario_idx": 0, "round": 0, "teams": {}, "status": "ACTIVE", "history_log": []}

state = get_engine()

def calculate_metrics(team_name):
    t, l, c, co = 100, 100, 100, 100
    team = state["teams"].get(team_name, {})
    for s_idx, scen_decs in team.get("decisions", {}).items():
        for r_num, roles in scen_decs.items():
            data = get_round_data(s_idx, r_num)
            for role, choice in roles.items():
                if choice in data["questions"][role]["options"]:
                    impact = data["questions"][role]["options"][choice]
                    t += impact.get("trust", 0); l += impact.get("liq", 0)
                    c += impact.get("cap", 0); co += impact.get("comp", 0)
    return [max(0, min(150, val)) for val in [t, l, c, co]]

# --- VIEWS ---

def login_view():
    st.markdown('<div class="command-header"><div class="brand-title">CyberBank // LOGIN</div></div>', unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        t_id = st.text_input("IDENTYFIKATOR ZESPOŁU:").upper()
        if st.button("AUTORYZUJ DOSTĘP", use_container_width=True):
            if t_id:
                if t_id not in state["teams"]:
                    state["teams"][t_id] = {"decisions": {}, "is_active": True, "ready": False, "last_scen": 0}
                st.session_state["team_name"] = t_id
                st.session_state["role"] = "team"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔐 ROOT CONTROL"):
            if st.text_input("ROOT KEY:", type="password") == "admin":
                if st.button("ZALOGUJ DO DOWÓDZTWA"):
                    st.session_state["role"] = "admin"
                    st.rerun()

def admin_view():
    st.markdown('<div class="command-header"><div class="brand-title">CyberBank // ROOT COMMAND CENTER</div></div>', unsafe_allow_html=True)
    
    # --- TOP CONTROL BAR ---
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.markdown(f"<div class='panel'>SCENARIUSZ: <b>{state['scenario_idx']+1} / 6</b></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='panel'>RUNDA: <b>{state['round']} / 5</b></div>", unsafe_allow_html=True)
    with c3:
        if st.button("🔄 SYNCHRONIZUJ STATUSY ZESPOŁÓW", use_container_width=True):
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- MAIN ADMIN TABS ---
    tab1, tab2, tab3 = st.tabs(["🎮 STEROWANIE RUNDĄ", "📊 MONITOR ZESPOŁÓW", "📜 PEŁNA HISTORIA ROZGRYWKI"])

    with tab1:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        if st.button("⏩ AKTYWUJ NASTĘPNY ETAP", use_container_width=True):
            if state["round"] < 5:
                state["round"] += 1
            else:
                for t in state["teams"]:
                    if state["teams"][t]["is_active"]:
                        m = calculate_metrics(t)
                        if any(v < 40 for v in m): state["teams"][t]["is_active"] = False
                        else: state["teams"][t]["last_scen"] = state["scenario_idx"] + 1
                
                if state["scenario_idx"] < 5:
                    state["scenario_idx"] += 1
                    state["round"] = 1
                else: state["status"] = "FINISHED"
            
            for t in state["teams"]: state["teams"][t]["ready"] = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        monitor_data = []
        for t, d in state["teams"].items():
            m = calculate_metrics(t)
            status_txt = "✅ GOTOWY" if d["ready"] else "⏳ MYŚLI"
            if not d["is_active"]: status_txt = "💀 ELIMINACJA"
            
            monitor_data.append({
                "ZESPÓŁ": t, "PUNKTY": sum(m), "STATUS": status_txt,
                "ZAUFANIE": m[0], "PŁYNNOŚĆ": m[1], "KAPITAŁ": m[2], "ZGODNOŚĆ": m[3]
            })
        if monitor_data:
            st.dataframe(pd.DataFrame(monitor_data).sort_values("PUNKTY", ascending=False), hide_index=True, use_container_width=True)
        else:
            st.info("Brak połączonych zespołów.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<span class='panel-label'>DANE ARCHIWALNE I BIEŻĄCE (Wszystkie Scenariusze)</span>", unsafe_allow_html=True)
        
        full_history = []
        # Przechodzimy przez wszystkie zespoły i wszystkie ich dotychczasowe decyzje
        for t_name, t_data in state["teams"].items():
            for s_idx, scen_decs in t_data.get("decisions", {}).items():
                for r_num, roles in scen_decs.items():
                    rd = get_round_data(s_idx, r_num)
                    for role, choice in roles.items():
                        is_correct = "✅" if choice == rd["questions"][role]["correct_option"] else "❌"
                        full_history.append({
                            "SCENARIUSZ": s_idx + 1,
                            "RUNDA": r_num,
                            "ZESPÓŁ": t_name,
                            "SEKCJA": rd["questions"][role]["label"],
                            "DECYZJA": choice,
                            "POPRAWNA": is_correct
                        })
        
        if full_history:
            df_hist = pd.DataFrame(full_history)
            st.dataframe(df_hist.sort_values(["SCENARIUSZ", "RUNDA"], ascending=[False, False]), use_container_width=True, hide_index=True)
        else:
            st.info("Historia jest pusta. Czekam na pierwsze decyzje.")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- DANGER ZONE ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.expander("⚠️ STREFA ZAGROŻENIA (DANGER ZONE)"):
        st.markdown("<div class='danger-zone'>", unsafe_allow_html=True)
        st.warning("Poniższy przycisk trwale usunie wszystkie zespoły, ich punkty oraz całą historię rozgrywki.")
        if st.button("☢️ RESETUJ CAŁĄ GRĘ (NIEODWRACALNE)"):
            state.update({"scenario_idx": 0, "round": 0, "teams": {}, "status": "ACTIVE", "history_log": []})
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def team_view():
    team_name = st.session_state["team_name"]
    team_data = state["teams"][team_name]
    m = calculate_metrics(team_name)
    
    st.markdown(f"<div class='command-header'><div class='brand-title'>CyberBank // {team_name}</div><div>S: {state['scenario_idx']+1} | R: {state['round']}</div></div>", unsafe_allow_html=True)

    if not team_data["is_active"]:
        st.markdown("<div class='bankrupt-panel'><h1>💀 STATUS: ELIMINACJA</h1><p>Twój bank nie spełnił wymogów kapitałowych lub utracił zaufanie rynkowe.</p></div>", unsafe_allow_html=True)
        return

    l, c, r = st.columns([1, 2.2, 0.9])
    
    with l:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<span class='panel-label'>WYNIKI OPERACYJNE</span>", unsafe_allow_html=True)
        render_kpi("ZAUFANIE", m[0]); render_kpi("PŁYNNOŚĆ", m[1])
        render_kpi("KAPITAŁ", m[2]); render_kpi("ZGODNOŚĆ", m[3])
        st.markdown("</div><br>", unsafe_allow_html=True)
        if st.button("ODŚWIEŻ TERMINAL 🔄", use_container_width=True): st.rerun()

    with c:
        if state["status"] == "FINISHED":
            st.success("BANK PRZETRWAŁ KRYZYS - GRATULACJE.")
        elif state["round"] == 0:
            st.info("SYSTEMY W GOTOWOŚCI. CZEKAJ NA ROZKAZY Z DOWÓDZTWA.")
        elif team_data["ready"]:
            st.warning("DECYZJE WYSŁANE. TRWA ANALIZA RYNKOWA...")
        else:
            rd = get_round_data(state["scenario_idx"], state["round"])
            st.markdown(f"<div class='scenario-header'><h2>{rd['title']}</h2><p>{rd['desc']}</p></div>", unsafe_allow_html=True)
            with st.form("team_decision"):
                choices = {}
                for role, q in rd["questions"].items():
                    st.write(f"**{q['label']}**")
                    choices[role] = st.radio("Strategia:", list(q["options"].keys()), key=role, label_visibility="collapsed")
                if st.form_submit_button("AUTORYZUJ I WYŚLIJ"):
                    if state["scenario_idx"] not in team_data["decisions"]: team_data["decisions"][state["scenario_idx"]] = {}
                    team_data["decisions"][state["scenario_idx"]][state["round"]] = choices
                    team_data["ready"] = True
                    st.rerun()

    with r:
        st.markdown(f"<div class='panel'><span class='panel-label'>ŁĄCZNOŚĆ</span><div style='text-align:center; font-size:2rem;'>{'🟢' if team_data['ready'] else '🟡'}</div></div>", unsafe_allow_html=True)

def render_kpi(label, value):
    pct = int((value/150)*100)
    color = "var(--accent-red)" if value < 45 else "var(--accent-cyan)"
    st.markdown(f'<div class="kpi-header"><span>{label}</span><span>{pct}%</span></div><div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{pct}%; background:{color}"></div></div><br>', unsafe_allow_html=True)

# --- ROUTER ---
if "role" not in st.session_state: login_view()
elif st.session_state["role"] == "admin": admin_view()
else: team_view()
