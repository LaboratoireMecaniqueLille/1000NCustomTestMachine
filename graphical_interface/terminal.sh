cd ..
source venv/bin/activate


export SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export BASE_DIR="$SCRIPTS_DIR/essai_traction"
cd "$BASE_DIR"

while true; do
    # Exécution de interface_graphique et récupération du choix
    path=$(python3 interface_graphique.py | tr -d '[:space:]')
    exit_code=$?
    echo "$path"

    # Gestion erreur interface
    if [ $exit_code -ne 0 ]; then
        echo "Critical error is the interface, stopping now" >&2
        break  # Sortie de la boucle
    fi

    # Gestion des cas de sortie
    if [[ "$path" == *protection_eprouvette ]]; then
        # Lance P2 et continue le cycle après
        python3 protection_eprouvette.py
        echo "Positioning of the jaw done, going back to the interface"
    elif [[ "$path" == *exit ]]; then
        # Lance P2 et continue le cycle après
        echo "Program closed, ending everything"
        break
    else
        # Mode normal avec lancement_essai + SORTIE
        message=$(python3 lancement_essai.py)
        if [[ "$message" == *probleme_toml_manquant ]]; then 
            echo "The .toml file to communicate experimental parameters was not found, the program stopped"
        elif [[ "$message" == *succes_test ]]; then  
            echo "Test done, closing now"
        fi
        break  # Sortie de la boucle après l'essai
        
    fi
done

deactivate
