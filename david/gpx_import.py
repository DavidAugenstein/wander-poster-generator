# =============================================================================
# gpx_import.py – GPX-Datei einlesen
# Verantwortlich: David
#
# Diese Datei liest eine GPX-Datei (aufgezeichnete Wanderung) ein und macht
# daraus ein Wanderung-Objekt mit einer Liste von Punkten.
#
# Was ist eine GPX-Datei?
# Eine ganz normale Textdatei im sogenannten XML-Format. XML ist ähnlich wie
# HTML aufgebaut: Es gibt "Tags" in spitzen Klammern, die ineinander stecken.
# Ein einzelner Punkt der Wanderung sieht zum Beispiel so aus:
#
#   <trkpt lat="51.80" lon="10.61">
#       <ele>971.0</ele>                      <- Höhe in Metern
#       <time>2026-07-04T09:12:00Z</time>     <- Uhrzeit (UTC)
#   </trkpt>
#
# "trkpt" steht für "track point" (Punkt der aufgezeichneten Strecke).
# =============================================================================

# xml.etree.ElementTree ist in Python schon eingebaut (kein pip install nötig).
# Es liest eine XML-Datei und macht daraus einen "Baum" aus Elementen,
# den wir mit einer for-Schleife durchlaufen können.
import xml.etree.ElementTree as ET
from datetime import datetime


class GpxFehler(Exception):
    """Eigene Ausnahme für Probleme mit der GPX-Datei.

    Sie erbt von Exception (Vorlesung 4 und 6: eigene Ausnahmen über
    Vererbung). So kann der Webserver gezielt diese Fehler abfangen und dem
    Benutzer eine verständliche Meldung anzeigen.
    """
    pass


class Punkt:
    """Ein einzelner GPS-Punkt der Wanderung."""

    def __init__(self, lat, lon, hoehe=None, zeit=None):
        self.lat = lat        # Breitengrad (Nord/Süd), z. B. 51.80
        self.lon = lon        # Längengrad (Ost/West), z. B. 10.61
        self.hoehe = hoehe    # Höhe in Metern oder None, wenn nicht vorhanden
        self.zeit = zeit      # Zeitpunkt als datetime oder None


class Wanderung:
    """Die ganze Wanderung: ein Name und eine Liste von Punkt-Objekten."""

    def __init__(self, name, punkte):
        self.name = name
        self.punkte = punkte

    def koordinaten(self):
        """Gibt alle Punkte als Liste von (lon, lat)-Paaren zurück.

        Achtung Reihenfolge: Die Kartenbibliothek staticmap erwartet zuerst den
        Längengrad (lon), dann den Breitengrad (lat).
        """
        return [(punkt.lon, punkt.lat) for punkt in self.punkte]

    def hoehen(self):
        """Gibt alle vorhandenen Höhen als Liste zurück (Punkte ohne Höhe fehlen)."""
        return [punkt.hoehe for punkt in self.punkte if punkt.hoehe is not None]

    def hat_hoehen(self):
        """True, wenn mindestens ein Punkt eine Höhenangabe hat."""
        return len(self.hoehen()) > 0


def tag_name(element):
    """Gibt den Namen eines XML-Elements ohne "Namespace" zurück.

    GPX-Dateien schreiben vor jeden Tag-Namen eine Internetadresse, z. B.
    "{http://www.topografix.com/GPX/1/1}trkpt". Uns interessiert nur der
    Teil hinter der geschweiften Klammer, also "trkpt".
    """
    return element.tag.split("}")[-1]


def zahl_umwandeln(text):
    """Wandelt einen Text in eine Kommazahl um. Bei Fehlern kommt None zurück."""
    try:
        return float(text)
    except (TypeError, ValueError):
        # TypeError: text war None, ValueError: text war keine Zahl
        return None


def zeit_umwandeln(text):
    """Wandelt einen Zeit-Text wie "2026-07-04T09:12:00Z" in ein datetime um.

    Das "Z" am Ende bedeutet UTC (Weltzeit). datetime.fromisoformat versteht
    das "Z" erst ab Python 3.11, darum ersetzen wir es durch "+00:00".
    Ist der Text kaputt oder fehlt, kommt None zurück.
    """
    if text is None:
        return None
    try:
        return datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
    except ValueError:
        return None


def punkt_aus_element(element):
    """Macht aus einem <trkpt>-Element ein Punkt-Objekt."""
    # lat und lon stehen als Attribute direkt im Tag: <trkpt lat="..." lon="...">
    lat = zahl_umwandeln(element.get("lat"))
    lon = zahl_umwandeln(element.get("lon"))
    if lat is None or lon is None:
        raise GpxFehler("Ein Punkt in der GPX-Datei hat keine gültigen Koordinaten.")

    # Höhe und Zeit stehen als eigene Unter-Elemente im Punkt
    hoehe = None
    zeit = None
    for kind in element:
        if tag_name(kind) == "ele":
            hoehe = zahl_umwandeln(kind.text)
        elif tag_name(kind) == "time":
            zeit = zeit_umwandeln(kind.text)

    return Punkt(lat, lon, hoehe, zeit)


def gpx_einlesen(dateipfad):
    """Liest eine GPX-Datei ein und gibt ein Wanderung-Objekt zurück.

    Parameter:
        dateipfad: Pfad zur GPX-Datei, z. B. "beispiele/harz_brocken.gpx"
    Rückgabe:
        Wanderung-Objekt mit Name und Liste von Punkten
    Fehler:
        GpxFehler, wenn die Datei fehlt, kaputt ist oder zu wenig Punkte hat
    """
    # 1. Datei öffnen und als XML einlesen
    try:
        baum = ET.parse(dateipfad)
    except FileNotFoundError:
        raise GpxFehler(f"Die Datei wurde nicht gefunden: {dateipfad}")
    except ET.ParseError:
        raise GpxFehler("Die Datei ist keine gültige GPX-Datei (XML-Fehler).")

    # 2. Alle Elemente der Datei durchgehen (iter() geht durch den ganzen Baum)
    punkte = []
    name = None
    for element in baum.getroot().iter():
        tag = tag_name(element)
        # trkpt = Punkt einer aufgezeichneten Strecke,
        # rtept = Punkt einer geplanten Route (gibt es in manchen Apps)
        if tag == "trkpt" or tag == "rtept":
            punkte.append(punkt_aus_element(element))
        elif tag == "name" and name is None and element.text:
            # Der erste Name in der Datei ist meistens der Name der Wanderung
            name = element.text.strip()

    # 3. Prüfen, ob genug Punkte gefunden wurden (für eine Linie braucht man 2)
    if len(punkte) < 2:
        raise GpxFehler("Die GPX-Datei enthält keine oder zu wenige Wegpunkte.")

    if name is None:
        name = "Meine Wanderung"

    return Wanderung(name, punkte)


# Kleiner Test: Diese Datei direkt ausführen (aus dem Hauptordner):
#   python -m david.gpx_import
if __name__ == "__main__":
    wanderung = gpx_einlesen("beispiele/harz_brocken.gpx")
    print("Name:", wanderung.name)
    print("Anzahl Punkte:", len(wanderung.punkte))
    erster = wanderung.punkte[0]
    print("Erster Punkt:", erster.lat, erster.lon, erster.hoehe, erster.zeit)
