# =============================================================================
# routen_design.py – Farbe und Dicke der Route
# Verantwortlich: Penélope
#
# Im Browser wählt man die Farbe mit einem Farbwähler. Der liefert die Farbe
# als Text im sogenannten Hex-Format, z. B. "#d62828":
#   "#"  + 2 Zeichen Rot + 2 Zeichen Grün + 2 Zeichen Blau
# Jeder Anteil ist eine Zahl von 0 bis 255, geschrieben im Sechzehnersystem
# (Hexadezimal: 0-9 und a-f). "d6" = 214, "28" = 40.
# =============================================================================

# Farben für die Markierung von Start und Ziel
START_FARBE = "#2a9d8f"   # Grün
ZIEL_FARBE = "#264653"    # Dunkelblau

# Standardwerte, falls im Formular etwas Ungültiges ankommt
STANDARD_FARBE = "#d62828"
STANDARD_DICKE = 6
MIN_DICKE = 1
MAX_DICKE = 20


def hex_zu_rgb(farbe):
    """Wandelt "#d62828" in das Tupel (214, 40, 40) um.

    Mit String-Slicing (wie in der Vorlesung bei Listen) holen wir die
    jeweils zwei Zeichen heraus. int(text, 16) liest eine Zahl im
    Sechzehnersystem.
    """
    rot = int(farbe[1:3], 16)
    gruen = int(farbe[3:5], 16)
    blau = int(farbe[5:7], 16)
    return rot, gruen, blau


def rgb_zu_hex(rot, gruen, blau):
    """Wandelt (214, 40, 40) zurück in "#d62828".

    :02x bedeutet: als Hexadezimalzahl mit mindestens 2 Stellen schreiben.
    """
    return f"#{rot:02x}{gruen:02x}{blau:02x}"


def farbe_pruefen(farbe):
    """Prüft, ob die Farbe im Format "#rrggbb" ist.

    Gibt die Farbe zurück, wenn sie gültig ist, sonst die Standardfarbe.
    """
    if not isinstance(farbe, str) or len(farbe) != 7 or farbe[0] != "#":
        return STANDARD_FARBE
    try:
        hex_zu_rgb(farbe)        # klappt nur, wenn alle Zeichen gültig sind
    except ValueError:
        return STANDARD_FARBE
    return farbe.lower()


def dicke_pruefen(wert):
    """Wandelt die Liniendicke in eine ganze Zahl zwischen 1 und 20 um.

    Aus dem Formular kommt die Zahl als Text (z. B. "6"). Ist der Text keine
    Zahl, wird die Standarddicke genommen.
    """
    try:
        dicke = int(wert)
    except (TypeError, ValueError):
        return STANDARD_DICKE
    # Auf den erlaubten Bereich begrenzen
    if dicke < MIN_DICKE:
        return MIN_DICKE
    if dicke > MAX_DICKE:
        return MAX_DICKE
    return dicke


def farbe_aufhellen(farbe, anteil):
    """Macht eine Farbe heller, indem sie mit Weiß gemischt wird.

    anteil = 0 -> Farbe bleibt gleich, anteil = 1 -> komplett weiß.
    Für jeden Farbanteil gilt: neu = alt + (255 - alt) * anteil
    Wird z. B. für die Fläche unter dem Höhenprofil benutzt.
    """
    rot, gruen, blau = hex_zu_rgb(farbe)
    rot = int(rot + (255 - rot) * anteil)
    gruen = int(gruen + (255 - gruen) * anteil)
    blau = int(blau + (255 - blau) * anteil)
    return rgb_zu_hex(rot, gruen, blau)


# Kleiner Test (aus dem Hauptordner): python -m penelope.routen_design
if __name__ == "__main__":
    print(hex_zu_rgb("#d62828"))          # (214, 40, 40)
    print(farbe_aufhellen("#d62828", 0.5))
    print(farbe_pruefen("rot"))           # ungültig -> Standardfarbe
    print(dicke_pruefen("99"))            # zu groß -> 20
