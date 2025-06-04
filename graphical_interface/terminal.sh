BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export BASE_DIR  # ToDo: Pourquoi l'exporter ? Utilisé ailleurs ?

while true; do

    # Exécution de interface_graphique.py et récupération du choix
    if ! python3 interface_graphique.py; then
        echo "Critical error is the interface, stopping now"
        exit 1  # Quitte le script Bash avec un code d'erreur
    fi

    commande=$(cat .parameters/commande.txt)
    echo "$path"  # ToDo: Elle sort d'où cette variable path ?

    # Gestion des cas de sortie
    if [[ "$commande" == *protection_eprouvette ]]; then
        # Lance protection_eprouvette.py et recommence le cycle après
        python3 protection_eprouvette.py

    elif [[ "$commande" == *exit ]]; then
        # Lance P2 et continue le cycle après
        echo "Program closed, ending everything"
        break

    elif [[ "$commande" == *demarrer_essai ]]; then
        # Mode normal avec lancement_essai + SORTIE
        python3 lancement_essai.py
        break  # Sortie de la boucle et arrêt après l'essai
        
    fi
done
