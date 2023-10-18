from parsing_functions import parse_card_body, parse_individual_page, process_individual_page, fetch_search_results
from properties import Property
from database_manager import delete_duplicate_rows, last_date_updated


page_number = 1
last_updated_date = last_date_updated()

def process_card(card, last_date_updated):

    #get those info from listing page
    priceUSD, post_date, address, post_id = parse_card_body(card)

    #access individual page
    individual_soup = process_individual_page(post_id)
    seller_name, seller_number, property_type = parse_individual_page(individual_soup)

    property_object = Property(seller_name, seller_number, property_type,
                                             priceUSD, post_date, address, post_id)

    #data motifications
    property_object.convert_date()
    property_object.check_seller_name_is_empty()

    if last_date_updated >= property_object.post_date:
        delete_duplicate_rows()
        print("database has been updated")
        exit()

    property_object.save_to_database()


def process_page(page_number):

    while True:
        print(f"Processing page {page_number}")
        search_content = fetch_search_results(page_number)

        #note thath this should be considered for only first run. stops program when there is nothing more to parrse
        if search_content is None:
            break
        else:
            card_body = search_content.find_all("a", class_="card-container")

            for card in card_body:
                process_card(card, last_updated_date)

        page_number += 1


if __name__ == "__main__":
    process_page(page_number)
    delete_duplicate_rows()