from cryptography.fernet import Fernet

KEY = Fernet.generate_key()

print(KEY)