# =============================================================================
# poster.py – das Poster: Format, leeres Bild und Aufteilung in Bereiche
# Verantwortlich: Penélope
#
# Die Klasse Poster ist sozusagen das leere Blatt Papier. Sie weiß, wie groß
# das Poster ist und wo darauf Karte, Höhenprofil und Text hinkommen:
#
#   +---------------------+
#   |                     |
#   |       KARTE         |
#   |                     |
#   +---------------------+
#   |    HÖHENPROFIL      |   (nur wenn ausgewählt)
#   +---------------------+
#   |   TITEL + STATISTIK |
#   +---------------------+
# =============================================================================

from PIL import Image, ImageDraw

# Formate in Pixeln (Breite, Höhe). A4 bei 150 dpi (Punkte pro Zoll) ergibt
# 1240 x 1754 Pixel. Das reicht für einen guten Ausdruck.
FORMATE = {
    "A4 hoch": (1240, 1754),
    "A4 quer": (1754, 1240),
    "Quadrat": (1500, 1500),
}

HINTERGRUND = "#fbfaf7"   # ganz leichtes Cremeweiß
RAHMEN_FARBE = "#222222"


class Poster:
    """Ein leeres Poster mit fester Größe und Bereichen für die Inhalte."""

    def __init__(self, format_name, mit_hoehenprofil):
        """Legt das leere Posterbild an.

        Parameter:
            format_name:      Schlüssel aus FORMATE, z. B. "A4 hoch"
            mit_hoehenprofil: True, wenn Platz für das Höhenprofil nötig ist
        """
        if format_name not in FORMATE:
            raise ValueError(f"Unbekanntes Format: {format_name}")

        self.breite, self.hoehe = FORMATE[format_name]
        # Image.new erzeugt ein neues, einfarbiges Bild (wie np.zeros bei OpenCV)
        self.bild = Image.new("RGB", (self.breite, self.hoehe), HINTERGRUND)
        self.bereiche = self.bereiche_berechnen(mit_hoehenprofil)

    def bereiche_berechnen(self, mit_hoehenprofil):
        """Teilt das Poster in Bereiche auf.

        Jeder Bereich ist ein Tupel (x, y, breite, hoehe) in Pixeln.
        Alle Größen sind Anteile der Postergröße, damit das Layout bei
        jedem Format passt.
        """
        rand = int(min(self.breite, self.hoehe) * 0.07)      # Außenrand
        abstand = int(rand * 0.6)                            # Abstand zwischen Bereichen
        innen_breite = self.breite - 2 * rand

        text_hoehe = int(self.hoehe * 0.15)
        if mit_hoehenprofil:
            profil_hoehe = int(self.hoehe * 0.10)
        else:
            profil_hoehe = 0

        # Die Karte bekommt den ganzen restlichen Platz
        karte_hoehe = self.hoehe - 2 * rand - text_hoehe - abstand
        if mit_hoehenprofil:
            karte_hoehe -= profil_hoehe + abstand

        bereiche = {}
        bereiche["karte"] = (rand, rand, innen_breite, karte_hoehe)
        if mit_hoehenprofil:
            profil_y = rand + karte_hoehe + abstand
            bereiche["profil"] = (rand, profil_y, innen_breite, profil_hoehe)
        bereiche["text"] = (rand, self.hoehe - rand - text_hoehe, innen_breite, text_hoehe)
        return bereiche

    def bereich(self, name):
        """Gibt den Bereich mit dem Namen "karte", "profil" oder "text" zurück."""
        return self.bereiche[name]

    def karte_einfuegen(self, kartenbild):
        """Klebt das Kartenbild in den Kartenbereich und zeichnet einen Rahmen.

        paste() funktioniert wie das Einfügen eines Logos in der Vorlesung
        (img[y1:y2, x1:x2] = logo), nur mit Pillow.
        """
        x, y, breite, hoehe = self.bereich("karte")
        self.bild.paste(kartenbild, (x, y))

        zeichner = ImageDraw.Draw(self.bild)
        zeichner.rectangle([x, y, x + breite - 1, y + hoehe - 1], outline=RAHMEN_FARBE, width=2)
