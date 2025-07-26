# categorie_data.py

subcategorie_dict = {
    "Afval en reiniging": [
        "Zwerfvuil", "Niet geleegde containers", "Dumping grofvuil", "Verstopte putten"
    ],
    "Verkeer en wegen": [
        "Gat in de weg", "Verkeersbord ontbreekt/beschadigd", "Losliggende stoeptegel", "Drukte op de weg"
    ],
    "Straatverlichting": [
        "Lantaarnpaal kapot", "Knipperende verlichting"
    ],
    "Groenvoorziening": [
        "Overhangend groen", "Omgevallen boom", "Onkruidbestrijding"
    ],
    "Spelen en sport": [
        "Beschadigde speeltoestellen", "Vervuiling sportveld"
    ],
    "Geluidsoverlast": [
        "Horeca", "Bouw/sloopwerkzaamheden"
    ],
    "Vandalisme": [
        "Beschadigde objecten", "Graffiti"
    ],
    "Illegale activiteiten": [
        "Hennepkwekerijen", "Woningdelen zonder vergunning"
    ],
    "Bouwvergunning": [
        "Overlast door projecten", "Illegale aanbouw"
    ],
    "Woningtoezicht": [
        "Achterstallig onderhoud", "Ongedierte"
    ],
    "Parkeerproblemen": [
        "Foutparkeren", "Parkeerplaatsen geblokkeerd"
    ],
    "Openbaar vervoer": [
        "Beschadigde haltes", "Klacht over dienstverlening"
    ],
    "Zorg en ondersteuning": [
        "Wmo/aanvragen", "Klachten over hulpverleners"
    ],
    "Jeugdzorg": [
        "Kindermishandeling (melding)", "Ondersteuning bij opvoeding"
    ],
    "Dieren": [
        "Dode of gewonde dieren - op straat", "Dode of gewonde dieren - in openbaar groen", "Overlast door dieren"
    ]
}

# Mapping van alternatieve kolomnamen naar standaardnamen
kolom_aliases = {
    "hoofdcategorie": "hoofdcategorie",
    "hoofdonderwerp": "hoofdcategorie",
    "categorie": "hoofdcategorie",

    "subcategorie": "subcategorie",
    "subonderwerp": "subcategorie",

    "gebiedsdeel": "gebied",
    "locatie": "gebied",

    "wijknaam": "wijk",

    "teamnaam": "team",

    "tevreden": "tevredenheid",

    # enzovoort: voeg zelf realistische varianten toe
}
#horizontale scroll voor heel de dataset
#st.selectbox maand moet vervangen worden voor totaal aantal meldingen
#de thema's staan er veel te veel in


#filters die weg moeten
#subcategorie, Team
#weken op de x as moeten netter.




#lijngrafiek




