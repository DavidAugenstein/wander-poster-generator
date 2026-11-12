# =============================================================================
# statistik.py – Statistiken über die Wanderung berechnen
# Verantwortlich: Marlene
#
# Diese Datei berechnet aus den GPS-Punkten:
#   - die Gesamtstrecke in Kilometern
#   - Anstieg und Abstieg in Höhenmetern
#   - höchsten und tiefsten Punkt
#   - die reine Gehzeit
#   - die Anzahl der Wandertage
# =============================================================================

import math

# Mittlerer Erdradius in Metern
ERDRADIUS_M = 6371000

# Pausen, die länger als diese Zeit sind (z. B. die Nacht im Hotel),
# zählen nicht zur Gehzeit.
MAX_PAUSE_SEKUNDEN = 30 * 60


def entfernung_m(punkt1, punkt2):
    """Berechnet den Abstand zwischen zwei Punkten in Metern.

    Die Erde ist (fast) eine Kugel, darum kann man nicht einfach mit
    Pythagoras rechnen. Wir nutzen die Haversine-Formel, die den Abstand
    auf einer Kugeloberfläche berechnet:

        d = 2 * r * asin( sqrt( sin²(Δφ/2) + cos(φ1) * cos(φ2) * sin²(Δλ/2) ) )

    φ = Breitengrad, λ = Längengrad, r = Erdradius.
    Die Winkel müssen im Bogenmaß sein, darum math.radians().
    """
    phi1 = math.radians(punkt1.lat)
    phi2 = math.radians(punkt2.lat)
    delta_phi = math.radians(punkt2.lat - punkt1.lat)
    delta_lambda = math.radians(punkt2.lon - punkt1.lon)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    return 2 * ERDRADIUS_M * math.asin(math.sqrt(a))


def strecken_liste_km(wanderung):
    """Gibt für jeden Punkt die bis dahin gelaufene Strecke in km zurück.

    Beispiel: [0.0, 0.12, 0.25, ...]. Der letzte Wert ist die Gesamtstrecke.
    Diese Liste braucht auch das Höhenprofil (x-Achse).
    """
    strecken = [0.0]
    summe_m = 0.0
    # Immer zwei aufeinanderfolgende Punkte vergleichen: (0,1), (1,2), (2,3) ...
    for i in range(1, len(wanderung.punkte)):
        summe_m += entfernung_m(wanderung.punkte[i - 1], wanderung.punkte[i])
        strecken.append(summe_m / 1000)
    return strecken


def hoehenmeter_berechnen(wanderung):
    """Berechnet Anstieg und Abstieg in Metern.

    Anstieg = Summe aller positiven Höhenunterschiede zwischen zwei Punkten,
    Abstieg = Summe aller negativen Höhenunterschiede (als positive Zahl).
    Punkte ohne Höhenangabe werden übersprungen.
    Rückgabe: (anstieg, abstieg)
    """
    hoehen = wanderung.hoehen()
    anstieg = 0.0
    abstieg = 0.0
    for i in range(1, len(hoehen)):
        unterschied = hoehen[i] - hoehen[i - 1]
        if unterschied > 0:
            anstieg += unterschied
        else:
            abstieg -= unterschied
    return anstieg, abstieg


def gehzeit_sekunden(wanderung):
    """Berechnet die reine Gehzeit in Sekunden (lange Pausen zählen nicht).

    Gibt None zurück, wenn die GPX-Datei keine Zeiten enthält.
    """
    zeiten = [punkt.zeit for punkt in wanderung.punkte if punkt.zeit is not None]
    if len(zeiten) < 2:
        return None

    summe = 0
    for i in range(1, len(zeiten)):
        # Differenz zweier datetime-Werte ergibt ein timedelta-Objekt
        abstand = (zeiten[i] - zeiten[i - 1]).total_seconds()
        if 0 < abstand <= MAX_PAUSE_SEKUNDEN:
            summe += abstand
    return summe


def zeit_als_text(sekunden):
    """Macht aus Sekunden einen Text wie "9 Std. 5 Min."."""
    stunden = int(sekunden // 3600)
    minuten = int((sekunden % 3600) // 60)
    if stunden == 0:
        return f"{minuten} Min."
    return f"{stunden} Std. {minuten} Min."


def anzahl_tage(wanderung):
    """Zählt, an wie vielen verschiedenen Tagen gewandert wurde.

    Dafür kommen alle Kalenderdaten in ein set (Menge, Vorlesung 3a).
    Ein set speichert jeden Wert nur einmal, doppelte Tage fallen also weg.
    Gibt None zurück, wenn die GPX-Datei keine Zeiten enthält.
    """
    tage = set()
    for punkt in wanderung.punkte:
        if punkt.zeit is not None:
            tage.add(punkt.zeit.date())
    if len(tage) == 0:
        return None
    return len(tage)


def statistik_berechnen(wanderung):
    """Berechnet alle Statistiken und gibt sie als Dictionary zurück.

    Werte, die sich nicht berechnen lassen (z. B. Gehzeit ohne Zeitangaben),
    sind None.
    """
    statistik = {
        "distanz_km": strecken_liste_km(wanderung)[-1],
        "anstieg_m": None,
        "abstieg_m": None,
        "hoechster_punkt_m": None,
        "tiefster_punkt_m": None,
        "gehzeit": None,
        "tage": anzahl_tage(wanderung),
    }

    if wanderung.hat_hoehen():
        anstieg, abstieg = hoehenmeter_berechnen(wanderung)
        hoehen = wanderung.hoehen()
        statistik["anstieg_m"] = anstieg
        statistik["abstieg_m"] = abstieg
        statistik["hoechster_punkt_m"] = max(hoehen)
        statistik["tiefster_punkt_m"] = min(hoehen)

    sekunden = gehzeit_sekunden(wanderung)
    if sekunden is not None:
        statistik["gehzeit"] = zeit_als_text(sekunden)

    return statistik


# Kleiner Test (aus dem Hauptordner): python -m marlene.statistik
if __name__ == "__main__":
    from david.gpx_import import gpx_einlesen
    test_wanderung = gpx_einlesen("beispiele/harz_brocken.gpx")
    for schluessel, wert in statistik_berechnen(test_wanderung).items():
        print(schluessel, "=", wert)
