# =============================================================================
# massstab.py – Maßstabsleiste auf die Karte zeichnen
# Verantwortlich: Alise
#
# Eine Maßstabsleiste zeigt, wie lang eine bestimmte Strecke auf der Karte
# ist, z. B.:    |__________|
#                    5 km
# Dafür müssen wir wissen, wie viele Meter ein Pixel der Karte entspricht.
# =============================================================================

import math

from PIL import ImageDraw

# "Schöne" Längen in Metern, aus denen die Maßstabsleiste gewählt wird
SCHOENE_LAENGEN = [50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]


def meter_pro_pixel_berechnen(zoom, breitengrad):
    """Berechnet, wie viele Meter ein Pixel einer Online-Karte sind.

    Bei Zoomstufe 0 passt die ganze Welt in ein Bild von 256 Pixeln. Am
    Äquator ist dann ein Pixel 156 543,03 Meter breit. Mit jeder Zoomstufe
    halbiert sich dieser Wert (darum 2 hoch zoom). Weiter im Norden werden
    die Abstände kleiner, das gleicht cos(breitengrad) aus:

        meter_pro_pixel = 156543.03 * cos(breitengrad) / 2^zoom
    """
    return 156543.03 * math.cos(math.radians(breitengrad)) / (2 ** zoom)


def runde_laenge_finden(max_meter):
    """Sucht die größte "schöne" Länge, die höchstens max_meter lang ist.

    Beispiel: max_meter = 3700  ->  2000 (also 2 km)
    """
    gefunden = SCHOENE_LAENGEN[0]
    for laenge in SCHOENE_LAENGEN:
        if laenge <= max_meter:
            gefunden = laenge
    return gefunden


def laenge_als_text(meter):
    """Macht aus Metern einen Text: 500 -> "500 m", 2000 -> "2 km"."""
    if meter >= 1000:
        return f"{meter // 1000} km"
    return f"{meter} m"


def massstab_zeichnen(bild, position, meter_pro_pixel, max_breite, schrift):
    """Zeichnet eine Maßstabsleiste auf das Bild.

    Parameter:
        bild:            Posterbild (Pillow-Image)
        position:        (x, y) der linken unteren Ecke der Leiste in Pixeln
        meter_pro_pixel: aus karte.py, wie viele Meter ein Pixel sind
        max_breite:      so viele Pixel darf die Leiste höchstens lang sein
        schrift:         Schriftart (Pillow-Font) für die Beschriftung
    """
    x, y = position
    zeichner = ImageDraw.Draw(bild)

    # 1. Passende Länge in Metern suchen und in Pixel umrechnen
    laenge_m = runde_laenge_finden(max_breite * meter_pro_pixel)
    laenge_px = round(laenge_m / meter_pro_pixel)
    text = laenge_als_text(laenge_m)

    # 2. Weißer Kasten als Hintergrund, damit man die Leiste auch auf
    #    dunklen Satellitenbildern gut lesen kann
    textbreite = zeichner.textlength(text, font=schrift)
    kasten_breite = max(laenge_px, textbreite) + 30
    kasten_hoehe = schrift.size + 40
    zeichner.rectangle([x - 15, y - kasten_hoehe, x - 15 + kasten_breite, y + 10], fill="white")

    # 3. Die Leiste: eine waagerechte Linie mit zwei kleinen senkrechten Strichen
    zeichner.line([(x, y), (x + laenge_px, y)], fill="black", width=4)
    zeichner.line([(x, y - 12), (x, y)], fill="black", width=4)
    zeichner.line([(x + laenge_px, y - 12), (x + laenge_px, y)], fill="black", width=4)

    # 4. Beschriftung mittig über der Leiste ("mb" = Mitte unten des Textes)
    zeichner.text((x + laenge_px / 2, y - 16), text, font=schrift, fill="black", anchor="mb")
