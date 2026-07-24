import json
import uuid
import os
import subprocess
from getpass import getpass
import bcrypt
from cryptography.fernet import Fernet



#set password for this user
user_env_pass_name="account_manager_password"
user_env_master_password=os.environ.get(user_env_pass_name)

if user_env_master_password == None:
    create_passwrod_info="""
    ==== Account Manager ====
    Before starting:
    1) Create a password for using this app
    2) The password will be asked each time you open it
    3) The password length must be over 4 characters and less than 100!
    Your password: 
"""
    while True:
        new_user_master_pass=getpass(create_passwrod_info)
        if len(new_user_master_pass) >= 5 and len(new_user_master_pass) <= 100:
            subprocess.run(["setx",'account_password_enc_key',Fernet.generate_key()],check=True)
            subprocess.run(["setx",user_env_pass_name,bcrypt.hashpw(new_user_master_pass.encode(),bcrypt.gensalt())],check=True)
            print("Your app is quite ready to use... Just one step")
            print("Please restart the app!")
            exit(1)
        else:
            print("The password length must be over 4 characters and less than 100!")
else:
    # user login
    while True:
     user_master_pass=getpass("Please enter your password: ")
     if bcrypt.checkpw(user_master_pass.encode(),user_env_master_password.encode() ) :
         cipher=Fernet(os.environ.get('account_password_enc_key').encode())
         break 
     else:
         print("The password is wrong, please try again.")

    


# access account/json file 
# with open("accounts.json","r") as f:
#     database=json.load(f) 

if not os.path.exists("accounts.json"):
    with open("accounts.json", "w") as file:
        json.dump({}, file)

with open("accounts.json", "r") as file:
    database = json.load(file)

    
def appStart():
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
    user=str(input(options))
  
    if user == "1":
        account_type=str(input(account_type_title))
        username=str(input("username: "))
        password=str(input("password: "))
        add_new_account(username,password,account_type)
    if user == "2":
        account_type=str(input(account_type_title))
        show_accounts(account_type)
    if user == "3":
        account_type=str(input(account_type_title))
        username=str(input("username: "))
        delete_account(account_type,username) 
    if user == "4":
        exit(0)
    





def save_databse():
    with open("accounts.json","w") as f:
        json.dump(database,f,indent=4)





def add_new_account(username,password,accountType):
    new_account_id=str(uuid.uuid4())
    if(accountType.lower() in database):
        service_modifying=database[accountType]
        service_modifying[new_account_id]={
            "password":cipher.encrypt(password.encode()).decode(),
            "username":username
        }
    else:
        database[accountType]={
            new_account_id:{
            "password":cipher.encrypt(password.encode()).decode(),
            "username":username
            }
        }
    save_databse()
    print("New account addedd successfuly")

    

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
    if  account_type not in database:
        print("you have no account saved in the database  for this service")
        return 
    else:
        selected_service=database[account_type]
        for s in selected_service:
            print(f"username: {selected_service[s]['username']}")
            print(f"password: {cipher.decrypt(selected_service[s]['password']).decode()}")
            print("---------")

def delete_account(account_type,username):
    if account_type in database:
        deleting_account=database[account_type]
        print(deleting_account)
        for a in deleting_account:
            if deleting_account[a]["username"] == username:
                deleting_account.pop(a)
                save_databse()
                print("The account deleted successfuly")
                break
        else:
            print("The username is invalid")
    else:
        print("you have no account saved in the database  for this service")


while True:
    appStart()




