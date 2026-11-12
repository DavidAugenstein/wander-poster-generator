# Wander Poster Generator

Uni-Abschlussprojekt im Fach Programmieren 1 (Python, HAW Hamburg).

Das Programm liest eine Wanderroute (GPX-Datei) ein, zeichnet sie auf eine Karte und
erstellt daraus ein Poster mit Höhenprofil, Statistik, Maßstab und eigenem Titel.
Bedient wird es über den Browser.

## Installieren und starten

Voraussetzung: Python ist installiert (wie in der Vorlesung).

**Windows, ganz einfach:**
1. `installieren.bat` doppelklicken (nur einmal nötig, lädt flask, staticmap und Pillow)
2. `starten.bat` doppelklicken
3. Im Browser öffnen: **http://localhost:5000**
4. Beenden: das schwarze Fenster schließen

**Im Terminal (Windows, Mac, Linux)**, im Hauptordner des Projekts:
```
pip install -r requirements.txt
python start.py
```
Beenden mit `Strg + C`. (Auf dem Mac ggf. `pip3` und `python3` schreiben.)

**In PyCharm:** Projektordner öffnen. PyCharm erkennt `requirements.txt` und zeigt oben
einen gelben Hinweis „Install requirements“ – draufklicken. Danach `start.py` öffnen und auf
den grünen Pfeil klicken.

Zum Ausprobieren ohne eigene GPX-Datei: `beispiele/harz_brocken.gpx` im Formular auswählen.

**Tests** (ohne Internet, im Hauptordner): `python tests.py`

## Ordnerstruktur

| Ordner / Datei | Inhalt |
|---|---|
| `start.py` | startet das Programm |
| `tests.py` | einfache Tests für alle Dateien |
| `installieren.bat`, `starten.bat` | Doppelklick-Dateien für Windows |
| `webserver/` | Webseite und Flask-Server (Rahmen) |
| `david/` | GPX einlesen, Karte, Texte |
| `marlene/` | Statistik, Höhenprofil |
| `alise/` | Hauptablauf, Maßstab |
| `penelope/` | Posterformat und Layout, Routendesign, Speichern |
| `schriften/` | Schriftarten (freie Lizenz) |
| `beispiele/` | Beispielroute zum Testen |
| `ausgabe/` | erzeugte Poster (wird automatisch angelegt, nicht in Git) |

## Regeln

- Code bleibt einfach und verständlich (KISS, DRY).
- Jede Funktion und jeder Abschnitt bekommt einen kurzen Erklärungstext.
- Code, der über die Vorlesung hinausgeht oder mit KI-Hilfe entstanden ist, wird im Code erklärt.

## Team

David Augenstein, Marlene, Penélope und Alise.
