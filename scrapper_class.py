from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import uuid
import json
import os
import urllib
import urllib.request
import sys

class Scrapper:
    """
    This class contains methods to scrape data from the website 'www.depop.com'.
    """


    def __init__(self):
        """
        Checks if 'accept cookies' button is present, and by passes it if present.
        """

        self.driver = webdriver.Chrome(service = Service('./chromedriver'))
        self.driver.get("https://www.depop.com")
        try:
            self.driver.find_element(by=By.CSS_SELECTOR, value="button[class='sc-kEqXSa sc-iqAclL sc-ciSkZP hQtFsL cmWQHQ exduyW']").click()
        except NoSuchElementException:
            print("no (accept cookies button) found")



    def nav_by_search(self, search_item):
        """
        Navigate to a specific search result corresponding to the 'search_item' input string.
        """

        search_url = "https://www.depop.com/search/?q="+search_item
        self.driver.get(search_url)



    def nav_by_shop(self, shop_name):
        """
        Navigate to a specific store front corresponding to the 'shop_name' input string.
        """

        shop_url = "https://www.depop.com/"+shop_name
        self.driver.get(shop_url)



    def header_url_list(self):
        """
        Returns a list with the URL from the webpage header.
        """

        header_url = []
        top_level_elements = self.driver.find_elements(by=By.CSS_SELECTOR, value="li[data-testid='treeNavigation__dropdown']")
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
        listing = self.driver.find_elements(by=By.CLASS_NAME, value="styles__ProductCardContainer-sc-__sc-13q41bc-8")
        listing_url = listing[n].find_element(by=By.XPATH, value=".//a").get_attribute("href")
        return listing_url



    def scroll_to_bottom(self):
        """
        Scrolls to the bottom of webpage.
        """

        webpage_height = self.driver.execute_script("return document.body.scrollHeight")
        current_height = 0
        while current_height <= webpage_height:
            self.driver.execute_script("window.scrollTo(0,"+str(current_height)+")")
            current_height += 30



    def back_page(self):
        """
        Navigates to the previous webpage.
        """

        self.driver.execute_script("window.history.go(-1)")



    def open_url_new_tab(self, url):
        """
        Takes an input URL string 'url' and opens the URL in a new tab.
        """
        self.driver.execute_script("window.open('" + url + "');")



    def close_tab(self):
        """
        Closes current active tab.
        """
        self.driver.close()



    def switch_tab(self, tab_no):
        """
        Switch to tab with the index 'tab_no'.
        """
        self.driver.switch_to.window(self.driver.window_handles[tab_no])

    

    def close_browser(self):
        """
        Close current active browser
        """
        self.driver.quit()



    # def page_not_found_error(self):
    #     """
    #     Raise error if page is not found
    #     """



    def get_shop_data(self):
        """
        Returns data from a store front in the form of a dictionary.
        
        Data collected are: Username, Items sold, Last Active Date, Followers, Following, Bio description.
        """

        data_dictionary={}

        username = self.driver.find_element(by=By.CSS_SELECTOR, value="p[data-testid='username']").get_attribute("innerText")
        data_dictionary.update({"Username": username})

        try:
            items_sold_container = self.driver.find_element(by=By.CSS_SELECTOR, value="div[data-testid='signals__sold']")
            items_sold = items_sold_container.find_element(by=By.XPATH, value=".//p").get_attribute("innerText")
        except NoSuchElementException:
            items_sold = '0 sold'
        data_dictionary.update({"Items Sold": items_sold})

        last_activity_container = self.driver.find_element(by=By.CSS_SELECTOR, value="div[data-testid='signals__active']")
        last_activity = last_activity_container.find_element(by=By.XPATH, value=".//p").get_attribute("innerText")
        data_dictionary.update({"Last Active Date": last_activity})
        
        followers_container = self.driver.find_element(by=By.CSS_SELECTOR, value="button[aria-label='followers']")
        followers = followers_container.find_element(by=By.XPATH, value=".//p").get_attribute("innerText")
        data_dictionary.update({"Followers": followers})

        following_container = self.driver.find_element(by=By.CSS_SELECTOR, value="button[aria-label='following']")
        following = following_container.find_element(by=By.XPATH, value=".//p").get_attribute("innerText")
        data_dictionary.update({"Following": following})
# <div class="styles__UserDescription-sc-__r941b9-7 emKGCV"><p class="sc-jrsJWt dfXtnW">Brand new, handmade crochet and second hand clothing | instant buy is on ⚡️</p></div>
        try:
            bio_text = self.driver.find_element(by=By.CLASS_NAME, value='styles__UserDescription-sc-__r941b9-7').get_attribute("innerText")
        except NoSuchElementException:
            bio_text = "None"
        data_dictionary.update({"Bio Description":bio_text})
        return data_dictionary     



    def product_availability(self):
        """
        Checks if an item is sold.
        """
        try:
            self.driver.find_element(by=By.CSS_SELECTOR, value="button.egHolT[color='yellow']")
            available = False
        except NoSuchElementException:
            available = True
        return available



    def get_product_page_data(self, img_folder_name):
        """
        Returns data from a item listing in the form of a dictionary, and generates a UUID to identify data point.
        
        Data collected are: Product ID (url used), Username, Location, Number of Reviews, Number of items sold, Last Active Date, Number of Likes, Price, Discount, Sizes Available, Brand
        Item Condition, Colour, Style and Images of listing.
        """

        data_dictionary = {}

        data_dictionary.update({"Product ID": self.driver.current_url})
        data_dictionary.update({"UUID": str(uuid.uuid4())})
        try:
            shop_name = self.driver.find_element(by=By.CSS_SELECTOR, value="a[data-testid='bio__username']").get_attribute("innerText")
            data_dictionary.update({"Shop Name": shop_name})
        except:
            data_dictionary.update({"Shop Name": "ERROR"})
            print("Shop Name ERROR:" + str(sys.exc_info()[0]))

        try:
            postcode = self.driver.find_element(by=By.CSS_SELECTOR, value="p[data-testid='bio__address']").get_attribute("innerText")
            data_dictionary.update({"Location": postcode})
        except:
            data_dictionary.update({"Location": "ERROR"})
            print("Location ERROR:" + str(sys.exc_info()[0]))

        try:
            review_num = self.driver.find_element(by=By.CSS_SELECTOR, value="p[data-testid='feedback-btn__total']").get_attribute("innerText")
            data_dictionary.update({"No. of Reviews": review_num})
        except:
            data_dictionary.update({"No. of Reviews": "0"})
        
        try:
            sold = self.driver.find_element(by=By.CSS_SELECTOR, value="div[data-testid='signals__sold']")
            items_sold = sold.find_element(by=By.XPATH, value=".//p").get_attribute("innerText")
            data_dictionary.update({"No. of Items Sold": items_sold})
        except:
            data_dictionary.update({"No. of Items Sold": "0 sold"})

        try:
            active = self.driver.find_element(by=By.CSS_SELECTOR, value="div[data-testid='signals__active']")
            last_activity = active.find_element(by=By.XPATH, value=".//p").get_attribute("innerText")
            data_dictionary.update({"Last Active Date": last_activity})
        except:
            data_dictionary.update({"Last Active Date": "ERROR"})
            print("Last Active Date ERROR:" + str(sys.exc_info()[0]))

        try:
            likes_num = self.driver.find_element(by=By.CSS_SELECTOR, value="span[data-testid='like-count']").get_attribute("innerText")
        except NoSuchElementException:
            likes_num = "0"
        data_dictionary.update({"No. of Likes": likes_num})

        try:
            price = self.driver.find_element(by=By.CSS_SELECTOR, value="p[data-testid='discountedPrice']").get_attribute("innerText")
            data_dictionary.update({"Price": price})
            data_dictionary.update({"Discount": True})
        except NoSuchElementException:
            price = self.driver.find_element(by=By.CSS_SELECTOR, value="p[data-testid='fullPrice']").get_attribute("innerText")
            data_dictionary.update({"Price": price})
            data_dictionary.update({"Discount": True})

        try:
            item_description = self.driver.find_element(by=By.CSS_SELECTOR, value="p[data-testid='product__description']").get_attribute("innerText")
        except:
            item_description = "ERROR"
            print("Item description ERROR:" + str(sys.exc_info()[0]))
        data_dictionary.update({"Item Description": item_description})

        try:
            last_refresh = self.driver.find_element(by=By.CSS_SELECTOR, value="time[data-testid='time']").get_attribute("innerText")
        except:
            last_refresh = "ERROR"
            print("Last Refresh ERROR:" + str(sys.exc_info()[0]))
        data_dictionary.update({"Last Update": last_refresh})

        try:
            one_size = self.driver.find_element(by=By.CSS_SELECTOR, value="tr[data-testid='product__singleSize']")
            size = one_size.find_element(by=By.XPATH, value=".//td").get_attribute("innerText")
        except NoSuchElementException:
            size = "Multiple sizes"
        data_dictionary.update({"Sizes Available": size})

        try:
            brand = self.driver.find_element(by=By.CSS_SELECTOR, value="a[data-testid='product__brand']").get_attribute("innerText")
        except NoSuchElementException:
            brand = "None"
        data_dictionary.update({"Brand": brand})

        try:
            condition = self.driver.find_element(by=By.CSS_SELECTOR, value="td[data-testid='product__condition']").get_attribute("innerText")
        except:
            condition = "none"
            # print("Condition ERROR:" + str(sys.exc_info()[0]))
        data_dictionary.update({"Item Condition": condition})

        try:
            colour = self.driver.find_element(by=By.CSS_SELECTOR, value="td[data-testid='product__colour']").get_attribute("innerText")
        except NoSuchElementException:
            colour = "None"
        data_dictionary.update({"Colour": colour})

        try:
            style_tag = self.driver.find_element(by=By.CSS_SELECTOR, value="td[data-testid='selected__styles']").get_attribute("innerText")
        except NoSuchElementException:
            style_tag = "None"
        data_dictionary.update({"Style": style_tag})

        item_availability = self.product_availability()
        if item_availability == True:
            data_dictionary.update({"Item Availability": "Available"})
        else:
            data_dictionary.update({"Item Availability": "Unavailable"})

        img_urls = []
        try:
            image_elements = self.driver.find_elements(by=By.CSS_SELECTOR, value="img[class='LazyLoadImage__StyledImage-sc-__bquzot-1 doaiRN styles__LazyImage-sc-__sc-1fk4zep-9 hRpLaq']")
            for image_element in image_elements:
                img_url = image_element.get_attribute("src")
                if img_url not in img_urls:
                    img_urls.append(img_url)
            data_dictionary.update({"Image Urls": img_urls})

            img_path = self.download_images(img_urls, self.driver.current_url, img_folder_name)
            data_dictionary.update({"Saved Images Path": img_path})
        except:
            data_dictionary.update({"Image Urls": "ERROR"})
            data_dictionary.update({"Saved Images Path": "ERROR"})
            print("Image ERROR:" + str(sys.exc_info()[0]))

        return data_dictionary



    def reset_json_file(self, filepath):
        """
        Method to create a JSON file
        """
        output =[]

        with open(filepath, "w") as outfile:
            json.dump(output, outfile)



    def add_data(self, new_data, filepath):
        """
        Method to add data to the JSON file
        """

        with open(filepath, 'r') as file:
            file_data = json.load(file)
        
        file_data.append(new_data)
        
        with open(filepath, "w") as file:
            json.dump(file_data, file)



    def download_images(self, url_list, product_id, img_test_folder_name):
        """
        Method to download images with from a url
        """

        folder = product_id[22:]
        folder_name = folder.replace('/', '-')
        copy = False
        copy_num = ""
        
        img_path = ""
        try:
            img_folder_name = img_test_folder_name+"/"+folder_name
            os.mkdir(img_folder_name)
        except FileExistsError:
            copy_num = str(uuid.uuid4())
            img_folder_name = img_test_folder_name+"/"+folder_name+copy_num
            os.mkdir(img_folder_name)
            copy = True
        for i in range(len(url_list)):
            if copy == False:    
                img_path = img_test_folder_name+"/"+folder_name
                open(img_path+"/"+str(i)+".jpg", 'w').close()
                urllib.request.urlretrieve(url_list[i], img_path+"/"+str(i)+".jpg")
            else:
                img_path = img_test_folder_name+"/"+folder_name+copy_num
                open(img_path+"/"+str(i)+".jpg", 'w').close()
                urllib.request.urlretrieve(url_list[i], img_path+"/"+str(i)+".jpg")

        return img_path
    

    def scrape_listing(self, number_of_listing, json_file_path):
        """
        Scrapes data from listing on a specific webpage, eg.search webpage, store front webpage. Stores the scraped data in 

        Number of listign to scrape data from is defined by the input 'number_of _listing', 'dict_name' defines the dictionary name to stare the data under
        """

        img_folder_name = "./raw_data/images/"

        for i in range(number_of_listing):
            # if ((i)%24 == 0) and i !=0:
            #     self.scroll_to_bottom()
            #     time.sleep(1)
            time.sleep(1)
            try:
                listing_url = self.listing_url(i)
            except IndexError:
                self.scroll_to_bottom()
                time.sleep(3)
                listing_url = self.listing_url(i)
            print(listing_url)
            self.open_url_new_tab(listing_url)
            self.switch_tab(1)
            self.scroll_to_bottom()
            scraped_data = self.get_product_page_data(img_folder_name)
            self.add_data(scraped_data, json_file_path)
            self.close_tab()
            self.switch_tab(0)




if __name__ == "__main__":
    # Scrapper()
    # Scrapper.nav_by_search(Scrapper, "top")
    # Scrapper.nav_by_url(Scrapper, Scrapper.header_url_list(Scrapper)[1])
    # Scrapper.scroll_to_bottom(Scrapper)
    # Scrapper.back_page(Scrapper)
    # Scrapper.open_url_new_tab(Scrapper, Scrapper.nav_listing(Scrapper, 2))
    # Scrapper.switch_tab(Scrapper, 0)
    # Scrapper.close_tab(Scrapper)
    bot = Scrapper()
    bot.nav_by_shop("cleopatress")
    print("Current Page Title is : %s" %bot.driver.title)
    json_file_path = "./raw_data/data.json"
    bot.reset_json_file(json_file_path)
    bot.scrape_listing(30, json_file_path)
    # bot.close_browser()
    



