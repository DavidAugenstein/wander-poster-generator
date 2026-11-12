# =============================================================================
# export.py – das fertige Poster als PNG und PDF speichern
# Verantwortlich: Penélope
# =============================================================================

import os

# Umlaute werden für den Dateinamen ersetzt, weil manche Programme mit
# Sonderzeichen in Dateinamen Probleme haben.
ERSETZUNGEN = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}

# Auflösung in dpi (Punkte pro Zoll). Passt zu den Formaten in poster.py:
# 1240 Pixel / 150 dpi = 8,27 Zoll = 21 cm = A4-Breite
DPI = 150


def dateiname_erstellen(titel):
    """Macht aus dem Titel einen einfachen Dateinamen ohne Endung.

    Beispiel: "Harz-Tour 2026: Brocken!" -> "harz-tour-2026-brocken"
    Erlaubt sind nur Buchstaben a-z, Ziffern und Bindestriche.
    """
    name = ""
    for zeichen in titel.lower():
        zeichen = ERSETZUNGEN.get(zeichen, zeichen)   # Umlaut ersetzen, sonst gleich lassen
        if zeichen.isascii() and zeichen.isalnum():
            name += zeichen
        elif zeichen in " -_" and not name.endswith("-"):
            name += "-"
    name = name.strip("-")      # Bindestriche am Anfang und Ende entfernen

    if name == "":
        name = "wander-poster"
    return name


def als_png_speichern(bild, pfad):
    """Speichert das Bild als PNG-Datei (gut für Bildschirm und Handy)."""
    try:
        bild.save(pfad, "PNG")
    except OSError as fehler:
        raise OSError(f"Das PNG konnte nicht gespeichert werden: {fehler}")


def als_pdf_speichern(bild, pfad):
    """Speichert das Bild als PDF-Datei (gut zum Drucken).

    resolution sorgt dafür, dass das PDF genau die richtige Papiergröße hat.
    """
    try:
        bild.save(pfad, "PDF", resolution=DPI)
    except OSError as fehler:
        raise OSError(f"Das PDF konnte nicht gespeichert werden: {fehler}")


def poster_speichern(bild, ordner, titel):
    """Speichert das Poster als PNG und PDF im angegebenen Ordner.

    Rückgabe: Dictionary mit den Dateinamen, z. B.
        {"png": "harz-tour.png", "pdf": "harz-tour.pdf"}
    """
    # Ordner anlegen, falls er noch nicht existiert
    os.makedirs(ordner, exist_ok=True)

    name = dateiname_erstellen(titel)
    dateien = {"png": name + ".png", "pdf": name + ".pdf"}

    als_png_speichern(bild, os.path.join(ordner, dateien["png"]))
    als_pdf_speichern(bild, os.path.join(ordner, dateien["pdf"]))
    return dateien


# Kleiner Test (aus dem Hauptordner): python -m penelope.export
if __name__ == "__main__":
    print(dateiname_erstellen("Harz-Tour 2026: Über den Brocken!"))
    print(dateiname_erstellen("???"))
