import json
from bs4 import BeautifulSoup
import requests


headers = {
    "User-Agent": "Chrome/58.0.3029.110"
}


def fetch_search_results(page_number):
    """use this to iterate though all the existing pages and get the search concent"""

    url = "https://www.myhome.ge/ka/s/?Keyword=" \
           "%E1%83%97%E1%83%91%E1%83%98%E1%83%9A%E1%83%98%E1%83%A1%E1%83%98&" \
           f"AdTypeID=1&Page={page_number}&SortID=1&cities=1996871&GID=1996871"

    result = requests.get(url, headers=headers)
    soup = BeautifulSoup(result.content, "html.parser")
    search_content = soup.find("div", class_="search-contents ml-0")

    return search_content


def process_individual_page(post_id):
    """parses individual page that will be accessed using the link and post_id as an argument.
     and returns content from where I will extract info """

    individual_url = f"https://www.myhome.ge/en/pr/{post_id}"
    individual_result = requests.get(individual_url, headers=headers)
    individual_soup = BeautifulSoup(individual_result.content, "html.parser")

    return individual_soup

def find_property_type(soup):
    """property type is hidden in the <script> tag in html, because of that this function does some modifications
    to extract the number that represents the property type which will be used for database relationship later"""

    scripts = soup.find_all("script")

    for script in scripts:
        script_text = script.get_text()
        if "var mortgage =" in script_text:
            lines = script_text.split("\n")
            for line in lines:
                if "var mortgage =" in line:
                    json_text = line.split("var mortgage =", 1)[1].strip().rstrip(";")

                    mortgage_data = json.loads(json_text)

                    propery_type = int(mortgage_data['prtype_id'])
                    return propery_type

def parse_card_body(card):
    """parses the listing page, gets the info from the card body, with this function we retrieve
    price, address, post_date and post_id. the lats one will be used to access individual post"""

    priceUSD = card.find('b', class_="item-price-usd mr-2").text.strip()
    priceUSD = int(priceUSD.replace(',', ''))

    address = card.find('div', class_="address").text.strip()

    post_date = card.find("div", class_="statement-date").text.strip()

    # since we cant acess seller number and seller name on the same page, we are going to parse individual posts
    # for it we are using the unique id each post has and using it for query in the link
    post_id = card.find('span', class_="d-block").text
    post_id = post_id.split(' ')[1]

    return priceUSD, post_date, address, post_id


def parse_individual_page(individual_soup):
    """info that is not available on the list page, we will parse from individual page.
    function returns seller name, seller_number and property_type"""

    property_type = find_property_type(individual_soup)

    number_div = individual_soup.find('div', class_='fixed-bottom-bar align-items-center justify-content-center d-lg-none')
    a_tag = number_div.find('a')
    seller_number = a_tag.get('href')[4:]

    seller_name = individual_soup.find('span', class_='name d-block').text.strip()

    return seller_name, seller_number, property_type