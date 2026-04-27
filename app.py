import streamlit as st
import pandas as pd
import base64
import os
import time

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="FINANCIAL OS // COMMAND CENTER",
    layout="wide",
    page_icon="🏦",
    initial_sidebar_state="collapsed"
)

# --- CSS (CYBERPUNK / MISSION CONTROL) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #0b101a !important; color: #a0aec0; font-family: 'Segoe UI', sans-serif; padding-bottom: 50px; }
    
    .top-bar {
        background-color: #060b13; border-bottom: 2px solid #1a2332;
        padding: 15px 30px; display: flex; justify-content: space-between; align-items: center;
        margin-top: -60px; margin-bottom: 30px; font-family: monospace;
    }
    .top-bar-title { color: #00f0ff; font-size: 22px; font-weight: 900; letter-spacing: 2px; }
    .top-bar-alert { background-color: #3b0a0a; color: #ff4d4d; border: 1px solid #ff4d4d; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }

    .cyber-panel { background-color: #121824; border: 1px solid #1e293b; border-radius: 6px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.5); }
    .panel-header { font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 15px; border-bottom: 1px solid #1e293b; padding-bottom: 8px; }

    .kpi-row { margin-bottom: 18px; }
    .kpi-labels { display: flex; justify-content: space-between; font-size: 12px; font-weight: 600; color: #cbd5e1; margin-bottom: 6px; text-transform: uppercase; }
    .kpi-bg { background-color: #1e293b; height: 6px; width: 100%; border-radius: 3px; overflow: hidden; }
    .kpi-fill { height: 100%; background-color: #00f0ff; box-shadow: 0 0 10px #00f0ff80; }
    .kpi-fill.critical { background-color: #ff4d4d; box-shadow: 0 0 10px #ff4d4d80; }

    .log-entry { font-family: monospace; font-size: 12px; margin-bottom: 15px; }
    .log-time { color: #eab308; font-weight: bold; }
    .log-title { color: #f8fafc; font-weight: bold; margin-top: 4px; }
    .log-desc { color: #64748b; font-size: 11px; margin-top: 2px; border-left: 2px solid #334155; padding-left: 8px; }

    .warning-box { background-color: #151a23; border: 1px solid #334155; border-left: 4px solid #00f0ff; padding: 20px; border-radius: 4px; color: #e2e8f0; font-size: 15px; line-height: 1.6; margin-bottom: 30px; }
    
    .status-box { text-align: center; padding: 20px; background-color: #121824; border: 1px solid #1e293b; border-radius: 6px; }
    .stRadio label { background: #1e293b !important; border: 1px solid #334155 !important; color: #f8fafc !important; padding: 12px 16px !important; border-radius: 4px !important; margin-bottom: 8px !important; }
    </style>
""", unsafe_allow_html=True)

# --- BAZA SCENARIUSZY (6 FAZ X 4 ODPOWIEDZI) ---
ALL_SCENARIOS = {
    1: {
        "title": "FAZA 1 - ANOMALIA W SYSTEMIE SWIFT",
        "desc": "Systemy monitoringu wykryły serię nieautoryzowanych przelewów na kwotę 500 mln USD. Wygląda to na atak na gateway SWIFT.",
        "questions": {
            "IT": {"label": "ZESPÓŁ IT / CYBER:", "options": {
                "Natychmiastowe odcięcie gatewaya (Hard Stop)": {"trst": 10, "liq": -30, "reg": 20},
                "Zdalna analiza pakietów bez przerywania sesji": {"trst": -10, "liq": 0, "reg": -15},
                "Izolacja zainfekowanego serwera i reset kluczy": {"trst": 5, "liq": -10, "reg": 10},
                "Uruchomienie procedury Shadow-Audit": {"trst": -5, "liq": -5, "reg": -20}
            }},
            "Dir": {"label": "ZARZĄD / COMPLIANCE:", "options": {
                "Zgłoszenie do KNF i Banków Korespondentów": {"trst": 15, "liq": 0, "reg": 30},
                "Wstrzymanie wszystkich płatności zagranicznych": {"trst": -20, "liq": -40, "reg": 10},
                "Próba wyciszenia incydentu do czasu diagnozy": {"trst": -30, "liq": 0, "reg": -50},
                "Powołanie zewnętrznej firmy Incident Response": {"trst": 10, "liq": -20, "reg": 15}
            }}
        }
    },
    2: {
        "title": "FAZA 2 - WYCIEK DANYCH WEALTH MANAGEMENT",
        "desc": "W darknecie opublikowano dane 500 najbogatszych klientów banku. Klienci zaczynają wycofywać depozyty.",
        "options": {
            "Pełna transparentność i infolinia 24/7": {"trst": 30, "liq": -15, "reg": 25},
            "Cicha wymiana tokenów i kart bez ogłoszenia wycieku": {"trst": -20, "liq": -10, "reg": -40},
            "Blokada kont VIP ze względów bezpieczeństwa": {"trst": -30, "liq": -20, "reg": 10},
            "Kampania PR o 'rzekomych' atakach na konkurencję": {"trst": -50, "liq": 0, "reg": -60}
        }
    },
    3: {
        "title": "FAZA 3 - FLASH CRASH (ALGO-TRADING)",
        "desc": "Wasz algorytm HFT wpadł w pętlę i wyprzedaje obligacje skarbowe po zaniżonej cenie. Rynek panikuje.",
        "options": {
            "Awaryjny Kill-Switch wszystkich algorytmów": {"trst": -10, "liq": -40, "reg": 20},
            "Ręczne zlecenia kupna w celu stabilizacji kursu": {"trst": 10, "liq": -50, "reg": -10},
            "Zgłoszenie błędu technicznego do Giełdy": {"trst": 15, "liq": 0, "reg": 20},
            "Zignorowanie błędu, liczenie na autokorektę rynku": {"trst": -60, "liq": -30, "reg": -70}
        }
    },
    4: {
        "title": "FAZA 4 - RUN NA BANK (KRYZYS PŁYNNOŚCI)",
        "desc": "Przed oddziałami ustawiają się kolejki. Bankomaty są pustoszone. Płynność drastycznie spada.",
        "options": {
            "Pożyczka płynnościowa z Banku Centralnego (LOLA)": {"trst": -10, "liq": 60, "reg": 15},
            "Ograniczenie dziennych limitów wypłat do 1000 PLN": {"trst": -80, "liq": 40, "reg": -20},
            "Publiczne wystąpienie Prezesa w mediach": {"trst": 25, "liq": -5, "reg": 0},
            "Wyprzedaż aktywów trwałych banku (Fire Sale)": {"trst": 0, "liq": 35, "reg": -10}
        }
    },
    5: {
        "title": "FAZA 5 - RANSOMWARE W KSIĘDZE GŁÓWNEJ",
        "desc": "Zaszyfrowano bazę rozliczeniową. Hakerzy żądają 10 mln EUR. Nie możecie zamknąć dnia operacyjnego.",
        "options": {
            "Odtwarzanie z backupów sprzed 12h": {"trst": -10, "liq": -15, "reg": 0},
            "Przejście na rozliczenia papierowe": {"trst": -5, "liq": -30, "reg": 30},
            "Zapłata okupu w celu odzyskania danych": {"trst": -50, "liq": -60, "reg": -100},
            "Zawiadomienie regulatora o przerwaniu ciągłości": {"trst": -20, "liq": 0, "reg": 20}
        }
    },
    6: {
        "title": "FAZA 6 - SABOTAŻ WEWNĘTRZNY",
        "desc": "Audyt wykrył ukrytą stratę 4 mld PLN. Szpital finansowy stoi na progu bankructwa.",
        "options": {
            "Wniosek o dokapitalizowanie od akcjonariuszy": {"trst": 20, "liq": 40, "reg": 10},
            "Próba kreatywnego księgowania straty": {"trst": -40, "liq": -10, "reg": -90},
            "Fuzja awaryjna z większym podmiotem": {"trst": -20, "liq": 50, "reg": 0},
            "Pełna współpraca z prokuraturą i odpis strat": {"trst": -15, "liq": -60, "reg": 40}
        }
    }
}

# --- STAN GRY ---
if "state" not in st.session_state:
    st.session_state.state = {"round": 0, "teams": {}}

state = st.session_state.state

def calculate_score(team_name):
    t_data = state["teams"][team_name]
    trst, liq, reg = 100, 100, 100
    elim_at = None
    for r in range(1, state["round"] + 1):
        if str(r) in t_data["decisions"]:
            for role, choice in t_data["decisions"][str(r)].items():
                impact = ALL_SCENARIOS[r]["questions" if role=="IT" else "options" if role=="Dir" else "questions"][role]["options"][choice]
                trst += impact["trst"]; liq += impact["liq"]; reg += impact["reg"]
            if (trst < 20 or liq < 20 or reg < 20) and elim_at is None:
                elim_at = r
    return max(0, trst), max(0, liq), max(0, reg), elim_at

def render_cyber_kpi(label, value):
    pct = int(min((value/150)*100, 100))
    cls = "kpi-fill critical" if value < 40 else "kpi-fill"
    return f"""<div class="kpi-row"><div class="kpi-labels"><span>{label}</span><span>{value} pkt</span></div><div class="kpi-bg"><div class="{cls}" style="width: {pct}%;"></div></div></div>"""

# --- ROUTER ---
if "role" not in st.session_state:
    # --- LOGOWANIE ---
    st.markdown("<div class='top-bar'><div class='top-bar-title'>FINANCIAL OS // AUTH</div></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div class='cyber-panel'>", unsafe_allow_html=True)
        tid = st.text_input("ID ZESPOŁU (ROOT dla admina):").strip()
        if st.button("LOG_IN", use_container_width=True):
            if tid.upper() == "ROOT": st.session_state.role = "admin"
            elif tid:
                if tid not in state["teams"]: state["teams"][tid] = {"decisions": {}, "ready": False}
                st.session_state.role, st.session_state.team_name = "team", tid
            st.rerun()

elif st.session_state.role == "admin":
    # --- ADMIN VIEW ---
    st.sidebar.button("LOGOUT", on_click=lambda: st.session_state.clear())
    st.markdown(f"<div class='top-bar'><div class='top-bar-title'>ROOT CONTROL // RUNDA {state['round']}</div></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.write("### STEROWANIE")
        if state["round"] < 6:
            if st.button("NASTĘPNA RUNDA ⏩"):
                state["round"] += 1
                for t in state["teams"]: state["teams"][t]["ready"] = False
                st.rerun()
        if st.button("RESET GRY 🔄"):
            state["round"] = 0; state["teams"] = {}; st.rerun()
    with c2:
        st.write("### STATUS ZESPOŁÓW")
        for t, d in state["teams"].items():
            _, _, _, elim = calculate_score(t)
            st.write(f"{'🔴' if elim else '🟢'} {t}: {'ZBANKRUTOWAŁ' if elim else ('GOTOWY' if d['ready'] else 'ANALIZA')}")
    
    # RANKING ADMINA
    if state["teams"]:
        st.write("---")
        results = []
        for t in state["teams"]:
            tr, li, re, elim = calculate_score(t)
            results.append({"Drużyna": t, "Zaufanie": tr, "Płynność": li, "Zgodność": re, "Suma": (tr+li+re) if not elim else 0, "Elim": elim})
        df = pd.DataFrame(results)
        if "Suma" in df.columns: st.dataframe(df.sort_values(by="Suma", ascending=False), use_container_width=True)

elif st.session_state.role == "team":
    # --- TEAM VIEW ---
    team = st.session_state.team_name
    tr, li, re, elim = calculate_score(team)
    st.markdown(f"<div class='top-bar'><div class='top-bar-title'>{team.upper()}</div></div>", unsafe_allow_html=True)
    
    col_l, col_c, col_r = st.columns([1.2, 2.8, 1.2], gap="large")
    
    with col_l:
        st.markdown("<div class='cyber-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-header'>METRYKI BANKOWE</div>", unsafe_allow_html=True)
        st.markdown(render_cyber_kpi("ZAUFANIE", tr), unsafe_allow_html=True)
        st.markdown(render_cyber_kpi("PŁYNNOŚĆ", li), unsafe_allow_html=True)
        st.markdown(render_cyber_kpi("ZGODNOŚĆ", re), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='cyber-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-header'>LOGI SESJI</div>", unsafe_allow_html=True)
        for i in range(1, state["round"] + 1):
            st.markdown(f"<div class='log-entry'><span class='log-time'>[R{i}]</span> FAZA ZAKOŃCZONA</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_c:
        if elim:
            st.error(f"INSTYTUCJA UPADŁA W RUNDZIE {elim}")
            st.markdown("<div class='warning-box'>Twoja licencja bankowa została cofnięta przez KNF ze względu na utratę płynności lub zaufania rynkowego.</div>", unsafe_allow_html=True)
        elif state["round"] == 0:
            st.info("OCZEKIWANIE NA START...")
            time.sleep(2); st.rerun()
        else:
            r = state["round"]
            scen = ALL_SCENARIOS[r]
            st.markdown(f"### {scen['title']}")
            st.markdown(f"<div class='warning-box'>{scen['desc']}</div>", unsafe_allow_html=True)
            
            if not state["teams"][team]["ready"]:
                with st.form(f"f{r}"):
                    choices = {}
                    for role, q in scen.get("questions", {}).items():
                        st.write(f"**{q['label']}**")
                        choices[role] = st.radio("Wybierz:", list(q["options"].keys()), label_visibility="collapsed")
                    
                    # Obsługa scenariuszy bez ról (wszystkie 4 opcje jako jedna grupa)
                    if "questions" not in scen:
                        st.write("**DECYZJA ZARZĄDU:**")
                        choices["Dir"] = st.radio("Wybierz:", list(scen["options"].keys()), label_visibility="collapsed")
                    
                    if st.form_submit_button("WDROŻYĆ PROCEDURĘ 📝"):
                        state["teams"][team]["decisions"][str(r)] = choices
                        state["teams"][team]["ready"] = True
                        st.rerun()
            else:
                st.success("PROCEDURA W TOKU. CZEKAJ...")
                time.sleep(3); st.rerun()

    with col_r:
        st.markdown("<div class='status-box'>", unsafe_allow_html=True)
        if elim: st.write("🏁 KONIEC")
        elif state["teams"][team]["ready"]: st.write("✅ WYŚŁANO")
        else: st.write("⚠️ AKCJA")
        st.markdown("</div>", unsafe_allow_html=True)

# RANKING KOŃCOWY (NA DOLE DLA WSZYSTKICH)
if state["round"] == 6 and all(d["ready"] for d in state["teams"].values()):
    st.markdown("---")
    st.markdown("## 🏆 FINALNY RAPORT KOMISJI NADZORU")
    final_data = []
    for t_name in state["teams"]:
        tr, li, re, elim = calculate_score(t_name)
        final_data.append({"DRUŻYNA": t_name, "SUMA": (tr+li+re) if not elim else 0, "STATUS": "STABILNY" if not elim else f"BANKRUT (R{elim})"})
    f_df = pd.DataFrame(final_data)
    if not f_df.empty: st.table(f_df.sort_values(by="SUMA", ascending=False))
