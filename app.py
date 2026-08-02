import json
import os
import subprocess
import uuid
import sys 

from getpass import getpass

import bcrypt
from cryptography.fernet import Fernet


#set password for this user
USER_ENV_PASSWORD_NAME="account_manager_password"
stored_master_password=os.environ.get(USER_ENV_PASSWORD_NAME)

if stored_master_password is None:
    create_password_info="""
    ==== Account Manager ====
    Before starting:
    1) Create a password for using this app
    2) The password will be asked each time you open it
    3) The password length must be over 4 characters and less than 100!
    Your password: 
"""
    while True:
        new_master_password=getpass(create_password_info)
        if len(new_master_password) >= 5 and len(new_master_password) <= 100:
            subprocess.run(["setx",'account_password_enc_key',Fernet.generate_key()],check=True)
            subprocess.run(["setx",USER_ENV_PASSWORD_NAME,bcrypt.hashpw(new_master_password.encode(),bcrypt.gensalt())],check=True)
            print("Your app is quite ready to use... Just one step")
            print("Please restart the app!")
            sys.exit(0)
        else:
            print("The password length must be over 4 characters and less than 100!")
else:
    # user login
    while True:
     entered_master_password=getpass("Please enter your password: ")
     if bcrypt.checkpw(entered_master_password.encode(),stored_master_password.encode() ) :
         cipher=Fernet(os.environ.get('account_password_enc_key').encode())
         break 
     else:
         print("The password is wrong, please try again.")

    

DATABASE_FILE = "accounts.json"

# access account/json file 
if not os.path.exists(DATABASE_FILE):
    with open(DATABASE_FILE, "w") as file:
        json.dump({}, file)

with open(DATABASE_FILE, "r") as file:
    database = json.load(file)


def app_start():
    options="""
    ==== Account Manager ====
    1) Add Account
    2) Show Accounts
    3) Delete Account
    4) Exit

    Choose:: 
"""
    account_type_title="""
  What's the name of the service? 
"""
    choice=input(options)
  
    if choice == "1":
        account_type=input(account_type_title)
        username=input("username: ")
        password=input("password: ")
        add_new_account(username,password,account_type)
    elif  choice == "2":
        account_type=input(account_type_title)
        show_accounts(account_type)
    elif  choice == "3":
        account_type=input(account_type_title)
        username=input("username: ")
        delete_account(account_type,username) 
    elif  choice == "4":
        sys.exit(0)
    else:
        print("Invalid choice")
    





def save_database():
    with open("accounts.json","w") as f:
        json.dump(database,f,indent=4)





def add_new_account(username,password,account_type):
    new_account_id=str(uuid.uuid4())
    lower_account_type=account_type.lower()
    if(lower_account_type in database):
        service_modifying=database[lower_account_type]
        service_modifying[new_account_id]={
            "password":cipher.encrypt(password.encode()).decode(),
            "username":username
        }
    else:
        database[lower_account_type]={
            new_account_id:{
            "password":cipher.encrypt(password.encode()).decode(),
            "username":username
            }
        }
    save_database()
    print("New account added successfully")

    

def show_accounts(account_type="*"):
    
    if account_type == "*" or account_type == "":
        services=list(database.keys())
     

        for s in services:
            print(f"-----{s}")
            for a in database[s]:
                print(f"username: {database[s][a]['username']}")
                password = database[s][a]["password"].encode("utf-8")
                print(f"password: {cipher.decrypt(password).decode()}")
                print("---------")
            
        
                
        return
    if  account_type.lower() not in database:
        print("you have no account saved in the database  for this service")
        return 
    else:
        selected_service=database[account_type.lower()]
        for s in selected_service:
            print(f"username: {selected_service[s]['username']}")
            print(f"password: {cipher.decrypt(selected_service[s]['password']).decode()}")
            print("---------")

def delete_account(account_type,username):
    lower_account_type=account_type.lower()
    if lower_account_type in database:
        deleting_account=database[lower_account_type]
        for a in deleting_account:
            if deleting_account[a]["username"] == username:
                deleting_account.pop(a)
                save_database()
                print("The account deleted successfuly")
                break
        else:
            print("The username is invalid")
    else:
        print("you have no account saved in the database  for this service")


while True:
    app_start()




