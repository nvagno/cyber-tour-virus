import os

from cryptography.fernet import Fernet, InvalidToken

from encrypt import read_key


def decrypt(targets, key):
    fernet_key = Fernet(key)
    for target in targets:
        with open(target, "rb") as f:
            file_content = f.read()

        try:
            decrypted_content = fernet_key.decrypt(file_content)
            with open(target, "wb") as f:
                f.write(decrypted_content)
            print(f"{target} has been decrypted.")
        except (InvalidToken, Exception):
            print(f"{target} is not encrypted or the key is invalid. Skipped.")


if __name__ == '__main__':
    key = read_key()
    targets = ["files/" + filename for filename in os.listdir("files")]

    decrypt(targets, key)
