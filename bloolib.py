#Third Party imports
from dotenv import load_dotenv, set_key
import psycopg

from operator import truediv
from gui import warning_postgres
import subprocess
import logging
import config
import re
import os



logger = logging.getLogger(__name__)
host = os.getenv("KABNIT_HOST")
user = os.getenv("KABNIT_DB_USER")
password = os.getenv("KABNIT_DB_PASSWORD")
port = os.getenv("KABNIT_PORT")
dsn = ("host=%s dbname=%s password=%s port=%s", host, user, password, port)

def validate_credentials(host, username, password, port="5432"):
    try:
        connection = psycopg.connect("host=%s dbname=%s password=%s port=%s", host, username, password, port)
        logger.info("Connection to PostgreSQL server successful")
        connection.close()
        return True
    except Exception as e:
        return False

def postgres_check():
    try:
        connection = psycopg.connect(dsn)
        logger.info("Connection to PostgreSQL server successful")
        connection.close()
        return True
    except Exception as e:
        return False

def start_postgres_server():
    try:
        subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info("PostgreSQL server started successfully.")
    except Exception as e:
        logger.error(f"Error occured: {e}")


def check_user():
    if config.USERNAME == None:
        set_user()

# def create_db():
#     try:
#         with psycopg.connect("dbname=postgres user=postgres") as admin_conn:
#             admin_conn.autocommit = True
#             with admin_conn.cursor() as cur:
#                 cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (f"{config.DB_NAME}",))
#                 if cur.fetchone() is None:
#                     admin_conn.autocommit = True
#                     with admin_conn.cursor() as cur:
#                         cur.execute(f'CREATE DATABASE "{config.DB_NAME}"')
#                 logger.info(f'Database "{config.DB_NAME}" created on postgres server')
#     except Exception as e:
#         logger.info(f"Failure creating initial database: {e}")

# Updates setting permanantly in config.py.
# Ensure you change value locally with config.{setting} = {update}
def config_update(setting, update):
    with open(file=f"{config.BASE_DIR}/config.py") as f:
        content = f.read()

    content = re.sub(rf'{setting}\s*=.*', f'{setting} = "{update}"', content)

    with open(file=f"{config.BASE_DIR}/config.py", mode="w") as f:
        f.write(content)

def create_table():
    try:
        with psycopg.connect(dsn) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS inventory (
                        id serial PRIMARY KEY,
                        item_name VARCHAR(255) NOT NULL,
                        brand_name VARCHAR(255),
                        amount integer NOT NULL,
                        units VARCHAR(255) NOT NULL,
                        location VARCHAR(255),
                        expiration_date DATE,
                        barcode VARCHAR(255),
                        price_paid NUMERIC(10, 2)
                        );
                        """)
                logger.info('Table "inventory" created on postgres server')
                return True
    except Exception as e:
        logger.info(f"Failure creating table: {e}")
        return False

def ensure_db():
    try:
        if config.DB_NAME is None:
            config.DB_NAME = "kabnit"
            config_update("DB_NAME", config.DB_NAME)

        create_db()
        return create_table()
    except Exception as e:
        logger.exception(f"ensure_db failed: {e}")
        return False

def set_user():
    print("Welcome to KabNit! Please enter a username to identify you:")
    username = input()
    config_update("USERNAME", f"{username}")
    config.USERNAME = username
    logger.info(f"User {username} saved as owner")
    print(f"Thanks {username}")


def pull_inventory():
    try:
        with psycopg.connect(dsn) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                    item_name AS Item,
                    brand_name AS Brand,
                    amount || ' ' || units AS Amount,
                    Location,
                    expiration_date AS "Expiration Date"
                    FROM inventory
                    WHERE amount > 0
                    ;
                    """)
                logger.info("Returned Current Inventory")
                rows = cur.fetchall()
                headers = [description[0] for description in cur.description]
                return rows, headers
    except Exception as e:
        logger.error(f"Unable to read inventory: {e}")
        print(f"Error: {e}")

def insert_sql_file(path_to_file):
    try:
        logger.info("Attempting to connect to inventory database")
        conn = psycopg.connect(dsn)
        logger.info("Connected to database")
        cur = conn.cursor()
        cur.execute(open(file=path_to_file).read())
        conn.commit()
        logger.info('File inserted into table "inventory"')
    except Exception as e:
        logger.error(f"Insert failed: {e}")
        print(f"Error: {e}")

def insert_form_data(rows):
    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO inventory (item_name, brand_name, amount, units, location, expiration_date, barcode, price_paid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    rows
                )
                conn.commit()
                logger.info(f"Successfully inserted {len(rows)} rows")
                return True
    except Exception as e:
        logger.error(f"Insert failed: {e}")
        print(f"Error: {e}")
        return False

def search(text: str):
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                item_name AS Item,
                brand_name AS Brand,
                amount || ' ' || units AS Amount,
                Location,
                expiration_date AS "Expiration Date"
                FROM inventory
                WHERE item_name ILIKE %s
                ;
                """,
                (f"%{text}%",)

            )
            rows = cur.fetchall()
            headers = [description[0] for description in cur.description]
            return rows, headers

def load_locations():
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT location
                FROM inventory
                ORDER BY location
               ;
            """)
            rows = cur.fetchall()
            list = [row[0] for row in rows]
            return list

def pull_location(location):
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT
                    item_name AS Item,
                    brand_name AS Brand,
                    amount || ' ' || units AS Amount,
                    expiration_date AS "Expiration Date"
                    FROM inventory
                    WHERE location ILIKE %s
                    ;
                """, (location,))
            rows = cur.fetchall()
            headers = [description[0] for description in cur.description]
            return rows, headers

def save_credentials(self):
    host, port, username, password = self.credentials()
    set_key(".env", "KABNIT_HOST", str(host))
    set_key(".env", "KABNIT_PORT", str(port))
    set_key(".env", "KABNIT_DB_USER", str(username))
    set_key(".env", "KABNIT_DB_PASSWORD", str(password))
