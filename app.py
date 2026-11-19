import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="QFlow",
    )

def join_queue():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT service_id, name, estimated_time FROM Services")
    services = cursor.fetchall()
    for service in services:
        service_id, name, estimated_time = service
        print(f"{service_id}. {name} — about {estimated_time} minutes")

    chosen_service_id = input("Enter the service ID you want to join: ")

    cursor.execute(
        """
        SELECT queue_id
        FROM Queues
        WHERE service_id = %s
        AND queue_date = CURDATE()
        AND status = 'Active'
        """,
        (chosen_service_id,),
    )

    queue = cursor.fetchone()

    if queue:
        print(f"Active queue found. Queue ID: {queue[0]}")
        cursor.execute("SELECT user_id, name FROM Users WHERE role = 'customer'")
        customers = cursor.fetchall()

        for customer in customers:
            print(f"{customer[0]}. {customer[1]}")

        customer_id = int(input("Enter your customer ID: "))
        print(f"You selected customer ID {customer_id}.")

        cursor.execute(
            "SELECT COALESCE(MAX(token_number), 0) + 1 "
            "FROM Tokens WHERE queue_id = %s",
            (queue[0],),
        )

        next_token_number = cursor.fetchone()[0]
        print(f"Your next token number is {next_token_number}.")

        cursor.execute(
            "INSERT INTO Tokens (queue_id, customer_id, token_number) "
            "VALUES (%s, %s, %s)",
            (queue[0], customer_id, next_token_number),
        )

        token_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO Queue_History (token_id, action) " "VALUES (%s, %s)",
            (token_id, "Joined queue"),
        )
        connection.commit()
        print(f"Token created: #{next_token_number}")
    else:
        print("There is no active queue for that service today.")

    cursor.close()
    connection.close()


def staff_call_next():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT service_id, name FROM Services WHERE is_active = TRUE "
        "ORDER BY service_id"
    )
    services = cursor.fetchall()

    if not services:
        print("No active services found.")
        cursor.close()
        connection.close()
        return

    for service_id, name in services:
        print(f"{service_id}. {name}")

    service_id = int(input("Enter the service ID: "))

    cursor.execute(
        """
        SELECT queue_id
        FROM Queues
        WHERE service_id = %s
          AND queue_date = CURDATE()
          AND status = 'Active'
        ORDER BY queue_id DESC
        LIMIT 1
        """,
        (service_id,),
    )
    queue = cursor.fetchone()

    if not queue:
        print("There is no active queue for that service today.")
        cursor.close()
        connection.close()
        return

    queue_id = queue[0]

    cursor.execute(
        """
        SELECT token_id, token_number
        FROM Tokens
        WHERE queue_id = %s AND status = 'Waiting'
        ORDER BY token_number
        LIMIT 1
        """,
        (queue_id,),
    )
    token = cursor.fetchone()

    if not token:
        print("There are no waiting tokens in that service's queue.")
        cursor.close()
        connection.close()
        return

    cursor.execute(
        """
        SELECT c.counter_id, c.name
        FROM Counters c
        JOIN Services s ON s.business_id = c.business_id
        WHERE s.service_id = %s AND c.is_active = TRUE
        ORDER BY c.counter_id
        """,
        (service_id,),
    )
    counters = cursor.fetchall()

    if not counters:
        print("There are no active counters for this service.")
        cursor.close()
        connection.close()
        return

    for counter_id, name in counters:
        print(f"{counter_id}. {name}")

    counter_id = int(input("Enter the counter ID: "))
    valid_counter_ids = [row[0] for row in counters]

    if counter_id not in valid_counter_ids:
        print("That counter isn't available for this service.")
        cursor.close()
        connection.close()
        return

    cursor.execute(
        """
        SELECT token_id
        FROM Tokens
        WHERE counter_id = %s AND status = 'Called'
        """,
        (counter_id,),
    )
    current_token = cursor.fetchone()

    if current_token:
        print(f"That counter is busy with token ID {current_token[0]}.")
        cursor.close()
        connection.close()
        return

    cursor.execute(
        """
        UPDATE Tokens
        SET status = 'Called',
            counter_id = %s,
            called_at = CURRENT_TIMESTAMP
        WHERE token_id = %s AND status = 'Waiting'
        """,
        (counter_id, token[0]),
    )

    if cursor.rowcount == 1:
        cursor.execute(
            "INSERT INTO Queue_History (token_id, action) VALUES (%s, %s)",
            (token[0], "Called"),
        )
        connection.commit()
        print(f"Token #{token[1]} called to the counter.")
    else:
        print("That token is no longer waiting.")

    cursor.close()
    connection.close()


def staff_complete_token():
    connection = connect_db()
    cursor = connection.cursor()

    token_id = int(input("Enter the token ID to complete: "))

    cursor.execute(
        "UPDATE Tokens "
        "SET status = 'Completed', completed_at = CURRENT_TIMESTAMP "
        "WHERE token_id = %s AND status = 'Called'",
        (token_id,),
    )

    if cursor.rowcount == 1:
        cursor.execute(
            "INSERT INTO Queue_History (token_id, action) " "VALUES (%s, %s) ",
            (token_id, "Completed"),
        )
        connection.commit()
        print("Token marked as completed.")
    else:
        print("Token not found or it isn't currently called.")

    cursor.close()
    connection.close()


def check_token_status():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT user_id, name FROM Users " "WHERE role = 'customer' ORDER BY name"
    )
    customers = cursor.fetchall()

    for user_id, name in customers:
        print(f"{user_id}. {name}")

    customer_id = int(input("Choose your customer ID: "))

    cursor.execute(
        """
        SELECT s.name, t.token_number, t.status,
               CASE WHEN t.status = 'Waiting' THEN (
                   SELECT COUNT(*)
                   FROM Tokens AS ahead
                   WHERE ahead.queue_id = t.queue_id
                     AND ahead.status = 'Waiting'
                     AND ahead.token_number < t.token_number
               ) ELSE NULL END AS people_ahead
        FROM Tokens AS t
        JOIN Queues AS q ON q.queue_id = t.queue_id
        JOIN Services AS s ON s.service_id = q.service_id
        WHERE t.customer_id = %s
          AND q.queue_date = CURDATE()
        ORDER BY t.token_id DESC
        """,
        (customer_id,),
    )

    tokens = cursor.fetchall()

    if tokens:
        for service, number, status, people_ahead in tokens:
            print(f"{service} — Token #{number}: {status}")
            if status == "Waiting":
                print(
                    f"People ahead: {people_ahead}; "
                    f"your position: {people_ahead + 1}"
                )
    else:
        print("No tokens found for that customer today.")

    cursor.close()
    connection.close()


def cancel_my_token():
    connection = connect_db()
    cursor = connection.cursor()

    token_id = int(input("Enter token ID: "))
    customer_id = int(input("Enter user ID: "))

    cursor.execute(
        """
        UPDATE tokens
        SET status='Cancelled'
        WHERE token_id=%s and customer_id=%s and status='Waiting'
        """,
        (token_id, customer_id),
    )

    if cursor.rowcount == 1:
        cursor.execute(
            """
            INSERT INTO Queue_History(token_id,action)
            VALUES (%s,%s)
            """,
            (
                token_id,
                "Cancelled",
            ),
        )
        connection.commit()
        print("Token is cancelled")
    else:
        print("Token wasn’t found, doesn’t belong to that customer, or isn’t waiting.")
    cursor.close()
    connection.close()


def show_token_history():
    connection = connect_db()
    cursor = connection.cursor()

    token_id = int(input("Enter token ID: "))

    cursor.execute(
        "SELECT action,action_time "
        "FROM Queue_History "
        "WHERE token_id=%s "
        "ORDER BY action_time ",
        (token_id,),
    )
    history = cursor.fetchall()
    if history:
        for event in history:
            print(f"{event[1]} — {event[0]}")
    else:
        print("No history found for that token.")
    cursor.close()
    connection.close()


def create_daily_queue():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT service_id,name FROM services
        WHERE is_active=True
        """)
    services = cursor.fetchall()
    for service in services:
        print(f"{service[0]}.{service[1]}")
    service_id = int(input("Enter service ID: "))
    cursor.execute(
        "SELECT service_id FROM Services "
        "WHERE service_id = %s AND is_active = TRUE ",
        (service_id,),
    )
    if cursor.fetchone() is None:
        print("That service ID isn't active.")
    else:
        cursor.execute(
            "SELECT queue_id FROM Queues "
            "WHERE service_id = %s "
            "AND queue_date = CURDATE() "
            "AND status = 'Active'",
            (service_id,),
        )
        existing_queue = cursor.fetchone()

        if existing_queue:
            print(f"An active queue already exists: {existing_queue[0]}")
        else:
            cursor.execute(
                "INSERT INTO Queues (service_id, queue_date, status) "
                "VALUES (%s, CURDATE(), 'Active') ",
                (service_id,),
            )
            connection.commit()
            print(f"Queue created. Queue ID: {cursor.lastrowid}")

    cursor.close()
    connection.close()


def staff_skip_token():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT service_id, name FROM Services "
        "WHERE is_active = TRUE ORDER BY service_id"
    )
    services = cursor.fetchall()

    for service_id, name in services:
        print(f"{service_id}. {name}")

    service_id = int(input("Enter the service ID: "))

    cursor.execute(
        """
        SELECT queue_id
        FROM Queues
        WHERE service_id = %s
          AND queue_date = CURDATE()
          AND status = 'Active'
        ORDER BY queue_id DESC
        LIMIT 1
        """,
        (service_id,),
    )
    queue = cursor.fetchone()

    if not queue:
        print("There is no active queue for that service today.")
        cursor.close()
        connection.close()
        return

    token_number = int(input("Enter the token number to skip: "))

    cursor.execute(
        """
        SELECT token_id, status
        FROM Tokens
        WHERE queue_id = %s AND token_number = %s
        """,
        (queue[0], token_number),
    )
    token = cursor.fetchone()

    if not token:
        print("Token not found in that service's queue.")
    elif token[1] != "Called":
        print("Only a called token can be skipped.")
    else:
        cursor.execute(
            "UPDATE Tokens SET status = 'Skipped' "
            "WHERE token_id = %s AND status = 'Called'",
            (token[0],),
        )

        if cursor.rowcount == 1:
            cursor.execute(
                "INSERT INTO Queue_History (token_id, action) " "VALUES (%s, %s)",
                (token[0], "Skipped"),
            )
            connection.commit()
            print(f"Token #{token_number} skipped.")
        else:
            print("Token status changed; it could not be skipped.")

    cursor.close()
    connection.close()


choice = input(
    "1. Join queue\n"
    "2. Staff: find next token\n"
    "3. Staff: complete a token \n"
    "4. Check token status \n"
    "5. Cancel my waiting token \n"
    "6. View token history \n"
    "7. Create today's queue \n"
    "8. Staff: Skip a token \n"
    "0. Exit\n"
    "Choose: "
)

if choice == "1":
    join_queue()
elif choice == "2":
    staff_call_next()
elif choice == "3":
    staff_complete_token()
elif choice == "4":
    check_token_status()
elif choice == "5":
    cancel_my_token()
elif choice == "6":
    show_token_history()
elif choice == "7":
    create_daily_queue()
elif choice == "8":
    staff_skip_token()
elif choice == "0":
    print("Goodbye.")
else:
    print("Invalid choice.")
