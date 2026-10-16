import os

from cryptography.fernet import Fernet, InvalidToken


def generate_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as f:
        f.write(key)


def read_key():
    with open("key.key", "rb") as f:
        return f.read()


def encrypt(targets, key):
    fernet_key = Fernet(key)
    for target in targets:
        with open(target, "rb") as f:
            file_content = f.read()

        try:
            fernet_key.decrypt(file_content)
            print(f"{target} is already encrypted. Skipped.")
            continue
        except (InvalidToken, Exception):
            encrypted_content = fernet_key.encrypt(file_content)
            with open(target, "wb") as f:
                f.write(encrypted_content)
            print(f"{target} has been encrypted.")


if __name__ == '__main__':
    if not os.path.exists("key.key"):
        generate_key()

    key = read_key()
    targets = ["files/" + filename for filename in os.listdir("files")]

    encrypt(targets, key)
