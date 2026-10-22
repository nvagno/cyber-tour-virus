import os
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

KEY_FILE = Path("key.key")
TARGET_DIR = Path("files")
LOCKED_SUFFIX = ".locked"
NOTE_NAME = "HOW_TO_RECOVER_FILES.txt"


def load_key(path: Path = KEY_FILE) -> bytes:
    return path.read_bytes()


def iter_locked(root: Path):
    for entry in root.rglob(f"*{LOCKED_SUFFIX}"):
        if entry.is_file():
            yield entry


def decrypt_file(fernet: Fernet, path: Path) -> bool:
    data = path.read_bytes()

    try:
        plaintext = fernet.decrypt(data)
    except InvalidToken:
        print(f"[SKIP] {path.name} : clé invalide ou fichier non chiffré")
        return False

    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(plaintext)
    original = path.with_suffix("")  # retire .locked
    os.replace(tmp, original)
    path.unlink(missing_ok=True)

    print(f"[OK]   {original.name}")
    return True


def decrypt_all(root: Path, key: bytes) -> tuple[int, int]:
    fernet = Fernet(key)
    ok = 0
    ko = 0
    for path in iter_locked(root):
        try:
            if decrypt_file(fernet, path):
                ok += 1
            else:
                ko += 1
        except OSError as exc:
            print(f"[ERR]  {path.name} : {exc}")
            ko += 1
    return ok, ko


def main() -> None:
    if not KEY_FILE.exists():
        raise SystemExit(f"Clé introuvable : {KEY_FILE}")

    if not TARGET_DIR.is_dir():
        raise SystemExit(f"Dossier cible introuvable : {TARGET_DIR}")

    key = load_key()
    ok, ko = decrypt_all(TARGET_DIR, key)
    print(f"\nTerminé : {ok} déchiffrés, {ko} échecs")


if __name__ == "__main__":
    main()