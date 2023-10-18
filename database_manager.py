import mysql.connector
from mysql.connector import pooling


connection_pool = pooling.MySQLConnectionPool(
    pool_name="myhome_pool",
    pool_size=7,
    host='localhost',
    user='root',
    password='password_SQL',
    port='3306',
    database='myhome'
)

def connect_to_database():
    # Get a connection from the pool
    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        return conn, cursor
    except mysql.connector.Error as e:
        print(f"Error connecting to the database: {e}")
        return None, None


def create_tables():

    """when the program is run for the first time, two tables,
     if not already existing, with a relation are created, see the columns below"""
    mydb, cursor = connect_to_database()

    create_property_types_table_query = """
    CREATE TABLE IF NOT EXISTS propertyTypes (
        property_type_id INT,
        property_type VARCHAR(25),
        INDEX idx_property_types_property_type_id (property_type_id)
    );
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS properties (
        property_id INT AUTO_INCREMENT PRIMARY KEY,
        seller_name VARCHAR(255),
        seller_number VARCHAR(20),
        property_type INT,
        priceUSD DECIMAL(10, 2),
        post_date DATE,
        address TEXT,
        post_id INT UNSIGNED,
        FOREIGN KEY (property_type) REFERENCES propertyTypes(property_type_id),
        INDEX idx_post_id (post_id)
    );
    """
    cursor.execute(create_property_types_table_query)
    cursor.execute(create_table_query)

    cursor.execute("SELECT COUNT(*) FROM propertyTypes")
    result = cursor.fetchone()

    # since prType is represented as numbers on the web, seeding the second table when it is created
    if result[0] == 0:
        insert_property_types_query = """
        INSERT INTO propertyTypes (property_type_id, property_type)
        VALUES
            (1, "apartment"),
            (2, 'house'),
            (4, 'commercial'),
            (5, 'land'),
            (7, 'hotel');
        """
        cursor.execute(insert_property_types_query)

    mydb.commit()

create_tables()


def insert_data(seller_name, seller_number,property_type, price_usd, post_date, address, post_id):
    """simply inserting data to database, I will use this function to insert data as an object"""

    mydb, cursor = connect_to_database()
    insert_query = "INSERT INTO properties (seller_name, seller_number, property_type, priceUSD, post_date, address, post_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"

    # Create a tuple with the data to be inserted
    data = (seller_name, seller_number, property_type, price_usd, post_date, address, post_id)

    try:
        # Execute the query with the data
        cursor.execute(insert_query, data)

        mydb.commit()
        print(f'post with id: {post_id}, inserted into database')
    except Exception as e:
        print(f'Error: {e}')
        mydb.rollback()
    finally:
        cursor.close()
        mydb.close()


def delete_duplicate_rows():
    """instead of checking every time if the post_id is in the table, let the parser input data
    and once its done use this functions to remove duplicates"""
    mydb, cursor = connect_to_database()
    try:
        # Execute the DELETE query to remove duplicate rows
        delete_query = """
        DELETE FROM properties
        WHERE property_id NOT IN (
            SELECT min_property_id
            FROM (
                SELECT MIN(property_id) AS min_property_id, post_id
                FROM properties
                GROUP BY post_id
            ) AS t
        );
        """
        cursor.execute(delete_query)
        mydb.commit()
        print("duplicate rows removed form the table")
    except Exception as e:
        print(f"Error: {e}")
        mydb.rollback()
    finally:
        cursor.close()
        mydb.close()


def last_date_updated():
    mydb, cursor = connect_to_database()

    query = """SELECT MAX(post_date) FROM properties"""
    cursor.execute(query)
    last_updated_date = cursor.fetchone()

    return last_updated_date[0]

