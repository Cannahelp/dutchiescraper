from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import sqlite3
import numpy as np

options = Options()
#options.add_argument('--headless')
options.add_argument("--window-size=1920,1200")
driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))

BASE_URL = "https://dutchie.com/dispensary"
repository = "the-next-level-wellness-2"
CATEGORIES = ["flower", "vaporizers", "concentrates", "tinctures", "topicals"]

DUTCHIE_KEY_PRODUCT_CELL = "jTzrhU"
DUTCHIE_KEY_PRODUCT_BRAND = "bUxuOp"
DUTCHIE_KEY_PRODUCT_NAME = "kjymBK"
DUTCHIE_KEY_PRODUCT_SIZE = "hYKiO"
DUTCHIE_KEY_PRODUCT_PRICE = "hJFddt"
DUTCHIE_KEY_PRODUCT_BUTTON_SINGLE = "zdtBd"
DUTCHIE_KEY_PRODUCT_BUTTON_DOUBLE = "esCRpt"
DUTCHIE_KEY_PRODUCT_STRAINTYPE = "gfWvo"
DUTCHIE_KEY_PRODUCT_CONCENTRATION = "hdncuE"
DUTCHIE_KEY_PAGE_BUTTON = "cwWhSO"
DUTCHIE_KEY_PAGE_NEXT = "hjQwsb"
DUTCHIE_KEY_PAGE_PREV = "deZqfc"
DUTCHIE_KEY_PAGE_NO_ITEMS = "nhlLt"

class Product:
    def __init__(self, brand, name, sizes, prices, straintype, concentration):
        self.brand = brand
        self.name = name
        self.sizes = sizes
        self.prices = prices
        self.strainType = straintype
        self.concentration = concentration

    def toString(self):
        string_build = self.brand.ljust(30, ' ') + self.name + "(" + self.strainType + ", " + self.concentration + ")"
        if len(self.sizes) > 0:
            for i in range(len(self.sizes)):
                string_build += "\n" + self.sizes[i].rjust(45, ' ') + self.prices[i].rjust(5, ' ')
        else:
            string_build += self.prices[0]
        return string_build

def dutchie_get_num_pages():
    page_buttons = driver.find_elements(By.CLASS_NAME, DUTCHIE_KEY_PAGE_BUTTON)
    if len(page_buttons) == 0:
        return 0
    return int(page_buttons[-1].text) - 1

startTime = time.time()

for category in CATEGORIES:

    print("Beginning scrape of category: " + category)
    categoryStartTime = time.time()

    driver.get(BASE_URL + "/" + repository + "/products/" + category)
    time.sleep(2)

    NUM_PAGES = dutchie_get_num_pages()
   
    productList = []

    for page in range(NUM_PAGES + 1):
        print("Processing page " + str(page + 1))
        scrollLevel = 0

        height = int(driver.execute_script("return document.documentElement.scrollHeight"))

        while scrollLevel < height:
            scrollLevel += 1000
            driver.execute_script("window.scrollTo(500," + str(scrollLevel) + ")")
            time.sleep(0.2)

        cells = driver.find_elements(By.CLASS_NAME, DUTCHIE_KEY_PRODUCT_CELL)

        if len(cells) == 0:
            try:
                driver.find_element(By.CLASS_NAME, DUTCHIE_KEY_PAGE_NO_ITEMS)
                print("No products found under this category, moving to next.")
                continue
            except NoSuchElementException:
                print("No products found, retrying once in case it was a loading error.")
                driver.execute_script("window.scrollTo(0, 0)")
                time.sleep(0.2)
                driver.execute_script("window.scrollTo(500," + str(scrollLevel) + ")")
                if len(cells) == 0:
                    print("Still no products found, moving to next category.")
                    continue

        for cell in cells:
            try:
                product_brand = cell.find_element(By.CLASS_NAME, DUTCHIE_KEY_PRODUCT_BRAND).text
            except NoSuchElementException:
                product_brand = "No brand specified"
            product_name = cell.find_element(By.CLASS_NAME, DUTCHIE_KEY_PRODUCT_NAME).text
            # have to grab size/price lists separately as otherwise the lists will go stale when referencing later on
            # cannot grab .text directly due to the plural find_elements method
            product_sizes_list = cell.find_elements(By.CLASS_NAME, DUTCHIE_KEY_PRODUCT_SIZE)
            product_prices_list = cell.find_elements(By.CLASS_NAME, DUTCHIE_KEY_PRODUCT_PRICE)
            product_sizes = []
            product_prices = []

            for index, price in enumerate(product_prices_list):
                if len(product_sizes_list) > 0:
                    product_sizes.append(product_sizes_list[index].text)
                product_prices.append(price.text)
            
            try:
                product_straintype = cell.find_element(By.CLASS_NAME, DUTCHIE_KEY_PRODUCT_STRAINTYPE).text
            except NoSuchElementException:
                product_straintype = "No strain info"

            try:
                product_concentration = cell.find_element(By.CLASS_NAME, DUTCHIE_KEY_PRODUCT_CONCENTRATION).text
            except NoSuchElementException:
                product_concentration = "No concentration info"

            newProduct = Product(product_brand, product_name, product_sizes, product_prices, product_straintype,
                                 product_concentration)
            productList.append(newProduct)

        if page < NUM_PAGES:
            driver.find_element(By.CLASS_NAME, DUTCHIE_KEY_PAGE_NEXT).click()
            time.sleep(1)

    print(str(len(productList)) + " items found.")
    

    con = sqlite3.connect("{}.sqlite".format(repository))
    cur = con.cursor()
    category_sql_friendly = category.replace("-", "")

    cur.execute("DROP TABLE IF EXISTS {}".format(category_sql_friendly))
    cur.execute("CREATE TABLE {} (brand text, name text, size real, price real, price_per_gram real, "
                "straintype text, concentration text)".format(category_sql_friendly))

    data = []
    
    for product in productList:
        for index, price in enumerate(product.prices):
            strippedPrice = float(price.strip("$"))
            if len(product.sizes) > 0:
                strippedSize = float(product.sizes[index].strip("- g"))
                pricePerGram = np.round(strippedPrice / strippedSize, 2)
            else:
                strippedSize, pricePerGram = "", ""
            data += [
                (product.brand, product.name, strippedSize, strippedPrice, pricePerGram, product.strainType,
                    product.concentration)
            ]
#        print(data)

    cur.executemany('INSERT INTO {} VALUES(?, ?, ?, ?, ?, ?, ?)'.format(category_sql_friendly), data)

    con.commit()
    con.close()
    print("Committed, took " + str(time.time() - float(categoryStartTime)) + " seconds.")

print("Total run took " + str(time.time() - float(startTime)) + " seconds.")

driver.quit()