# QFlow – Queue Management System

A command-line queue management system built with **Python** and **MySQL**. QFlow lets businesses such as hospitals and restaurants manage daily queues: customers join a queue and get a token number, and staff call, complete or skip tokens at service counters.

## Features

- **Join a queue** for a service and get an automatically generated token number
- **Call the next token** to an available counter (staff)
- **Complete** or **skip** a token (staff)
- **Check token status** with the number of people ahead and your position in the queue
- **Cancel** your own waiting token
- **View token history** to see every action taken on a token
- **Create today's queue** for any active service
- Supports **multiple businesses**, each with its own services, counters and users
- **Role-based users:** admin, staff and customer

## Tech Stack

| Area | Technology |
|------|------------|
| Language | Python 3 |
| Database | MySQL |
| Libraries | mysql-connector-python, python-dotenv |

## Database Design

The database (`QFlow`) has 7 related tables:

| Table | Purpose |
|-------|---------|
| `Businesses` | Hospitals, restaurants and other businesses |
| `Users` | Admin, staff and customer accounts |
| `Services` | Services offered by a business, with estimated time |
| `Counters` | Service counters for each business |
| `Queues` | One queue per service per day (Active, Paused or Closed) |
| `Tokens` | Each customer's token and its status (Waiting, Called, Completed, Cancelled, Skipped) |
| `Queue_History` | Log of every action on a token |

The schema uses foreign keys, `UNIQUE` constraints (a token number is unique within a queue) and `CHECK` constraints. All queries in the app use parameterized SQL.

## Getting Started

### Prerequisites

- Python 3
- MySQL Server

### Setup

1. **Clone the repository**
   ```
   git clone https://github.com/Rajeev-2024/QFlow-Queue-Management-System.git
   cd QFlow-Queue-Management-System
   ```

2. **Install the dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Create the database.** Run `queries.sql` in MySQL (for example in MySQL Workbench, or from the command line):
   ```
   mysql -u root -p < queries.sql
   ```
   This creates the `QFlow` database, all 7 tables and some sample data.

4. **Add your database password.** Copy `.env.example` to a new file named `.env` and put your MySQL password in it:
   ```
   DB_PASSWORD=your_password_here
   ```

5. **Run the app**
   ```
   python app.py
   ```

## How to Use

When you run the app, it shows a menu:

```
1. Join queue
2. Staff: find next token
3. Staff: complete a token
4. Check token status
5. Cancel my waiting token
6. View token history
7. Create today's queue
8. Staff: Skip a token
0. Exit
```

**Example flow**

1. Choose **7** to create today's queue for a service.
2. Choose **1** to join that queue as a customer and receive a token number.
3. Choose **4** to check your position in the queue.
4. Choose **2** as staff to call the next token to a counter.
5. Choose **3** to complete the token, or **8** to skip it.
6. Choose **6** with a token ID to see its full history.

## Documentation

The full project requirements are in [QFlow_Requirements_Document.pdf](QFlow_Requirements_Document.pdf).

## Notes

- The sample data in `queries.sql` is for demonstration only. Its passwords are plain text and should never be used in a real application.
- Customers are currently chosen by ID from a list. There is no login system yet.
- The menu runs one action and then exits.

## Possible Future Improvements

- Login with securely hashed passwords
- A loop so the menu keeps running until you choose Exit
- A web interface for customers and staff

## Author

**A Rajeev** – [GitHub](https://github.com/Rajeev-2024) · [LinkedIn](https://linkedin.com/in/a-rajeev-72a9023ba)
