import psycopg
import logging
import config
import re


logger = logging.getLogger(__name__)

def create_db():
    try:
        with psycopg.connect("dbname=postgres user=postgres") as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE {config.DB_NAME};")
                logger.info(f'Database "{config.DB_NAME}" created on postgres server')
    except Exception as e:
        logger.info(f"Failure creating initial database: {e}")

def create_table():
    try:
        with psycopg.connect(f"dbname={config.DB_NAME} user=postgres") as conn:
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
    except Exception as e:
        logger.info(f"Failure creating initial database: {e}")

# Updates setting permanantly in config.py.
# Ensure you change value locally with config.{setting} = {update}
def config_update(setting, update):
    with open(file="config.py") as f:
        content = f.read()

    content = re.sub(rf'{setting}\s*=.*', f'{setting} = "{update}"', content)

    with open(file="config.py", mode="w") as f:
        f.write(content)

def pull_inventory():
    try:
        with psycopg.connect(f"dbname={config.DB_NAME} user=postgres") as conn:
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
        logger.info(f"Unable to read inventory: {e}")
        print(f"Error: {e}")

def insert_sql_file(path_to_file):
    try:
        logger.info("Attempting to connect to inventory database")
        conn = psycopg.connect(f"dbname={config.DB_NAME} user=postgres")
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
        with psycopg.connect(f"dbname={config.DB_NAME} user=postgres") as conn:
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
