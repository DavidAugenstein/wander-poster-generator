# =============================================================================
# start.py – startet den Wander Poster Generator
#
# Ausführen (im Hauptordner des Projekts):
#     python start.py
# Danach im Browser öffnen: http://localhost:5000
# Beenden: im Terminal Strg + C drücken.
# =============================================================================

from webserver.app import app

if __name__ == "__main__":
    print("Wander Poster Generator läuft. Im Browser öffnen: http://localhost:5000")
    # debug=True: Der Server startet bei jeder Code-Änderung automatisch neu.
    app.run(host="127.0.0.1", port=5000, debug=True)
