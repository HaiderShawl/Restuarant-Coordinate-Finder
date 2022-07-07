# importing packages
from seleniumwire import webdriver
from seleniumwire.utils import decode

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json
import time
import sys
import pandas as pd


from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# declaring a variable to store the final data
final_data = [["Restaurant Name", "Latitude", "Longitude"]]

# configuring selenium chrome driver
service = Service(
    executable_path="/Users/haidershawl/Desktop/Anakin (YC)/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)


# opening the target website
driver.get("https://food.grab.com/sg/en/")

# waiting for the website to load
driver.implicitly_wait(5)

# finding the necessary elements
search_box = driver.find_element(by=By.ID, value="location-input")
search_button = driver.find_element(
    by=By.CLASS_NAME, value="submitBtn___2roqB")
load_more_button = driver.find_element(
    by=By.CLASS_NAME, value="ant-btn-block")


# entering location
search_box.send_keys(
    "Chinatown Point")

# selecting the first autocomplete location option available
try:
    list = WebDriverWait(driver, 20).until(EC.visibility_of_element_located(
        (By.CLASS_NAME, "ant-select-dropdown-menu")))
    list.find_elements(by=By.TAG_NAME, value="li")[0].click()
except:
    # exiting the program if no autocomplete location option was found
    sys.exit("Invalid Address. Try again")

# searching for restaurants around the selected loaction
search_button.click()

# printing the autocompleted location
location_element = driver.find_element(
    by=By.CLASS_NAME, value="title___dCI3A").find_elements(by=By.TAG_NAME, value="span")
location = location_element[1].get_attribute('innerHTML')
print(location)


# scrapping existing data on screen
existing_data = driver.find_element(
    by=By.ID, value="__NEXT_DATA__").get_attribute('innerHTML')
data1 = json.loads(existing_data)

# formatting the existing data
restaurant_data1 = data1["props"]["initialReduxState"]["pageRestaurantsV2"]["entities"]["restaurantList"]
restaurant_data2 = data1["props"]["initialReduxState"]["pageRestaurantsV2"]["entities"]["recommendedMerchants"]

for attr, value in restaurant_data1.items():
    final_data.append([value["name"], value["latitude"], value["longitude"]])
    print(value["name"], value["latitude"], value["longitude"])
for attr, value in restaurant_data2.items():
    final_data.append([value["name"], value["latitude"], value["longitude"]])
    print(value["name"], value["latitude"], value["longitude"])


# clicking load more button to get new retaurants
while (True):
    try:
        time.sleep(10)
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "ant-btn-block"))).click()
    except:
        break

# extracting new data from the network requests
for request in driver.requests:
    if request.response and request.url == 'https://portal.grab.com/foodweb/v2/search':
        body = decode(request.response.body, request.response.headers.get(
            'Content-Encoding', 'identity'))
        body = body.decode()
        body = body.replace('\\\"', '')
        body = body.replace('\\ "', '')
        body = body.replace('\\', '')

        new_data = json.loads(body)
        restaurant_data3 = new_data["searchResult"]["searchMerchants"]

        for value in restaurant_data3:
            final_data.append([value["address"]["name"], value["latlng"]["latitude"],
                               value["latlng"]["longitude"]])
            print(value["address"]["name"], value["latlng"]["latitude"],
                  value["latlng"]["longitude"])


df = pd.DataFrame(final_data)
df.to_csv(location + '.csv', index=False)

# driver.quit()
