# =============================================================================
# hoehenprofil.py – Höhenprofil als Diagramm auf das Poster zeichnen
# Verantwortlich: Marlene
#
# Das Höhenprofil zeigt, wie hoch man an welcher Stelle der Wanderung war:
#   x-Achse (waagerecht) = gelaufene Strecke in km
#   y-Achse (senkrecht)  = Höhe in Metern
#
# Gezeichnet wird mit Pillow (ImageDraw). Das funktioniert wie das Zeichnen
# mit OpenCV aus der Vorlesung: Linien und Flächen über Pixel-Koordinaten.
# Wichtig: Im Bild liegt der Punkt (0, 0) oben links, y wächst nach unten.
# =============================================================================

from PIL import ImageDraw

from marlene.statistik import strecken_liste_km
from penelope.routen_design import farbe_aufhellen
from david.texte import zahl_formatieren

# Farbe für Beschriftung und Grundlinie
TEXT_FARBE = "#444444"


def wert_zu_pixel(wert, wert_min, wert_max, pixel_start, pixel_laenge):
    """Rechnet einen Wert (z. B. eine Höhe) in eine Pixelposition um.

    Der kleinste Wert landet bei pixel_start, der größte bei
    pixel_start + pixel_laenge. Dazwischen wird gleichmäßig verteilt
    ("Dreisatz"):

        pixel = pixel_start + (wert - wert_min) / (wert_max - wert_min) * pixel_laenge
    """
    if wert_max == wert_min:
        # Alle Werte gleich (z. B. komplett flache Strecke): in die Mitte legen
        return pixel_start + pixel_laenge / 2
    anteil = (wert - wert_min) / (wert_max - wert_min)
    return pixel_start + anteil * pixel_laenge


def hoehenprofil_zeichnen(bild, bereich, wanderung, farbe, schrift):
    """Zeichnet das Höhenprofil in einen Bereich des Posters.

    Parameter:
        bild:      das Posterbild (Pillow-Image), auf das gezeichnet wird
        bereich:   (x, y, breite, hoehe) des Diagrammbereichs in Pixeln
        wanderung: Wanderung-Objekt aus gpx_import.py
        farbe:     Farbe der Route, z. B. "#d62828"
        schrift:   Schriftart (Pillow-Font) für die Beschriftung
    """
    x, y, breite, hoehe = bereich
    zeichner = ImageDraw.Draw(bild)

    # Ohne Höhenangaben kann kein Profil gezeichnet werden
    if not wanderung.hat_hoehen():
        zeichner.text((x, y), "Keine Höhendaten in der GPX-Datei vorhanden.",
                      font=schrift, fill=TEXT_FARBE)
        return

    # 1. Daten sammeln: Strecke (x-Achse) und Höhe (y-Achse) für jeden Punkt
    strecken = strecken_liste_km(wanderung)
    werte = []   # Liste von (strecke_km, hoehe_m)
    for strecke, punkt in zip(strecken, wanderung.punkte):
        if punkt.hoehe is not None:
            werte.append((strecke, punkt.hoehe))

    strecke_max = strecken[-1]
    hoehe_min = min(wanderung.hoehen())
    hoehe_max = max(wanderung.hoehen())

    # 2. Platz für die Beschriftung links frei lassen (Breite des längsten Textes)
    text_oben = zahl_formatieren(hoehe_max) + " m"
    text_unten = zahl_formatieren(hoehe_min) + " m"
    text_breite = max(zeichner.textlength(text_oben, font=schrift),
                      zeichner.textlength(text_unten, font=schrift))
    diagramm_x = x + text_breite + 15
    diagramm_breite = breite - (diagramm_x - x)
    unten = y + hoehe   # y-Pixel der Grundlinie

    # 3. Jeden Wert in Pixel umrechnen.
    # Bei der Höhe wird von "unten" abgezogen, weil y im Bild nach unten wächst.
    linie = []
    for strecke, hoehe_m in werte:
        px = wert_zu_pixel(strecke, 0, strecke_max, diagramm_x, diagramm_breite)
        py = unten - wert_zu_pixel(hoehe_m, hoehe_min, hoehe_max, 0, hoehe)
        linie.append((px, py))

    # 4. Gefüllte Fläche unter der Linie: Linie + die zwei unteren Ecken
    flaeche = linie + [(linie[-1][0], unten), (linie[0][0], unten)]
    zeichner.polygon(flaeche, fill=farbe_aufhellen(farbe, 0.6))

    # 5. Linie oben drauf und Grundlinie unten
    zeichner.line(linie, fill=farbe, width=3, joint="curve")
    zeichner.line([(diagramm_x, unten), (x + breite, unten)], fill=TEXT_FARBE, width=1)

    # 6. Beschriftung: höchster und tiefster Wert links, Gesamtstrecke rechts.
    # "anchor" sagt, an welcher Ecke des Textes die Position liegt:
    # "ld" = links unten (left/descender), "ra" = rechts oben (right/ascender).
    # Ohne anchor ist die Position immer die linke obere Ecke.
    zeichner.text((x, y), text_oben, font=schrift, fill=TEXT_FARBE)
    zeichner.text((x, unten), text_unten, font=schrift, fill=TEXT_FARBE, anchor="ld")
    strecke_text = zahl_formatieren(strecke_max, 1) + " km"
    zeichner.text((x + breite, unten + 5), strecke_text, font=schrift, fill=TEXT_FARBE, anchor="ra")
