# =============================================================================
# tests.py – einfache Tests für alle Dateien des Projekts
#
# Ausführen (im Hauptordner des Projekts):
#     python tests.py
#
# Jeder Test ist eine kleine Funktion. Darin prüft "assert", ob ein Ergebnis
# stimmt. Ist die Bedingung hinter assert falsch, bricht Python mit einem
# AssertionError ab und wir sehen, welcher Test fehlgeschlagen ist.
# Alle Tests brauchen kein Internet (Kartenstil "schlicht").
# =============================================================================

import os

from david.gpx_import import gpx_einlesen, GpxFehler
from david.texte import zahl_formatieren
from marlene.statistik import entfernung_m, statistik_berechnen, zeit_als_text
from alise.massstab import runde_laenge_finden, laenge_als_text
from alise.poster_erstellen import poster_erstellen
from penelope.routen_design import hex_zu_rgb, farbe_pruefen, dicke_pruefen
from penelope.export import dateiname_erstellen

BEISPIEL = "beispiele/harz_brocken.gpx"
TEST_ORDNER = "ausgabe"   # hier landen die Testdateien (ist nicht in Git)

# Anfang jeder GPX-Datei, die wir für die Tests selbst schreiben
GPX_ANFANG = '<?xml version="1.0"?><gpx version="1.1" xmlns="http://www.topografix.com/GPX/1/1">'


def gpx_datei_schreiben(name, inhalt):
    """Schreibt eine kleine GPX-Datei für einen Test und gibt den Pfad zurück."""
    os.makedirs(TEST_ORDNER, exist_ok=True)
    pfad = os.path.join(TEST_ORDNER, name)
    with open(pfad, "w", encoding="utf-8") as datei:
        datei.write(GPX_ANFANG + inhalt + "</gpx>")
    return pfad


# ---- David: GPX einlesen und Texte ----

def test_beispiel_einlesen():
    wanderung = gpx_einlesen(BEISPIEL)
    assert len(wanderung.punkte) == 310
    assert wanderung.name == "Harz: Bad Harzburg – Brocken – Elend"
    assert wanderung.hat_hoehen()


def test_name_nicht_vom_autor():
    # Der Name des Autors darf nicht zum Titel werden
    pfad = gpx_datei_schreiben("test_autor.gpx",
        '<metadata><author><name>Max Mustermann</name></author></metadata>'
        '<trk><name>Brocken-Runde</name><trkseg>'
        '<trkpt lat="51.80" lon="10.60"/><trkpt lat="51.81" lon="10.61"/>'
        '</trkseg></trk>')
    assert gpx_einlesen(pfad).name == "Brocken-Runde"


def test_zu_wenige_punkte():
    # Mit nur einem Punkt muss ein GpxFehler kommen
    pfad = gpx_datei_schreiben("test_ein_punkt.gpx",
        '<trk><trkseg><trkpt lat="51.80" lon="10.60"/></trkseg></trk>')
    try:
        gpx_einlesen(pfad)
        assert False, "Es hätte ein GpxFehler kommen müssen"
    except GpxFehler:
        pass   # richtig: der Fehler wurde erkannt


def test_datei_fehlt():
    try:
        gpx_einlesen("gibt_es_nicht.gpx")
        assert False, "Es hätte ein GpxFehler kommen müssen"
    except GpxFehler:
        pass


def test_zahl_formatieren():
    assert zahl_formatieren(1234.5, 1) == "1.234,5"
    assert zahl_formatieren(980) == "980"


# ---- Marlene: Statistik ----

def test_entfernung():
    # Ein Breitengrad sind ungefähr 111 km
    pfad = gpx_datei_schreiben("test_entfernung.gpx",
        '<trk><trkseg><trkpt lat="50.0" lon="10.0"/><trkpt lat="51.0" lon="10.0"/></trkseg></trk>')
    punkte = gpx_einlesen(pfad).punkte
    meter = entfernung_m(punkte[0], punkte[1])
    assert 111000 < meter < 111400


def test_statistik_beispiel():
    statistik = statistik_berechnen(gpx_einlesen(BEISPIEL))
    assert round(statistik["distanz_km"], 1) == 20.9
    assert statistik["hoechster_punkt_m"] == 1149
    assert statistik["tage"] == 2


def test_zeiten_gemischt():
    # Eine Zeit mit "Z" (UTC), eine ohne Zeitzone: darf nicht abstürzen
    pfad = gpx_datei_schreiben("test_zeiten.gpx",
        '<trk><trkseg>'
        '<trkpt lat="51.80" lon="10.60"><time>2026-07-04T09:00:00Z</time></trkpt>'
        '<trkpt lat="51.81" lon="10.61"><time>2026-07-04T09:10:00</time></trkpt>'
        '</trkseg></trk>')
    assert statistik_berechnen(gpx_einlesen(pfad))["gehzeit"] == "10 Min."


def test_zeit_als_text():
    assert zeit_als_text(600) == "10 Min."
    assert zeit_als_text(3 * 3600 + 5 * 60) == "3 Std. 5 Min."


# ---- Alise: Maßstab und Hauptablauf ----

def test_runde_laenge():
    assert runde_laenge_finden(3700) == 2000
    assert laenge_als_text(2000) == "2 km"
    assert laenge_als_text(500) == "500 m"


def test_poster_erstellen():
    dateien = poster_erstellen(BEISPIEL, {"kartenstil": "schlicht", "titel": "Testposter"}, TEST_ORDNER)
    assert dateien["png"] == "testposter.png"
    assert os.path.exists(os.path.join(TEST_ORDNER, "testposter.pdf"))


# ---- Penélope: Farben und Dateinamen ----

def test_farben():
    assert hex_zu_rgb("#d62828") == (214, 40, 40)
    assert farbe_pruefen("rot") == "#d62828"     # ungültig -> Standardfarbe
    assert dicke_pruefen("99") == 20             # zu groß -> Maximum
    assert dicke_pruefen("abc") == 6             # keine Zahl -> Standard


def test_dateiname():
    assert dateiname_erstellen("Über den Brocken!") == "ueber-den-brocken"
    assert dateiname_erstellen("Wanderung mit Penélope") == "wanderung-mit-penelope"
    assert dateiname_erstellen("???") == "wander-poster"


# ---- Alle Tests nacheinander ausführen ----
if __name__ == "__main__":
    alle_tests = [
        test_beispiel_einlesen, test_name_nicht_vom_autor, test_zu_wenige_punkte,
        test_datei_fehlt, test_zahl_formatieren, test_entfernung, test_statistik_beispiel,
        test_zeiten_gemischt, test_zeit_als_text, test_runde_laenge, test_poster_erstellen,
        test_farben, test_dateiname,
    ]
    fehlgeschlagen = 0
    for test in alle_tests:
        try:
            test()
            print("OK    ", test.__name__)
        except AssertionError as fehler:
            print("FEHLER", test.__name__, fehler)
            fehlgeschlagen += 1
    print(f"\n{len(alle_tests) - fehlgeschlagen} von {len(alle_tests)} Tests bestanden.")
