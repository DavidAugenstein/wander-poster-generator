# =============================================================================
# poster_erstellen.py – der Hauptablauf des Programms
# Verantwortlich: Alise
#
# Diese Datei verbindet alle anderen Dateien. Der Webserver ruft nur die
# Funktion poster_erstellen() auf. Sie arbeitet nach dem EVA-Prinzip
# aus der Vorlesung:
#   Eingabe:      GPX-Datei einlesen                    (david/gpx_import.py)
#   Verarbeitung: Statistik, Karte, Höhenprofil,        (alle anderen Dateien)
#                 Maßstab und Texte aufs Poster bringen
#   Ausgabe:      Poster als PNG und PDF speichern      (penelope/export.py)
# =============================================================================

from david.gpx_import import gpx_einlesen
from david.karte import karte_erstellen
from marlene.statistik import statistik_berechnen
from marlene.hoehenprofil import hoehenprofil_zeichnen
from alise.massstab import massstab_zeichnen
from david.texte import texte_schreiben, quelle_schreiben, schrift_laden
from penelope.poster import Poster
from penelope.routen_design import farbe_pruefen, dicke_pruefen
from penelope.export import poster_speichern


# Diese Einstellungen gelten, wenn nichts anderes gewählt wurde.
# Der Webserver nutzt sie auch als Vorauswahl im Formular.
STANDARD_EINSTELLUNGEN = {
    "titel": "",                  # leer = Name aus der GPX-Datei nehmen
    "untertitel": "",
    "kartenstil": "topografisch",
    "routen_farbe": "#d62828",
    "routen_dicke": 6,
    "format": "A4 hoch",
    "rand": "mittel",
    "schriftart": "Modern",
    "hoehenprofil": True,
    "statistik": True,
    "massstab": True,
}


def poster_erstellen(gpx_pfad, einstellungen, ausgabe_ordner):
    """Erstellt aus einer GPX-Datei ein fertiges Poster und speichert es.

    Parameter:
        gpx_pfad:       Pfad zur hochgeladenen GPX-Datei
        einstellungen:  Dictionary wie STANDARD_EINSTELLUNGEN (aus dem Formular)
        ausgabe_ordner: Ordner, in dem PNG und PDF gespeichert werden
    Rückgabe:
        Dictionary mit den Dateinamen, z. B. {"png": "harz.png", "pdf": "harz.pdf"}
    Fehler:
        GpxFehler, RuntimeError, ValueError usw. werden an den Webserver
        weitergegeben, der sie als Meldung im Browser anzeigt.
    """
    # Fehlende Einstellungen mit den Standardwerten auffüllen:
    # Erst alle Standardwerte kopieren, dann mit den eigenen überschreiben.
    e = dict(STANDARD_EINSTELLUNGEN)
    e.update(einstellungen)
    farbe = farbe_pruefen(e["routen_farbe"])
    dicke = dicke_pruefen(e["routen_dicke"])

    # ---- 1. EINGABE: GPX-Datei einlesen ----
    wanderung = gpx_einlesen(gpx_pfad)
    titel = e["titel"] or wanderung.name      # "or": wenn titel leer ist, Name nehmen

    # ---- 2. VERARBEITUNG ----
    # Leeres Poster im gewählten Format
    poster = Poster(e["format"], e["hoehenprofil"])

    # Karte genau so groß wie der Kartenbereich des Posters erstellen
    _, _, karte_breite, karte_hoehe = poster.bereich("karte")
    karte, meter_pro_pixel, quelle = karte_erstellen(
        wanderung, e["kartenstil"], karte_breite, karte_hoehe, farbe, dicke, e["rand"]
    )
    poster.karte_einfuegen(karte)
    quelle_schreiben(poster, quelle)

    # Kleine Schrift für Höhenprofil und Maßstab (Größe passend zum Poster)
    kleine_schrift = schrift_laden(e["schriftart"], int(poster.breite * 0.018))

    if e["hoehenprofil"]:
        hoehenprofil_zeichnen(poster.bild, poster.bereich("profil"), wanderung, farbe, kleine_schrift)

    if e["massstab"]:
        # Maßstab unten links in die Karte, höchstens ein Viertel der Kartenbreite lang
        x, y, breite, hoehe = poster.bereich("karte")
        position = (x + 40, y + hoehe - 40)
        massstab_zeichnen(poster.bild, position, meter_pro_pixel, breite / 4, kleine_schrift)

    statistik = None
    if e["statistik"]:
        statistik = statistik_berechnen(wanderung)
    texte_schreiben(poster, titel, e["untertitel"], statistik, e["schriftart"])

    # ---- 3. AUSGABE: als PNG und PDF speichern ----
    return poster_speichern(poster.bild, ausgabe_ordner, titel)


# Test ohne Webserver (aus dem Hauptordner): python -m alise.poster_erstellen
# Erstellt ein Poster aus der Beispielroute im Stil "schlicht" (ohne Internet).
if __name__ == "__main__":
    dateien = poster_erstellen(
        "beispiele/harz_brocken.gpx",
        {"kartenstil": "schlicht", "untertitel": "Zwei Tage durch den Harz"},
        "ausgabe",
    )
    print("Fertig! Dateien im Ordner ausgabe:", dateien)
