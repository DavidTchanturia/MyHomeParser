from parsing_functions import parse_card_body, parse_individual_page, process_individual_page, fetch_search_results
from properties import Property
from database_manager import DatabaseManager
from logger import logger

page_number = 5
db_manager = DatabaseManager()
db_manager.create_tables() #create if does not exist
last_updated_date = db_manager.last_date_updated() #last updated date


def process_card(card, last_date_updated):
    priceUSD, post_date, address, post_id = parse_card_body(card) #get info from listing page
    individual_soup = process_individual_page(post_id)
    seller_name, seller_number, property_type = parse_individual_page(individual_soup) #rest of the info from individual page

    property_object = Property(seller_name, seller_number, property_type, priceUSD, post_date, address, post_id)
    property_object.convert_date()
    property_object.check_seller_name_is_empty()

    if last_date_updated is not None: #if the db is empty at the beginning, we avoid error
        if last_date_updated >= property_object.post_date:
            db_manager.delete_duplicate_rows()  #if that date is already in the db, means we have updated db
            logger.info("Database has been updated")
            exit()

    property_object.save_to_database()


def process_page(page_number):
    while True:
        logger.info(f"Processing page {page_number}")
        search_content = fetch_search_results(page_number)

        if search_content is None: #note this is to break the loop when we parse all 5000+ pages
            break
        else:
            card_body = search_content.find_all("a", class_="card-container")
            for card in card_body:
                process_card(card, last_updated_date)
        page_number += 1

    db_manager.delete_duplicate_rows()  # after updating, delete the duplicates

if __name__ == "__main__":
    process_page(page_number)
