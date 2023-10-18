from parsing_functions import parse_card_body, parse_individual_page, process_individual_page, fetch_search_results
from properties import Property
from database_manager import DatabaseManager
from logger import logger

page_number = 1
db_manager = DatabaseManager()
db_manager.create_tables()
last_updated_date = db_manager.last_date_updated()


def process_card(card, last_date_updated):
    priceUSD, post_date, address, post_id = parse_card_body(card)
    individual_soup = process_individual_page(post_id)
    seller_name, seller_number, property_type = parse_individual_page(individual_soup)

    property_object = Property(seller_name, seller_number, property_type, priceUSD, post_date, address, post_id)
    property_object.convert_date()
    property_object.check_seller_name_is_empty()

    if last_date_updated is not None:
        if last_date_updated >= property_object.post_date:
            db_manager.delete_duplicate_rows()  # Use the method from the DatabaseManager class
            logger.info("Database has been updated")
            exit()

    property_object.save_to_database()

def process_page(page_number):
    while True:
        logger.info(f"Processing page {page_number}")
        search_content = fetch_search_results(page_number)

        if search_content is None:
            break
        else:
            card_body = search_content.find_all("a", class_="card-container")
            for card in card_body:
                process_card(card, last_updated_date)
        page_number += 1

    db_manager.delete_duplicate_rows()  # Use the method from the DatabaseManager class

if __name__ == "__main__":
    process_page(page_number)
