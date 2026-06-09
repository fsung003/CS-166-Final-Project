import os
import psycopg2
from decimal import Decimal

username = os.getlogin() 
db_name = f"{username}_DB" # Change to name of database

try:
    #Connect via TCP network using your username
    conn = psycopg2.connect(
        dbname=db_name,
        user=username,
        host="127.0.0.1",  
        port= "32237" # Change to personal port number
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
            port="32237" # Change to personal port number
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
    login_input = input("\nEnter your username/login: ")
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
        print("Account created! You can now log in. \n \n")
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
            print("8. Monitor Users")
        if current_user.role == "Seller":
            print("7. Create Listing")
            print("8. Manage Listing")

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
        elif choice == "8" and current_user.role == "Admin":
            monitor_users()
        elif choice == "8" and current_user.role == "Seller":
            manage_listing()
        elif choice == "0":
            logout()
            break
        else:
            print("Invalid option")

def browse_items():
    cursor.execute("""
        SELECT I.item_id, I.item_name, I.category, I.starting_price, I.item_condition, A.auction_status
        FROM item I JOIN auction A ON I.item_id = A.item_id;
    """)

    print("\nid | Item Name | Category | Current Bid | Condition | Status")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    print("Items displayed.")

    if input("\nPress Enter to return to the menu..."):
        return

def search_auctions():

    searchType = input("\nSearch for (1) Item Name, (2) Category, or (3) Seller. Enter 1, 2, or 3: ")
    searchTerm = input("Enter term to search: ")

    if(searchType == "1"):
        cursor.execute("""
            SELECT A.auction_id, I.item_name, A.seller_login, A.current_highest_bid, A.auction_status 
            FROM auction A INNER JOIN item I ON A.item_id = I.item_id
            WHERE I.item_name ILIKE %s; """, (f"%{searchTerm}%",))
    elif(searchType == "2"):
        cursor.execute("""
            SELECT A.auction_id, I.item_name, A.seller_login, A.current_highest_bid, A.auction_status 
            FROM auction A INNER JOIN item I ON A.item_id = I.item_id
            WHERE I.category ILIKE %s; """, (f"%{searchTerm}%",))
    elif(searchType == "3"):
         cursor.execute("""
            SELECT A.auction_id, I.item_name, A.seller_login, A.current_highest_bid, A.auction_status 
            FROM auction A INNER JOIN item I ON A.item_id = I.item_id
            WHERE A.seller_login ILIKE %s; """, (f"%{searchTerm}%",))
    else:
        print("Invalid search type. Showing all auctions.")

    print("\nid | Item Name | Seller | Current Bid | Status")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    print("Auctions displayed.")

    if input("\nPress Enter to return to the menu..."):
        return


def place_bids():
    if current_user.role == "Seller":
        print("\nUser is a Seller, cannot place bids on auctions.")
        return
    # Display auctions with current highest bid
    cursor.execute("""
        SELECT A.auction_id, I.item_name, I.category, A.current_highest_bid, I.starting_price, I.item_condition, A.auction_status
        FROM item I 
        INNER JOIN auction A ON I.item_id = A.item_id
        WHERE A.auction_status = 'Active';
    """)
    print("\nAuction id | Item Name | Category | Highest Bid | Listed Price | Condition | Status")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    choice_auction_id = input("\nPlease insert the auction_id to make a bid on: ")
    cursor.execute("""
        SELECT A.auction_id, I.item_name, I.category, A.current_highest_bid, I.starting_price, I.item_condition, A.auction_status
        FROM item I 
        INNER JOIN auction A ON I.item_id = A.item_id
        WHERE A.auction_status = 'Active' AND A.auction_id = %s;
    """, (choice_auction_id,))
    row = cursor.fetchone()

    if row is None:
        print("\nAuction does not exist.")
        return
    print(row)
    
    # Get highest price for auction
    starting_price = Decimal(row[3]) # gets current_highest_bid
    print("Starting Price: $", starting_price)

    # Get bid amount from user input
    while True:
        try:
            bid_input = (input("\nPlease enter a bid higher than the current auction price (or enter 0 to cancel): "))
            bid = Decimal(bid_input)
            if bid == 0:
                return
            if bid > starting_price:
                break
        except:
            print("Invalid input. Please enter a number.")
    print("Bid: $", bid)
    
    # Get new bid id
    cursor.execute("SELECT MAX(bid_id) FROM bid;")
    max_bid_id = cursor.fetchone()[0]
    bid_id = 0
    if max_bid_id is None:
        bid_id = 1
    else:
        bid_id = max_bid_id + 1

    # Insert new bid into database
    cursor.execute("""
        INSERT INTO bid (bid_id, auction_id, buyer_login, buyer_role, bid_amount) VALUES (%s, %s, %s, %s, %s);
    """, (bid_id, choice_auction_id, current_user.login, "Buyer", bid))
    conn.commit()
    print("Bid placed.")
    
    # Change highest bid of auction
    cursor.execute("""
        UPDATE auction
        SET current_highest_bid = %s
        WHERE auction_id = %s;
    """, (bid, choice_auction_id))
    conn.commit()

    if input("\nPress Enter to return to the menu..."):
        return
        
def view_auction_status():
    cursor.execute("""
        SELECT A.auction_id, B.bid_id, A.item_id, I.item_name, A.seller_login, B.buyer_login, B.bid_amount, A.auction_status
        FROM auction A
        INNER JOIN bid B ON A.auction_id = B.auction_id
        INNER JOIN item I on A.item_id = I.item_id
    """)
    print("\nAuction id | Bid id | Item id | Seller | Buyer | Bid | Status")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    print("Auctions and bids made displayed.")

    if input("\nPress Enter to return to the menu..."):
        return

def view_profile():
    print("\n--- PROFILE ---")
    cursor.execute("""
        SELECT login, phone_num, address, role, favorite_category
        FROM users
        WHERE login = %s;
    """, (current_user.login,))
    row = cursor.fetchone()
    login, phone, address, role, favorite_category = row
    print("Username/Login:", login)
    print("Phone:", phone)
    print("Address:", address)
    print("Role:", role)
    print("Favorite Category:", favorite_category)
    
    if input("\nPress Enter to return to the menu..."):
        return

def edit_profile():
    change = input("\nWhat would you like to edit? (1) Username, (2) Phone, (3) Address, (4) Favorite Category: ")

    if(change == "1"):
        new_login = input("New username/login: ")
        cursor.execute(
            """UPDATE users
            SET login = %s
            WHERE login = %s""", (new_login, current_user.login))
        current_user.login = new_login  # Update current user object
    elif(change == "2"):
        new_phone = input("New phone number: ")
        cursor.execute(
            """UPDATE users
            SET phone_num = %s
            WHERE login = %s""", (new_phone, current_user.login))
    elif(change == "3"):
        address = input("New address: ")
        cursor.execute(
            """UPDATE users
            SET address = %s
            WHERE login = %s""", (address, current_user.login))
    elif(change == "4"):
        favorite_category = input("New favorite category: ")
        cursor.execute(
            """UPDATE users
            SET favorite_category = %s
            WHERE login = %s """, (favorite_category, current_user.login))
    else:
        print("Invalid choice.")
        return

    conn.commit()
    print("Profile updated.")

    if input("\nPress Enter to return to the menu..."):
        return

def create_listing():
    item_name = input("\nPlease enter the name of item being listed: ")
    category = input("Please enter the category of the item: ")
    while True:
        try:
            starting_price = Decimal(input("Please enter the minimum price for bidding: "))
            if starting_price < 0:
                print("Price cannot be negative.")
                continue
            break
        except:
            print("Invalid input. Please enter a valid number.")
    condition = input("Please enter the condition of the item(Used or New): ")
    while condition not in ("Used", "New"):
        condition = input("Please enter the condition of the item(Used or New): ")
    description = input("Enter a description for the item: ")
    choice = (input("Create auction for item? Select 1 to create listing, or 0 to exit: "))
    while choice not in ("1", "0"):
        choice = input("Please enter a value between 0 and 1: ")
    if choice == "0":
        return

    # Get new auction id
    cursor.execute("SELECT MAX(auction_id) FROM auction;")
    max_auction_id = cursor.fetchone()[0]
    new_auction_id = 0
    if max_auction_id is None:
        new_auction_id = 1
    else:
        new_auction_id = max_auction_id + 1

    # Get new item id
    cursor.execute("SELECT MAX(item_id) FROM item;")
    max_item_id = cursor.fetchone()[0]
    new_item_id = 0
    if max_item_id is None:
        new_item_id = 1
    else:
        new_item_id = max_item_id + 1

    # Add item into system
    cursor.execute("""
        INSERT INTO item (item_id, item_name, category, starting_price, item_condition, description, seller_login, seller_role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """, (new_item_id, item_name, category, starting_price, condition, description, current_user.login, "Seller"))
    conn.commit()

    # Create auction based on item
    # INSERT INTO auction (auction_id, item_id, seller_login, seller_role) VALUES (1, 517, 'alice', 'Seller');
    cursor.execute("""
        INSERT INTO auction (auction_id, item_id, seller_login, seller_role) VALUES (%s, %s, %s, %s);
    """, (new_auction_id, new_item_id, current_user.login, "Seller"))
    conn.commit()

    print("\nAuction has been created.")

    if input("\nPress Enter to return to the menu..."):
        return

    return

def manage_listing():
    print("\nDisplaying current active auctions and bids.")
    # Display auctions
    cursor.execute("""
        SELECT *
        FROM auction
        WHERE auction_status = %s AND seller_login = %s;
    """, ("Active", current_user.login))
    rows = cursor.fetchall()
    print("\nAuction id | Item id | Seller | Role | Highest Bid | Status")
    for row in rows:
        print(row)
    print("Auctions displayed.")

    cursor.execute("""
        SELECT *
        FROM bid B
        INNER JOIN auction A on B.auction_id = A.auction_id
        WHERE seller_login = %s;
    """, (current_user.login,))
    rows = cursor.fetchall()
    print("\nBid id | Auction id | Buyer | Role | Bid Amount | Timestamp")
    for row in rows:
        print(row)
    print("Bids displayed.")

    auction_choice = input("\nChoose Auction ID to manage: ")
    # Verify auction if owned by seller
    cursor.execute("""
        SELECT auction_id
        FROM auction
        WHERE auction_id = %s AND seller_login = %s AND auction_status = 'Active';
    """, (auction_choice, current_user.login))
    row = cursor.fetchone()
    if row is None:
        print("Invalid auction selection or not owned by you.")
        return
    
    choice = input("\nClose auction and sell to highest bidder (Y or N)?: ")
    while choice not in ("Y", "N"):
        choice = input("\nClose auction and sell to highest bidder (Y or N)?: ")
    if choice == "N":
        print("\nAuction will remain open.")
        return

    # Update auction to closed, begin payment from buyer to seller, start shipping
    # Get amount of highest bid and winner
    cursor.execute("""
        SELECT bid_amount, buyer_login
        FROM bid
        WHERE auction_id = %s
        ORDER BY bid_amount DESC
        LIMIT 1;
    """, (auction_choice,))
    row = cursor.fetchone()
    if row is None:
        print("No bids where placed on auction. Closing auction without buyers.")
        cursor.execute("""
            UPDATE auction
            SET auction_status = 'Closed'
            WHERE auction_id = %s;
        """, (auction_choice,))
        conn.commit()
        return

    highest_bid, buyer_login = row

    # Close auction
    cursor.execute("""
        UPDATE auction
        SET auction_status = 'Closed'
        WHERE auction_id = %s;
    """, (auction_choice,))

    # Get new payment id
    cursor.execute("SELECT MAX(payment_id) FROM payment;")
    max_payment_id = cursor.fetchone()[0]
    new_payment_id = 1 if max_payment_id is None else max_payment_id + 1

    # Create payment
    cursor.execute("""
        INSERT INTO payment (payment_id, auction_id, buyer_login, buyer_role, amount, payment_status) VALUES (%s, %s, %s, %s, %s, %s);
    """, (new_payment_id, auction_choice, buyer_login, "Buyer", highest_bid, "Pending"))

    # Get new shipment id
    cursor.execute("SELECT MAX(shipment_id) FROM shipment;")
    max_shipment_id = cursor.fetchone()[0]
    new_shipment_id = 1 if max_shipment_id is None else max_shipment_id + 1

    # Get buyer address 
    cursor.execute("""
        SELECT address
        FROM users
        WHERE login = %s;
    """, (buyer_login,))

    row = cursor.fetchone()
    address = row[0] if row else None

    cursor.execute("""
        INSERT INTO shipment (shipment_id, auction_id, address,shipment_status, tracking_number) VALUES (%s, %s, %s, %s, %s);
    """, (new_shipment_id,auction_choice,address,"Pending" ,None))

    conn.commit()
    print("Auction closed, payment created, shipment started.")

    return

def change_role():
    target_login = input("User login to modify: ")
    new_role = input("New role (Buyer/Seller/Admin): ")

    if new_role not in ["Buyer", "Seller", "Admin"]:
        print("Invalid role.")
        return

    # Check if target_login exists
    cursor.execute("""
        SELECT login, role
        FROM users
        WHERE login = %s;
    """, (target_login,))
    row = cursor.fetchone()
    if row is None:
        print("\nSelected user is invalid or does not exist.")
        return
    
    curr_role = row[1]
    if new_role == curr_role:
        print("\nNew role is the same as the current role.")
        return
    elif curr_role == "Buyer":
        cursor.execute("""
            DELETE FROM bid
            WHERE buyer_login = %s;
        """, (target_login,))
        cursor.execute("""
            DELETE FROM payment
            WHERE buyer_login = %s;
        """, (target_login,))
    elif curr_role == "Seller":
        pass
    
    cursor.execute("""
        UPDATE users
        SET role = %s
        WHERE login = %s;
    """, (new_role, target_login))


    conn.commit()
    print("Role updated.")

    if input("\nPress Enter to return to the menu..."):
        return

def monitor_users():
    cursor.execute("""
        SELECT *
        FROM users
    """)
    rows = cursor.fetchall()
    print("\nLogin | Password | Phone | Address | Role | Favorite Category")
    for row in rows:
        print(row)

    print("\nAll users displayed.")
    return

def logout():
    global current_user
    current_user = None
    print("Logged out.")

# --- Execution Entry Point ---
if __name__ == "__main__":
    main()
