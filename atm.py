import random
import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ATM:
    # connection of db
    @staticmethod
    def connect_to_database():
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="ATM"
            )
            return conn
        except mysql.connector.Error as error:
            print("Error while connecting to the database:", error)
        return None
# send otp

    @staticmethod
    def send_otp_email(email, otp):
        sender_email = "shubhamrahile620@gmail.com"
        sender_password = "jkhthamxgykixqzh"
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        subject = "OTP for PIN Change"
        message = f"Your OTP to change the PIN: {otp}"

        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = email

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                print("OTP sent successfully.")
        except smtplib.SMTPException as e:
            print("Error sending OTP:", str(e))


    def __init__(self):
        self.accounts = []
        self.total_balance = 0
        self.current_account = None

    @staticmethod
    def generate_account_id():
        return random.randint(100, 999)

    # create new Account
    def create_account(self, name, balance, pin):
        account_id = self.generate_account_id()
        conn = self.connect_to_database()
        if conn is not None:
            cursor = conn.cursor()
            query = "INSERT INTO accounts (account_id, amount, pin, name) VALUES (%s, %s, %s, %s)"
            values = (account_id, balance, pin, name)
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            account = {
                "account_id": account_id,
                "name": name,
                "pin": pin,
                "balance": balance
            }
            self.accounts.append(account)
            self.total_balance += balance
            return account
        else:
            print("Failed to create an account. Please try again later.")
            return None

    # login user
    def login(self, account_id, pin):
        result = self.verify_pin(account_id, pin)
        if result:
            conn = self.connect_to_database()
            if conn is not None:
                cursor = conn.cursor()
                query = "SELECT * FROM accounts WHERE account_id = %s"
                cursor.execute(query, (account_id,))
                result = cursor.fetchone()
                cursor.close()
                conn.close()
                if result:
                    self.current_account = {
                        "account_id": result[0],
                        "pin": pin,
                        "balance": result[1]
                    }
                    return True
            print("Invalid account ID or PIN.")
        return False

# Verify PIN
    def verify_pin(self, account_id, pin):
        conn = self.connect_to_database()
        if conn is not None:
            cursor = conn.cursor()
            query = "SELECT * FROM accounts WHERE account_id = %s AND pin = %s"
            values = (account_id, pin)
            cursor.execute(query, values)
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            if result:
                return True
        return False

    # deposit operation
    def deposit(self, amount):
        if self.current_account:
            account_id = self.current_account["account_id"]
            conn = self.connect_to_database()
            if conn is not None:
                cursor = conn.cursor()
                query = "UPDATE accounts SET amount = amount + %s WHERE account_id = %s"
                values = (amount, account_id)
                cursor.execute(query, values)
                conn.commit()
                cursor.close()
                conn.close()
                self.current_account["balance"] += amount
                self.total_balance += amount
                print(f"Deposited {amount:.2f} successfully.\n")
            else:
                print("No account logged in.\n")
        else:
            print("No account logged in.\n")

    # withdraw operation
    def withdraw(self, amount):
        if self.current_account:
            account_id = self.current_account["account_id"]
            conn = self.connect_to_database()
            if conn is not None:
                cursor = conn.cursor()
                query = "UPDATE accounts SET amount = amount - %s WHERE account_id = %s"
                values = (amount, account_id)
                cursor.execute(query, values)
                conn.commit()
                cursor.close()
                self.current_account["balance"] -= amount
                self.total_balance -= amount
                print(f"Withdrawn {amount:.2f} successfully.\n")
            else:
                print("No account logged in.\n")
        else:
            print("No account logged in.\n")

#Account Information operation
    def display_account_info(self):
        if self.current_account:
            account_id = self.current_account["account_id"]
            conn = self.connect_to_database()
            if conn is not None:
                cursor = conn.cursor()
                query = "SELECT * FROM accounts WHERE account_id = %s"
                cursor.execute(query, (account_id,))
                result = cursor.fetchone()
                cursor.close()
                conn.close()
                if result:
                    print(f"Account ID: {result[0]}")
                    print(f"Account Holder: {result[3]}")
                    print(f"Balance: {result[1]:.2f}\n")
                else:
                    print("Account not found.\n")
            else:
                print("No account logged in.\n")
        else:
            print("No account logged in.\n")

#Change pin (update in db) operation
    def change_pin(self, pin):
        if self.current_account:
            entered_pin = input("Check Your PIN: ")
            if entered_pin == self.current_account["pin"]:
                new_pin = input("Enter your new PIN: ")
                email = input("Enter your email address: ")
                otp = random.randint(100000, 999999)
                self.send_otp_email(email, otp)
                entered_otp = input("Enter the OTP you received: ")
                if entered_otp == str(otp):
                    account_id = self.current_account["account_id"]
                    conn = self.connect_to_database()
                    if conn is not None:
                        cursor = conn.cursor()
                        query = "UPDATE accounts SET pin = %s WHERE account_id = %s"
                        values = (new_pin, account_id)
                        cursor.execute(query, values)
                        conn.commit()
                        cursor.close()
                        conn.close()
                        self.current_account["pin"] = new_pin
                        print("PIN changed successfully.\n")
                    else:
                        print("No account logged in.\n")
                else:
                    print("Incorrect OTP. PIN change aborted.\n")
            else:
                print("Incorrect PIN.\n")
        else:
            print("No account logged in.\n")


#Log out operation
    def logout(self):
        if self.current_account:
            self.current_account = None
            print("Logged out successfully.\n")
        else:
            print("No account logged in.\n")

# Check Total Account in(db)
    def get_total_accounts(self):
        conn = self.connect_to_database()
        if conn is not None:
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM accounts"
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            if result:
                total_accounts = result[0]
                return total_accounts
            else:
                return 0
        else:
            return 0

# Check Total Balance in(db)
    def get_total_balance(self):
        conn = self.connect_to_database()
        if conn is not None:
            cursor = conn.cursor()
            query = "SELECT SUM(amount) FROM accounts"
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            if result and result[0]:
                total_balance = result[0]
                return total_balance
            else:
                return 0.0
        else:
            return 0.0
    
# main Function 
def main():
    atm = ATM()   
    while True:
        print("########## Welcome TO ATM ##########")
        print("1. User Page")
        print("2. Admin Page")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            print("1. Create Account")
            print("2. Login Account")
            print("3. Exit")
            ch = input("Enter your choice: ")
            print(" ")
            if ch == "1":
                name = input("Enter account holder's name: ")
                balance = float(input("Enter initial balance: "))
                pin = input("Enter PIN: ")
                account = atm.create_account(name, balance, pin)
                print(f"Account created successfully! Account ID: {account['account_id']}\n")
                
            elif ch == "2":
                account_id = int(input("Enter account ID: "))
                pin = input("Enter PIN: ")
                if atm.login(account_id, pin):
                    print(f"Logged in successfully! Account ID: {account_id}\n")
                    while True:
                        print("########## MENU ##########")
                        print("1. Deposit")
                        print("2. Withdraw")
                        print("3. Account Information")
                        print("4. Change PIN")
                        print("5. Logout")

                        option = input("Enter your option: ")

                        if option == "1":
                            amount = float(input("Enter amount to deposit: "))
                            atm.deposit(amount)

                        elif option == "2":
                            amount = float(input("Enter amount to withdraw: "))
                            atm.withdraw(amount)

                        elif option == "3":
                            atm.display_account_info()

                        elif option == "4":
                            pin = input("Enter your current PIN: ")
                            atm.change_pin(pin)

                        elif option == "5":
                            atm.logout()
                            break
            elif ch == "3":
                continue
            else:
                print("Invalid choice. Please try again.\n")
        elif choice == "2":
            print("1. Total Account")
            print("2. Total balance")
            print("3. Exit")
            ch = input("Enter your choice: ")
            print(" ")
            if ch == "1":
                total_accounts = atm.get_total_accounts()
                print(f"Total Accounts: {total_accounts}\n")
            elif ch == "2":
                total_balance = atm.get_total_balance()
                print(f"Total Balance: {total_balance}\n")
            elif ch == "3":
                continue
            else:
                print("Invalid choice. Please try again.\n")
        elif choice == "3":
            print("Exit...")
            break
        else:
            print("Invalid choice. Please try again.\n")

#create database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="ATM"
 )

main()