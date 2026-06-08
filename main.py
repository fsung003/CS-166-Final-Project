import os
import psycopg2

username = os.getlogin() 
db_name = f"{username}_DB"

try:
    #Connect via TCP network using your username
    conn = psycopg2.connect(
        dbname=db_name,
        user=username,
        host="127.0.0.1",  
        port="32237"       
    )
    cursor = conn.cursor()
    print(f"Successfully connected to university database: {db_name} on port 32237!")
except Exception as e:
    try:
        # Fallback to the 'postgres' user if username is blocked
        conn = psycopg2.connect(
            dbname=db_name,
            user="postgres",
            host="127.0.0.1",
            port="32237"
        )
        cursor = conn.cursor()
        print(f"Successfully connected to university database: {db_name} (as postgres) on port 32237!")
    except Exception as fallback_error:
        print(f"Database Connection Failed!\n")
        print(f"Attempt with user '{username}' failed: {e}\n")
        print(f"Attempt with user 'postgres' failed: {fallback_error}")
        exit(1)

current_user = None

class User:
    def __init__(self, login, role):
        self.login = login
        self.role = role

def main():
    # Test connection by making sure we can query the users table
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    
    print("Welcome to CASE: The Coolest Auction Site Ever!")
    print("Please follow the prompts to interact with the auction system.")
    print("1. Login")
    print("2. Register")
    choice = input("Enter your choice (1 or 2): ")

    if choice == '1':
        login()
    elif choice == '2':
        register()
    else:
        print("Invalid choice. Please restart the program and select either 1 or 2.")
    
def login():
    global current_user
    login_input = input("Enter your username/login: ")
    password = input("Enter your password: ")

    # Schema uses 'login' instead of 'username' and returns 'login, role'
    cursor.execute("""
        SELECT login, role
        FROM users
        WHERE login = %s AND password = %s
    """, (login_input, password))

    user = cursor.fetchone()

    if user:
        # User initialized with login and role (your schema doesn't use an integer ID)
        current_user = User(user[0], user[1])
        print(f"Login successful! Role: {current_user.role}")
        user_menu()
    else:
        print("Invalid credentials.")

def register():
    login_input = input("Choose a login/username: ")
    password = input("Choose a password: ")
    phone = input("Enter your phone number: ")
    address = input("Enter your address: ")
    # Optional field from your new schema
    fav_category = input("Enter your favorite category (optional): ") or None 

    try:
        # Columns updated to match: login, password, phone_num, address, role, favorite_category
        cursor.execute("""
            INSERT INTO users (login, password, phone_num, address, role, favorite_category)
            VALUES (%s, %s, %s, %s, 'Buyer', %s)
        """, (login_input, password, phone, address, fav_category))

        conn.commit()
        print("Account created! You can now log in.")
        main()

    except psycopg2.IntegrityError:
        print("Login username already exists.")

def user_menu():
    while True:
        print("\n--- MENU ---")
        print("1. Browse Items")
        print("2. Search Auctions")
        print("3. Place Bids")
        print("4. View Auction Status")
        print("5. View Profile")
        print("6. Edit Profile")
        
        if current_user.role == "Admin":
            print("7. Change User Role")
        if current_user.role == "Seller":
            print("7. Create Listing")

        print("0. Logout")

        choice = input("Select option: ")

        if choice == "1":
            browse_items()
        elif choice == "2":
            search_auctions()
        elif choice == "3":
            place_bids()
        elif choice == "4":
            view_auction_status()
        elif choice == "5":
            view_profile()
        elif choice == "6":
            edit_profile()
        elif choice == "7" and current_user.role == "Admin":
            change_role()
        elif choice == "7" and current_user.role == "Seller":
            create_listing()
        elif choice == "0":
            logout()
            break
        else:
            print("Invalid option")

def browse_items():
    pass

def search_auctions():
    pass

def place_bids():
    pass

def view_auction_status():
    pass

def view_profile():
    print("\n--- PROFILE ---")
    print("Username/Login:", current_user.login)
    print("Role:", current_user.role)

def edit_profile():
    phone = input("New phone number: ")
    address = input("New address: ")

    # Schema changes: 'phone_num' instead of 'phone', and 'login' instead of 'id'
    cursor.execute("""
        UPDATE users
        SET phone_num = %s, address = %s
        WHERE login = %s
    """, (phone, address, current_user.login))

    conn.commit()
    print("Profile updated.")

def change_role():
    target_login = input("User login to modify: ")
    new_role = input("New role (Buyer/Seller/Admin): ")

    if new_role not in ["Buyer", "Seller", "Admin"]:
        print("Invalid role.")
        return

    # Schema uses 'login' instead of 'username'
    cursor.execute("""
        UPDATE users
        SET role = %s
        WHERE login = %s
    """, (new_role, target_login))

    conn.commit()
    print("Role updated.")

def logout():
    global current_user
    current_user = None
    print("Logged out.")

# --- Execution Entry Point ---
if __name__ == "__main__":
    main()