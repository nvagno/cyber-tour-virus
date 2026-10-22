# Le virus liste les cibles potentielles, sans les modifier.

import os

def lister_cibles(repertoire):
    virus_abs = os.path.abspath(__file__)
    cibles = []
    for nom in os.listdir(repertoire):
        chemin = os.path.join(repertoire, nom)
        if os.path.isfile(chemin) and chemin.endswith(".py") \
           and os.path.abspath(chemin) != virus_abs:
            cibles.append(chemin)
    return cibles

if __name__ == "__main__":
    repertoire = os.path.dirname(os.path.abspath(__file__))
    cibles = lister_cibles(repertoire)
    print(f"[ÉTAPE 1] {len(cibles)} cible(s) potentielle(s) :")
    for c in cibles:
        print(f"  - {os.path.basename(c)}")