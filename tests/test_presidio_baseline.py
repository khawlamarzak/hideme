"""
HIDEme - Semaine 1 : que trouve Presidio, sans adaptation, sur des messages marocains ?

Toutes les données personnelles ci-dessous sont inventées.
Lancer : python3 tests/test_presidio_baseline.py
"""
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

# Chaque message : le texte, puis ce qu'un bon bouclier devrait trouver.
MESSAGES = [
    ("Salam, smiti Karim Alaoui, CIN dyali BK123456, bghit nbdel numéro dyal tele l 0612345678.",
     [("NOM", "Karim Alaoui"), ("CIN", "BK123456"), ("TEL", "0612345678")]),
    ("Bonjour, je suis Fatima Zahra Bennani, mon RIB est 011780000012345678901234.",
     [("NOM", "Fatima Zahra Bennani"), ("RIB", "011780000012345678901234")]),
    ("3afak 3ayto 3lia f +212661234567, ana Youssef El Idrissi.",
     [("TEL", "+212661234567"), ("NOM", "Youssef El Idrissi")]),
    ("السلام، سميتي خديجة التازي، رقم البطاقة ديالي J456789",
     [("NOM", "خديجة التازي"), ("CIN", "J456789")]),
    ("Mon email c'est hamid.berrada@example.ma et ma carte 4111 1111 1111 1111 a été bloquée.",
     [("EMAIL", "hamid.berrada@example.ma"), ("CARTE", "4111 1111 1111 1111")]),
    ("kan sken f 12 Derb Sultan, Casablanca, bghit nbdel l'adresse dyali.",
     [("ADRESSE", "12 Derb Sultan, Casablanca")]),
    ("Smiya dyal khoya Mohamed Amrani, CIN AB98765, tel 07 12 34 56 78.",
     [("NOM", "Mohamed Amrani"), ("CIN", "AB98765"), ("TEL", "07 12 34 56 78")]),
    ("Je m'appelle Salma Chraibi, mon IBAN est MA64011519000001205000534921.",
     [("NOM", "Salma Chraibi"), ("IBAN", "MA64011519000001205000534921")]),
    ("wach ymken tsiftou liya l code l 0522334455 ? smiti Krim.",
     [("TEL", "0522334455"), ("NOM", "Krim")]),
    ("Numéro CNSS dyali 123456789, w smiti Nadia Ouazzani, sakna f Hay Riad Rabat.",
     [("CNSS", "123456789"), ("NOM", "Nadia Ouazzani"), ("ADRESSE", "Hay Riad Rabat")]),
]


def make_analyzer():
    provider = NlpEngineProvider(nlp_configuration={
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_sm"},
                   {"lang_code": "fr", "model_name": "fr_core_news_sm"}],
    })
    return AnalyzerEngine(nlp_engine=provider.create_engine(), supported_languages=["en", "fr"])


def overlaps(text, expected_value, results):
    """Vrai si un résultat de Presidio couvre au moins la moitié de la valeur attendue."""
    start = text.find(expected_value)
    end = start + len(expected_value)
    for r in results:
        common = min(end, r.end) - max(start, r.start)
        if common >= len(expected_value) / 2:
            return r.entity_type
    return None


def run(lang):
    analyzer = make_analyzer()
    found_by_type, total_by_type, false_alarms = {}, {}, 0
    print(f"\n===== Presidio, langue = {lang} =====")
    for text, expected in MESSAGES:
        results = [r for r in analyzer.analyze(text=text, language=lang) if r.score >= 0.4]
        matched = set()
        for kind, value in expected:
            total_by_type[kind] = total_by_type.get(kind, 0) + 1
            hit = overlaps(text, value, results)
            if hit:
                found_by_type[kind] = found_by_type.get(kind, 0) + 1
                matched.add(hit)
            print(f"  {'OK  ' if hit else 'RATE'} {kind:8} {value}" + (f"  (vu comme {hit})" if hit else ""))
        for r in results:
            span = text[r.start:r.end]
            if not any(overlaps(text, v, [r]) for _, v in expected):
                false_alarms += 1
                print(f"  FAUX {r.entity_type:8} « {span} »")
    print("\n  Bilan par type :")
    tot_f = tot_t = 0
    for kind, total in total_by_type.items():
        f = found_by_type.get(kind, 0)
        tot_f, tot_t = tot_f + f, tot_t + total
        print(f"    {kind:8} {f}/{total}")
    print(f"    TOTAL    {tot_f}/{tot_t} trouvés, {false_alarms} fausses alertes")


if __name__ == "__main__":
    run("en")
    run("fr")
