import os
import psycopg2
from decimal import Decimal

# Dynamically gets your lab username ("ali229")
username = os.getlogin() 
db_name = f"{username}_phase3_DB"

try:
    # Attempt 1: Connect via TCP network using your username
    conn = psycopg2.connect(
        dbname=db_name,
        user=username,
        host="127.0.0.1",   # Force network connection
        port="35945"        # Your exact custom port
    )
    cursor = conn.cursor()
    print(f"Successfully connected to university database: {db_name} on port 35945!")
except Exception as e:
    try:
        # Attempt 2: Fallback to the 'postgres' user if username is blocked
        conn = psycopg2.connect(
            dbname=db_name,
            user="postgres",
            host="127.0.0.1",
            port="35945"
        )
        cursor = conn.cursor()
        print(f"Successfully connected to university database: {db_name} (as postgres) on port 35945!")
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
        print()
        
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
        elif choice == "4" and current_user.role != "Seller":
            print("User is a buyer. No current auctions to display.")
        elif choice == "4" and current_user.role == "Seller":
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
    cursor.execute("""
        SELECT item_id, item_name, category, starting_price, item_condition
        FROM item;
    """)

    rows = cursor.fetchall()
    for row in rows:
        print(row)
    print("Items displayed.")

def search_auctions():
    cursor.execute("""
        SELECT A.auction_id, I.item_name, A.seller_login, A.current_highest_bid, A.auction_status 
        FROM auction A INNER JOIN item I ON A.item_id = I.item_id;
    """)

    rows = cursor.fetchall()
    for row in rows:
        print(row)
    print("Auctions displayed.")

def place_bids():
    browse_items()
    choice = input("\nSelect an item_id to make a bid on: ")
    cursor.execute("""
        SELECT item_id, item_name, starting_price, category, item_condition 
        FROM item WHERE item_id = %s;
    """, (choice,))
    print(cursor.fetchone())

    # Get highest price for auction # NEED TO CHANGE
    cursor.execute("""
        SELECT starting_price FROM item WHERE item_id = %s;
    """, (choice,))
    starting_price = cursor.fetchone()[0]
    print("Starting Price: ", starting_price)

    # Get bid amount from user input
    bid = 0
    while bid < starting_price:
        bid = Decimal(input("\nPlease enter a bid equal to or higher than the current auction price, or enter 0 to not make a bid: "))
        if bid == 0:
            return

    # Get new bid id
    cursor.execute("SELECT MAX(bid_id) FROM bid;")
    bid_id = cursor.fetchone()[0] + 1

    # Insert new bid into database
    cursor.execute("""
        INSERT INTO bid (bid_id, auction_id, buyer_login, buyer_role, bid_amount) VALUES (%s, %s, %s, %s, %s);
    """, (bid_id, 1, current_user.login, "Buyer", bid))
    conn.commit()
    print("Bid placed.")

def view_auction_status():
    cursor.execute("""
        SELECT B.bid_id, A.auction_id, A.item_id, B.buyer_login, B.bid_amount
        FROM auction A
        INNER JOIN bid B ON A.auction_id = B.auction_id
    """)

    rows = cursor.fetchall()
    for row in rows:
        print(row)
    print("Auctions displayed.")

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
