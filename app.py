import streamlit as st
import pandas as pd
import datetime
import time

# --- CONFIGURATION ---
st.set_page_config(
    page_title="CyberBank - Global Crisis Control",
    layout="wide",
    page_icon="🏦",
    initial_sidebar_state="collapsed"
)

# --- ORIGINAL CSS RESTORED ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

    :root {
        --bg-color: #0f172a;
        --panel-bg: #1e293b;
        --border-color: #334155;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --accent-cyan: #06b6d4;
        --accent-red: #ef4444;
        --accent-green: #22c55e;
        --accent-yellow: #f59e0b;
        --font-sans: 'Inter', sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
    }

    .stApp { background-color: var(--bg-color) !important; color: var(--text-primary); font-family: var(--font-sans); }
    #MainMenu, footer, header { visibility: hidden; }

    .command-header {
        height: 64px; background: rgba(15, 23, 42, 0.8); border-bottom: 1px solid var(--border-color);
        padding: 0 24px; display: flex; justify-content: space-between; align-items: center;
        margin-top: -75px; margin-bottom: 24px; position: sticky; top: 0; z-index: 1000;
    }

    .brand-title { font-family: var(--font-mono); font-weight: 700; font-size: 1.2rem; letter-spacing: 0.1em; color: var(--accent-cyan); text-transform: uppercase; }
    .status-badge { background: rgba(239, 68, 68, 0.2); border: 1px solid var(--accent-red); color: var(--accent-red); padding: 4px 12px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }
    
    .panel { background: var(--panel-bg); border: 1px solid var(--border-color); border-radius: 6px; padding: 16px; height: 100%; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .panel-label { font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 12px; display: block; }

    .kpi-container { margin-bottom: 14px; }
    .kpi-header { display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 6px; font-weight: 500; }
    .kpi-value { font-family: var(--font-mono); color: var(--text-primary); }
    .progress-bar-bg { background: var(--bg-color); height: 4px; border-radius: 2px; overflow: hidden; }
    .progress-bar-fill { height: 100%; transition: width 1s cubic-bezier(0.4, 0, 0.2, 1); background: var(--accent-cyan); box-shadow: 0 0 8px rgba(6, 182, 212, 0.4); }

    .scenario-header { background: linear-gradient(135deg, var(--panel-bg) 0%, var(--bg-color) 100%); border-left: 4px solid var(--accent-cyan); border-radius: 0 6px 6px 0; padding: 20px; margin-bottom: 20px; }
    .scenario-id { font-family: var(--font-mono); color: var(--accent-cyan); font-size: 0.75rem; margin-bottom: 4px; }
    .scenario-title { font-size: 1.5rem; font-weight: 800; color: var(--text-primary); }
    
    .stButton > button { background: var(--accent-cyan) !important; color: #000 !important; font-weight: 700 !important; border: none !important; text-transform: uppercase !important; }
    .log-item { font-family: var(--font-mono); font-size: 0.7rem; padding: 4px 0 4px 8px; border-left: 2px solid var(--border-color); margin-bottom: 8px; }
    .log-ts { color: var(--accent-yellow); }
    .log-act { color: var(--accent-cyan); font-weight: 600; margin-left: 4px; }
    .log-msg { color: var(--text-secondary); display: block; margin-top: 2px; }
    
    .bankrupt-panel { background: rgba(239, 68, 68, 0.1); border: 2px solid var(--accent-red); padding: 40px; text-align: center; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- GAME ENGINE STATE ---
@st.cache_resource
def get_engine():
    return {
        "scenario_idx": 0,
        "round": 0,
        "teams": {}, # {name: {"decisions": {scen_idx: {round: choices}}, "is_active": True, "ready": False}}
        "logs": []
    }

state = get_engine()

# --- FINANCIAL SCENARIOS (4 OPTIONS) ---
FIN_SCENARIOS = [
    {
        "name": "OPERACJA: CZARNY PONIEDZIAŁEK (Ransomware)",
        "rounds": {
            1: {
                "title": "AWARIA SYSTEMÓW CORE-BANKING",
                "desc": "Systemy księgowe przestały przetwarzać przelewy przychodzące. Na ekranach pracowników IT pojawia się komunikat o zaszyfrowaniu kluczy baz danych.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Pełna izolacja sieci i wyłączenie serwerów": {"trust": 0, "liq": -30, "cap": 0, "comp": +10},
                        "Próba deszyfracji 'w locie'": {"trust": -5, "liq": -10, "cap": 0, "comp": -10},
                        "Przełączenie na zapasowe centrum danych": {"trust": +5, "liq": -15, "cap": -10, "comp": 0},
                        "Pasywne monitorowanie eksfiltracji": {"trust": -20, "liq": 0, "cap": 0, "comp": -20}
                    }},
                    "Ops": {"label": "OPERACJE / SKARBIEC", "options": {
                        "Wstrzymanie sesji ELIXIR": {"trust": -15, "liq": -40, "cap": 0, "comp": +5},
                        "Ręczne księgowanie transakcji": {"trust": +10, "liq": -10, "cap": -5, "comp": 0},
                        "Limitowanie wypłat w bankomatach": {"trust": -30, "liq": +20, "cap": 0, "comp": -10},
                        "Cisza informacyjna dla oddziałów": {"trust": -25, "liq": 0, "cap": 0, "comp": -15}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Oficjalny komunikat o ataku hakerskim": {"trust": +15, "liq": 0, "cap": 0, "comp": +20},
                        "Zrzucenie winy na 'prace modernizacyjne'": {"trust": -20, "liq": 0, "cap": 0, "comp": -30},
                        "Wynajęcie negocjatorów okupu": {"trust": 0, "liq": 0, "cap": -15, "comp": -10},
                        "Powiadomienie KNF i prokuratury": {"trust": +5, "liq": 0, "cap": 0, "comp": +40}
                    }}
                }
            },
            # Dodaj więcej rund w tej samej strukturze...
        }
    },
    {
        "name": "OPERACJA: SZKLANA PUŁAPKA (Insider Threat)",
        "rounds": {
            1: {
                "title": "KRADZIEŻ TOŻSAMOŚCI ZARZĄDU",
                "desc": "Wewnętrzne systemy bankowe wykazały, że konto Wiceprezesa ds. Ryzyka autoryzowało przelewy na kwotę 20 mln USD do rajów podatkowych.",
                "questions": {
                    "IT": {"label": "INCIDENT RESPONSE", "options": {
                        "Blokada konta Prezesa i audyt logów": {"trust": 0, "liq": 0, "cap": 0, "comp": +10},
                        "Ciche śledzenie transakcji": {"trust": -10, "liq": 0, "cap": -30, "comp": -5},
                        "Reset wszystkich uprawnień adminów": {"trust": -5, "liq": -20, "cap": 0, "comp": +5},
                        "Odłączenie terminala Prezesa od prądu": {"trust": -15, "liq": 0, "cap": 0, "comp": 0}
                    }},
                    "Ops": {"label": "SKARBIEC / RYZYKO", "options": {
                        "Zablokowanie wszystkich przelewów SWIFT": {"trust": -10, "liq": -50, "cap": 0, "comp": +5},
                        "Zgłoszenie podejrzenia do banku odbiorcy": {"trust": +10, "liq": 0, "cap": +5, "comp": +10},
                        "Ignorowanie (oczekiwanie na powrót Prezesa)": {"trust": -20, "liq": 0, "cap": -40, "comp": -30},
                        "Weryfikacja telefoniczna transakcji": {"trust": +5, "liq": -10, "cap": 0, "comp": 0}
                    }},
                    "Dir": {"label": "ZARZĄD", "options": {
                        "Wydanie oświadczenia o błędzie technicznym": {"trust": -10, "liq": 0, "cap": 0, "comp": -20},
                        "Powiadomienie służb specjalnych": {"trust": +5, "liq": 0, "cap": 0, "comp": +30},
                        "Powołanie wewnętrznej komisji śledczej": {"trust": +10, "liq": 0, "cap": -5, "comp": +5},
                        "Zwolnienie dyscyplinarne całego działu IT": {"trust": -30, "liq": -20, "cap": 0, "comp": -10}
                    }}
                }
            }
        }
    }
]

# --- HELPERS ---
def calculate_metrics(team_name):
    t, l, c, co = 100, 100, 100, 100
    team = state["teams"].get(team_name, {})
    
    for s_idx, scen_data in enumerate(FIN_SCENARIOS):
        if s_idx > state["scenario_idx"]: break
        
        decisions = team.get("decisions", {}).get(s_idx, {})
        for r_num, roles in decisions.items():
            # Sprawdzamy czy runda istnieje w scenariuszu (zabezpieczenie)
            if r_num in scen_data["rounds"]:
                for role, choice in roles.items():
                    impact = scen_data["rounds"][r_num]["questions"][role]["options"][choice]
                    t += impact.get("trust", 0)
                    l += impact.get("liq", 0)
                    c += impact.get("cap", 0)
                    co += impact.get("comp", 0)
    
    return [max(0, min(150, m)) for m in [t, l, c, co]]

def render_kpi(label, value, color="var(--accent-cyan)"):
    pct = int((value/150)*100)
    current_color = "var(--accent-red)" if value < 40 else color
    st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-header"><span>{label}</span><span class="kpi-value">{pct}%</span></div>
            <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {pct}%; background: {current_color};"></div></div>
        </div>
    """, unsafe_allow_html=True)

# --- VIEWS ---

def login_view():
    st.markdown('<div class="command-header"><div class="brand-title">CyberBank // LOGIN</div></div>', unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        t_id = st.text_input("IDENTYFIKATOR JEDNOSTKI:", placeholder="np. ALPHA-FIN").upper()
        if st.button("AUTORYZUJ DOSTĘP", use_container_width=True):
            if t_id:
                if t_id not in state["teams"]:
                    state["teams"][t_id] = {"decisions": {}, "is_active": True, "ready": False}
                st.session_state["team_name"] = t_id
                st.session_state["role"] = "team"
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔐 ROOT ACCESS"):
            pwd = st.text_input("PASSWORD:", type="password")
            if st.button("ADMIN LOGIN"):
                if pwd == "admin":
                    st.session_state["role"] = "admin"
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def admin_view():
    st.markdown('<div class="command-header"><div class="brand-title">CyberBank // ROOT COMMAND</div></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.write(f"### SCENARIUSZ: {state['scenario_idx'] + 1}")
        st.write(f"### RUNDA: {state['round']}")
        
        if st.button("⏩ URUCHOM KOLEJNY ETAP", use_container_width=True):
            # Sprawdź eliminacje po końcu scenariusza (np. runda 5)
            # W tym przykładzie mamy tylko 1 rundę per scenariusz dla testu
            if state["round"] >= 1: 
                for t in state["teams"]:
                    m = calculate_metrics(t)
                    if any(val < 40 for val in m):
                        state["teams"][t]["is_active"] = False
                
                if state["scenario_idx"] < len(FIN_SCENARIOS) - 1:
                    state["scenario_idx"] += 1
                    state["round"] = 1
                else:
                    state["round"] = 99 # Koniec gry
            else:
                state["round"] += 1
            
            for t in state["teams"]: state["teams"][t]["ready"] = False
            st.rerun()
            
        if st.button("🔄 RESETUJ SYSTEM", use_container_width=True):
            state["round"] = 0
            state["scenario_idx"] = 0
            state["teams"] = {}
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-label'>MONITOR JEDNOSTEK</div>", unsafe_allow_html=True)
        scores = []
        for t in state["teams"]:
            m = calculate_metrics(t)
            status = "✅" if state["teams"][t]["is_active"] else "❌"
            ready = "GOTOWY" if state["teams"][t]["ready"] else "MYŚLI..."
            scores.append({
                "STATUS": status,
                "JEDNOSTKA": t,
                "WYNIK": sum(m),
                "ZAUFANIE": m[0],
                "LIKWIDNOŚĆ": m[1],
                "AKCJA": ready
            })
        if scores:
            st.dataframe(pd.DataFrame(scores).sort_values(by="WYNIK", ascending=False), hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

def team_view():
    team_name = st.session_state.get("team_name")
    team_data = state["teams"][team_name]
    m = calculate_metrics(team_name)
    now = datetime.datetime.now().strftime("%H:%M:%S")

    # HEADER
    st.markdown(f"""
        <div class="command-header">
            <div class="brand">
                <div class="brand-title">CyberBank // TERMINAL</div>
                <div style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-secondary); margin-left: 20px;">
                    NODE: <span style="color: var(--accent-cyan)">{team_name}</span> | 
                    SCENARIUSZ: {state['scenario_idx']+1}/2 | RUNDA: {state['round']}
                </div>
            </div>
            <div class="status-badge" style="border-color: var(--accent-cyan); color: var(--accent-cyan);">POŁĄCZENIE SZYFROWANE</div>
        </div>
    """, unsafe_allow_html=True)

    # CHECK ELIMINATION
    if not team_data["is_active"]:
        st.markdown("""
            <div class='bankrupt-panel'>
                <h1 style='color: var(--accent-red);'>💀 BANKRUCTWO OPERACYJNE</h1>
                <p style='font-size: 1.2rem;'>Twoje decyzje doprowadziły do utraty płynności lub zaufania rynkowego.</p>
                <p>Nadzór finansowy wygasił licencję bankową Twojej jednostki. Dostęp zablokowany.</p>
            </div>
        """, unsafe_allow_html=True)
        return

    left, center, right = st.columns([1, 2.2, 0.9], gap="medium")

    with left:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-label'>PARAMETRY BANKU</div>", unsafe_allow_html=True)
        render_kpi("ZAUFANIE RYNKU", m[0], "#f43f5e")
        render_kpi("PŁYNNOŚĆ (LIQUIDITY)", m[1], "#06b6d4")
        render_kpi("KAPITAŁ WŁASNY", m[2], "#10b981")
        render_kpi("ZGODNOŚĆ (COMPLIANCE)", m[3], "#facc15")
        st.markdown("</div><br>", unsafe_allow_html=True)
        
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-label'>SYSTEM LOGS</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='log-item'><span class='log-ts'>[{now}]</span> <span class='log-act'>SYS</span>: <span class='log-msg'>Synchronizacja z bankiem centralnym...</span></div>", unsafe_allow_html=True)
        if state["round"] > 0:
            st.markdown(f"<div class='log-item'><span class='log-ts'>[R-{state['round']}]</span> <span class='log-act'>INCIDENT</span>: <span class='log-msg'>Wykryto anomalię w scenariuszu {state['scenario_idx']+1}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with center:
        if state["round"] == 0:
            st.markdown("""
                <div class='panel' style='text-align: center; padding: 5rem 2rem;'>
                    <div style='font-size: 3rem; margin-bottom: 1rem;'>📡</div>
                    <h2 style='color: #f8fafc;'>NASŁUCH PASYWNY</h2>
                    <p style='color: #64748b;'>Rynek międzybankowy stabilny. <br>Oczekiwanie na sygnał z Dowództwa (KNF).</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("SYNCHRONIZUJ TERMINAL 🔄", use_container_width=True): st.rerun()
        
        elif state["round"] == 99:
            st.markdown("<div class='panel' style='text-align: center;'><h2>OPERACJA ZAKOŃCZONA</h2><p>Sprawdź ranking końcowy u administratora.</p></div>", unsafe_allow_html=True)

        elif not team_data["ready"]:
            scen = FIN_SCENARIOS[state["scenario_idx"]]
            round_data = scen["rounds"][state["round"]]
            st.markdown(f"""
                <div class='scenario-header'>
                    <div class='scenario-id'>SITREP_BANK_0x0{state['round']}</div>
                    <div class='scenario-title'>{round_data['title']}</div>
                </div>
                <div class='panel' style='margin-bottom: 1.5rem;'><div class='scenario-desc'>{round_data['desc']}</div></div>
            """, unsafe_allow_html=True)
            
            with st.form(f"f_{state['scenario_idx']}_{state['round']}"):
                decisions = {}
                for role, q in round_data["questions"].items():
                    st.markdown(f"<div style='color:var(--accent-cyan); font-weight:700; font-size:0.8rem;'>{q['label']}</div>", unsafe_allow_html=True)
                    decisions[role] = st.radio("Opcje:", list(q["options"].keys()), label_visibility="collapsed")
                    st.markdown("<br>", unsafe_allow_html=True)
                
                if st.form_submit_button("WDROŻYJ PROCEDURY KRYZYSOWE"):
                    if state["scenario_idx"] not in team_data["decisions"]: team_data["decisions"][state["scenario_idx"]] = {}
                    team_data["decisions"][state["scenario_idx"]][state["round"]] = decisions
                    team_data["ready"] = True
                    st.rerun()
        else:
            st.markdown("""
                <div class='panel' style='background: rgba(6, 182, 212, 0.05); border-color: var(--accent-cyan);'>
                    <h4 style='color: var(--accent-cyan);'>✓ PROCEDURY W TOKU</h4>
                    <p style='color: var(--text-secondary);'>Decyzje zostały przesłane do walidacji przez Zarząd.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("ODŚWIEŻ DANE SIECIOWE", use_container_width=True): st.rerun()

    with right:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-label'>STATUS TERMINALA</div>", unsafe_allow_html=True)
        s_icon = "🟢" if team_data["ready"] else "🟡"
        s_text = "GOTOWY" if team_data["ready"] else "OCZEKIWANIE"
        st.markdown(f"""
            <div style="text-align: center; padding: 1.5rem 0;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{s_icon}</div>
                <div style="font-weight: 800; color: #f8fafc;">{s_text}</div>
            </div>
            <div style="font-size: 0.65rem; color: #475569; line-height: 1.4;">
                ENCRYPTION: AES-512<br>
                UPTIME: 99.99%<br>
                REGULATION: KNF-Cyber-2.0
            </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- ROUTER ---
if "role" not in st.session_state:
    login_view()
elif st.session_state["role"] == "admin":
    admin_view()
else:
    team_view()
