# =============================================================================
# karte.py – Karte mit eingezeichneter Route erstellen
# Verantwortlich: David
#
# Diese Datei erzeugt das Kartenbild für das Poster. Es gibt vier Kartenstile:
#   - standard:      normale Straßenkarte (OpenStreetMap)
#   - topografisch:  Wanderkarte mit Höhenlinien (OpenTopoMap)
#   - satellit:      Luftbilder (Esri)
#   - schlicht:      nur die Route auf einfarbigem Hintergrund (ohne Internet)
#
# Wie funktionieren Online-Karten?
# Die Karte der ganzen Welt ist in viele kleine Bilder ("Kacheln", 256 x 256
# Pixel) zerschnitten. Je höher die Zoomstufe, desto mehr und desto genauere
# Kacheln gibt es. Die Bibliothek "staticmap" (pip install staticmap) erledigt
# die schwierige Arbeit für uns:
#   1. Sie berechnet, welche Zoomstufe zur Route passt,
#   2. lädt die nötigen Kacheln aus dem Internet,
#   3. setzt sie zu einem Bild zusammen und
#   4. zeichnet unsere Route als Linie darauf.
# Ein anderer Kartenstil ist deshalb nur eine andere Internetadresse.
#
# Das Ergebnis ist ein Bild der Bibliothek Pillow (PIL). Pillow ist ähnlich
# wie OpenCV aus der Vorlesung, kann aber Text mit Umlauten schreiben.
# =============================================================================

import math

from staticmap import StaticMap, Line, CircleMarker
from PIL import Image, ImageDraw

from alise.massstab import meter_pro_pixel_berechnen
from penelope.routen_design import START_FARBE, ZIEL_FARBE


# Alle Kartenstile in einem Dictionary.
#   "name":    wird im Formular angezeigt
#   "adresse": Internetadresse der Kacheln. {z} = Zoomstufe, {x}/{y} = Nummer
#              der Kachel. staticmap setzt die Werte selbst ein.
#   "quelle":  Quellenangabe, die laut Nutzungsbedingungen aufs Poster muss
KARTENSTILE = {
    "standard": {
        "name": "Straßenkarte",
        "adresse": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        "quelle": "Karte: © OpenStreetMap-Mitwirkende",
    },
    "topografisch": {
        "name": "Topografisch (Höhenlinien)",
        "adresse": "https://tile.opentopomap.org/{z}/{x}/{y}.png",
        "quelle": "Karte: © OpenStreetMap-Mitwirkende, SRTM | © OpenTopoMap (CC-BY-SA)",
    },
    "satellit": {
        "name": "Satellit",
        # Achtung: Bei Esri ist die Reihenfolge {y}/{x} statt {x}/{y}
        "adresse": "https://server.arcgisonline.com/ArcGIS/rest/services/"
                   "World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "quelle": "Luftbild: © Esri, Maxar, Earthstar Geographics",
    },
    "schlicht": {
        "name": "Schlicht (ohne Karte)",
        "adresse": None,      # keine Kacheln, wir zeichnen selbst
        "quelle": "",
    },
}

# Abstand zwischen Route und Kartenrand in Pixeln (= Ausschnitt der Karte)
RAENDER = {
    "klein": 40,
    "mittel": 100,
    "groß": 200,
}

# Hintergrundfarbe für den Stil "schlicht"
SCHLICHT_HINTERGRUND = "#f1ede4"

# Die Kartendienste möchten wissen, welches Programm die Kacheln lädt.
# Das schicken wir als "User-Agent" mit.
KOPFZEILEN = {"User-Agent": "WanderPosterGenerator/1.0 (Uni-Projekt HAW Hamburg)"}


def mittlerer_breitengrad(wanderung):
    """Gibt den Breitengrad in der Mitte der Route zurück."""
    breiten = [punkt.lat for punkt in wanderung.punkte]
    return (min(breiten) + max(breiten)) / 2


def kachel_karte_erstellen(wanderung, stil, breite, hoehe, farbe, dicke, rand):
    """WEG A: Erstellt eine Karte aus Online-Kacheln mit staticmap.

    Wird für die Stile standard, topografisch und satellit benutzt.
    Rückgabe: (Kartenbild, Meter pro Pixel)
    """
    # 1. Karten-Objekt anlegen: Größe, Rand und Adresse des Kartendienstes.
    #    StaticMap ist eine Klasse aus der Bibliothek, "karte" ist ein Objekt davon.
    karte = StaticMap(
        breite, hoehe,
        padding_x=rand, padding_y=rand,
        url_template=KARTENSTILE[stil]["adresse"],
        headers=KOPFZEILEN,
        tile_request_timeout=10,   # höchstens 10 Sekunden pro Kachel warten
    )

    # 2. Route eintragen (gezeichnet wird erst in Schritt 4)
    koordinaten = wanderung.koordinaten()

    # Weißer "Schatten" unter der Route, damit sie auf jeder Karte gut sichtbar ist
    karte.add_line(Line(koordinaten, "white", dicke + 4))
    # Die eigentliche Route in der gewählten Farbe
    karte.add_line(Line(koordinaten, farbe, dicke))

    # 3. Start und Ziel als Kreise (erst weiß und etwas größer = weißer Rand)
    start = koordinaten[0]
    ziel = koordinaten[-1]
    groesse = dicke * 2
    karte.add_marker(CircleMarker(start, "white", groesse + 6))
    karte.add_marker(CircleMarker(start, START_FARBE, groesse))
    karte.add_marker(CircleMarker(ziel, "white", groesse + 6))
    karte.add_marker(CircleMarker(ziel, ZIEL_FARBE, groesse))

    # 4. Jetzt werden die Kacheln geladen und das Bild gezeichnet: staticmap wählt
    #    die Zoomstufe, lädt die Kacheln, setzt sie zusammen und zeichnet die Route.
    #    Ohne Internet wirft staticmap einen RuntimeError.
    try:
        bild = karte.render()
    except RuntimeError:
        raise RuntimeError(
            "Die Karte konnte nicht geladen werden. Besteht eine Internetverbindung? "
            "Tipp: Der Kartenstil „Schlicht“ funktioniert auch ohne Internet."
        )

    # 5. staticmap merkt sich die gewählte Zoomstufe in karte.zoom.
    # Daraus berechnen wir für den Maßstab, wie viele Meter ein Pixel sind.
    meter_pro_pixel = meter_pro_pixel_berechnen(karte.zoom, mittlerer_breitengrad(wanderung))
    return bild.convert("RGB"), meter_pro_pixel


def schlichte_karte_erstellen(wanderung, breite, hoehe, farbe, dicke, rand):
    """WEG B: Zeichnet die Route ohne Kartenhintergrund auf eine einfarbige Fläche.

    Wird für den Stil "schlicht" benutzt und braucht kein Internet.

    Hier rechnen wir die Koordinaten selbst in Pixel um:
      - x = Längengrad * cos(mittlerer Breitengrad)
        (Längengrade liegen weiter im Norden enger zusammen, der cos-Faktor
        gleicht das aus, damit die Route nicht in die Breite gezogen wird)
      - y = Breitengrad
    Dann wird alles so vergrößert, dass die Route genau in das Bild passt.

    Rückgabe: (Kartenbild, Meter pro Pixel)
    """
    # 1. Koordinaten in x/y-Werte umrechnen (x mit cos-Faktor gegen Verzerrung)
    faktor = math.cos(math.radians(mittlerer_breitengrad(wanderung)))
    xs = [punkt.lon * faktor for punkt in wanderung.punkte]
    ys = [punkt.lat for punkt in wanderung.punkte]

    # 2. Größe der Route bestimmen
    # Kleinster x-Wert (ganz links) und größter y-Wert (ganz oben = Norden)
    x_min = min(xs)
    y_max = max(ys)

    # Wie groß ist die Route (in Grad)? max(..., 0.0001) verhindert eine
    # Division durch 0, falls alle Punkte auf einer Linie liegen.
    spanne_x = max(max(xs) - x_min, 0.0001)
    spanne_y = max(y_max - min(ys), 0.0001)

    # 3. Maßstab berechnen: Wie viele Pixel entspricht ein Grad?
    # Platz im Bild ohne den Rand
    platz_x = breite - 2 * rand
    platz_y = hoehe - 2 * rand

    # Pixel pro Grad: der kleinere Wert, damit die Route in beide Richtungen passt
    pixel_pro_grad = min(platz_x / spanne_x, platz_y / spanne_y)

    # Verschiebung, damit die Route in der Mitte des Bildes liegt
    versatz_x = rand + (platz_x - spanne_x * pixel_pro_grad) / 2
    versatz_y = rand + (platz_y - spanne_y * pixel_pro_grad) / 2

    # 4. Jeden Punkt in Pixel umrechnen.
    # Bei y wird "umgedreht" (y_max - y), weil im Bild y=0 oben ist,
    # auf der Karte aber Norden (großer Breitengrad) oben sein soll.
    pixel_punkte = []
    for x, y in zip(xs, ys):
        px = versatz_x + (x - x_min) * pixel_pro_grad
        py = versatz_y + (y_max - y) * pixel_pro_grad
        pixel_punkte.append((px, py))

    # 5. Leeres Bild anlegen und die Route als Linie einzeichnen
    bild = Image.new("RGB", (breite, hoehe), SCHLICHT_HINTERGRUND)
    zeichner = ImageDraw.Draw(bild)
    zeichner.line(pixel_punkte, fill=farbe, width=dicke, joint="curve")

    # 6. Start und Ziel als Kreise mit weißem Rand
    radius = dicke * 1.5
    for (px, py), kreis_farbe in [(pixel_punkte[0], START_FARBE), (pixel_punkte[-1], ZIEL_FARBE)]:
        zeichner.ellipse([px - radius, py - radius, px + radius, py + radius],
                         fill=kreis_farbe, outline="white", width=3)

    # 7. Meter pro Pixel für den Maßstab:
    #    Ein Grad Breitengrad sind überall auf der Erde ca. 111 320 Meter
    meter_pro_pixel = 111320 / pixel_pro_grad
    return bild, meter_pro_pixel


def karte_erstellen(wanderung, stil, breite, hoehe, farbe, dicke, rand_name):
    """Erstellt das Kartenbild mit der eingezeichneten Route.

    Parameter:
        wanderung: Wanderung-Objekt aus gpx_import.py
        stil:      Schlüssel aus KARTENSTILE, z. B. "topografisch"
        breite, hoehe: Größe des Kartenbildes in Pixeln
        farbe:     Farbe der Route als Text, z. B. "#d62828"
        dicke:     Liniendicke der Route in Pixeln
        rand_name: Schlüssel aus RAENDER, z. B. "mittel"
    Rückgabe:
        (Kartenbild, Meter pro Pixel, Quellenangabe)
    """
    # 1. Prüfen, ob es den gewählten Kartenstil überhaupt gibt
    if stil not in KARTENSTILE:
        raise ValueError(f"Unbekannter Kartenstil: {stil}")

    # 2. Rand (Ausschnitt) im Dictionary nachschlagen, z. B. "mittel" -> 100 Pixel
    rand = RAENDER.get(rand_name, RAENDER["mittel"])

    # 3. Weiche: welcher Weg wird genommen?
    if stil == "schlicht":
        # Weg B: nur die Route, ohne Kartenkacheln (funktioniert ohne Internet)
        bild, meter_pro_pixel = schlichte_karte_erstellen(wanderung, breite, hoehe, farbe, dicke, rand)
    else:
        # Weg A: echte Karte aus Online-Kacheln (standard, topografisch, satellit)
        bild, meter_pro_pixel = kachel_karte_erstellen(wanderung, stil, breite, hoehe, farbe, dicke, rand)

    # Rückgabe an Alise: Bild, Meter pro Pixel (für den Maßstab) und Quellenangabe
    return bild, meter_pro_pixel, KARTENSTILE[stil]["quelle"]


# Kleiner Test (aus dem Hauptordner): python -m david.karte
if __name__ == "__main__":
    from david.gpx_import import gpx_einlesen
    test_wanderung = gpx_einlesen("beispiele/harz_brocken.gpx")
    test_bild, test_mpp, _ = karte_erstellen(test_wanderung, "schlicht", 800, 600, "#d62828", 5, "mittel")
    import os
    os.makedirs("ausgabe", exist_ok=True)
    test_bild.save("ausgabe/test_karte.png")
    print("Gespeichert: ausgabe/test_karte.png, Meter pro Pixel:", round(test_mpp, 1))
