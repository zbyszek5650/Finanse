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

# --- CSS (Wersja Oryginalna) ---
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
    .progress-bar-bg { background: var(--bg-color); height: 4px; border-radius: 2px; overflow: hidden; }
    .progress-bar-fill { height: 100%; transition: width 1s; background: var(--accent-cyan); }
    .scenario-header { background: linear-gradient(135deg, var(--panel-bg) 0%, var(--bg-color) 100%); border-left: 4px solid var(--accent-cyan); padding: 20px; margin-bottom: 20px; }
    .log-item { font-family: var(--font-mono); font-size: 0.7rem; padding: 4px 0 4px 8px; border-left: 2px solid var(--border-color); margin-bottom: 8px; }
    .log-ts { color: var(--accent-yellow); }
    .log-act { color: var(--accent-cyan); }
    .bankrupt-panel { background: rgba(239, 68, 68, 0.1); border: 2px solid var(--accent-red); padding: 40px; text-align: center; border-radius: 10px; margin-top: 50px; }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE: 6 SCENARIOS x 5 ROUNDS ---
FIN_SCENARIOS = [
    {"name": "I: Atak Ransomware", "rounds": 5},
    {"name": "II: Insider Threat", "rounds": 5},
    {"name": "III: Supply Chain Sabotage", "rounds": 5},
    {"name": "IV: Phishing Masowy", "rounds": 5},
    {"name": "V: Atak na SWIFT", "rounds": 5},
    {"name": "VI: Deepfake & Social Engineering", "rounds": 5}
]

# Przykładowe dane rundy (należy uzupełnić dla każdej rundy każdego scenariusza)
def get_round_data(s_idx, r_num):
    # Domyślny szablon pytania, jeśli konkretne nie jest zdefiniowane
    return {
        "title": f"FAZA {r_num}: KRYZYS W TOKU",
        "desc": f"Sytuacja w scenariuszu {FIN_SCENARIOS[s_idx]['name']} rozwija się. Wykryto nowe wektory ataku wpływające na stabilność jednostki.",
        "questions": {
            "IT": {"label": "CYBER-SECURITY", "options": {
                "Pełna izolacja systemów": {"trust": 0, "liq": -20, "cap": 0, "comp": +10},
                "Próba neutralizacji bez wyłączania": {"trust": -5, "liq": 0, "cap": 0, "comp": -10},
                "Zewnętrzny audyt śledczy": {"trust": +5, "liq": 0, "cap": -10, "comp": +15},
                "Ignorowanie (fałszywy alarm)": {"trust": -20, "liq": 0, "cap": 0, "comp": -30}
            }},
            "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                "Blokada wypłat powyżej limitu": {"trust": -30, "liq": +20, "cap": 0, "comp": 0},
                "Weryfikacja manualna transakcji": {"trust": +10, "liq": -30, "cap": 0, "comp": +5},
                "Uruchomienie rezerw płynności": {"trust": 0, "liq": +40, "cap": -20, "comp": 0},
                "Brak ograniczeń operacyjnych": {"trust": +5, "liq": -20, "cap": 0, "comp": -10}
            }},
            "Dir": {"label": "ZARZĄD / PR", "options": {
                "Pełna transparentność medialna": {"trust": +20, "liq": 0, "cap": 0, "comp": +10},
                "Utrzymanie ciszy informacyjnej": {"trust": -40, "liq": 0, "cap": 0, "comp": -20},
                "Zgłoszenie do organów nadzoru": {"trust": 0, "liq": 0, "cap": 0, "comp": +40},
                "Kampania dezinformacyjna": {"trust": -10, "liq": 0, "cap": 0, "comp": -50}
            }}
        }
    }

# --- ENGINE ---
@st.cache_resource
def get_engine():
    return {"scenario_idx": 0, "round": 0, "teams": {}, "status": "ACTIVE"}

state = get_engine()

def calculate_metrics(team_name):
    t, l, c, co = 100, 100, 100, 100
    team = state["teams"].get(team_name, {})
    for s_idx in range(state["scenario_idx"] + 1):
        scen_decisions = team.get("decisions", {}).get(s_idx, {})
        for r_num, roles in scen_decisions.items():
            data = get_round_data(s_idx, r_num)
            for role, choice in roles.items():
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
        t_id = st.text_input("KRYPTONIM JEDNOSTKI:").upper()
        if st.button("WEJDŹ DO SYSTEMU", use_container_width=True):
            if t_id:
                if t_id not in state["teams"]:
                    state["teams"][t_id] = {"decisions": {}, "is_active": True, "ready": False, "last_scen": 0}
                st.session_state["team_name"] = t_id
                st.session_state["role"] = "team"
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔐 ROOT"):
            if st.text_input("Hasło:", type="password") == "admin":
                if st.button("ZALOGUJ JAKO ADMIN"):
                    st.session_state["role"] = "admin"
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def admin_view():
    st.markdown('<div class="command-header"><div class="brand-title">CyberBank // CONTROL UNIT</div></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.write(f"### KAMPANIA: {state['scenario_idx']+1} / 6")
        st.write(f"### RUNDA: {state['round']} / 5")
        
        if st.button("⏩ NASTĘPNY ETAP", use_container_width=True):
            if state["round"] < 5:
                state["round"] += 1
            else:
                # Koniec scenariusza -> Sprawdź eliminacje
                for t in state["teams"]:
                    if state["teams"][t]["is_active"]:
                        m = calculate_metrics(t)
                        if any(v < 40 for v in m): state["teams"][t]["is_active"] = False
                        else: state["teams"][t]["last_scen"] = state["scenario_idx"] + 1
                
                if state["scenario_idx"] < 5:
                    state["scenario_idx"] += 1
                    state["round"] = 1
                else:
                    state["status"] = "FINISHED"
            
            for t in state["teams"]: state["teams"][t]["ready"] = False
            st.rerun()
            
        if st.button("🔄 RESET CAŁKOWITY", use_container_width=True):
            state.update({"scenario_idx": 0, "round": 0, "teams": {}, "status": "ACTIVE"})
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-label'>RANKING LIVE</div>", unsafe_allow_html=True)
        data = []
        for t, d in state["teams"].items():
            m = calculate_metrics(t)
            data.append({
                "JEDNOSTKA": t, "PUNKTY": sum(m), 
                "STATUS": "✅ OK" if d["is_active"] else "❌ BANKRUT",
                "SCENARIUSZ": d["last_scen"] + (1 if d["is_active"] else 0),
                "GOTOWOŚĆ": "GOTOWY" if d["ready"] else "W TRAKCIE"
            })
        if data: st.dataframe(pd.DataFrame(data).sort_values("PUNKTY", ascending=False), hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

def team_view():
    team_name = st.session_state["team_name"]
    team_data = state["teams"][team_name]
    m = calculate_metrics(team_name)
    
    st.markdown(f"<div class='command-header'><div class='brand-title'>CyberBank // {team_name}</div><div>SCENARIUSZ {state['scenario_idx']+1} | RUNDA {state['round']}</div></div>", unsafe_allow_html=True)

    if not team_data["is_active"]:
        st.markdown("<div class='bankrupt-panel'><h1>💀 SYSTEM LOCKED</h1><p>Bankructwo operacyjne. Twoja jednostka została wyłączona z rynku.</p></div>", unsafe_allow_html=True)
        return

    l, c, r = st.columns([1, 2.2, 0.9])
    
    with l:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-label'>METRYKI OPERACYJNE</div>", unsafe_allow_html=True)
        render_kpi("ZAUFANIE", m[0]); render_kpi("PŁYNNOŚĆ", m[1])
        render_kpi("KAPITAŁ", m[2]); render_kpi("ZGODNOŚĆ", m[3])
        st.markdown("</div><br><div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='log-item'><span class='log-ts'>["+datetime.datetime.now().strftime("%H:%M")+"]</span> <span class='log-act'>SYS:</span> Synchronizacja...</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c:
        if state["status"] == "FINISHED":
            st.success("GRATULACJE! Bank przetrwał wszystkie 6 scenariuszy.")
        elif state["round"] == 0:
            st.info("OCZEKIWANIE NA ROZPOCZĘCIE SYMULACJI...")
            if st.button("SYNCHRONIZUJ TERMINAL 🔄", use_container_width=True): st.rerun()
        elif team_data["ready"]:
            st.warning("DECYZJE WYSŁANE. OCZEKIWANIE NA ANALIZĘ DOWÓDZTWA...")
            if st.button("ODŚWIEŻ DANE SIECIOWE 🔄", use_container_width=True): st.rerun()
        else:
            rd = get_round_data(state["scenario_idx"], state["round"])
            st.markdown(f"<div class='scenario-header'><h2>{rd['title']}</h2><p>{rd['desc']}</p></div>", unsafe_allow_html=True)
            with st.form("f"):
                choices = {}
                for role, q in rd["questions"].items():
                    st.write(f"**{q['label']}**")
                    choices[role] = st.radio("Wybierz strategię:", list(q["options"].keys()), key=role, label_visibility="collapsed")
                if st.form_submit_button("WYŚLIJ ROZKAZY"):
                    if state["scenario_idx"] not in team_data["decisions"]: team_data["decisions"][state["scenario_idx"]] = {}
                    team_data["decisions"][state["scenario_idx"]][state["round"]] = choices
                    team_data["ready"] = True
                    st.rerun()

    with r:
        st.markdown(f"<div class='panel'><div class='panel-label'>STATUS</div><div style='text-align:center'>{'🟢 READY' if team_data['ready'] else '🟡 WAITING'}</div></div>", unsafe_allow_html=True)

def render_kpi(label, value):
    pct = int((value/150)*100)
    color = "var(--accent-red)" if value < 45 else "var(--accent-cyan)"
    st.markdown(f'<div class="kpi-header"><span>{label}</span><span>{pct}%</span></div><div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{pct}%; background:{color}"></div></div><br>', unsafe_allow_html=True)

# --- ROUTER ---
if "role" not in st.session_state: login_view()
elif st.session_state["role"] == "admin": admin_view()
else: team_view()
