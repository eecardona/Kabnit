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
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {config.DB_NAME} (
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
