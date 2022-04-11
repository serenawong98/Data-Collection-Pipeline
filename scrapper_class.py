from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import uuid
import json
import os
import urllib

driver = webdriver.Chrome(service = Service('./chromedriver'))
driver.get("https://www.depop.com")
    
class Scrapper:

    """
    This class contains methods to scrape data from the website 'www.depop.com'.
    """
    
    def __init__(self):

        """
        Checks if 'accept cookies' button is present, and by passes it if present.
        """

        try:
            driver.find_element(by=By.CSS_SELECTOR, value="button[class='sc-kEqXSa sc-iqAclL sc-ciSkZP hQtFsL cmWQHQ exduyW']").click()
        except NoSuchElementException:
            print("no (accept cookies button) found")


    def nav_by_search(self, search_item):

        """
        Navigate to a specific search result corresponding to the 'search_item' input string.
        """

        search_url = "https://www.depop.com/search/?q="+search_item
        driver.get(search_url)

    def nav_by_shop(self, shop_name):

        """
        Navigate to a specific store front corresponding to the 'shop_name' input string.
        """

        shop_url = "https://www.depop.com/"+shop_name
        driver.get(shop_url)

    def header_url_list(self):

        """
        Returns a list with the URL from the webpage header.
        """

        header_url = []
        top_level_elements = driver.find_elements(by=By.CLASS_NAME, value="styles__NavigationItem-sc-__sc-10mkzda-3")
        for i in top_level_elements:
            try:
                child_level_elements = i.find_elements(by=By.XPATH, value=".//div/ul/li")
                for j in child_level_elements:
                    child_nav_option = j.find_element(by=By.XPATH, value=".//a").get_attribute("href")
                    header_url.append(child_nav_option)
            except NoSuchElementException:
                pass
        return header_url


    def listing_url(self, n):

        """
        Takes the input 'n' and returns the URL of the nth listing.
        """
        listing = driver.find_elements(by=By.CLASS_NAME, value="styles__ProductCardContainer-sc-__sc-13q41bc-8")
        listing_url = listing[n].find_element(by=By.XPATH, value=".//a").get_attribute("href")
        return listing_url

    def scroll_to_bottom(self):

        """
        Scrolls to the bottom of webpage.
        """

        webpage_height = driver.execute_script("return document.body.scrollHeight")
        current_height = 0
        while current_height <= webpage_height:
            driver.execute_script("window.scrollTo(0,"+str(current_height)+")")
            current_height += 30

    def back_page(self):

        """
        Navigates to the previous webpage.
        """

        driver.execute_script("window.history.go(-1)")

    def open_url_new_tab(self, url):
        """
        Takes an input URL string 'url' and opens the URL in a new tab.
        """
        driver.execute_script("window.open('" + url + "');")

    def close_tab(self):
        """
        Closes current active tab.
        """
        driver.close()

    def switch_tab(self, tab_no):
        """
        Switch to tab with the index 'tab_no'.
        """
        driver.switch_to.window(driver.window_handles[tab_no])

    def get_shop_data(self):
        """
        Returns data from a store front in the form of a dictionary.
        
        Data collected are: Username, Items sold, Last Active Date, Followers, Following, Bio description.
        """
        data_dictionary={}

        username = driver.find_element(by=By.CLASS_NAME, value="styles__UserName-sc-__r941b9-4").get_attribute("innerText")
        data_dictionary.update({"Username": username})
        items_sold = driver.find_element(by=By.XPATH, value="//*[@id='main']/div[1]/div[1]/div/div[2]/div[1]/p").get_attribute("innerText")
        data_dictionary.update({"Items Sold": items_sold})
        last_activity = driver.find_element(by=By.XPATH, value='//*[@id="main"]/div[1]/div[1]/div/div[2]/div[2]/p').get_attribute("innerText")
        data_dictionary.update({"Last Active Date": last_activity})
        followers = driver.find_element(by=By.XPATH, value='//*[@id="main"]/div[1]/div[2]/button[1]/p[1]').get_attribute("innerText")
        data_dictionary.update({"Followers": followers})
        following = driver.find_element(by=By.XPATH, value='//*[@id="main"]/div[1]/div[2]/button[2]/p[1]').get_attribute("innerText")
        data_dictionary.update({"Following": following})
        try:
            bio_text = driver.find_element(by=By.XPATH, value='//*[@id="main"]/div[1]/div[3]/p').get_attribute("innerText")
        except NoSuchElementException:
            bio_text = "None"
        data_dictionary.update({"Bio Description":bio_text})
        return data_dictionary        

    def product_availability(self):
        """
        Checks if an item is sold.
        """
        try:
            driver.find_element(by=By.CSS_SELECTOR, value="button.egHolT[color='yellow']")
            sold = True
        except NoSuchElementException:
            sold = False
        print("Product sold? "+ str(sold))
        return sold


    def get_product_page_data(self):
        """
        Returns data from a item listing in the form of a dictionary, and generates a UUID to identify data point.
        
        Data collected are: Product ID (url used), Username, Location, Number of Reviews, Number of items sold, Last Active Date, Number of Likes, Price, Discount, Sizes Available, Brand
        Item Condition, Colour, Style and Images of listing.
        """

        data_dictionary = {}

        data_dictionary.update({"Product ID": driver.current_url})
        data_dictionary.update({"UUID": str(uuid.uuid4())})
        shop_name = driver.find_element(by=By.CSS_SELECTOR, value="a[data-testid='bio__username']").get_attribute("innerText")
        data_dictionary.update({"Shop Name": shop_name})
        postcode = driver.find_element(by=By.CSS_SELECTOR, value="p[data-testid='bio__address']").get_attribute("innerText")
        data_dictionary.update({"Location": postcode})

        # <p data-testid="bio__address" type="caption1" class="sc-jrsJWt eoZhdh">United Kingdom</p>

        # rating = 0
        # for i in range(1, 5):

        #     star = driver.find_element(by=By.XPATH, value="//*[@id='feedback-star-" + str(i) + "-19262048']/title").get_attribute("innerText")
        #     if star == "Full Star":
        #         rating += 1
        #     elif star == "Half Star":
        #         rating += 0.5
        #     elif star == "Empty Star":
        #         rating += 0
        
        review_num = driver.find_element(by=By.CSS_SELECTOR, value="p[data-testid='feedback-btn__total']").get_attribute("innerText")
        data_dictionary.update({"No. of Reviews": review_num})
        sold = driver.find_element(by=By.CSS_SELECTOR, value="div[data-testid='signals__sold']")
        items_sold = sold.find_element(by=By.XPATH, value=".//p").get_attribute("innerText")

        data_dictionary.update({"No. of Items Sold": items_sold})
        active = driver.find_element(by=By.CSS_SELECTOR, value="div[data-testid='signals__active']")
        last_activity = active.find_element(by=By.XPATH, value=".//p").get_attribute("innerText")
        data_dictionary.update({"Last Active Date": last_activity})

        try:
            likes_num = driver.find_element(by=By.CSS_SELECTOR, value="span[data-testid='like-count']").get_attribute("innerText")
        except NoSuchElementException:
            likes_num = "0"
        data_dictionary.update({"No. of Likes": likes_num})

        try:
            price = driver.find_element(by=By.CSS_SELECTOR, value="p[data-testid='discountedPrice']").get_attribute("innerText")
            data_dictionary.update({"Price": price})
            data_dictionary.update({"Discount": True})
        except NoSuchElementException:
            price = driver.find_element(by=By.CSS_SELECTOR, value="p[data-testid='fullPrice']").get_attribute("innerText")
            data_dictionary.update({"Price": price})
            data_dictionary.update({"Discount": True})

        item_description = driver.find_element(by=By.CSS_SELECTOR, value="p[data-testid='product__description']").get_attribute("innerText")
        data_dictionary.update({"Item Description": item_description})
        last_refresh = driver.find_element(by=By.CSS_SELECTOR, value="time[data-testid='time']").get_attribute("innerText")
        data_dictionary.update({"Last Update": last_refresh})

        try:
            one_size = driver.find_element(by=By.CSS_SELECTOR, value="tr[data-testid='product__singleSize']")
            size = one_size.find_element(by=By.XPATH, value=".//td").get_attribute("innerText")

        except NoSuchElementException:
            size = "Multiple sizes"
        data_dictionary.update({"Sizes Available": size})

        try:
            brand = driver.find_element(by=By.CSS_SELECTOR, value="a[data-testid='product__brand']").get_attribute("innerText")
        except NoSuchElementException:
            brand = "None"
        data_dictionary.update({"Brand": brand})

        condition = driver.find_element(by=By.CSS_SELECTOR, value="td[data-testid='product__condition']").get_attribute("innerText")
        data_dictionary.update({"Item Condition": condition})

        try:
            colour = driver.find_element(by=By.CSS_SELECTOR, value="td[data-testid='product__colour']").get_attribute("innerText")
        except NoSuchElementException:
            colour = "None"
        data_dictionary.update({"Colour": colour})

        try:
            style_tag = driver.find_element(by=By.CSS_SELECTOR, value="td[data-testid='selected__styles']").get_attribute("innerText")
        except NoSuchElementException:
            style_tag = "None"
        data_dictionary.update({"Style": style_tag})

        img_urls = []
        image_elements = driver.find_elements(by=By.CSS_SELECTOR, value="img[class='LazyLoadImage__StyledImage-sc-__bquzot-1 doaiRN styles__LazyImage-sc-__sc-1fk4zep-9 hRpLaq']")
        for image_element in image_elements:
            img_url = image_element.get_attribute("src")
            if img_url not in img_urls:
                img_urls.append(img_url)
        data_dictionary.update({"Image Urls": img_urls})

        self.download_images(img_urls, driver.current_url)

        # print(rating)

        return data_dictionary

    def scrape_listing(self, number_of_listing, dict_name):
        """
        Scrapes data from listing on a specific webpage, eg.search webpage, store front webpage. Stores the scraped data in 

        Number of listign to scrape data from is defined by the input 'number_of _listing', 'dict_name' defines the dictionary name to stare the data under
        """
        for i in range(number_of_listing):
            if ((i)%24 == 0) and i !=0:
                self.scroll_to_bottom()
                time.sleep(1)
            listing_url = self.listing_url(i)
            self.open_url_new_tab(listing_url)
            self.switch_tab(1)
            self.scroll_to_bottom()
            scraped_data = self.get_product_page_data()
            self.add_data(scraped_data, "./raw_data/data.json", dict_name)
            self.close_tab()
            self.switch_tab(0)

    def create_json_file(self, filepath, main_dictionaries,):
        """
        Method to create a JSON file
        """
        output ={}
        for dictionary in main_dictionaries:
            output[dictionary]=[]
        with open(filepath, "w") as outfile:
            json.dump(output, outfile)

    def add_data(self, new_data, filepath, main_dictionary):
        """
        Method to add data to the JSON file
        """
        with open(filepath, 'r+') as file:
            file_data = json.load(file)
            file_data[main_dictionary].append(new_data)
            file.seek(0)
            json.dump(file_data, file)

    def download_images(self, url_list, product_id):
        """
        Method to download images with from a url
        """
        folder = product_id[22:]
        folder_name = folder.replace('/', '-')
        os.mkdir("./raw_data/images/"+folder_name)
        for i in range(len(url_list)):
            open("./raw_data/images/"+folder_name+"/"+str(i)+".jpg", 'w').close()
            urllib.request.urlretrieve(url_list[i], "./raw_data/images/"+folder_name+"/"+str(i)+".jpg")

        


if __name__ == "__main__":
    Scrapper()
    # Scrapper.nav_by_search(Scrapper, "top")
    # Scrapper.nav_by_url(Scrapper, Scrapper.header_url_list(Scrapper)[1])
    # Scrapper.scroll_to_bottom(Scrapper)
    # Scrapper.back_page(Scrapper)
    # Scrapper.open_url_new_tab(Scrapper, Scrapper.nav_listing(Scrapper, 2))
    # Scrapper.switch_tab(Scrapper, 0)
    # Scrapper.close_tab(Scrapper)

bot = Scrapper()
bot.nav_by_shop("cleopatress")
print("Current Page Title is : %s" %driver.title)
bot.create_json_file("./raw_data/data.json", ["Test_ShopData"])
bot.scrape_listing(150, "Test_ShopData")