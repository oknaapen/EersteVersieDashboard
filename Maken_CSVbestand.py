import pandas as pd
import random
import uuid
from datetime import datetime, timedelta

def generate_complaint_data(aantal=20000, bestandsnaam="klacht.csv"):
    voornamen = ["Sophie", "Daan", "Liam", "Emma", "Julia", "Noah", "Mila", "Tess", "Finn", "Sara"]
    achternamen = ["Jansen", "de Vries", "Bakker", "van Dijk", "Visser", "Smit", "Meijer", "Mulder", "de Boer", "Koster"]
    domeinen = ["@gmail.com", "@hotmail.com", "@outlook.com", "@voorbeeld.nl"]
    status_lijst = ["Afgehandelde klacht", "In behandeling", "Heropend", "Geannuleerd", "Openstaand"]

    tevredenheidsniveaus = ["Zeer tevreden", "Tevreden", "Neutraal", "Ontevreden", "Zeer ontevreden", "Ontevreden", "Ontevreden"]

    gebied_wijk_dict = {
        "Centrum": ["Binnenstad", "De Bergen", "Fellenoord", "TU-terrein", "Witte Dame"],
        "Stratum": ["Oud-Stratum", "Kortonjo", "Putten"],
        "Tongelre": ["De Laak", "Oud-Tongelre"],
        "Woensel Zuid": ["Oud-Woensel", "Erp", "Begijnenbroek"],
        "Woensel Noord": ["Ontginning", "Achtse Molen", "Aanschot", "Dommelbeemd"],
        "Strijp": ["Oud-Strijp", "Halve Maan", "Meerhoven"],
        "Gestel": ["Rozenknopje", "Oud-Gestel", "Oud Kasteel"]
    }

    gebied_gewichten = {
        "Centrum": 30,
        "Stratum": 15,
        "Tongelre": 15,
        "Woensel Zuid": 23,
        "Woensel Noord": 15,
        "Strijp": 8,
        "Gestel": 4
            }

    categorie_dict = {
        "Afval en reiniging": [
            ("Zwerfvuil", "5 dagen", "Team Reiniging"),
            ("Niet geleegde containers", "3 dagen", "Team Reiniging"),
            ("Dumping grofvuil", "5 dagen", "Team Reiniging"),
            ("Verstopte putten", "3 dagen", "Team Reiniging")
        ],
        "Verkeer en wegen": [
            ("Gat in de weg", "5 dagen", "Team Wegen & Verkeer"),
            ("Verkeersbord ontbreekt/beschadigd", "10 dagen", "Team Wegen & Verkeer"),
            ("Losliggende stoeptegel", "10 dagen", "Team Wegen & Verkeer"),
            ("Drukte op de weg", "N.v.t. (signaal)", "Team Wegen & Verkeer")
        ],
        "Straatverlichting": [
            ("Lantaarnpaal kapot", "10 dagen", "Team Verlichting"),
            ("Knipperende verlichting", "10 dagen", "Team Verlichting")
        ],
        "Groenvoorziening": [
            ("Overhangend groen", "14 dagen", "Team Groenvoorziening"),
            ("Omgevallen boom", "2 dagen", "Team Groenvoorziening"),
            ("Onkruidbestrijding", "14 dagen", "Team Groenvoorziening")
        ],
        "Spelen en sport": [
            ("Beschadigde speeltoestellen", "5 dagen", "Team Spelen & Sport"),
            ("Vervuiling sportveld", "7 dagen", "Team Spelen & Sport")
        ],
        "Geluidsoverlast": [
            ("Horeca", "7 dagen", "Team Handhaving"),
            ("Bouw/sloopwerkzaamheden", "7 dagen", "Team Handhaving")
        ],
        "Vandalisme": [
            ("Beschadigde objecten", "5 dagen", "Team Handhaving"),
            ("Graffiti", "10 dagen", "Team Handhaving")
        ],
        "Illegale activiteiten": [
            ("Hennepkwekerijen", "1 dag (melden politie)", "Team Handhaving"),
            ("Woningdelen zonder vergunning", "7 dagen", "Team Handhaving")
        ],
        "Bouwvergunning": [
            ("Overlast door projecten", "7 dagen", "Team Bouw & Toezicht"),
            ("Illegale aanbouw", "14 dagen", "Team Bouw & Toezicht")
        ],
        "Woningtoezicht": [
            ("Achterstallig onderhoud", "10 dagen", "Team Bouw & Toezicht"),
            ("Ongedierte", "5 dagen", "Team Bouw & Toezicht")
        ],
        "Parkeerproblemen": [
            ("Foutparkeren", "1 dag", "Team Handhaving"),
            ("Parkeerplaatsen geblokkeerd", "1 dag", "Team Handhaving")
        ],
        "Openbaar vervoer": [
            ("Beschadigde haltes", "7 dagen", "Team Wegen & Verkeer"),
            ("Klacht over dienstverlening", "5 dagen", "Team Wegen & Verkeer")
        ],
        "Zorg en ondersteuning": [
            ("Wmo/aanvragen", "14 dagen", "Team Sociaal Domein"),
            ("Klachten over hulpverleners", "10 dagen", "Team Sociaal Domein")
        ],
        "Jeugdzorg": [
            ("Kindermishandeling (melding)", "1 dag", "Team Sociaal Domein"),
            ("Ondersteuning bij opvoeding", "14 dagen", "Team Sociaal Domein")
        ],
        "Dieren": [
            ("Dode of gewonde dieren - op straat", "1 dag", "Team Handhaving"),
            ("Dode of gewonde dieren - in openbaar groen", "2 dagen", "Team Handhaving"),
            ("Overlast door dieren", "7 dagen", "Team Handhaving")
        ],
    }

    categorie_gewichten = {
        "Afval en reiniging": 50,
        "Verkeer en wegen": 5,
        "Straatverlichting": 3,
        "Groenvoorziening": 1,
        "Spelen en sport": 1,
        "Geluidsoverlast": 4,
        "Vandalisme": 4,
        "Illegale activiteiten": 3,
        "Bouwvergunning": 3,
        "Woningtoezicht": 4,
        "Parkeerproblemen": 6,
        "Openbaar vervoer": 4,
        "Zorg en ondersteuning": 5,
        "Jeugdzorg": 3,
        "Dieren": 4
    }

    bron_dict = {
        "telefoon": 30,
        "internet": 30,
        "app": 80,
        "formulier": 15,
        "onbekend": 5
    }


    start_datum = datetime(2025, 1, 28)
    eind_datum = datetime(2025, 2, 26)
    delta_dagen = (eind_datum - start_datum).days

    data = []

    for i in range(aantal):
        voornaam = random.choice(voornamen)
        achternaam = random.choice(achternamen)
        naam = f"{voornaam} {achternaam}"

        domein = random.choices(domeinen, weights=[40, 30, 20, 10])[0]
        email = f"{voornaam.lower()}.{achternaam.lower()}{random.randint(1,999)}{domein}" if random.random() > 0.1 else None
        telefoon = f"06{random.randint(10000000, 99999999)}" if random.random() > 0.15 else None

        hoofdcategorie = random.choices(
            population=list(categorie_dict.keys()),
            weights=[categorie_gewichten[k] for k in categorie_dict.keys()]
        )[0]

        subcategorie, behandeltermijn, standaard_team = random.choice(categorie_dict[hoofdcategorie])

        status = random.choice(status_lijst)

        bron = random.choices(list(bron_dict.keys()), weights=bron_dict.values())[0]

        gebied = random.choices(
            population=list(gebied_wijk_dict.keys()),
            weights=[gebied_gewichten[k] for k in gebied_wijk_dict.keys()]
        )[0]


        wijk = random.choice(gebied_wijk_dict[gebied])



        tevredenheid = random.choice(tevredenheidsniveaus) if status == "Afgehandelde klacht" else None

        if random.random() > 0.95:
            andere_teams = [t for t in {
                "Team Reiniging", "Team Groenvoorziening", "Team Wegen & Verkeer", "Team Verlichting",
                "Team Spelen & Sport", "Team Handhaving", "Team Bouw & Toezicht", "Team Sociaal Domein"
            } if t != standaard_team]
            team = random.choice(andere_teams)
            wijziging = 1
        else:
            team = standaard_team
            wijziging = 0

        datum = start_datum + timedelta(days=random.randint(0, delta_dagen))

        # Voeg behandelsduur toe alleen als de klacht is afgehandeld
        if status == "Afgehandelde klacht":
            behandelsduur = random.randint(1, 20)  # Aantal dagen om klacht af te handelen
        else:
            behandelsduur = None

        data.append({
            "indexnummer": i,
            "klachtnummer": f"KL{str(uuid.uuid4())[:8].upper()}",
            "naam": naam,
            "email": email,
            "telefoon": telefoon,
            "hoofdcategorie": hoofdcategorie,
            "subcategorie": subcategorie,
            "behandeltermijn": behandeltermijn,
            "status": status,
            "bron": bron,
            "gebied": gebied,
            "wijk": wijk,
            "tevredenheid": tevredenheid,
            "team": team,
            "wijziging": wijziging,
            "datum": datum.strftime("%Y-%m-%d"),
            "behandelsduur": behandelsduur
        })

    df = pd.DataFrame(data)
    df.to_csv(bestandsnaam, index=False)
    print(f"{aantal} regels succesvol opgeslagen in '{bestandsnaam}'.")


# Voorbeeld van gebruik:
generate_complaint_data(4000, "test_1.csv")

["Alles"] + sorted(df["team"].dropna().unique())