import streamlit as st
import pandas as pd
import base64
import os

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="FINANCIAL OS // CRISIS CONTROL",
    layout="wide",
    page_icon="🏦",
    initial_sidebar_state="collapsed"
)

# --- CSS (FINTECH / DARK TERMINAL THEME) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #050a0f !important; color: #cbd5e1; }
    
    .top-bar {
        background-color: #0d1117;
        border-bottom: 2px solid #30363d;
        padding: 15px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: -60px;
        margin-bottom: 30px;
    }
    .top-bar-title { color: #58a6ff; font-size: 20px; font-weight: 900; letter-spacing: 2px; font-family: monospace; }
    .status-eliminated { background-color: #3e1010; color: #f85149; border: 1px solid #f85149; padding: 4px 12px; border-radius: 4px; font-weight: bold; }
    
    .cyber-panel { background-color: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
    .kpi-row { margin-bottom: 15px; }
    .kpi-bg { background-color: #161b22; height: 8px; border-radius: 4px; overflow: hidden; }
    .kpi-fill { height: 100%; background-color: #238636; }
    .kpi-fill.low { background-color: #da3633; }

    .warning-box {
        background-color: #0d1117;
        border-left: 4px solid #f85149;
        padding: 15px;
        margin-bottom: 20px;
        font-size: 14px;
    }
    .stRadio label { background: #161b22 !important; border: 1px solid #30363d !important; color: #c9d1d9 !important; padding: 10px !important; border-radius: 5px !important; margin-bottom: 5px !important; }
    </style>
""", unsafe_allow_html=True)

# --- STAN GRY ---
if "state" not in st.session_state:
    st.session_state.state = {
        "round": 0,
        "teams": {},
        "active_scenario_idx": 0
    }

state = st.session_state.state

# --- SCENARIUSZE (6 SCENARIUSZY x 4 ODPOWIEDZI) ---
SCENARIOS = [
    {
        "name": "I. Atak na infrastrukturę SWIFT",
        "desc": "Wykryto nieautoryzowane próby transferów międzybankowych na kwotę 500 mln USD. Systemy monitoringu zgłaszają anomalie w pakietach danych wychodzących.",
        "options": {
            "Natychmiastowe odcięcie gatewaya SWIFT (Paraliż operacyjny)": {"trst": +10, "liq": -30, "reg": +20},
            "Selektywne blokowanie kont i analiza manualna (Ryzyko błędu)": {"trst": -10, "liq": -10, "reg": 0},
            "Uruchomienie 'Shadow Honeypot' do śledzenia hakerów": {"trst": 0, "liq": 0, "reg": -20},
            "Brak blokady, prośba do banków korespondentów o wstrzymanie": {"trst": -30, "liq": +10, "reg": -30}
        }
    },
    {
        "name": "II. Wyciek danych klientów Wealth Management",
        "desc": "W darknecie pojawiła się paczka danych zawierająca stany kont i numery telefonów najbogatszych klientów banku.",
        "options": {
            "Pełna transparentność i infolinia dla klientów (Koszty PR)": {"trst": +20, "liq": -10, "reg": +20},
            "Ciche blokowanie dostępów i wymiana kart": {"trst": -5, "liq": -10, "reg": -10},
            "Zaprzeczenie wyciekowi do czasu audytu biegłych": {"trst": -40, "liq": 0, "reg": -40},
            "Wykupienie danych od hakerów (Szantaż)": {"trst": -20, "liq": -30, "reg": -50}
        }
    },
    {
        "name": "III. Flash Crash - Błąd Algorytmu",
        "desc": "Wasz algorytm HFT oszalał. W ciągu 3 minut sprzedał aktywa o wartości 2 mld PLN, powodując załamanie kursu złotego.",
        "options": {
            "Awaryjny 'Kill-Switch' wszystkich systemów tradingu": {"trst": -10, "liq": -40, "reg": +20},
            "Ręczne kontr-zlecenia kupna w celu stabilizacji": {"trst": 0, "liq": -30, "reg": -10},
            "Zgłoszenie awarii technicznej do Giełdy z prośbą o cofnięcie sesji": {"trst": +10, "liq": 0, "reg": +10},
            "Ignorowanie i liczenie na autokorektę rynku": {"trst": -50, "liq": -20, "reg": -50}
        }
    },
    {
        "name": "IV. Run na Bank (Liquidity Crisis)",
        "desc": "Fake news w mediach społecznościowych o Waszej niewypłacalności spowodował, że klienci wypłacili 15% depozytów w 4 godziny.",
        "options": {
            "Pożyczka płynnościowa z Banku Centralnego (LOLA)": {"trst": -10, "liq": +40, "reg": +10},
            "Ograniczenie limitów wypłat w bankomatach": {"trst": -60, "liq": +20, "reg": -20},
            "Kampania w mediach z Prezesem zapewniającym o stabilności": {"trst": +20, "liq": -5, "reg": 0},
            "Wyprzedaż portfela obligacji długoterminowych ze stratą": {"trst": 0, "liq": +30, "reg": -10}
        }
    },
    {
        "name": "V. Ransomware w systemie rozliczeniowym",
        "desc": "Systemy księgowe zostały zaszyfrowane. Nie możecie zamknąć dnia, co grozi zawieszeniem licencji przez KNF.",
        "options": {
            "Przejście na rozliczanie offline (Dokumentacja papierowa)": {"trst": -10, "liq": -20, "reg": +20},
            "Zapłata okupu w celu szybkiego przywrócenia (Ryzykowne)": {"trst": -30, "liq": -40, "reg": -50},
            "Odtwarzanie z backupów (Utrata transakcji z 6h)": {"trst": -5, "liq": -10, "reg": 0},
            "Fuzja awaryjna z innym bankiem pod przymusem regulatora": {"trst": -20, "liq": +10, "reg": -10}
        }
    },
    {
        "name": "VI. Sabotaż wewnętrzny (Rogue Trader)",
        "desc": "Dyrektor tradingu ukrywał straty na instrumentach pochodnych przez 2 lata. Dziura wynosi 4 mld PLN.",
        "options": {
            "Natychmiastowe zawiadomienie prokuratury i odpis strat": {"trst": -10, "liq": -50, "reg": +30},
            "Próba 'odrobienia' strat w tajnej operacji rynkowej": {"trst": -80, "liq": -40, "reg": -100},
            "Rozłożenie strat w czasie poprzez kreatywną księgowość": {"trst": -20, "liq": -10, "reg": -80},
            "Wniosek o dokapitalizowanie od akcjonariuszy": {"trst": +10, "liq": +30, "reg": +10}
        }
    }
]

# --- LOGIKA ---
def calculate_scores(team_data):
    trst, liq, reg = 100, 100, 100
    eliminated_at = None
    
    for i in range(state["round"]):
        if str(i) in team_data["decisions"]:
            choice = team_data["decisions"][str(i)]
            impact = SCENARIOS[i]["options"][choice]
            trst += impact["trst"]
            liq += impact["liq"]
            reg += impact["reg"]
            
            # Próg eliminacji: 20 pkt
            if (trst < 20 or liq < 20 or reg < 20) and eliminated_at is None:
                eliminated_at = i + 1
    
    return trst, liq, reg, eliminated_at

def render_kpi(label, val):
    color = "#238636" if val >= 50 else "#da3633"
    pct = max(0, min(val, 150))
    return f"""
        <div class="kpi-row">
            <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px;">
                <span>{label}</span><span>{val} PKT</span>
            </div>
            <div class="kpi-bg"><div class="kpi-fill" style="width:{pct/1.5}%; background-color:{color};"></div></div>
        </div>
    """

# --- WIDOKI ---
if "role" not in st.session_state:
    st.markdown("<div class='top-bar'><div class='top-bar-title'>FINANCIAL OS // AUTH</div></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        name = st.text_input("KRYPTONIM ZESPOŁU:")
        if st.button("ZALOGUJ"):
            if name == "admin": 
                st.session_state.role = "admin"
            elif name:
                if name not in state["teams"]:
                    state["teams"][name] = {"decisions": {}, "ready": False}
                st.session_state.role = "team"
                st.session_state.team_name = name
            st.rerun()

elif st.session_state.role == "admin":
    st.markdown("<div class='top-bar'><div class='top-bar-title'>ROOT CONTROL PANEL</div></div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"### Runda: {state['round']} / {len(SCENARIOS)}")
        if state["round"] < len(SCENARIOS):
            if st.button("URUCHOM KOLEJNĄ FAZĘ ⏩"):
                state["round"] += 1
                for t in state["teams"]: state["teams"][t]["ready"] = False
                st.rerun()
        else:
            if st.button("RESTART SYSTEMU"):
                st.session_state.state = {"round": 0, "teams": {}, "active_scenario_idx": 0}
                st.rerun()
    
    with c2:
        st.write("### Aktywne zespoły")
        for t, d in state["teams"].items():
            _, _, _, elim = calculate_scores(d)
            status = "❌ WYELIMINOWANY" if elim else ("✅ GOTOWY" if d["ready"] else "⏳ MYŚLI...")
            st.write(f"- {t}: {status}")

elif st.session_state.role == "team":
    team = st.session_state.team_name
    trst, liq, reg, elim = calculate_scores(state["teams"][team])
    
    st.markdown(f"""
        <div class="top-bar">
            <div class="top-bar-title">FINANCIAL OS // {team.upper()}</div>
            {"<div class='status-eliminated'>BANKRUCTWO / ZABLOKOWANY</div>" if elim else ""}
        </div>
    """, unsafe_allow_html=True)

    if elim:
        st.error(f"Zostałeś wyeliminowany w rundzie {elim}. Twoje decyzje doprowadziły do utraty licencji lub płynności.")
        st.info("Oczekuj na ranking końcowy.")
    elif state["round"] == 0:
        st.info("System w trybie gotowości. Oczekiwanie na otwarcie rynków (Runda 1)...")
    elif state["round"] > len(SCENARIOS):
        st.success("Wszystkie fazy zakończone. Sprawdź wynik na ekranie głównym.")
    else:
        curr_idx = state["round"] - 1
        scenario = SCENARIOS[curr_idx]
        
        col_l, col_r = st.columns([1, 2])
        with col_l:
            st.markdown("<div class='cyber-panel'>", unsafe_allow_html=True)
            st.write("### STATUS")
            st.markdown(render_kpi("ZAUFANIE RYNKU", trst), unsafe_allow_html=True)
            st.markdown(render_kpi("PŁYNNOŚĆ (CASH)", liq), unsafe_allow_html=True)
            st.markdown(render_kpi("REGULACJE / KNF", reg), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_r:
            if not state["teams"][team]["ready"]:
                st.markdown(f"### {scenario['name']}")
                st.warning(scenario['desc'])
                with st.form("decision"):
                    choice = st.radio("WYBIERZ REAKCJĘ (4 opcje):", list(scenario["options"].keys()))
                    if st.form_submit_button("POTWIERDŹ ROZKAZ"):
                        state["teams"][team]["decisions"][str(curr_idx)] = choice
                        state["teams"][team]["ready"] = True
                        st.rerun()
            else:
                st.success("Rozkazy przesłane. Oczekiwanie na reakcję rynków...")

# RANKING KOŃCOWY (Widoczny dla wszystkich po zakończeniu rund)
if state["round"] >= len(SCENARIOS):
    st.write("---")
    st.markdown("## 🏆 RAPORT KOŃCOWY KOMISJI NADZORU")
    results = []
    for t_name, t_data in state["teams"].items():
        trst, liq, reg, elim = calculate_scores(t_data)
        total = trst + liq + reg
        status = f"Padł w rundzie {elim}" if elim else "STABILNY"
        results.append({
            "Zespół": t_name,
            "Status": status,
            "Suma Punktów": total if not elim else 0,
            "Zaufanie": trst,
            "Płynność": liq,
            "Zgodność": reg
        })
    
    df = pd.DataFrame(results).sort_values(by="Suma Punktów", ascending=False)
    st.table(df)