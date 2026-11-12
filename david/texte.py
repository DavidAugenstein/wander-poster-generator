# =============================================================================
# texte.py – Titel, Untertitel, Statistik und Quellenangabe schreiben
# Verantwortlich: David
#
# Texte werden mit Pillow geschrieben. Anders als cv2.putText aus der
# Vorlesung kann Pillow normale Schriftdateien (.ttf) laden und schreibt
# damit auch Umlaute (ä, ö, ü, ß) richtig.
# Die Schriftdateien liegen im Ordner "schriften" im Hauptordner.
# =============================================================================

import os

from PIL import ImageDraw, ImageFont

# Ordner mit den Schriftdateien. __file__ ist der Pfad dieser Datei,
# ".." bedeutet "ein Ordner höher", also vom Ordner david in den Hauptordner.
SCHRIFTEN_ORDNER = os.path.join(os.path.dirname(__file__), "..", "schriften")

# Schriftarten: Anzeigename -> (Datei normal, Datei fett)
SCHRIFTARTEN = {
    "Modern": ("Lato-Regular.ttf", "Lato-Bold.ttf"),
    "Klassisch": ("PT_Serif-Web-Regular.ttf", "PT_Serif-Web-Bold.ttf"),
    "Handschrift": ("Kalam-Regular.ttf", "Kalam-Bold.ttf"),
}

TEXT_FARBE = "#222222"
GRAU = "#666666"


def schrift_laden(schriftart, groesse, fett=False):
    """Lädt eine Schriftart in der gewünschten Größe (in Pixeln).

    Falls die Datei fehlt, wird die eingebaute Standardschrift von Pillow
    benutzt, damit das Programm trotzdem weiterläuft.
    """
    normal, fettdruck = SCHRIFTARTEN.get(schriftart, SCHRIFTARTEN["Modern"])
    dateiname = fettdruck if fett else normal
    try:
        return ImageFont.truetype(os.path.join(SCHRIFTEN_ORDNER, dateiname), groesse)
    except OSError:
        print("Schriftdatei nicht gefunden, nutze Standardschrift:", dateiname)
        return ImageFont.load_default(size=groesse)


def zahl_formatieren(zahl, nachkommastellen=0):
    """Schreibt eine Zahl im deutschen Format: 1234.5 -> "1.234,5".

    Python schreibt Zahlen im englischen Format (1,234.5). Darum tauschen
    wir Komma und Punkt über einen Zwischenschritt mit "#".
    """
    text = f"{zahl:,.{nachkommastellen}f}"          # z. B. "1,234.5"
    return text.replace(",", "#").replace(".", ",").replace("#", ".")


def statistik_text_erstellen(statistik):
    """Macht aus dem Statistik-Dictionary eine Textzeile für das Poster.

    Beispiel: "38,2 km  ·  1.130 m Aufstieg  ·  9 Std. 5 Min. Gehzeit  ·  2 Tage"
    Werte, die None sind (nicht vorhanden), werden weggelassen.
    """
    teile = [zahl_formatieren(statistik["distanz_km"], 1) + " km"]

    if statistik["anstieg_m"] is not None:
        teile.append(zahl_formatieren(statistik["anstieg_m"]) + " m Aufstieg")
        teile.append(zahl_formatieren(statistik["abstieg_m"]) + " m Abstieg")
    if statistik["hoechster_punkt_m"] is not None:
        teile.append("höchster Punkt " + zahl_formatieren(statistik["hoechster_punkt_m"]) + " m")
    if statistik["gehzeit"] is not None:
        teile.append(statistik["gehzeit"] + " Gehzeit")
    if statistik["tage"] is not None and statistik["tage"] > 1:
        teile.append(f"{statistik['tage']} Tage")

    # join setzt zwischen alle Teile den Trenner "  ·  "
    return "  ·  ".join(teile)


def text_zentriert_schreiben(bild, text, mitte_x, y, schrift, farbe):
    """Schreibt einen Text waagerecht zentriert um mitte_x.

    anchor="ma" bedeutet: Die Position ist die Mitte oben des Textes.
    """
    zeichner = ImageDraw.Draw(bild)
    zeichner.text((mitte_x, y), text, font=schrift, fill=farbe, anchor="ma")


def passende_schrift(bild, text, schriftart, groesse, max_breite, fett=False):
    """Lädt die Schrift und verkleinert sie, bis der Text in max_breite passt."""
    zeichner = ImageDraw.Draw(bild)
    schrift = schrift_laden(schriftart, groesse, fett)
    while zeichner.textlength(text, font=schrift) > max_breite and groesse > 10:
        groesse -= 2
        schrift = schrift_laden(schriftart, groesse, fett)
    return schrift


def texte_schreiben(poster, titel, untertitel, statistik, schriftart):
    """Schreibt Titel, Untertitel und (falls vorhanden) die Statistik
    untereinander in den Textbereich des Posters.

    Parameter:
        poster:     Poster-Objekt aus penelope/poster.py
        titel, untertitel: Texte aus dem Formular (dürfen leer sein)
        statistik:  Dictionary aus statistik.py oder None (= nicht anzeigen)
        schriftart: Schlüssel aus SCHRIFTARTEN
    """
    x, y, breite, hoehe = poster.bereich("text")
    mitte_x = x + breite / 2

    # Schriftgrößen abhängig von der Postergröße, damit es überall passt
    titel_groesse = int(poster.breite * 0.06)
    klein_groesse = int(poster.breite * 0.022)

    # Wir gehen von oben nach unten durch den Textbereich
    aktuelle_y = y + hoehe * 0.12

    if titel:
        schrift = passende_schrift(poster.bild, titel, schriftart, titel_groesse, breite, fett=True)
        text_zentriert_schreiben(poster.bild, titel, mitte_x, aktuelle_y, schrift, TEXT_FARBE)
        aktuelle_y += schrift.size * 1.4

    if untertitel:
        schrift = passende_schrift(poster.bild, untertitel, schriftart, int(titel_groesse * 0.45), breite)
        text_zentriert_schreiben(poster.bild, untertitel, mitte_x, aktuelle_y, schrift, GRAU)
        aktuelle_y += schrift.size * 1.8

    if statistik is not None:
        text = statistik_text_erstellen(statistik)
        schrift = passende_schrift(poster.bild, text, schriftart, klein_groesse, breite)
        text_zentriert_schreiben(poster.bild, text, mitte_x, aktuelle_y, schrift, TEXT_FARBE)


def quelle_schreiben(poster, quelle):
    """Schreibt die Quellenangabe der Karte klein unter die Karte (rechts)."""
    if not quelle:
        return
    x, y, breite, hoehe = poster.bereich("karte")
    schrift = schrift_laden("Modern", int(poster.breite * 0.011))
    zeichner = ImageDraw.Draw(poster.bild)
    # anchor="ra" = rechts oben: Text endet genau am rechten Kartenrand
    zeichner.text((x + breite, y + hoehe + 6), quelle, font=schrift, fill=GRAU, anchor="ra")
