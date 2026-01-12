import ee

def verifier_gee():
    etat = {"authentifie": False, "initialise": False}
    # Vérifie authentification
    try:
        ee.Authenticate()
        etat["authentifie"] = True
    except Exception as e:
        etat["authentifie"] = False

    # Vérifie initialisation
    try:
        ee.Initialize()
        etat["initialise"] = True
    except Exception:
        etat["initialise"] = False

    return etat
print(verifier_gee())
