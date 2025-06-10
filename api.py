from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def scrape_t2c_horaires_theoriques(stop_id):
    url = f"https://www.t2c.fr/admin/synthese?SERVICE=page&p=17732927961956359&roid={stop_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        table = soup.find('table', class_='services')
        if not table:
            return None, "Tableau des horaires non trouvé"

        departures = []
        current_hour = None

        for row in table.find_all('tr'):
            # Récupère l'heure si présente (colonne avec class 'hour')
            hour_cell = row.find('td', class_='hour')
            if hour_cell:
                current_hour = hour_cell.text.strip().zfill(2)  # pour garder 2 chiffres

            # Récupère les minutes (colonne avec class 'minutes')
            minute_cell = row.find('td', class_='minutes')
            if not minute_cell or current_hour is None:
                continue
            minute = minute_cell.text.strip().zfill(2)

            # Ligne : récupère l'image dans la colonne 'line'
            line_cell = row.find('td', class_='line')
            line = "Inconnu"
            if line_cell:
                img = line_cell.find('img')
                if img and 'src' in img.attrs:
                    match = re.search(r'ligne-([a-zA-Z0-9]+)\.jpg', img['src'])
                    if match:
                        line = match.group(1)

            # Destination : récupère le texte dans la colonne 'place'
            place_cell = row.find('td', class_='place')
            destination = place_cell.text.strip() if place_cell else "Non spécifiée"

            # Ajoute le résultat
            departures.append({
                'ligne': line,
                'heure': f"{current_hour}:{minute}",
                'destination': destination
            })

        return departures, None

    except requests.RequestException as e:
        return None, f"Erreur lors de la requête : {e}"
    except Exception as e:
        return None, f"Une erreur inattendue s'est produite : {e}"

@app.route('/horairetheorique/<stop_id>')
def get_horaires_theoriques(stop_id):
    resultats, erreur = scrape_t2c_horaires_theoriques(stop_id)

    if resultats is None:
        return jsonify({"error": erreur}), 400

    return jsonify({"horaires": resultats})

def scrape_t2c_horaires(stop_id):
    url = f"http://qr.t2c.fr/qrcode?_stop_id={stop_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        table = soup.find('table')
        if not table:
            return None, None

        departures = []
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) == 4:
                departure = {
                    'ligne': cols[0].text.strip(),
                    'destination': cols[1].text.strip() or "Non spécifiée",
                    'depart': cols[2].text.strip() or "Non spécifié",
                    'info': cols[3].text.strip()
                }
                departures.append(departure)

        warning = soup.find('h3', string=lambda t: t and "Arrêt perturbé ou reporté" in t)
        perturbation = warning.text.strip() if warning else None

        return departures, perturbation

    except requests.RequestException as e:
        return None, f"Erreur lors de la requête : {e}"
    except Exception as e:
        return None, f"Une erreur inattendue s'est produite : {e}"

@app.route('/horaire/<stop_id>')
def get_horaires(stop_id):
    resultats, perturbation = scrape_t2c_horaires(stop_id)

    if resultats is None:
        return jsonify({"error": perturbation}), 400

    return jsonify({
        "departures": resultats,
        "perturbation": perturbation
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
