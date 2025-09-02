#!/bin/bash

. /home/tensiletest/venv/bin/activate 
#This path has to be adapted to the path of your venv, but in any case it must 
#start by ". " and end by "venv/bin/activate"

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export BASE_DIR 

while true; do
    
    # Executing interface_graphique.py
    if ! python3 interface_graphique.py; then
        echo "Critical error is the interface, stopping now"
        exit 1  # Stops the bash script with an error code
    fi

    commande=$(cat .parameters/commande.txt)

    # Managing the different exit options
    if [[ "$commande" == *protection_eprouvette ]]; then
        # Starts protection_eprouvette.py and start the cycle again after
        python3 protection_eprouvette.py

    elif [[ "$commande" == *exit ]]; then
        # Stops everything because interface_graphique.py was stoppped 
        #through the cross
        echo "Program closed, ending everything"
        break

    elif [[ "$commande" == *demarrer_essai ]]; then
        # Starts protection_eprouvette.py and stops the cycle
        python3 lancement_essai.py
        break  
        
    fi
done
