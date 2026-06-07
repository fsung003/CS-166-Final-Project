#!/usr/bin/env python3
# ----------------------------------------------------------
# Template Python User Interface
# ================================
#
# Database Management Systems
# Department of Computer Science & Engineering
# University of California - Riverside
#
# Target DBMS: 'Postgres'
#
# ----------------------------------------------------------

import sys
import psycopg2
from decimal import Decimal


class EmbeddedSQL:
    """
    A simple embedded SQL utility class designed to work with PostgreSQL
    via the psycopg2 driver.
    """

    def __init__(self, dbname, dbport, user, passwd=""):
        """
        Creates a new instance of EmbeddedSQL and establishes a physical
        connection to the database.

        :param dbname:  the name of the database
        :param dbport:  the port the PostgreSQL server is running on
        :param user:    the user name used to login to the database
        :param passwd:  the user login password
        """
        print("Connecting to database...")
        try:
            self._connection = psycopg2.connect(
                database=dbname,
                user=user,
                password=passwd,
                host="localhost",
                port=dbport
            )
            print(f"Connection URL: postgresql://localhost:{dbport}/{dbname}\n")
            print("Done")
        except Exception as e:
            print(f"Error - Unable to Connect to Database: {e}", file=sys.stderr)
            print("Make sure you started postgres on this machine")
            sys.exit(-1)

    def execute_update(self, sql, params=None):
        """
        Executes an update SQL statement (CREATE, INSERT, UPDATE, DELETE, DROP).

        :param sql: the input SQL string
        """
        cursor = self._connection.cursor()
        cursor.execute(sql, params)
        self._connection.commit()
        cursor.close()

    def execute_query(self, query, params=None):
        """
        Executes a SELECT query and prints the results to standard output.

        :param query:  the input query string
        :param params: optional tuple of parameters for parameterized queries
        :return:       the number of rows returned
        """
        cursor = self._connection.cursor()
        cursor.execute(query, params)

        col_names = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        row_count = 0

        # Print header
        print("\t".join(col_names))

        # Print each row
        for row in rows:
            print("\t".join(str(val) for val in row))
            row_count += 1

        cursor.close()
        return row_count

    def get_data_from_query(self, query, params=None):
        cursor = self._connection.cursor()
        cursor.execute(query, params)

        rows = cursor.fetchall()
        cursor.close()

        return rows

    def cleanup(self):
        """
        Closes the physical connection if it is open.
        """
        try:
            if self._connection is not None:
                self._connection.close()
        except Exception:
            pass  # ignored


# ----------------------------------------------------------
# Helper functions
# ----------------------------------------------------------

def greeting():
    print("\n\n*******************************************************")
    print("              Ebay App Implementation Interface          ")
    print("*******************************************************\n")


def read_choice():
    """
    Reads the user's menu choice from the keyboard.
    Keeps prompting until a valid integer is entered.
    """
    while True:
        try:
            return int(input("Please make your choice: "))
        except ValueError:
            print("Your input is invalid!")


# ----------------------------------------------------------
# Query functions
# ----------------------------------------------------------

def query_getSellers(esql):
    """Example query: find users with Seller role."""
    try:
        #cost = input("\tEnter cost: $")
        row_count = esql.execute_query(
            #"SELECT * FROM Catalog WHERE cost < %s;",
            "SELECT login FROM users WHERE role = 'Seller'",
            #(cost,)
        )
        print(f"total row(s): {row_count}")
    except Exception as e:
        print(e, file=sys.stderr)


def insertBuyerUser(esql):
    try:
        row_count = esql.execute_query(
            # UNFINISHED

           # "SELECT S.sname, COUNT(DISTINCT C.pid) as number_of_parts FROM suppliers S, catalog C WHERE S.sid = C.sid GROUP BY S.sname;",
        )
        print(f"total row(s): {row_count}")
    except Exception as e:
        print(e, file=sys.stderr)

# ----------------------------------------------------------
# Main
# ----------------------------------------------------------

def main():
    if len(sys.argv) != 4:
        print(
            f"Usage: python {sys.argv[0]} <dbname> <port> <user>",
            file=sys.stderr
        )
        return

    greeting()

    dbname = sys.argv[1]
    dbport = sys.argv[2]
    user   = sys.argv[3]

    esql = None
    try:
        esql = EmbeddedSQL(dbname, dbport, user, "")

        keepon = True
        while keepon:
            print("MAIN MENU")
            print("---------")
            print("0. Get names of users with the Seller role (example)")
            print("1. Insert Buyer user with name ____ (UNFINISHED)")
            print("2.  < EXIT")

            choice = read_choice()

            if   choice == 0: query_getSellers(esql)
            elif choice == 1: insertBuyerUser(esql)
            elif choice == 2: keepon = False
            else: print("Unrecognized choice!")

    except Exception as e:
        print(e, file=sys.stderr)
    finally:
        if esql is not None:
            print("Disconnecting from database...", end="")
            esql.cleanup()
            print("Done\n\nBye!")


#if __name__ == "__main__":
#    main()

# Choice 0
def BrowseItems(esql):
    try:
        print("Displaying items... \n") 
        row_count = esql.execute_query(
            "SELECT item_id, item_name, category, starting_price, item_condition FROM item;",
        )
        print(f"total row(s): {row_count}\n")
    except Exception as e:
        print(e, file=sys.stderr)

# Choice 1
def SearchAuctions(esql):
    try:
        print("Searching auctions...")
        row_count = esql.execute_query(
            "SELECT A.auction_id, I.item_name, A.seller_login, A.current_highest_bid, A.auction_status FROM auction A INNER JOIN item I ON A.item_id = I.item_id;"
        )
        print(f"total row(s): {row_count}\n")
    except Exception as e:
        print(e, file=sys.stderr)

# Choice 2
def PlaceBids(esql, username):
    # needs to be higher than highest bid
    try:
        BrowseItems(esql)
        # rows_count = esql.execute_query(
        #     "SELECT * FROM bid"
        # )
        choice = input("\tSelect an item_id to make a bid on: ")
        row_count = esql.execute_query(
            "SELECT item_id, item_name, starting_price, category, item_condition FROM item WHERE item_id = %s;",
            (choice,)
        )
        rows = esql.get_data_from_query(
            "SELECT starting_price FROM item WHERE item_id = %s;",
            (choice,)
        )

        starting_price = rows[0][0]
        print("Starting Price: ", starting_price)
        bid = Decimal(input("\tPlease enter a bid equal to or higher than the current auction price, or enter 0 to not make a bid: "))
        while bid < starting_price:
            if bid == 0:
                return
            bid = Decimal(input("\tPlease enter a bid equal to or higher than the current auction price, or enter 0 to not make a bid: "))

        esql.execute_update(
            "INSERT INTO bid (bid_id, auction_id, buyer_login, buyer_role, bid_amount) VALUES (%s, %s, %s, %s, %s)",
            (5, 1, username, "Buyer", bid)
        )
            
        rows_count = esql.execute_query(
            "SELECT * FROM bid"
        )

    except Exception as e:
        print(e, file=sys.stderr)

# # Choice 3
# def ViewAuctionStatus(esql):
#     try:


# # Choice 4 - view or edit profile
# def ViewProfile(esql, login):
#     try:


def userMenu():
    if len(sys.argv) != 4:
        print(
            f"Usage: python {sys.argv[0]} <dbname> <port> <user>",
            file=sys.stderr
        )
        return

    greeting()

    dbname = sys.argv[1]
    dbport = sys.argv[2]
    user   = sys.argv[3]

    esql = None
    try:
        esql = EmbeddedSQL(dbname, dbport, user, "")

        keepon = True
        while keepon:
            print("USER ACTIONS MENU")
            print("---------")
            print("0. Browse items (example)")
            print("1. Search auctions")
            print("2. Place bids")
            print("3. View auction status")
            print("4. View Profile")
            print("5.  < EXIT")

            choice = read_choice()
            
            if   choice == 0: BrowseItems(esql) # Browse items
            elif choice == 1: SearchAuctions(esql) # Search auctions
            elif choice == 2: PlaceBids(esql, "bob") # Place bids
            elif choice == 3: print("Displaying status of auctions...") # View Auction status
            elif choice == 4: print("Displaying profile...") # View Profile
            elif choice == 5: keepon = False
            else: print("Unrecognized choice!")

    except Exception as e:
        print(e, file=sys.stderr)
    finally:
        if esql is not None:
            print("Disconnecting from database...", end="")
            esql.cleanup()
            print("Done\n\nBye!")

userMenu()
