import mysql.connector
from mysql.connector import pooling
from logger import logger

class DatabaseManager:
    def __init__(self, host='localhost', user='root', password='password_SQL', port='3306', database='myhome', pool_size=7):
        # Get a connection from the pool
        self.connection_pool = pooling.MySQLConnectionPool(
            pool_name="myhome_pool",
            pool_size=pool_size,
            host=host,
            user=user,
            password=password,
            port=port,
            database=database
        )

    def connect_to_database(self):
        try:
            conn = self.connection_pool.get_connection()
            cursor = conn.cursor()
            return conn, cursor
        except mysql.connector.Error as e:
            logger.info(f"Error connecting to the database: {e}")
            return None, None

    def create_tables(self):
        """when the program is run for the first time, two tables,
         if not already existing, with a relation are created, see the columns below"""
        mydb, cursor = self.connect_to_database()

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

    def delete_duplicate_rows(self):
        """instead of checking every time if the post_id is in the table, let the parser input data
        and once its done use this method to remove duplicates"""
        mydb, cursor = self.connect_to_database()
        try:
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
            logger.info("Duplicate rows removed from the table")
        except Exception as e:
            logger.error(f"Error: {e}")
            mydb.rollback()
        finally:
            cursor.close()
            mydb.close()

    def last_date_updated(self):
        """retrieving latest property to have been inserted in the database,
        then it will be compared to ones being inserted. used for stopping criteria"""
        mydb, cursor = self.connect_to_database()
        query = """SELECT MAX(post_date) FROM properties"""
        cursor.execute(query)
        last_updated_date = cursor.fetchone()

        if last_updated_date is not None:
            return last_updated_date[0]
        else:
            return None

