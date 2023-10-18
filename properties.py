from database_manager import DatabaseManager
import datetime
from logger import logger

db_manager = DatabaseManager()

class Property:
    def __init__(self, seller_name, seller_number, property_type, priceUSD, post_date, address, post_id):
        self.seller_name = seller_name
        self.seller_number = seller_number
        self.property_type = property_type
        self.priceUSD = priceUSD
        self.post_date = post_date
        self.address = address
        self.post_id = post_id

    def __str__(self):
        return f"seller name:{self.seller_name}, seller number{self.seller_number}, price: {self.priceUSD}"

    def convert_date(self):
        """myhome.ge has a date format that is not usable for databases, because of that
        thit method takes the object and converts unusable date format to YYYY-MM-DD"""

        month_mapping = {
            "იან.": 1,
            "თებ.": 2,
            "მარ.": 3,
            "აპრ.": 4,
            "მაი.": 5,
            "ივნ.": 6,
            "ივლ.": 7,
            "აგვ.": 8,
            "სექტ.": 9,
            "ოქტ.": 10,
            "ნოე.": 11,
            "დეკ.": 12,
        }

        date_time_parts = self.post_date.split(" ")

        day = int(date_time_parts[0])
        month = month_mapping[date_time_parts[1]]

        current_year = datetime.datetime.now().year

        converted_date = datetime.date(current_year, month, day)

        self.post_date = converted_date

    def check_seller_name_is_empty(self):
        """most of the seller names are empty, since I want to avoid putting an empty string in a database,
        it the name is empty, we replace it with None and put None in the db"""
        if self.seller_name == '' or self.seller_name is None:
            self.seller_name = None

    def save_to_database(self):
        """simple insertion to the database"""
        mydb, cursor = db_manager.connect_to_database()
        insert_query = "INSERT INTO properties (seller_name, seller_number, property_type, priceUSD, post_date, address, post_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"

        # Create a tuple with the data to be inserted
        data = (self.seller_name, self.seller_number, self.property_type, self.priceUSD,
                self.post_date, self.address, self.post_id)

        try:
            # Execute the query with the data
            cursor.execute(insert_query, data)
            mydb.commit()
            logger.info(f'post with id: {self.post_id}, inserted into database')
        except Exception as e:
            logger.error(f'Error: {e}')
            mydb.rollback()
        finally:
            cursor.close()
            mydb.close()