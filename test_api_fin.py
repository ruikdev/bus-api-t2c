import requests
import json


def test_api(stop_id):
    # Remplacez l'URL par l'adresse de votre serveur
    url = f"http://172.252.236.136:2064/{stop_id}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP

        data = response.json()

        print(f"Horaires pour l'arrêt {stop_id}:")
        print("-" * 50)

        if "departures" in data:
            for departure in data["departures"]:
                print(
                    f"Ligne {departure['ligne']:3} | {departure['destination']:20} | Départ : {departure['depart']:10} | {departure['info']}")

        if "perturbation" in data and data["perturbation"]:
            print("\n⚠️ ATTENTION :")
            print(data["perturbation"])

    except requests.RequestException as e:
        print(f"Erreur lors de la requête : {e}")
    except json.JSONDecodeError:
        print("Erreur lors du décodage de la réponse JSON")
    except Exception as e:
        print(f"Une erreur inattendue s'est produite : {e}")


# Test de l'API avec un ID d'arrêt
stop_id = "3377837159481522"  # Remplacez par l'ID de l'arrêt que vous voulez tester
test_api(stop_id)
