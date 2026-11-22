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
ENV_FILE = config.BASE_DIR / '.env'

def get_dsn():
    load_dotenv(ENV_FILE, override=True)
    return {
        "host": os.getenv("DB_HOST"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "port": os.getenv("DB_PORT", "5432"),
    }

def validate_credentials(host, db, username, password, port="5432"):
    try:
        connection = psycopg.connect(
            host=host,
            dbname=db,
            user=username,
            password=password,
            port=port,
        )
        logger.info("Connection to PostgreSQL server successful")
        connection.close()
        create_table()
        config_update("INITIAL_SETUP", True)
        return True
    except Exception:
        logger.exception("Connection failed")
        return False

def postgres_check():
    try:
        connection = psycopg.connect(**get_dsn())
        logger.info("Connection to PostgreSQL server successful")
        connection.close()
        return True
    except Exception:
        logger.exception("Connection failed")
        return False

def start_postgres_server():
    try:
        subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info("PostgreSQL server started successfully.")
    except Exception:
        logger.exception("Server failed start")


def check_user():
    if config.USERNAME == None:
        set_user()

def config_update(setting, update):
    with open(file=f"{config.BASE_DIR}/config.py") as f:
        content = f.read()

    content = re.sub(rf'{setting}\s*=.*', f'{setting} = {update}', content)

    with open(file=f"{config.BASE_DIR}/config.py", mode="w") as f:
        f.write(content)

def create_table():
    try:
        with psycopg.connect(**get_dsn()) as conn:
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
    except Exception:
        logger.info("Unable to create table")
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
        with psycopg.connect(**get_dsn()) as conn:
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
        conn = psycopg.connect(**get_dsn())
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
        with psycopg.connect(**get_dsn()) as conn:
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
    with psycopg.connect(**get_dsn()) as conn:
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
    with psycopg.connect(**get_dsn()) as conn:
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
    with psycopg.connect(**get_dsn()) as conn:
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
    host, db, username, password, port = self.credentials()

    set_key(str(ENV_FILE), "DB_HOST", host)
    set_key(str(ENV_FILE), "DB_NAME", db)
    set_key(str(ENV_FILE), "DB_USER", username)
    set_key(str(ENV_FILE), "DB_PASSWORD", password)
    set_key(str(ENV_FILE), "DB_PORT", port or "5432")

    load_dotenv(ENV_FILE, override=True)
