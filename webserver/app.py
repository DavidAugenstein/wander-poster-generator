# =============================================================================
# app.py – der Webserver (Rahmen, geschrieben von Claude)
#
# Diese Datei müsst ihr nicht im Detail verstehen. Kurz gesagt:
#   - Flask startet ein kleines Programm, das auf Anfragen vom Browser wartet
#     (ähnlich wie die Event-Loop bei PyQt).
#   - Jede Funktion mit @app.route(...) darüber gehört zu einer Adresse.
#     Ruft der Browser diese Adresse auf, wird die Funktion ausgeführt
#     (ähnlich wie Signal/Slot bei PyQt).
#   - Die Webseite selbst steht in templates/index.html.
#
# Der einzige Kontakt zu unserem eigentlichen Programm ist die Funktion
# poster_erstellen() aus alise/poster_erstellen.py.
# =============================================================================

import os

from flask import Flask, render_template, request, send_from_directory

from alise.poster_erstellen import poster_erstellen, STANDARD_EINSTELLUNGEN
from david.karte import KARTENSTILE, RAENDER
from penelope.poster import FORMATE
from david.texte import SCHRIFTARTEN

# Wichtige Ordner (alle relativ zum Hauptordner des Projekts)
PROJEKT_ORDNER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUSGABE_ORDNER = os.path.join(PROJEKT_ORDNER, "ausgabe")
LETZTE_GPX = os.path.join(AUSGABE_ORDNER, "letzte_route.gpx")

app = Flask(__name__)


def auswahl_optionen():
    """Sammelt die Auswahlmöglichkeiten für das Formular aus den Projektdateien.

    So passt das Formular automatisch, wenn z. B. ein neuer Kartenstil in
    david/karte.py hinzukommt.
    """
    return {
        "kartenstile": {schluessel: stil["name"] for schluessel, stil in KARTENSTILE.items()},
        "formate": list(FORMATE.keys()),
        "raender": list(RAENDER.keys()),
        "schriftarten": list(SCHRIFTARTEN.keys()),
    }


def einstellungen_aus_formular(formular):
    """Liest die Eingaben aus dem Formular in ein Einstellungs-Dictionary.

    Häkchen (Checkboxen) werden nur mitgeschickt, wenn sie angehakt sind.
    """
    return {
        "titel": formular.get("titel", "").strip(),
        "untertitel": formular.get("untertitel", "").strip(),
        "kartenstil": formular.get("kartenstil", STANDARD_EINSTELLUNGEN["kartenstil"]),
        "routen_farbe": formular.get("routen_farbe", STANDARD_EINSTELLUNGEN["routen_farbe"]),
        "routen_dicke": formular.get("routen_dicke", STANDARD_EINSTELLUNGEN["routen_dicke"]),
        "format": formular.get("format", STANDARD_EINSTELLUNGEN["format"]),
        "rand": formular.get("rand", STANDARD_EINSTELLUNGEN["rand"]),
        "schriftart": formular.get("schriftart", STANDARD_EINSTELLUNGEN["schriftart"]),
        "hoehenprofil": "hoehenprofil" in formular,
        "statistik": "statistik" in formular,
        "massstab": "massstab" in formular,
    }


def seite_anzeigen(einstellungen, ergebnis=None, fehler=None, dateiname=""):
    """Zeigt die Webseite (templates/index.html) mit den aktuellen Werten an."""
    return render_template(
        "index.html",
        e=einstellungen,
        optionen=auswahl_optionen(),
        ergebnis=ergebnis,
        fehler=fehler,
        dateiname=dateiname,
    )


@app.route("/")
def startseite():
    """Adresse "/": zeigt das leere Formular mit den Standardeinstellungen."""
    return seite_anzeigen(STANDARD_EINSTELLUNGEN)


@app.route("/erstellen", methods=["POST"])
def erstellen():
    """Adresse "/erstellen": wird aufgerufen, wenn das Formular abgeschickt wird."""
    einstellungen = einstellungen_aus_formular(request.form)
    os.makedirs(AUSGABE_ORDNER, exist_ok=True)

    # Welche GPX-Datei soll benutzt werden?
    hochgeladen = request.files.get("gpx_datei")
    dateiname = request.form.get("letzter_dateiname", "")
    if hochgeladen and hochgeladen.filename:
        # Neue Datei hochgeladen: speichern, damit man sie erneut nutzen kann
        hochgeladen.save(LETZTE_GPX)
        gpx_pfad = LETZTE_GPX
        dateiname = hochgeladen.filename
    elif dateiname and os.path.exists(LETZTE_GPX):
        # Keine neue Datei, aber vorher schon eine hochgeladen
        gpx_pfad = LETZTE_GPX
    else:
        return seite_anzeigen(einstellungen, fehler="Bitte zuerst eine GPX-Datei auswählen.")

    # Unser eigentliches Programm aufrufen. Jeder Fehler wird als Meldung angezeigt.
    try:
        ergebnis = poster_erstellen(gpx_pfad, einstellungen, AUSGABE_ORDNER)
    except Exception as fehler:
        return seite_anzeigen(einstellungen, fehler=str(fehler), dateiname=dateiname)

    return seite_anzeigen(einstellungen, ergebnis=ergebnis, dateiname=dateiname)


@app.route("/ausgabe/<dateiname>")
def ausgabe_datei(dateiname):
    """Adresse "/ausgabe/...": liefert ein erzeugtes Poster an den Browser.

    Mit ?download=1 wird die Datei heruntergeladen statt angezeigt.
    """
    herunterladen = request.args.get("download") == "1"
    return send_from_directory(AUSGABE_ORDNER, dateiname, as_attachment=herunterladen)
