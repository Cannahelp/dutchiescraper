import csv
import time
import datetime
import pandas as pd #Using this to write CSV file
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

###################################################################
#               Initialize Selenium Web Driver
###################################################################
options = Options()
options.add_argument('--incognito')
#options.add_experimental_option("detach", True)
CHROMEDRIVERPATH = '/Users/justinwaugh/Downloads/chromedriver-mac-arm64/chromedriver'
s = Service(CHROMEDRIVERPATH)
driver = webdriver.Chrome(service=s, options=options)

# Setting up the dispensaries to be scraped. Section also sets up their base URLs (extra path details can be appended later)
dispos = ['The Landing', 'Zen Leaf', 'The Next Level Wellness', 'Trulieve', 'WV Relief']
dispodomains = ['https://the-landing-dispensary-bridgeport.thelandingwv.com/', 'https://zenleafdispensaries.com/locations/clarksburg/medical-menu/', 'https://tnlw.us/shop-online/', 'https://shop.trulieve.com/', 'https://wv-relief.com/online-ordering/']


###############################################################################################################################################################################################
#                                           THE LANDING SCRAPING
#       This part of the script will scrape The Landing Dispensary Database for product and then append it to a sheet in the db so that the database can contain old data as well. 
#                                       May be easier to just have it create a file with the date and time appended to the file name.
###############################################################################################################################################################################################

#def landingflowerscrape():


####################################################
#    Flower Listings, Quantities and Prices
####################################################

domain = dispodomains[0] + 'stores/the-landing-dispensary-bridgeport/products/flower'
driver.get(domain);
time.sleep(2)

# Section below sets up the browser to press the space bar 4 times to scrape all of the items on the page (without this you can't scrape past what the initial page load displays)
actions = ActionChains(driver)
for _ in range(5):
    actions.send_keys(Keys.SPACE).perform()
    time.sleep(.5)

time.sleep(3) #Stuck this here to give the page enough time to load completely before scraping the data

# This line sets up the lists needed to be able to split the data up into their respective columns in the database.
flower_brand, flower_name, flower_sih, flower_potency, flower_qty, flower_price = ([] for i in range(6)) 


flowerbrand = driver.find_elements(By.XPATH, "//span[contains(@class, 'ProductBrand')]")    #Finds all brands on the page
flowername = driver.find_elements(By.XPATH, "//span[contains(@class, 'ProductName')]")      #Finds all products on the page
flowersih = driver.find_elements(By.XPATH, "//p[contains(@class, 'StrainText')]")           #Finds all strain types on page
flowerpotency = driver.find_elements(By.XPATH, "//div[contains(@class, 'Potency')]")        #Finds all potency info on page
#flowerprice = driver.find_elements(By.XPATH, "")        #Finds all pricing info on page

# This section appends information to respective lists.
for match in flowerbrand:
    flower_brand.append(match.text)
for match in flowername:
    flower_name.append(match.text)
for match in flowersih:
    flower_sih.append(match.text)
for match in flowerpotency:
    flower_potency.append(match.text)


#print('\n\n\n\n\n\n', flower_brand[1], "\n", flower_name[1], "\n", flower_sih[1], "\n", flower_potency[1], "\n\n\n")


###################################
#    CSV FILE OPERATIONS BELOW
###################################

############################
# Section below gets date information to prepend to CSV filename
import csv
import datetime

current_date = datetime.datetime.now().strftime("%Y%m%d") # Get the current date in the format "yyyymmdd"
#############################
current_time = datetime.datetime.now()
filetime = current_time.strftime('%H%M%S')

data = [] # Create a list to store the data

# Iterate through the elements and extract data
for brand, name, sih, potency in zip(flowerbrand, flowername, flowersih, flowerpotency):
    flowerbrand = brand.text
    flowername = name.text
    flowersih = sih.text
    flowerpotency = potency.text
    data.append([flowerbrand, flowername, flowersih, flowerpotency])

# Store the data in a CSV file
csv_file = f"{current_date}_{filetime}_thelandingflowerpricestest.csv"
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Write header
    writer.writerow(['Product Brand', 'Product Name', 'Sativa/Indica/Hybrid', 'Potency', '1/8 Oz Price', '1/4 Oz Price', '1/2 Oz Price'])
    
    # Write data
    writer.writerows(data)

print(f'Pricing data has been scraped and stored in {csv_file}.')

# Section below stores scraped flower shopping page data
announcement = driver.find_element(By.ID, "main-content")
flowerlistings = announcement.text
print("Flower price page scraped.")

##################################################################
#          Concentrates Listings, Quantities and Prices
##################################################################
domain = 'https://the-landing-dispensary-bridgeport.thelandingwv.com/stores/the-landing-dispensary-bridgeport/products/concentrates'
driver.get(domain);
time.sleep(1)

actions = ActionChains(driver)
for _ in range(4):
    actions.send_keys(Keys.SPACE).perform()
    time.sleep(.5)

# Section below stores scraped concentrate shopping page data
announcement = driver.find_element(By.ID, "main-content")
concentratelistings = announcement.text
print("Concentrate price page scraped.")

##################################################################
#           Vaporizers Listings, Quantities and Prices             
##################################################################
domain = 'https://the-landing-dispensary-bridgeport.thelandingwv.com/stores/the-landing-dispensary-bridgeport/products/vaporizers'

driver.get(domain);
time.sleep(1)

actions = ActionChains(driver)
for _ in range(5):
    actions.send_keys(Keys.SPACE).perform()
    time.sleep(.5)

# Section below stores scraped vape shopping page data
announcement = driver.find_element(By.ID, "main-content")
vapelistings = announcement.text
print("Vape price page scraped.")

#####################################################################
#
# Writes completed flower, concentrate, vape price list in plaintext             
#
#####################################################################
testtxtfile = f"{current_date}_{filetime}_text.txt"
with open(testtxtfile,'w') as file:
    file.write('The Landing Menu')
    file.write('\n\n')
    file.write(flowerlistings)
    file.write('\n\n\n\n')
    file.write(concentratelistings)
    file.write('\n\n\n\n')
    file.write(vapelistings)
    
print(testtxtfile, "written")

#landingflowerscrape();