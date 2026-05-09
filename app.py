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

# --- SCENARIOS DATABASE ---
# Format metryk: trust (zaufanie), liq (płynność), cap (kapitał), comp (zgodność)

FULL_SCENARIOS = {
    0: {
        "name": "I: Atak Ransomware",
        "rounds": {
            1: {
                "title": "FAZA 1: PIERWSZE SZYFROWANIE",
                "desc": "Wykryto drastyczne obciążenie procesorów na stacjach w dziale obsługi klienta. Pojawiają się pierwsze zgłoszenia o samoczynnej zmianie rozszerzeń plików. Rozpoczyna się proces szyfrowania.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Natychmiastowe odłączenie całej podsieci biurowej (Blackout)": {"trust": -5, "liq": -10, "cap": 0, "comp": +10},
                        "Próba wyśledzenia procesów i punktowej blokady stacji": {"trust": 0, "liq": +5, "cap": -10, "comp": -5}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Wstrzymanie obsługi klienta w oddziałach dotkniętych awarią": {"trust": -10, "liq": -5, "cap": 0, "comp": +5},
                        "Przejście na dokumentację papierową dla operacji kasowych": {"trust": +5, "liq": -10, "cap": -5, "comp": 0}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Cisza medialna do czasu poznania skali ataku": {"trust": 0, "liq": 0, "cap": 0, "comp": -10},
                        "Poufne zgłoszenie incydentu do KNF / KSC": {"trust": 0, "liq": 0, "cap": 0, "comp": +20}
                    }}
                }
            },
            2: {
                "title": "FAZA 2: ŻĄDANIE OKUPU",
                "desc": "Ekrany zostają zablokowane czerwoną planszą. Żądanie okupu wynosi 15 milionów dolarów w kryptowalutach. Atakujący grożą usunięciem kluczy deszyfrujących w ciągu 24 godzin.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Fizyczne wyłączenie serwerów centralnych dla ochrony rdzenia": {"trust": -20, "liq": -30, "cap": 0, "comp": +15},
                        "Utrzymanie serwerów online i skanowanie w poszukiwaniu backdoorów": {"trust": -10, "liq": +10, "cap": -20, "comp": -10}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Przekierowanie logistyki bankomatów na tryb awaryjny (limity)": {"trust": -15, "liq": +20, "cap": 0, "comp": 0},
                        "Zamknięcie systemów bankowości mobilnej na czas analizy": {"trust": -30, "liq": -20, "cap": 0, "comp": +10}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Rozpoczęcie cichych negocjacji z hakerami w celu kupna czasu": {"trust": -5, "liq": 0, "cap": -25, "comp": -20},
                        "Powołanie sztabu z zewnętrzną firmą Incident Response (koszty)": {"trust": +10, "liq": 0, "cap": -15, "comp": +10}
                    }}
                }
            },
            3: {
                "title": "FAZA 3: RYZYKO WYCIEKU BAZY",
                "desc": "Złośliwe oprogramowanie dotarło do magazynów backupów. Media społecznościowe zalewa fala spekulacji. Atakujący grożą upublicznieniem bazy kredytowej na Dark Webie.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Odcięcie magazynów taśmowych offline (zaprzestanie ratowania online)": {"trust": 0, "liq": -10, "cap": 0, "comp": +20},
                        "Uruchomienie deszyfratorów open-source (ryzyko korupcji plików)": {"trust": -15, "liq": +15, "cap": -10, "comp": -15}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Całkowite wstrzymanie księgowania przelewów wychodzących": {"trust": -25, "liq": +10, "cap": 0, "comp": +5},
                        "Autoryzacja tylko kluczowych transakcji korporacyjnych": {"trust": -10, "liq": -10, "cap": 0, "comp": 0}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Wydanie oficjalnego komunikatu o 'awarii technicznej' (zatajenie)": {"trust": -30, "liq": +5, "cap": 0, "comp": -40},
                        "Transparentne przyznanie się do ataku hakerskiego": {"trust": +20, "liq": -10, "cap": -5, "comp": +25}
                    }}
                }
            },
            4: {
                "title": "FAZA 4: IMPAS OPERACYJNY",
                "desc": "Przez opóźnienia, klienci masowo szturmują oddziały żądając wypłat gotówki (Bank Run na małą skalę). Zaczyna brakować płynności w kasach.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Zaakceptowanie utraty logów z ostatnich 24h i postawienie starych baz": {"trust": -20, "liq": +15, "cap": -10, "comp": -20},
                        "Mozolne, chirurgiczne czyszczenie logów (długi przestój)": {"trust": +10, "liq": -25, "cap": -5, "comp": +15}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Awaryjne ściągnięcie gotówki z NBP / rezerw międzybankowych": {"trust": +15, "liq": -30, "cap": -10, "comp": 0},
                        "Wprowadzenie rygorystycznych limitów wypłat w oddziałach": {"trust": -40, "liq": +25, "cap": 0, "comp": -10}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Zgłoszenie masowego naruszenia danych RODO do UODO": {"trust": 0, "liq": 0, "cap": -10, "comp": +35},
                        "Próba wykupienia polisy ubezpieczeniowej cyber w trakcie kryzysu": {"trust": 0, "liq": 0, "cap": -20, "comp": -15}
                    }}
                }
            },
            5: {
                "title": "FAZA 5: ODBUDOWA",
                "desc": "Zasadniczy wektor ataku opanowany. Zarząd i akcjonariusze oczekują raportu końcowego oraz wdrożenia strategii pokontrolnej.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Wdrożenie infrastruktury Immutable Backups (wysoki koszt)": {"trust": +10, "liq": 0, "cap": -25, "comp": +20},
                        "Pozostanie przy obecnej architekturze z nowym antywirusem": {"trust": -15, "liq": 0, "cap": +15, "comp": -20}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Pełny, wielotygodniowy audyt wszystkich kont klientów detalicznych": {"trust": +20, "liq": -15, "cap": -10, "comp": +10},
                        "Zignorowanie anomalii mikropłatności, szybki powrót do normy": {"trust": -20, "liq": +15, "cap": 0, "comp": -15}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Dymisja CIO/CISO celem uspokojenia rynków i inwestorów": {"trust": +15, "liq": +10, "cap": 0, "comp": 0},
                        "Obrona zespołu IT i wzięcie odpowiedzialności przez cały Zarząd": {"trust": -10, "liq": -5, "cap": 0, "comp": +10}
                    }}
                }
            }
        }
    },
    1: {
        "name": "II: Insider Threat",
        "rounds": {
            1: {
                "title": "FAZA 1: NIEAUTORYZOWANY EKSKPORT",
                "desc": "Systemy DLP (Data Loss Prevention) odnotowują masowe pobieranie danych analitycznych i portfeli VIP na zewnętrzny, nieszyfrowany dysk w nocy.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Zablokowanie podejrzanego konta i konfiskata sprzętu": {"trust": +5, "liq": 0, "cap": 0, "comp": +15},
                        "Cicha inwigilacja użytkownika celem zebrania dowodów": {"trust": -10, "liq": 0, "cap": 0, "comp": -10}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Natychmiastowy reset haseł dla wszystkich kont klienckich z pobranej puli": {"trust": +10, "liq": -15, "cap": -5, "comp": +10},
                        "Brak działań wobec klientów do czasu potwierdzenia wycieku": {"trust": -15, "liq": +5, "cap": 0, "comp": -15}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Zawiadomienie prokuratury o podejrzeniu szpiegostwa przemysłowego": {"trust": 0, "liq": 0, "cap": 0, "comp": +25},
                        "Skierowanie sprawy wyłącznie do wewnętrznego działu HR": {"trust": 0, "liq": 0, "cap": 0, "comp": -20}
                    }}
                }
            },
            2: {
                "title": "FAZA 2: ODKRYCIE SPRAWCY",
                "desc": "Logowania pochodzą z konta zwolnionego w ubiegłym tygodniu architekta baz danych. Nikt z IT nie zablokował jego wirtualnego profilu VPN (błąd procedur).",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Rewokacja wszystkich certyfikatów VPN dla całego banku (szok operacyjny)": {"trust": -5, "liq": -25, "cap": 0, "comp": +15},
                        "Usunięcie tylko konta sprawcy i ukrycie logów audytu przed audytorem": {"trust": -30, "liq": +10, "cap": 0, "comp": -40}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Tymczasowe zablokowanie operacji zagranicznych dla klientów z listy": {"trust": -20, "liq": -10, "cap": 0, "comp": +5},
                        "Tylko wzmożony monitoring manualny transakcji": {"trust": +5, "liq": -10, "cap": 0, "comp": -5}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Zawieszenie szefa IT i HR do czasu wyjaśnienia luk proceduralnych": {"trust": +10, "liq": 0, "cap": 0, "comp": +10},
                        "Brak decyzji personalnych, zamiatanie pod dywan": {"trust": -20, "liq": 0, "cap": 0, "comp": -20}
                    }}
                }
            },
            3: {
                "title": "FAZA 3: SZANTAŻ",
                "desc": "Były pracownik kontaktuje się z zarządem. Szantażuje bank: sprzeda bazę VIP konkurencji lub na czarny rynek, jeśli nie otrzyma 5 milionów PLN 'odprawy'.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Wynajęcie hakerów (Red Team) do namierzenia i skasowania dysku szantażysty": {"trust": -20, "liq": 0, "cap": -15, "comp": -40},
                        "Zabezpieczanie logów jako dowodów dla Policji (działanie pasywne)": {"trust": +5, "liq": 0, "cap": 0, "comp": +15}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Przygotowanie rezerw na ewentualne procesy z klientami VIP": {"trust": 0, "liq": -20, "cap": -20, "comp": +10},
                        "Zignorowanie ryzyka procesowego, ochrona płynności": {"trust": -15, "liq": +20, "cap": +10, "comp": -20}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Wypłata okupu pod przykrywką umowy NDA (złamaniem prawa)": {"trust": -40, "liq": 0, "cap": -30, "comp": -50},
                        "Zdecydowana odmowa i pełna współpraca z organami ścigania": {"trust": +15, "liq": 0, "cap": 0, "comp": +30}
                    }}
                }
            },
            4: {
                "title": "FAZA 4: MEDIA I PANIKA",
                "desc": "Dziennikarz śledczy kontaktuje się z biurem prasowym. Twierdzi, że otrzymał 'próbkę' plików bankowych od anonimowego sygnalisty.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Analiza przesłanych próbek w odizolowanym środowisku (sandbox)": {"trust": +5, "liq": 0, "cap": 0, "comp": +10},
                        "Odpowiedź do dziennikarza z plikiem infekującym jego komputer": {"trust": -50, "liq": 0, "cap": 0, "comp": -60}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Wstrzymanie akwizycji nowych klientów biznesowych": {"trust": -15, "liq": -15, "cap": 0, "comp": 0},
                        "Normalne kontynuowanie sprzedaży i kampanii marketingowych": {"trust": +5, "liq": +10, "cap": 0, "comp": -10}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Nałożenie sądowego zakazu publikacji (tzw. gag order)": {"trust": -25, "liq": 0, "cap": -10, "comp": -15},
                        "Otwarte oświadczenie: Byliśmy ofiarą kradzieży, chronimy klientów": {"trust": +25, "liq": 0, "cap": 0, "comp": +15}
                    }}
                }
            },
            5: {
                "title": "FAZA 5: POST-MORTEM (KONTROLA)",
                "desc": "Sytuacja eskaluje prawnie. Prokuratura i UODO żądają wydania nośników serwerowych jako dowodów, co grozi wyłączeniem bankowości internetowej.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Zestawienie zapasowego data center i oddanie serwerów Policji": {"trust": +10, "liq": -25, "cap": -20, "comp": +25},
                        "Odmowa wydania fizycznego sprzętu, przekazanie tylko cyfrowych kopii": {"trust": -15, "liq": +20, "cap": 0, "comp": -20}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Restrykcyjne zaostrzenie dostępu do danych (spadek wydajności pracy)": {"trust": +15, "liq": -15, "cap": 0, "comp": +15},
                        "Powrót do starych metod by nie frustrować pracowników": {"trust": -20, "liq": +10, "cap": 0, "comp": -20}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Uruchomienie funduszu rekompensat dla poszkodowanych VIP-ów": {"trust": +30, "liq": 0, "cap": -30, "comp": +10},
                        "Brak rekompensat, zmuszenie klientów do procesów sądowych": {"trust": -30, "liq": 0, "cap": +20, "comp": -25}
                    }}
                }
            }
        }
    },
    2: {
        "name": "III: Supply Chain Sabotage",
        "rounds": {
            1: {
                "title": "FAZA 1: AKTUALIZACJA VENDORA",
                "desc": "Dostawca zewnętrznego systemu księgowego (Vendor) wgrywa aktualizację. SOC wykrywa nietypowe zapytania wychodzące z serwera aplikacji do dziwnych domen.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Blokada komunikacji serwera aplikacji na zewnątrz (ruch wychodzący)": {"trust": 0, "liq": -10, "cap": 0, "comp": +10},
                        "Tylko wzmożony monitoring, czekanie na odpowiedź supportu": {"trust": -15, "liq": +5, "cap": 0, "comp": -10}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Wstrzymanie księgowań paczek przelewów (Elixir/Express)": {"trust": -15, "liq": -15, "cap": 0, "comp": +5},
                        "Kontynuacja księgowań przy użyciu zaktualizowanego systemu": {"trust": +5, "liq": +10, "cap": 0, "comp": -20}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Oficjalna eskalacja problemu do Zarządu Vendora": {"trust": 0, "liq": 0, "cap": 0, "comp": +10},
                        "Traktowanie incydentu jako rutynowego błędu IT": {"trust": -10, "liq": 0, "cap": 0, "comp": -15}
                    }}
                }
            },
            2: {
                "title": "FAZA 2: INFEKCJA POTWIERDZONA",
                "desc": "Infrastruktura dostawcy została przejęta (APT). Przez zaufany kanał do banku wpuszczono backdoora. Klienci zgłaszają, że salda na ich kontach się nie zgadzają.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Air-gap (fizyczne odłączenie) całej strefy DMZ banku": {"trust": -10, "liq": -35, "cap": 0, "comp": +20},
                        "Próba wyizolowania złośliwego kodu na żywym organizmie": {"trust": -25, "liq": +10, "cap": 0, "comp": -15}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Przejście na awaryjną, ręczną weryfikację sald korporacyjnych": {"trust": +15, "liq": -25, "cap": -10, "comp": +10},
                        "Poleganie na systemach anty-fraudowych bez zmian": {"trust": -30, "liq": +15, "cap": 0, "comp": -20}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Natychmiastowe zgłoszenie incydentu krytycznego do KNF": {"trust": +5, "liq": 0, "cap": 0, "comp": +30},
                        "Opóźnianie zgłoszenia, czekanie na oficjalne pismo od Vendora": {"trust": -20, "liq": 0, "cap": 0, "comp": -30}
                    }}
                }
            },
            3: {
                "title": "FAZA 3: UTRATA DOSTAWCY",
                "desc": "Vendor oficjalnie ogłasza upadek swoich systemów. Bank traci kluczowe oprogramowanie analityczne i operacyjne, stając przed wizją manualnego zarządzania setkami tysięcy kont.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Agresywne formatowanie i reinstalacja systemów księgowych z czystych kopii": {"trust": 0, "liq": -20, "cap": -10, "comp": +15},
                        "Próba załatania złośliwego oprogramowania Vendora siłami własnych devów": {"trust": -20, "liq": +10, "cap": 0, "comp": -25}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Zamrożenie wszystkich kont podejrzanych o anomalię (złość klientów)": {"trust": -25, "liq": +5, "cap": 0, "comp": +10},
                        "Uruchomienie nielimitowanych debetów awaryjnych dla stałych klientów": {"trust": +20, "liq": -30, "cap": -20, "comp": -10}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Wydanie oświadczenia uderzającego w Vendora ('To nie nasza wina')": {"trust": -15, "liq": 0, "cap": 0, "comp": -15},
                        "Wzięcie odpowiedzialności za ciągłość usług własnego banku": {"trust": +25, "liq": 0, "cap": 0, "comp": +15}
                    }}
                }
            },
            4: {
                "title": "FAZA 4: ANALIZA STRAT",
                "desc": "Czas na inwentaryzację szkód. Zewnętrzni audytorzy sprawdzają, czy przez backdoora nie wyprowadzono środków na konta zagraniczne. Systemy działają wolno.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Rozwiązanie umowy z Vendorem i budowa rozwiązania in-house (ogromne koszty)": {"trust": +10, "liq": 0, "cap": -40, "comp": +15},
                        "Czekanie na bezpieczną łatkę od Vendora (paraliż tygodniami)": {"trust": -25, "liq": -15, "cap": +15, "comp": -20}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Ręczna rekoncyliacja 100% logów finansowych (zatrzymanie innych projektów)": {"trust": +20, "liq": -15, "cap": -10, "comp": +25},
                        "Użycie algorytmów estymujących by przyspieszyć proces": {"trust": -20, "liq": +15, "cap": 0, "comp": -25}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Przygotowanie pozwów sądowych przeciwko Vendorowi": {"trust": +5, "liq": 0, "cap": -5, "comp": +10},
                        "Próba wymuszenia na Vendorze darmowych usług w ramach ugody": {"trust": -5, "liq": +10, "cap": +10, "comp": -5}
                    }}
                }
            },
            5: {
                "title": "FAZA 5: NOWY ŁAŃCUCH DOSTAW",
                "desc": "Wymagane jest strategiczne przegrupowanie modelu bezpieczeństwa dla wszystkich zewnętrznych dostawców banku.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Wdrożenie architektury Zero Trust dla wszystkich integracji API": {"trust": +15, "liq": 0, "cap": -25, "comp": +30},
                        "Brak zmian strukturalnych, uznanie tego za 'wypadek przy pracy'": {"trust": -30, "liq": 0, "cap": +10, "comp": -40}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Powołanie drogiego zespołu Vendor Risk Management (DORA / NIS2)": {"trust": +10, "liq": 0, "cap": -20, "comp": +25},
                        "Pozostawienie weryfikacji dostawców działowi zakupów": {"trust": -20, "liq": 0, "cap": +15, "comp": -30}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Dywersyfikacja dostawców IT (multi-vendor strategy)": {"trust": +15, "liq": 0, "cap": -20, "comp": +15},
                        "Monopolizacja IT u jednego 'najtańszego' giganta technologicznego": {"trust": -15, "liq": 0, "cap": +20, "comp": -20}
                    }}
                }
            }
        }
    },
    3: {
        "name": "IV: Phishing Masowy",
        "rounds": {
            1: {
                "title": "FAZA 1: ZŁOŚLIWY ZAŁĄCZNIK",
                "desc": "Setki pracowników otwiera maila wyglądającego jak pismo z HR ('Tabela podwyżek inflacyjnych'). Oprogramowanie Stealer instaluje się w tle na stacjach bankowych.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Natychmiastowa blokada ruchu pocztowego w całym banku": {"trust": 0, "liq": -15, "cap": 0, "comp": +10},
                        "Ciche skryptowe usuwanie złośliwych maili ze skrzynek (część przetrwa)": {"trust": -10, "liq": +5, "cap": 0, "comp": -5}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Rozesłanie alertów SMS do pracowników i wymuszenie wylogowań": {"trust": +5, "liq": -10, "cap": -5, "comp": +10},
                        "Zignorowanie ryzyka na rzecz ciągłości działania oddziałów": {"trust": -20, "liq": +10, "cap": 0, "comp": -15}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Oficjalny komunikat: To atak phishingowy, sprawdzamy skutki": {"trust": +10, "liq": 0, "cap": 0, "comp": +5},
                        "Ukrywanie faktu naiwności personelu przed mediami": {"trust": -15, "liq": 0, "cap": 0, "comp": -10}
                    }}
                }
            },
            2: {
                "title": "FAZA 2: PRZEJĘCIE KONT",
                "desc": "Złośliwa witryna przechwytuje loginy. Intruzi logują się do wewnętrznego systemu intranetu banku, omijając słabe mechanizmy uwierzytelniania.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Globalny, natychmiastowy reset haseł dla 100% personelu (chaos)": {"trust": +5, "liq": -25, "cap": 0, "comp": +15},
                        "Monitorowanie i wybiórcze blokowanie dziwnych logowań": {"trust": -20, "liq": +10, "cap": 0, "comp": -20}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Ręczna weryfikacja wszystkich faktur kosztowych banku": {"trust": +10, "liq": -15, "cap": -5, "comp": +10},
                        "Utrzymanie automatycznego autoryzowania płatności": {"trust": -30, "liq": +15, "cap": 0, "comp": -25}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Ostrzeżenie kluczowych partnerów biznesowych o możliwych fałszywkach": {"trust": +15, "liq": 0, "cap": 0, "comp": +10},
                        "Brak komunikacji na zewnątrz w obawie przed kompromitacją": {"trust": -25, "liq": 0, "cap": 0, "comp": -20}
                    }}
                }
            },
            3: {
                "title": "FAZA 3: BUSINESS EMAIL COMPROMISE",
                "desc": "Z przejętych skrzynek wysyłane są sfałszowane dyspozycje do dużych klientów korporacyjnych o zmianie numerów rachunków. Rozpoczyna się masowe wyłudzanie środków.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Wyłączenie serwerów Exchange / Office365 dla całego banku": {"trust": -10, "liq": -30, "cap": 0, "comp": +20},
                        "Próba ustawienia reguł kwarantanny dla wychodzących maili": {"trust": -15, "liq": -5, "cap": 0, "comp": -10}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Dzwonienie do każdego klienta korporacyjnego z ostrzeżeniem (paraliż)": {"trust": +25, "liq": -20, "cap": -10, "comp": +15},
                        "Ograniczenie się do wysłania masowego, automatycznego maila ostrzegawczego": {"trust": -20, "liq": +5, "cap": 0, "comp": -15}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Zgłoszenie incydentu na infolinię CERT oraz Policję": {"trust": +5, "liq": 0, "cap": 0, "comp": +20},
                        "Blokowanie informacji w celu ochrony kursu akcji": {"trust": -30, "liq": 0, "cap": +10, "comp": -35}
                    }}
                }
            },
            4: {
                "title": "FAZA 4: REKLAMACJE KLIENTÓW",
                "desc": "Klienci wykonali przelewy na konta oszustów i żądają zwrotu skradzionych milionów. Argumentują to rażącym brakiem bezpieczeństwa ze strony banku.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Udostępnienie organom ścigania i klientom pełnych logów (transparentność)": {"trust": +15, "liq": 0, "cap": 0, "comp": +25},
                        "Manipulacja logami w celu zrzucenia winy na systemy pocztowe klientów": {"trust": -50, "liq": 0, "cap": -20, "comp": -60}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Zawiązanie potężnych rezerw finansowych na poczet spraw sądowych": {"trust": 0, "liq": -20, "cap": -30, "comp": +10},
                        "Odmowa uznania reklamacji i odesłanie klientów do sądu": {"trust": -40, "liq": +20, "cap": +20, "comp": -30}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Dobrowolne rekompensaty dla oszukanych (ratowanie wizerunku)": {"trust": +40, "liq": 0, "cap": -40, "comp": +5},
                        "Twarda obrona prawna: 'To wy nie zachowaliście ostrożności'": {"trust": -40, "liq": 0, "cap": +30, "comp": -20}
                    }}
                }
            },
            5: {
                "title": "FAZA 5: HIGIENA CYFROWA",
                "desc": "Naiwność personelu obnażyła słabości kultury organizacyjnej. Nadzór wymusza plan naprawczy.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Wymuszenie sprzętowych kluczy FIDO2 / U2F (ogromny wydatek)": {"trust": +20, "liq": 0, "cap": -30, "comp": +30},
                        "Pozostawienie haseł domenowych bez sprzętowego MFA": {"trust": -30, "liq": 0, "cap": +15, "comp": -40}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Comiesięczne, agresywne kampanie phishingowe przeciwko pracownikom": {"trust": +10, "liq": -10, "cap": -5, "comp": +15},
                        "Jednorazowe szkolenie e-learningowe (tanie)": {"trust": -20, "liq": +5, "cap": +10, "comp": -25}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Zwolnienie dyscyplinarne pracowników, którzy kliknęli (zastraszenie)": {"trust": -20, "liq": 0, "cap": 0, "comp": -10},
                        "Budowa kultury zgłaszania błędów (Brak kar za przyznanie się)": {"trust": +20, "liq": 0, "cap": -5, "comp": +15}
                    }}
                }
            }
        }
    },
    4: {
        "name": "V: Atak na SWIFT",
        "rounds": {
            1: {
                "title": "FAZA 1: ANOMALIE WALUTOWE",
                "desc": "Autoryzowano trzy wielomilionowe transfery SWIFT do rajów podatkowych bez zlecenia klienta. Wskaźniki rezerw walutowych alarmują o potężnym odpływie.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Fizyczne wyjęcie kabli z terminali SWIFT (Air-Gap)": {"trust": 0, "liq": -30, "cap": 0, "comp": +15},
                        "Zdalna analiza i próba zablokowania portów logicznych": {"trust": -15, "liq": -5, "cap": 0, "comp": -10}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Całkowite wstrzymanie międzynarodowych rozliczeń dla klientów (panika)": {"trust": -20, "liq": -20, "cap": 0, "comp": +10},
                        "Autoryzacja manualna 4-eyes dla każdego przelewu SWIFT": {"trust": +10, "liq": -15, "cap": -5, "comp": +5}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Natychmiastowe powiadomienie banków korespondentów w USA/UE": {"trust": +15, "liq": 0, "cap": 0, "comp": +25},
                        "Zatajenie wycieku do czasu ustalenia źródła wektora": {"trust": -30, "liq": 0, "cap": 0, "comp": -35}
                    }}
                }
            },
            2: {
                "title": "FAZA 2: ZACIERANIE ŚLADÓW",
                "desc": "Złośliwy kod nadpisuje logi w bazie Oracle. Raporty dla dyrekcji i księgowości generują sztuczne, fałszywie dodatnie salda. Pieniądze wciąż znikają.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Zrzut pamięci RAM (forensic dump) i całkowity restart infrastruktury": {"trust": +5, "liq": -25, "cap": -10, "comp": +20},
                        "Wykorzystanie starych logów, ignorowanie bieżącej aktywności bazy": {"trust": -25, "liq": +10, "cap": 0, "comp": -25}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Zamrożenie operacji walutowych na rynku Forex": {"trust": -10, "liq": -15, "cap": -20, "comp": +10},
                        "Zignorowanie błędu sald i poleganie na fałszywych raportach": {"trust": -40, "liq": +20, "cap": 0, "comp": -30}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Powiadomienie KNF i NBP o utracie integralności księgi głównej": {"trust": +5, "liq": 0, "cap": 0, "comp": +40},
                        "Fałszowanie raportów przed nadzorem by uniknąć paniki": {"trust": -50, "liq": 0, "cap": 0, "comp": -60}
                    }}
                }
            },
            3: {
                "title": "FAZA 3: MIĘDZYNARODOWY KRYZYS",
                "desc": "Służby Interpolu blokują niektóre zagraniczne konta banku. Operacje zagraniczne zostają formalnie zamrożone na globalnym rynku.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Pełne otwarcie systemów dla śledczych Interpolu (oddanie kontroli)": {"trust": +15, "liq": 0, "cap": 0, "comp": +30},
                        "Ograniczanie dostępu, maskowanie własnej niekompetencji IT": {"trust": -30, "liq": 0, "cap": 0, "comp": -40}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Gorączkowe, manualne próby cofnięcia zagranicznych przelewów MT103": {"trust": +10, "liq": -10, "cap": -5, "comp": +10},
                        "Uznanie straconych środków za nieściągalne i zamknięcie tematu": {"trust": -20, "liq": 0, "cap": -30, "comp": -15}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Zatrudnienie elitarnych międzynarodowych kancelarii prawnych (koszt)": {"trust": +15, "liq": 0, "cap": -25, "comp": +20},
                        "Samodzielne przepychanki prawne z bankami azjatyckimi": {"trust": -15, "liq": 0, "cap": +10, "comp": -15}
                    }}
                }
            },
            4: {
                "title": "FAZA 4: UTRATA PŁYNNOŚCI WALUTOWEJ",
                "desc": "Bank nie ma dolarów i euro na pokrycie zobowiązań swoich największych importerów. Firmy grożą masowymi pozwami za zablokowanie ich biznesów.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Izolowana, powolna budowa nowego węzła SWIFT (bezpieczeństwo)": {"trust": +10, "liq": -20, "cap": -10, "comp": +15},
                        "Szybkie postawienie starego węzła i ignorowanie luki (ryzyko powtórki)": {"trust": -30, "liq": +25, "cap": 0, "comp": -25}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Wymuszona sprzedaż aktywów lokalnych w celu dokapitalizowania rezerw": {"trust": -10, "liq": +30, "cap": -30, "comp": 0},
                        "Zamrożenie kont firmowych i odmowa realizacji wypłat": {"trust": -40, "liq": +10, "cap": 0, "comp": -10}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Wniosek do NBP o ratunkową linię kredytową (przyznanie się do porażki)": {"trust": -10, "liq": +40, "cap": 0, "comp": +20},
                        "Tuszowanie braku płynności i ukryte rolowanie długów": {"trust": -40, "liq": -10, "cap": 0, "comp": -50}
                    }}
                }
            },
            5: {
                "title": "FAZA 5: STRUKTURY OBRONNE",
                "desc": "Śledztwo wykazuje, że luki w SWIFT pochodziły z zaniedbań na poziomie mikrosegmentacji sieci banku. KNF żąda radykalnych zmian strukturalnych.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Wdrożenie zaawansowanych systemów anomalii behawioralnych AI (duży wydatek)": {"trust": +20, "liq": 0, "cap": -30, "comp": +25},
                        "Dalsze poleganie na standardowych firewallach i politykach": {"trust": -25, "liq": 0, "cap": +15, "comp": -30}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Restrykcyjny rozdział obowiązków w back-office (wymaga nowych etatów)": {"trust": +15, "liq": -15, "cap": -15, "comp": +20},
                        "Dalsze zatwierdzanie przelewów przez pojedyncze osoby z IT": {"trust": -30, "liq": +10, "cap": 0, "comp": -35}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Akceptacja nałożonej przez KNF kary i pełna współpraca": {"trust": +25, "liq": -10, "cap": -20, "comp": +30},
                        "Odwlekanie wdrożenia zaleceń i zaskarżenie decyzji KNF": {"trust": -20, "liq": +10, "cap": +10, "comp": -20}
                    }}
                }
            }
        }
    },
    5: {
        "name": "VI: Deepfake & Social Engineering",
        "rounds": {
            1: {
                "title": "FAZA 1: FAŁSZYWY PREZES",
                "desc": "Dyrektor Finansowy odbiera telefon. Głos brzmiący identycznie jak Prezes Zarządu zleca pilny przelew 30 mln EUR ('tajne przejęcie spółki'). Przelew wychodzi.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Zatrzymanie bramek wyjściowych sieci celem zablokowania protokołu": {"trust": 0, "liq": -15, "cap": 0, "comp": +10},
                        "Sprawdzanie logów centrali telefonicznej (pozwolenie na przepływ srodków)": {"trust": -10, "liq": -5, "cap": -10, "comp": -5}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Autorytarna blokada przelewu w Clearingu mimo 'nakazu prezesa'": {"trust": +10, "liq": -5, "cap": +20, "comp": +15},
                        "Puszczenie przelewu (zaufanie do głosu i procedur autorytetu)": {"trust": -20, "liq": 0, "cap": -30, "comp": -20}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Wewnętrzne śledztwo i ciche poinformowanie wyższego zarządu": {"trust": 0, "liq": 0, "cap": 0, "comp": +5},
                        "Ignorowanie incydentu, strach przed wpadką Dyrektora Finansowego": {"trust": -15, "liq": 0, "cap": 0, "comp": -15}
                    }}
                }
            },
            2: {
                "title": "FAZA 2: KOMPROMITACJA WIDEO",
                "desc": "W serwisie YouTube pojawia się wygenerowane AI wideo 'Prezesa' ogłaszającego niewypłacalność banku. Film szybko staje się viralem (Deepfake).",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Oficjalne zgłoszenie na YouTube o usunięcie wideo jako scam": {"trust": +5, "liq": 0, "cap": 0, "comp": +5},
                        "Atak DDoS na serwery hostujące pliki (nielegalne)": {"trust": -30, "liq": 0, "cap": -10, "comp": -40}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Zgromadzenie natychmiastowych rezerw gotówki w oddziałach na wypadek paniki": {"trust": +15, "liq": -20, "cap": -5, "comp": +5},
                        "Ignorowanie zagrożenia – 'ludzie nie uwierzą w fake video'": {"trust": -25, "liq": +10, "cap": 0, "comp": -10}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Wydanie nagrania z prawdziwym Prezesem dementującym plotki": {"trust": +25, "liq": 0, "cap": -5, "comp": +10},
                        "Wysłanie tylko suchego, tekstowego oświadczenia biura prasowego": {"trust": -10, "liq": 0, "cap": 0, "comp": -5}
                    }}
                }
            },
            3: {
                "title": "FAZA 3: BANK RUN",
                "desc": "Rozpoczyna się panika. Klienci ustawiają się w gigantycznych kolejkach pod oddziałami, a serwery internetowe padają pod naporem prób zerwania lokat.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Zakup najwyższych pakietów ochrony Anty-DDoS dla bankowości online": {"trust": +10, "liq": 0, "cap": -20, "comp": +5},
                        "Odłączenie logowań mobilnych 'ze względów technicznych' (blokada ucieczki środków)": {"trust": -40, "liq": +25, "cap": 0, "comp": -30}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Tymczasowe zawieszenie wypłat depozytów (łamie prawo bankowe)": {"trust": -50, "liq": +40, "cap": 0, "comp": -50},
                        "Wypłacanie gotówki bez ograniczeń, aż do opróżnienia skarbców": {"trust": +20, "liq": -40, "cap": 0, "comp": +10}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Publiczna prośba do Premiera / NBP o deklarację bezpieczeństwa banku": {"trust": +25, "liq": +10, "cap": 0, "comp": +15},
                        "Samodzielne uspokajanie tłumów przez pracowników oddziałów": {"trust": -15, "liq": 0, "cap": 0, "comp": -10}
                    }}
                }
            },
            4: {
                "title": "FAZA 4: WEWNETRZNA PARANOJA",
                "desc": "Pracownicy boją się wykonywać polecenia przełożonych przez telefon. Procedury weryfikacji tożsamości paraliżują codzienną pracę banku.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Wdrożenie biometrii głosowej dla kadry kierowniczej (drogi system)": {"trust": +15, "liq": 0, "cap": -25, "comp": +15},
                        "Poleganie na hasłach wypowiadanych przez telefon": {"trust": -20, "liq": 0, "cap": +5, "comp": -15}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Rygorystyczne wymaganie fizycznego podpisu dla transakcji VIP": {"trust": +10, "liq": -15, "cap": 0, "comp": +10},
                        "Kontynuacja procesowania 'na maila i telefon' dla przyspieszenia obsługi": {"trust": -25, "liq": +15, "cap": 0, "comp": -20}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Wytoczenie gigantycznych procesów platformom social media za opieszałość": {"trust": +10, "liq": 0, "cap": -10, "comp": +5},
                        "Ciche zaakceptowanie strat wizerunkowych jako 'uroku dzisiejszych czasów'": {"trust": -20, "liq": 0, "cap": +5, "comp": -10}
                    }}
                }
            },
            5: {
                "title": "FAZA 5: NOWA RZECZYWISTOŚĆ",
                "desc": "Atak deepfake ujawnił nieadekwatność starych procedur 'na zaufanie'. Instytucja wymaga transformacji kulturowej i technologicznej.",
                "questions": {
                    "IT": {"label": "CYBER-SECURITY", "options": {
                        "Budowa dedykowanego zespołu analityków OSINT monitorujących Dark Web": {"trust": +15, "liq": 0, "cap": -20, "comp": +10},
                        "Obcięcie budżetów na innowacje bezpieczeństwa z powodu strat": {"trust": -30, "liq": 0, "cap": +20, "comp": -25}
                    }},
                    "Ops": {"label": "OPERACJE / RYZYKO", "options": {
                        "Całkowite usunięcie jednoosobowej autoryzacji w banku dla kwot >1M PLN": {"trust": +20, "liq": -10, "cap": 0, "comp": +25},
                        "Utrzymanie starej matrycy autoryzacji dla 'wygody zarządu'": {"trust": -25, "liq": +15, "cap": 0, "comp": -30}
                    }},
                    "Dir": {"label": "ZARZĄD / PR", "options": {
                        "Zwolnienie Dyrektora Finansowego, który uwierzył w fałszywy telefon": {"trust": 0, "liq": 0, "cap": +10, "comp": -10},
                        "Ochrona CFO: 'Każdy mógł dać się nabrać na deepfake', nacisk na procesy": {"trust": +15, "liq": 0, "cap": -5, "comp": +15}
                    }}
                }
            }
        }
    }
}

def get_round_data(s_idx, r_num):
    # Zabezpieczenie na wypadek braku danych
    if s_idx not in FULL_SCENARIOS or r_num not in FULL_SCENARIOS[s_idx]["rounds"]:
        return {
            "title": f"FAZA {r_num}: KRYZYS W TOKU",
            "desc": "Sytuacja operacyjna rozwija się. Czekam na dane.",
            "questions": {}
        }
    return FULL_SCENARIOS[s_idx]["rounds"][r_num]

# --- ENGINE ---
@st.cache_resource
def get_engine():
    return {"scenario_idx": 0, "round": 0, "teams": {}, "status": "ACTIVE"}

state = get_engine()

def calculate_metrics(team_name):
    t, l, c, co = 100, 100, 100, 100
    team = state["teams"].get(team_name, {})
    for s_idx, scen_decs in team.get("decisions", {}).items():
        for r_num, roles in scen_decs.items():
            data = get_round_data(s_idx, r_num)
            for role, choice in roles.items():
                if role in data.get("questions", {}) and choice in data["questions"][role]["options"]:
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
        s_name = FULL_SCENARIOS[state["scenario_idx"]]["name"] if state["scenario_idx"] in FULL_SCENARIOS else "Koniec Gry"
        st.markdown(f"<div class='panel'>SCENARIUSZ: <b>{s_name}</b></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='panel'>RUNDA: <b>{state['round']} / 5</b></div>", unsafe_allow_html=True)
    with c3:
        if st.button("🔄 SYNCHRONIZUJ STATUSY ZESPOŁÓW", use_container_width=True):
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- MAIN ADMIN TABS ---
    tab1, tab2, tab3 = st.tabs(["🎮 STEROWANIE RUNDĄ", "📊 MONITOR ZESPOŁÓW", "📜 PEŁNA HISTORIA DECYZJI"])

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
        st.markdown("<span class='panel-label'>DANE ARCHIWALNE (DECYZJE ZESPOŁÓW)</span>", unsafe_allow_html=True)
        
        full_history = []
        for t_name, t_data in state["teams"].items():
            for s_idx, scen_decs in t_data.get("decisions", {}).items():
                for r_num, roles in scen_decs.items():
                    rd = get_round_data(s_idx, r_num)
                    for role, choice in roles.items():
                        # Znajdujemy punktację dla podjętej decyzji
                        impact = rd.get("questions", {}).get(role, {}).get("options", {}).get(choice, {"trust": 0, "liq": 0, "cap": 0, "comp": 0})
                        
                        full_history.append({
                            "SCENARIUSZ": s_idx + 1,
                            "RUNDA": r_num,
                            "ZESPÓŁ": t_name,
                            "SEKCJA": rd["questions"][role]["label"],
                            "WYBRANA DECYZJA": choice,
                            "WPŁYW (PKT)": sum(impact.values())
                        })
        
        if full_history:
            df_hist = pd.DataFrame(full_history)
            st.dataframe(df_hist.sort_values(["SCENARIUSZ", "RUNDA", "ZESPÓŁ"], ascending=[False, False, True]), use_container_width=True, hide_index=True)
        else:
            st.info("Historia jest pusta. Czekam na pierwsze decyzje.")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- DANGER ZONE ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.expander("⚠️ STREFA ZAGROŻENIA (DANGER ZONE)"):
        st.markdown("<div class='danger-zone'>", unsafe_allow_html=True)
        st.warning("Poniższy przycisk trwale usunie wszystkie zespoły, ich punkty oraz całą historię rozgrywki.")
        if st.button("☢️ RESETUJ CAŁĄ GRĘ (NIEODWRACALNE)"):
            state.update({"scenario_idx": 0, "round": 0, "teams": {}, "status": "ACTIVE"})
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def team_view():
    team_name = st.session_state["team_name"]
    team_data = state["teams"][team_name]
    m = calculate_metrics(team_name)
    
    st.markdown(f"<div class='command-header'><div class='brand-title'>CyberBank // {team_name}</div><div>S: {state['scenario_idx']+1} | R: {state['round']}</div></div>", unsafe_allow_html=True)

    if not team_data["is_active"]:
        st.markdown("<div class='bankrupt-panel'><h1>💀 STATUS: ELIMINACJA</h1><p>Twój bank nie spełnił wymogów nadzorczych lub utracił płynność. Opuść centrum dowodzenia.</p></div>", unsafe_allow_html=True)
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
            st.warning("DECYZJE WYSŁANE. TRWA WRAŻANIE W SYSTEMIE...")
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
