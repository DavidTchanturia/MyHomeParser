# Myhome.ge parser
## Using beautiful soup, a task for Making Science - Sweeft

This is a pipeline design that parses $${\color{green}myhome.ge}$$ Georgian real estate website. The program parses information about selling properties in Tbilisi. The info that you will be getting:
- seller name
- seller number
- property price
- property type
- address
- post date

Program is designed to run once a day and update existing database to keep up to date. After gathering 100 000+ rows of data, I used them to create a visual as well, For more details prease keep reading

## Technical Description
- Due to websites structure, not only does the program parse listing pages, but it visits individual posts and parses them to get the info
- Program runs daily at the end of the day, scheduled by Cron command.
- ⚠️ **important to remember** ⚠️- some posts that have already been on the website keep being posted, however, since they are already in the database. parser will not keep two instances of the same object in the database, so new post might not appear in the database with the same post date.
- during each run program might insert duplicate rows in the database, instead of checking them one by one for each insertion, program finishes the parsing and then uses a function to remove the duplicates.

## Tech

- MySQL
- BeautifulSoup (for web scraping)
- Requests (for making HTTP requests)
- JSON (for parsing JSON data)
- Logging (for logging information)
- GitHub (for version control and sharing the project)


## Installation

start by downloading project from github. first change the variables to connect to your schema on the local machine. 

```
connection_pool = pooling.MySQLConnectionPool(
    pool_name="myhome_pool",
    pool_size=7,
    host='localhost',
    user='root',
    password='password_SQL',
    port='3306',
    database='myhome'
)
```

In the github repository you will find sql file as well, use it to seed the database so that you do not have to wait for it to get all the old information from the website. Database contains posts including 17th Octomber and earlier.

```
mysql -u username -p
USE your_schema_name
source properties_table_dump.sql
```

To schedule the program to run at the end of each day, on linux use Cron. This will run the main.py every day at 23:40 making sure to include newly addade data to the database.
Note that you need to use a full path of main.py instead of this /MyHomeParser/main.py, for the command to work.
```
40 23 * * * /MyHomeParser/main.py >/dev/null 2>&1
```

## Visualisation
After gathering 100k+ data, I used PowerBI to visualize the data and have some idea of the current real estate situation in Georgia.
![analysis](https://github.com/DavidTchanturia/MyHomeParser/assets/104893522/b8e00afe-c342-4af1-b6b2-9750cab96899)

