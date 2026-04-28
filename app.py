import streamlit as st
import pandas as pd
import datetime

# --- CONFIGURATION ---
st.set_page_config(
    page_title="CyberBank: Global Crisis Response",
    layout="wide",
    page_icon="🏦",
    initial_sidebar_state="collapsed"
)

# --- CSS (Zachowanie stylu Command Center) ---
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
    .status-badge { background: rgba(239, 68, 68, 0.2); border: 1px solid var(--accent-red); color: var(--accent-red); padding: 4px 12px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }
    .panel { background: var(--panel-bg); border: 1px solid var(--border-color); border-radius: 6px; padding: 16px; height: 100%; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .panel-label { font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; margin-bottom: 12px; display: block; }
    .kpi-container { margin-bottom: 14px; }
    .kpi-header { display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 6px; }
    .progress-bar-bg { background: var(--bg-color); height: 6px; border-radius: 3px; overflow: hidden; }
    .progress-bar-fill { height: 100%; transition: width 0.8s ease; }
    .scenario-header { background: linear-gradient(135deg, var(--panel-bg) 0%, var(--bg-color) 100%); border-left: 4px solid var(--accent-cyan); border-radius: 0 6px 6px 0; padding: 20px; margin-bottom: 20px; }
    .stButton > button { background: var(--accent-cyan) !important; color: #000 !important; font-weight: 700 !important; width: 100%; }
    .eliminated { background: rgba(239, 68, 68, 0.1) !important; border: 1px solid var(--accent-red) !important; color: var(--accent-red) !important; padding: 20px; text-align: center; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- DATA: FINANCIAL SCENARIOS (4 OPTIONS) ---
# Każdy scenariusz ma 5 rund. Każda runda ma 3 role. Każda rola ma 4 opcje.
SCENARIOS = [
    {
        "name": "I: Cyfrowy Paraliż (Ransomware)",
        "content": {
            1: {
                "title": "LOCKDOWN SYSTEMÓW KASOWYCH",
                "desc": "O godzinie 8:50 systemy transakcyjne w placówkach przestają odpowiadać. Na ekranach bankomatów pojawia się logo grupy 'BlackBit'. Żądają 100 BTC.",
                "questions": {
                    "IT": {"label": "IT / SECURITY", "options": {
                        "Pełna izolacja DC i odcięcie Internetu": {"tru": 0, "liq": -30, "cap": 0, "com": +10},
                        "Próba wybiórczego blokowania ruchu": {"tru": -5, "liq": -10, "cap": 0, "com": -5},
                        "Analiza wektora bez wyłączania systemów": {"tru": -10, "liq": 0, "cap": 0, "com": -20},
                        "Przywracanie z backupów 'na żywo'": {"tru": 0, "liq": -15, "cap": -5, "com": 0}
                    }},
                    "Ops": {"label": "OPERACJE / PR", "options": {
                        "Oficjalny komunikat o 'pracach serwisowych'": {"tru": -10, "liq": 0, "cap": 0, "com": -15},
                        "Pełna transparentność o ataku": {"tru": +10, "liq": -5, "cap": 0, "com": +15},
                        "Milczenie i blokada infolinii": {"tru": -30, "liq": 0, "cap": 0, "com": -20},
                        "Przekierowanie klientów do aplikacji mobilnej": {"tru": +5, "liq": -10, "cap": 0, "com": 0}
                    }},
                    "Dir": {"label": "ZARZĄD / COMPLIANCE", "options": {
                        "Zgłoszenie do KNF i prokuratury natychmiast": {"tru": +5, "liq": 0, "cap": 0, "com": +30},
                        "Podjęcie tajnych negocjacji z hakerami": {"tru": -20, "liq": 0, "cap": -10, "com": -40},
                        "Wynajęcie zewnętrznej firmy IR (Incident Response)": {"tru": +5, "liq": 0, "cap": -15, "com": +10},
                        "Utworzenie rezerwy celowej na kary": {"tru": 0, "liq": 0, "cap": -20, "com": +5}
                    }}
                }
            },
            # ... (Dla zwięzłości w przykładzie definiuję 2 rundy, w pełnej wersji byłoby 5)
            2: {
                "title": "WYCIEK DANYCH KLIENTÓW VIP",
                "desc": "Hakerzy publikują w sieci DarkWeb dane 100 najbogatszych klientów banku. Media zaczynają spekulować o bankructwie.",
                "questions": {
                    "IT": {"label": "IT / SECURITY", "options": {
                        "Wymuszona zmiana haseł dla wszystkich": {"tru": +10, "liq": -20, "cap": 0, "com": +5},
                        "Szyfrowanie bazy danych 'post factum'": {"tru": -5, "liq": -5, "cap": 0, "com": -10},
                        "Odcięcie dostępu API dla partnerów": {"tru": 0, "liq": -25, "cap": -5, "com": 0},
                        "Dezinformacja hakerów (fałszywe bazy)": {"tru": 0, "liq": 0, "cap": -10, "com": -20}
                    }},
                    "Ops": {"label": "OPERACJE / PR", "options": {
                        "Osobisty kontakt z poszkodowanymi VIP": {"tru": +20, "liq": 0, "cap": -5, "com": 0},
                        "Darmowe ubezpieczenie od kradzieży tożsamości": {"tru": +15, "liq": 0, "cap": -15, "com": +5},
                        "Zaprzeczanie autentyczności wycieku": {"tru": -40, "liq": 0, "cap": 0, "com": -50},
                        "Konferencja prasowa z Prezesem": {"tru": +10, "liq": 0, "cap": 0, "com": +5}
                    }},
                    "Dir": {"label": "ZARZĄD / COMPLIANCE", "options": {
                        "Dobrowolne poddanie się karze regulatora": {"tru": +5, "liq": 0, "cap": -20, "com": +40},
                        "Zrzucenie winy na dostawcę chmury": {"tru": -10, "liq": 0, "cap": 0, "com": -20},
                        "Zwiększenie budżetu na cyberbezpieczeństwo o 200%": {"tru": +10, "liq": 0, "cap": -30, "com": +10},
                        "Dymisja Dyrektora IT (szukanie winnego)": {"tru": -10, "liq": 0, "cap": 0, "com": -10}
                    }}
                }
            }
        }
    },
    {
        "name": "II: Atak na Systemy Płatności (SWIFT)",
        "content": {
            1: {
                "title": "NIEAUTORYZOWANE PRZELEWY",
                "desc": "Systemy monitorowania wykryły pakiety transakcyjne wychodzące do banków w rajach podatkowych. Zniknęło już 50 mln USD.",
                "questions": {
                    "IT": {"label": "IT / SECURITY", "options": {
                        "Natychmiastowe zatrzymanie bramy SWIFT": {"tru": -5, "liq": -50, "cap": 0, "com": +20},
                        "Analiza ruchu bez przerywania sesji": {"tru": -10, "liq": 0, "cap": -30, "com": -20},
                        "Wdrożenie dodatkowego MFA dla przelewów": {"tru": +5, "liq": -10, "cap": 0, "com": +10},
                        "Próba 'hack-back' (kontratak)": {"tru": -20, "liq": 0, "cap": 0, "com": -100}
                    }},
                    "Ops": {"label": "OPERACJE", "options": {
                        "Wstrzymanie wszystkich przelewów zagranicznych": {"tru": -20, "liq": -40, "cap": 0, "com": 0},
                        "Ręczna weryfikacja każdej transakcji > 10k": {"tru": +10, "liq": -30, "cap": 0, "com": +10},
                        "Cicha współpraca z innymi bankami": {"tru": +5, "liq": 0, "cap": 0, "com": +5},
                        "Ignorowanie małych kwot (poniżej progu)": {"tru": -10, "liq": 0, "cap": -20, "com": -20}
                    }},
                    "Dir": {"label": "ZARZĄD", "options": {
                        "Blokada wypłat z depozytów (Bank Run prevention)": {"tru": -60, "liq": +20, "cap": 0, "com": -30},
                        "Uruchomienie linii kredytowej z Banku Centralnego": {"tru": 0, "liq": +40, "cap": -20, "com": 0},
                        "Publiczne oskarżenie obcego wywiadu": {"tru": +5, "liq": 0, "cap": 0, "com": -10},
                        "Pełny audyt zewnętrzny": {"tru": +10, "liq": 0, "cap": -10, "com": +20}
                    }}
                }
            }
        }
    }
]

# --- GAME ENGINE STATE ---
@st.cache_resource
def get_engine():
    return {
        "round": 0,
        "scenario_idx": 0,
        "teams": {}, # {name: {"decisions": {scen: {round: {role: choice}}}, "is_active": True}}
        "status": "SETUP"
    }

state = get_engine()

# --- HELPERS ---
def calculate_metrics(team_name):
    tru, liq, cap, com = 100, 100, 100, 100
    team = state["teams"].get(team_name, {})
    
    # Przelicz wszystkie scenariusze i rundy
    for s_idx, scenario in enumerate(SCENARIOS):
        if s_idx > state["scenario_idx"]: break
        
        scen_decisions = team.get("decisions", {}).get(s_idx, {})
        for r_num, roles in scen_decisions.items():
            for role, choice in roles.items():
                impact = SCENARIOS[s_idx]["content"][r_num]["questions"][role]["options"][choice]
                tru += impact.get("tru", 0)
                liq += impact.get("liq", 0)
                cap += impact.get("cap", 0)
                com += impact.get("com", 0)
    
    return [max(0, min(150, m)) for m in [tru, liq, cap, com]]

def is_team_eliminated(metrics):
    return any(m < 40 for m in metrics)

def render_kpi(label, value):
    pct = int((value/150)*100)
    color = "var(--accent-red)" if value < 50 else "var(--accent-cyan)"
    st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-header"><span>{label}</span><span style="color:{color}">{pct}%</span></div>
            <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{pct}%; background:{color};"></div></div>
        </div>
    """, unsafe_allow_html=True)

# --- VIEWS ---
def login_view():
    st.markdown("<div class='command-header'><div class='brand-title'>CyberBank // AUTH</div></div>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        t_id = st.text_input("KRYPTONIM JEDNOSTKI (np. BANK-ALPHA):").upper()
        if st.button("DOŁĄCZ DO OPERACJI"):
            if t_id:
                if t_id not in state["teams"]:
                    state["teams"][t_id] = {"decisions": {}, "is_active": True, "ready": False, "last_scen": 0}
                st.session_state["team_name"] = t_id
                st.session_state["role"] = "team"
                st.rerun()
        
        st.markdown("---")
        pwd = st.text_input("ADMIN ROOT ACCESS:", type="password")
        if st.button("LOG AS COMMANDER"):
            if pwd == "cyber2024":
                st.session_state["role"] = "admin"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def admin_view():
    st.markdown("<div class='command-header'><div class='brand-title'>CyberBank // COMMANDER</div></div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.write(f"**SCENARIUSZ:** {SCENARIOS[state['scenario_idx']]['name']}")
        st.write(f"**RUNDA:** {state['round']} / 5")
        
        if st.button("NASTĘPNA ETAP (RUNDA/SCENARIUSZ)"):
            if state["round"] < 2: # Tu docelowo 5
                state["round"] += 1
            else:
                # Koniec scenariusza -> eliminacja słabych
                for t_name in state["teams"]:
                    if state["teams"][t_name]["is_active"]:
                        m = calculate_metrics(t_name)
                        if is_team_eliminated(m):
                            state["teams"][t_name]["is_active"] = False
                        else:
                            state["teams"][t_name]["last_scen"] = state["scenario_idx"] + 1
                
                if state["scenario_idx"] < len(SCENARIOS) - 1:
                    state["scenario_idx"] += 1
                    state["round"] = 1
                else:
                    state["status"] = "FINISHED"
            
            for t in state["teams"]: state["teams"][t]["ready"] = False
            st.rerun()
            
        if st.button("RESETUJ GRĘ", type="secondary"):
            state["round"] = 0
            state["scenario_idx"] = 0
            state["teams"] = {}
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-label'>RANKING LIVE</div>", unsafe_allow_html=True)
        data = []
        for t, d in state["teams"].items():
            m = calculate_metrics(t)
            status = "✅ AKTYWNY" if d["is_active"] else "❌ BANKRUT"
            data.append({
                "TEAM": t, 
                "PUNKTY": sum(m), 
                "SCENARIUSZ": f"{d['last_scen'] + 1}",
                "STATUS": status,
                "ZAUFANIE": m[0], "LIKWIDNOŚĆ": m[1]
            })
        if data:
            df = pd.DataFrame(data).sort_values(by=["PUNKTY"], ascending=False)
            st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

def team_view():
    team_name = st.session_state["team_name"]
    team_data = state["teams"][team_name]
    metrics = calculate_metrics(team_name)
    
    # Header
    st.markdown(f"<div class='command-header'><div class='brand-title'>TERMINAL: {team_name}</div><div>ETAP: {state['scenario_idx']+1}.{state['round']}</div></div>", unsafe_allow_html=True)

    if not team_data["is_active"]:
        st.markdown(f"""
            <div class='eliminated'>
                <h1>💀 ELIMINACJA</h1>
                <p>Twój bank ogłosił upadłość w scenariuszu {state['scenario_idx'] + 1}.</p>
                <p>Wskaźniki spadły poniżej progu bezpieczeństwa (40%). Nadzór finansowy odebrał licencję.</p>
            </div>
        """, unsafe_allow_html=True)
        return

    col_stats, col_main = st.columns([1, 3])
    
    with col_stats:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        render_kpi("ZAUFANIE RYNKU", metrics[0])
        render_kpi("LIKWIDNOŚĆ", metrics[1])
        render_kpi("KAPITAŁ WŁASNY", metrics[2])
        render_kpi("ZGODNOŚĆ (COMP)", metrics[3])
        st.markdown("</div>", unsafe_allow_html=True)

    with col_main:
        if state["round"] == 0:
            st.info("Oczekiwanie na rozpoczęcie symulacji przez dowództwo...")
        elif team_data["ready"]:
            st.success("Decyzje wysłane. Oczekiwanie na wyniki rundy...")
        else:
            scen = SCENARIOS[state["scenario_idx"]]
            round_data = scen["content"][state["round"]]
            
            st.markdown(f"""
                <div class='scenario-header'>
                    <div style='font-size:0.8rem; opacity:0.7'>SCENARIUSZ {scen['name']}</div>
                    <h2>{round_data['title']}</h2>
                    <p>{round_data['desc']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("decision_form"):
                user_choices = {}
                for role, q in round_data["questions"].items():
                    st.subheader(q["label"])
                    user_choices[role] = st.radio("Wybierz strategię:", list(q["options"].keys()), key=f"{role}_{state['round']}")
                
                if st.form_submit_button("ZATWIERDŹ DECYZJE"):
                    if state["scenario_idx"] not in state["teams"][team_name]["decisions"]:
                        state["teams"][team_name]["decisions"][state["scenario_idx"]] = {}
                    state["teams"][team_name]["decisions"][state["scenario_idx"]][state["round"]] = user_choices
                    state["teams"][team_name]["ready"] = True
                    st.rerun()

# --- ROUTER ---
if "role" not in st.session_state:
    login_view()
elif st.session_state["role"] == "admin":
    admin_view()
else:
    team_view()
