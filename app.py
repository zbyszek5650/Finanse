import streamlit as st
import pandas as pd

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="FINANCIAL OS // COMMAND CENTER",
    layout="wide",
    page_icon="🏦",
    initial_sidebar_state="collapsed"
)

# --- 2. ZAAWANSOWANY CSS (CYBERPUNK FINTECH) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #050a0f !important; color: #cbd5e1; font-family: 'Courier New', Courier, monospace; }
    
    .top-bar {
        background-color: #0d1117; border-bottom: 2px solid #30363d;
        padding: 15px 30px; display: flex; justify-content: space-between;
        align-items: center; margin-top: -60px; margin-bottom: 30px;
    }
    .top-bar-title { color: #58a6ff; font-size: 22px; font-weight: 900; letter-spacing: 2px; }
    .status-eliminated { background-color: #3e1010; color: #f85149; border: 1px solid #f85149; padding: 5px 15px; border-radius: 4px; font-weight: bold; }

    .cyber-panel { background-color: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
    .panel-header { font-size: 11px; color: #8b949e; text-transform: uppercase; border-bottom: 1px solid #30363d; margin-bottom: 15px; padding-bottom: 5px; }

    .kpi-row { margin-bottom: 15px; }
    .kpi-bg { background-color: #161b22; height: 10px; border-radius: 5px; overflow: hidden; border: 1px solid #30363d; }
    .kpi-fill { height: 100%; background-color: #238636; box-shadow: 0 0 10px #238636aa; transition: width 0.5s ease; }
    .kpi-fill.critical { background-color: #da3633; box-shadow: 0 0 10px #da3633aa; }

    .warning-box { background-color: #0d1117; border-left: 5px solid #58a6ff; padding: 20px; margin-bottom: 25px; color: #e6edf3; font-size: 15px; }
    
    .stRadio label { background: #161b22 !important; border: 1px solid #30363d !important; color: #c9d1d9 !important; padding: 12px !important; border-radius: 6px !important; margin-bottom: 8px !important; }
    .stRadio label:hover { border-color: #58a6ff !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. BAZA SCENARIUSZY ---
SCENARIOS = [
    {
        "name": "I. ATAK NA SWIFT",
        "desc": "Systemy monitoringu wykryły nieautoryzowane transfery na kwotę 500 mln USD do rajów podatkowych.",
        "options": {
            "Natychmiastowy Blackout systemów (Hard Stop)": {"trst": 10, "liq": -35, "reg": 20},
            "Analiza na żywo i blokowanie kont (Ryzykowny wyciek)": {"trst": -10, "liq": -5, "reg": -5},
            "Honeypot - śledzenie hakerów bez blokady": {"trst": 0, "liq": -10, "reg": -25},
            "Brak blokady - manualna weryfikacja u korespondentów": {"trst": -30, "liq": 10, "reg": -40}
        }
    },
    {
        "name": "II. WYCIEK DANYCH KLIENTÓW VIP",
        "desc": "W darknecie opublikowano bazy danych 500 najbogatszych klientów banku.",
        "options": {
            "Pełna transparentność i darmowy audyt dla poszkodowanych": {"trst": 25, "liq": -15, "reg": 25},
            "Ciche blokowanie dostępów i wymiana tokenów": {"trst": -5, "liq": -10, "reg": 0},
            "Oficjalne zaprzeczenie wycieku do czasu audytu": {"trst": -20, "liq": 0, "reg": -45},
            "Próba odkupienia danych od hakerów": {"trst": -25, "liq": -35, "reg": -60}
        }
    },
    {
        "name": "III. BŁĄD ALGORYTMU HFT (FLASH CRASH)",
        "desc": "Wasz algorytm wyprzedał obligacje skarbowe, wywołując panikę giełdową.",
        "options": {
            "Awaryjny Kill-Switch i zawieszenie handlu na 24h": {"trst": -15, "liq": -45, "reg": 25},
            "Ręczne wprowadzanie zleceń przeciwstawnych": {"trst": 0, "liq": -35, "reg": -10},
            "Wniosek do Giełdy o anulowanie transakcji (Awaria)": {"trst": 15, "liq": 0, "reg": 15},
            "Ukrywanie awarii pod pozorem rebalansacji": {"trst": -55, "liq": -20, "reg": -50}
        }
    },
    {
        "name": "IV. RUN NA BANK",
        "desc": "Plotki o problemach spowodowały masowe wycofywanie depozytów.",
        "options": {
            "Pożyczka płynnościowa z Banku Centralnego (LOLA)": {"trst": -15, "liq": 50, "reg": 15},
            "Ograniczenie limitów wypłat w bankomatach": {"trst": -70, "liq": 25, "reg": -25},
            "Przedłużenie godzin pracy i publiczne uspokajanie": {"trst": 30, "liq": -10, "reg": 0},
            "Gwałtowna wyprzedaż portfela aktywów (Fire Sale)": {"trst": 0, "liq": 35, "reg": -15}
        }
    },
    {
        "name": "V. RANSOMWARE W KSIĘDZE GŁÓWNEJ",
        "desc": "System księgowy jest zaszyfrowany. Nie można zamknąć dnia operacyjnego.",
        "options": {
            "Odtwarzanie z backupów (Utrata transakcji z 12h)": {"trst": -10, "liq": -15, "reg": 0},
            "Przejście na procedury offline (Papierowo)": {"trst": -5, "liq": -25, "reg": 25},
            "Zapłata okupu hakerom": {"trst": -40, "liq": -45, "reg": -70},
            "Zawiadomienie regulatora o 'Sile Wyższej'": {"trst": -25, "liq": 0, "reg": 15}
        }
    },
    {
        "name": "VI. SABOTAŻ WEWNĘTRZNY",
        "desc": "Szef biura maklerskiego ukrył stratę 4 mld PLN. Instytucja stoi przed upadłością.",
        "options": {
            "Wniosek o dokapitalizowanie i dymisja Zarządu": {"trst": 15, "liq": 40, "reg": 20},
            "Próba kreatywnego księgowania straty": {"trst": -30, "liq": -10, "reg": -90},
            "Agresywny handel w celu 'odrobienia' strat": {"trst": -90, "liq": -50, "reg": -100},
            "Pełna współpraca z prokuraturą i odpis strat": {"trst": -10, "liq": -60, "reg": 35}
        }
    }
]

# --- 4. LOGIKA SYSTEMOWA ---
if "state" not in st.session_state:
    st.session_state.state = {"round": 0, "teams": {}}

def calculate_scores(team_name):
    t_data = st.session_state.state["teams"][team_name]
    trst, liq, reg = 100, 100, 100
    elim_round = None
    for i in range(st.session_state.state["round"]):
        if str(i) in t_data["decisions"]:
            impact = SCENARIOS[i]["options"][t_data["decisions"][str(i)]]
            trst += impact["trst"]; liq += impact["liq"]; reg += impact["reg"]
            if (trst < 20 or liq < 20 or reg < 20) and elim_round is None:
                elim_round = i + 1
    return max(0, trst), max(0, liq), max(0, reg), elim_round

def render_kpi(label, val):
    color = "critical" if val < 40 else ""
    return f"""<div class="kpi-row"><div style="display:flex; justify-content:space-between; font-size:12px; font-weight:bold;"><span>{label}</span><span>{val} PKT</span></div><div class="kpi-bg"><div class="kpi-fill {color}" style="width:{min(val, 150)/1.5}%"></div></div></div>"""

# --- 5. ROUTER WIDOKÓW ---
if "role" not in st.session_state:
    st.markdown("<div class='top-bar'><div class='top-bar-title'>FINANCIAL OS // AUTH</div></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div class='cyber-panel'>", unsafe_allow_html=True)
        uid = st.text_input("ID OPERATORA (ROOT LUB NAZWA):").strip()
        if st.button("ZALOGUJ"):
            if uid.upper() == "ROOT": st.session_state.role = "admin"
            elif uid:
                if uid not in st.session_state.state["teams"]: st.session_state.state["teams"][uid] = {"decisions": {}, "ready": False}
                st.session_state.role, st.session_state.team_name = "team", uid
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.role == "admin":
    st.sidebar.button("LOGOUT", on_click=lambda: st.session_state.clear())
    st.markdown(f"<div class='top-bar'><div class='top-bar-title'>COMMAND CENTER // ROUND {st.session_state.state['round']}</div></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='cyber-panel'>", unsafe_allow_html=True)
        if st.session_state.state["round"] < len(SCENARIOS):
            if st.button("🚀 URUCHOM NASTĘPNĄ RUNDĘ", use_container_width=True):
                st.session_state.state["round"] += 1
                for t in st.session_state.state["teams"]: st.session_state.state["teams"][t]["ready"] = False
                st.rerun()
        if st.button("🔄 RESET GRY"): st.session_state.state = {"round": 0, "teams": {}}; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='cyber-panel'>", unsafe_allow_html=True)
        for t, d in st.session_state.state["teams"].items():
            _, _, _, elim = calculate_scores(t)
            st.write(f"{'🔴' if elim else '🟢'} **{t}**: {'ELIMINACJA' if elim else ('GOTOWY' if d['ready'] else 'MYŚLI')}")
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.role == "team":
    team = st.session_state.team_name
    trst, liq, reg, elim = calculate_scores(team)
    st.markdown(f"<div class='top-bar'><div class='top-bar-title'>{team.upper()}</div></div>", unsafe_allow_html=True)
    
    if elim:
        st.error(f"ZABALOKOWANY PRZEZ REGULATORA W RUNDZIE {elim}")
        st.markdown("<div class='warning-box'>Twoja instytucja upadła. Czekaj na wyniki końcowe.</div>", unsafe_allow_html=True)
    elif st.session_state.state["round"] == 0:
        st.info("OCZEKIWANIE NA START...")
    else:
        idx = st.session_state.state["round"] - 1
        scen = SCENARIOS[idx]
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("<div class='cyber-panel'>", unsafe_allow_html=True)
            st.markdown(render_kpi("ZAUFANIE", trst), unsafe_allow_html=True)
            st.markdown(render_kpi("PŁYNNOŚĆ", liq), unsafe_allow_html=True)
            st.markdown(render_kpi("ZGODNOŚĆ", reg), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            if not st.session_state.state["teams"][team]["ready"]:
                st.markdown(f"### {scen['name']}")
                st.markdown(f"<div class='warning-box'>{scen['desc']}</div>", unsafe_allow_html=True)
                with st.form("f"):
                    choice = st.radio("DECYZJA:", list(scen["options"].keys()))
                    if st.form_submit_button("WYŚLIJ"):
                        st.session_state.state["teams"][team]["decisions"][str(idx)] = choice
                        st.session_state.state["teams"][team]["ready"] = True
                        st.rerun()
            else:
                st.success("DECYZJA PRZYJĘTA. CZEKAJ...")

# Ranking końcowy
if st.session_state.state["round"] == len(SCENARIOS):
    st.markdown("### 🏆 RANKING KOŃCOWY")
    res = []
    for t in st.session_state.state["teams"]:
        tr, li, re, elim = calculate_scores(t)
        res.append({"Drużyna": t, "Suma": (tr+li+re if not elim else 0), "Status": "AKTYWNY" if not elim else f"ELIMINACJA R{elim}"})
    st.table(pd.DataFrame(res).sort_values("Suma", ascending=False))
