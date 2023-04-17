import time
import requests
from cryptography.fernet import Fernet
import os

KEY = b'V9EetliiTqq6huT6kr5W4zA-7ssmHhxPLWHbVyH4JQM='
FOLDER_NAME = "Locked"

if not os.path.isdir(FOLDER_NAME):
    os.mkdir(FOLDER_NAME)

def encrypt(text):
    f = Fernet(KEY)
    return f.encrypt(text.encode()).decode()

def decrypt(text):
    f = Fernet(KEY)
    return f.decrypt(text.encode()).decode()

def lock_text():
    title = input("Enter a title for the text: ")
    text = input("Enter the text you want to lock: ")
    days = -1
    while days < 0:
        try:
            days = int(input("Enter the number of days you want to lock the text for: "))
        except ValueError:
            print("Please enter a valid integer value.")
    lock_time = int(time.time()) + days * 86400
    locked_text = f"{str(lock_time)}_{str(hash(text))[:3]}_{text}_{str(hash(text))[-3:]}"
    encrypted_text = encrypt(locked_text)
    with open(f"{FOLDER_NAME}/{title}.lock", "w") as f:
        f.write(encrypted_text)
    print(f"Text '{title}' locked successfully.")

def see_text():
    for i in range(5):
        try:
            response = requests.get("http://worldtimeapi.org/api/timezone/Asia/Karachi")
            if response.status_code == 200:
                current_time = int(response.json()["unixtime"])
                break
            else:
                print("Failed to retrieve current time.")
                return
        except requests.exceptions.RequestException:
            print("Failed to connect to time server.")
            time.sleep(2)
    else:
        print("Try again later")
        return
    print("Available locked texts:")
    files_list = []
    for filename in os.listdir(FOLDER_NAME):
        if filename.endswith(".lock"):
            with open(f'{FOLDER_NAME}/{filename}', "r") as f:
                encrypted_text = f.read()
                try:
                    locked_text = decrypt(encrypted_text)
                except:
                    continue
                parts = locked_text.split("_")
                if len(parts) == 4:
                    lock_time, start_hash, text, end_hash = parts
                    remaining_days = (int(lock_time) - current_time) // 86400
                    if remaining_days >= -1:
                        files_list.append(filename)
                        print(f"{len(files_list)}_ {filename[:-4]} - {remaining_days+1} days left")
    if len(files_list) == 0:
        input("No text locked yet.\nPress any key to go back")
        return
    
    text_num = int(input("Select text you want to unlock: "))
    filename = files_list[text_num-1]
    with open(f'{FOLDER_NAME}/{filename}', "r") as f:
        encrypted_text = f.read()
        locked_text = decrypt(encrypted_text)
        parts = locked_text.split("_")
        if len(parts) == 4:
            lock_time, start_hash, text, end_hash = parts
            if int(lock_time) <= current_time:
                print("Text unlocked successfully.")
                print(f"The text '{filename}' was: {text}")
                with open(f'{FOLDER_NAME}/{filename.split(".")[0]}.txt', "w") as file:
                    file.write(text)
                f.close()


                os.remove(f'{FOLDER_NAME}/{filename}')
            else:
                print("This text is not yet unlocked.")

while True:
    print("\nLockText options:")
    print("1. Lock Text")
    print("2. See Text")
    print("3. Quit")
    choice = input("Enter your choice (1-3): ")
    if choice == "1":
        lock_text()
    elif choice == "2":
        see_text()
    elif choice == "3":
        break
    else:
        print("Invalid choice. Please enter a number between 1 and 3.")
