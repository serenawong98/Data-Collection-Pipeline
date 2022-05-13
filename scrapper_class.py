from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
import shutil
import time
import uuid
import json
import os
import urllib
import sys
import boto3
import requests
import pandas as pd
import sqlalchemy


class Scrapper:
    """
    This class is used to scrape data from the website 'www.depop.com'.
    """


    def __init__(self):
        """
        Checks if 'accept cookies' button is present and bypasses it if present.
        """
        options = Options()
        options.add_argument('--headless')

        self.driver = webdriver.Firefox(service = Service(GeckoDriverManager().install()), options=options)
        # self.driver = webdriver.Firefox(service = Service('/usr/local/bin/geckodriver'))
        # self.driver = webdriver.Chrome(service=Service('./chromedriver'))
        self.driver.get("https://www.depop.com")
        try:
            self.driver.find_element(by=By.CSS_SELECTOR, value="button[class='sc-kEqXSa sc-iqAclL sc-ciSkZP hQtFsL cmWQHQ exduyW']").click()
        except NoSuchElementException:
            print("no (accept cookies button) found")

        database_type = 'postgresql'
        db_api = 'psycopg2'
        endpoint = 'datacollectionpipeline.ch75hznqokor.eu-west-2.rds.amazonaws.com'
        user = 'postgres'
        password = 'AvoNaru20172209'
        port = 5432
        database = 'postgres'
        self.engine = sqlalchemy.create_engine(f"{database_type}+{db_api}://{user}:{password}@{endpoint}:{port}/{database}")
        self.engine.connect()


    def nav_by_url(self, url):
        """
        This method is used to navigate to a webpage with the specified URL.

        Args:
            url (str): Ther URL to navigate to.
        """

        self.driver.get(url)



    def nav_by_search(self, search_item):
        """
        This method is used to navigate to a search result webpage.

        Args:
            search_item (str): A string of the search page to navigate to.

        """

        search_url = "https://www.depop.com/search/?q="+search_item
        self.driver.get(search_url)



    def nav_by_shop(self, shop_name):
        """
        This method is used to navigate to a depop store front webpage.

        Args:
            shop_name (str): The name of the depop store front to navigate to.

        """

        shop_url = "https://www.depop.com/"+shop_name
        self.driver.get(shop_url)



    def header_url_list(self):
        """
        This method is used to obtains a list of URLs in the depop webpage header.

        Returns:
            list of str: A list of the URLs found in the webpage header excluding the final URL.
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
        return header_url[:-1]



    def listing_url(self, n):
        """
        This method is used to obtain the URL of the (n-1)th indexed product listing on a search 
        webpage or a store front.

        Args:
            n (int): An integer representing the index of product on the current webpage.

        Returns:
            str: The URL of the (n-1)th indexed product on the webpage.
        """
        listing = self.driver.find_elements(by=By.CLASS_NAME, value="styles__ProductCardContainer-sc-__sc-13q41bc-8")
        listing_url = listing[n].find_element(by=By.XPATH, value=".//a").get_attribute("href")
        return listing_url



    def scroll_to_bottom(self):
        """
        This method is used to scroll slowly to the bottom of the webpage, making sure all
        contents of the webpage are loaded.
        """

        webpage_height = self.driver.execute_script("return document.body.scrollHeight")
        current_height = 0
        while current_height <= webpage_height:
            self.driver.execute_script("window.scrollTo(0,"+str(current_height)+")")
            current_height += 30



    def back_page(self):
        """
        This method is used to navigate to the previous webpage.
        """

        self.driver.execute_script("window.history.go(-1)")



    def open_url_new_tab(self, url):
        """
        This method is used to open a URL in a new tab.

        Args:
            url (str): The URL to open in a new tab
        """
        self.driver.execute_script("window.open('" + url + "');")



    def close_tab(self):
        """
        The method is used to close the current active tab.
        """
        self.driver.close()



    def switch_tab(self, tab_no):
        """
        This method is used to switch the active tab to the tab with the index number tab_no.

        Args:
            tab_no (int): The index of the active tab to switch to.
        """
        self.driver.switch_to.window(self.driver.window_handles[tab_no])

    

    def close_browser(self):
        """
        This method is used to close the current active browser.
        """
        self.driver.quit()



    def page_http_status(self):
        """
        This method is used to check the HTTPS status of the a webpage with a specific URL.

        Args:
            url (str): The URL of the webpage to check.

        Returns:
            int: The status code of the HTTPS request.
        """
        passed = False
        while passed == False:
            try:
                r = requests.get(self.driver.current_url)
                passed = True
            except requests.exceptions.InvalidSchema:
                time.sleep(1)
        return r.status_code
        


    def check_initiate_scraping(self):

        """
        This method is used to check if scraping functions should be initiated. If the HTTPS
        status is 4XX or 5XX, this function returns a False to indicate scrapping should not
        be initiated.
        
        Returns:
            bool: False if page cannot be loaded sucessfully. True if page was loaded sucessfully.
        """
        page_status = self.page_http_status()
        page_working = True
        print(page_status)
        if page_status >= 400:
            print("more than 400")
            self.driver.refresh()
            time.sleep(2)
            try:
                self.listing_url(2)
            except IndexError:
                print("PAGE UNAVAILABLE")
                page_working = False
        
        return page_working



    def get_shop_data(self):
        """
        This method is used to obtain data from a store front. 

        Returns:
            dict[str, str or bool]: Data returned in dictionary are Username, Items sold, 
                                    Last Active Date, Followers, Following, Bio description,
                                    HTTPS request status code of webpage.
        """

        data_dictionary={}

        try:
            username = self.driver.find_element(by=By.CSS_SELECTOR, value="p[data-testid='username']").get_attribute("innerText")
            data_dictionary.update({"Username": username})
        except:
            data_dictionary.update({"Username": "ERROR" + str(sys.exc_info()[0])})
            print("Username ERROR:" + str(sys.exc_info()[0]))

        try:
            items_sold_container = self.driver.find_element(by=By.CSS_SELECTOR, value="div[data-testid='signals__sold']")
            items_sold = items_sold_container.find_element(by=By.XPATH, value=".//p").get_attribute("innerText")
        except NoSuchElementException:
            items_sold = '0 sold'
        data_dictionary.update({"Items Sold": items_sold})

        try:
            last_activity_container = self.driver.find_element(by=By.CSS_SELECTOR, value="div[data-testid='signals__active']")
            last_activity = last_activity_container.find_element(by=By.XPATH, value=".//p").get_attribute("innerText")
            data_dictionary.update({"Last Active Date": last_activity})
        except:
            data_dictionary.update({"Last Active Date": "ERROR" + str(sys.exc_info()[0])})
            print("Last Active Date ERROR:" + str(sys.exc_info()[0]))

        try:
            followers_container = self.driver.find_element(by=By.CSS_SELECTOR, value="button[aria-label='followers']")
            followers = followers_container.find_element(by=By.XPATH, value=".//p").get_attribute("innerText")
            data_dictionary.update({"Followers": followers})
        except:
            data_dictionary.update({"Followers": "ERROR" + str(sys.exc_info()[0])})
            print("Followers ERROR:" + str(sys.exc_info()[0]))

        try:
            following_container = self.driver.find_element(by=By.CSS_SELECTOR, value="button[aria-label='following']")
            following = following_container.find_element(by=By.XPATH, value=".//p").get_attribute("innerText")
            data_dictionary.update({"Following": following})
        except:
            data_dictionary.update({"Following": "ERROR" + str(sys.exc_info()[0])})
            print("Following ERROR:" + str(sys.exc_info()[0]))

        try:
            bio_text = self.driver.find_element(by=By.CLASS_NAME, value='styles__UserDescription-sc-__r941b9-7').get_attribute("innerText")
        except NoSuchElementException:
            bio_text = "None"
        data_dictionary.update({"Bio Description":bio_text})

        data_dictionary.update({"HTTP Request Status Code": self.page_http_status()})

        return data_dictionary     



    def product_availability(self):
        """
        This method is used to check if an product is sold.
        """
        # value="td[data-testid='product__condition']"
        try:
            self.driver.find_element(by=By.CSS_SELECTOR, value="button[data-testid='button__sold']")
            available = False
        except NoSuchElementException:
            available = True
        return available



    def get_product_page_data(self, img_filepath, listing_location):
        """
        This method is used to obtain data from a product listing. It generates a UUID to 
        identify the data point, and downloads images associated witht he product listing.

        Args: 
            img_filepath (str): The file path containing the location to store downloaded images
        
        Returns:
            dict[str, str or bool]: Data returned in the dictionary are Product ID (url used), 
                                    Username, Location, Number of Reviews, Number of items sold,
                                    Last Active Date, Number of Likes, Price, Discount, Sizes 
                                    Available, Brand Item Condition, Colour, Style, URL of Images, 
                                    Filepath of Images Downloaded, HTTPS Request Status Code,
                                    and the URL location of where the listing was found.
        """

        data_dictionary = {}

        data_dictionary.update({"Product ID": self.driver.current_url})
        uuid_generated = str(uuid.uuid4())
        data_dictionary.update({"UUID": uuid_generated})

        try:
            shop_name = self.driver.find_element(by=By.CSS_SELECTOR, value="a[data-testid='bio__username']").get_attribute("innerText")
            data_dictionary.update({"Shop Name": shop_name})
        except:
            data_dictionary.update({"Shop Name": "ERROR"+ str(sys.exc_info()[0])})
            print("Shop Name ERROR:" + str(sys.exc_info()[0]))

        try:
            postcode = self.driver.find_element(by=By.CSS_SELECTOR, value="p[data-testid='bio__address']").get_attribute("innerText")
            data_dictionary.update({"Location": postcode})
        except:
            data_dictionary.update({"Location": "ERROR" + str(sys.exc_info()[0])})
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
            data_dictionary.update({"Last Active Date": "ERROR" + str(sys.exc_info()[0])})
            print("Last Active Date ERROR:" + str(sys.exc_info()[0]))

        try:
            likes_num = self.driver.find_element(by=By.CSS_SELECTOR, value="span[data-testid='like-count']").get_attribute("innerText")
        except NoSuchElementException:
            likes_num = "0"
        data_dictionary.update({"No. of Likes": likes_num})
    
        try:
            price_container = self.driver.find_element(by=By.CLASS_NAME, value="styles__Layout-sc-__sc-1fk4zep-4")
            price = price_container.find_element(by=By.CSS_SELECTOR, value="p[data-testid='discountedPrice']").get_attribute("innerText")
            data_dictionary.update({"Price": price})
            data_dictionary.update({"Discount": True})
        except NoSuchElementException:
            price_container = self.driver.find_element(by=By.CLASS_NAME, value="styles__Layout-sc-__sc-1fk4zep-4")
            price = price_container.find_element(by=By.CSS_SELECTOR, value="p[data-testid='fullPrice']").get_attribute("innerText")
            data_dictionary.update({"Price": price})
            data_dictionary.update({"Discount": False})
        except:
            data_dictionary.update({"Price": "ERROR" + str(sys.exc_info()[0])})
            print("Price" + str(sys.exc_info()[0]))


        try:
            item_description = self.driver.find_element(by=By.CSS_SELECTOR, value="p[data-testid='product__description']").get_attribute("innerText")
        except:
            item_description = "ERROR" + str(sys.exc_info()[0])
            print("Item description ERROR:" + str(sys.exc_info()[0]))
        data_dictionary.update({"Item Description": item_description})

        try:
            last_refresh = self.driver.find_element(by=By.CSS_SELECTOR, value="time[data-testid='time']").get_attribute("innerText")
        except:
            last_refresh = "ERROR" + str(sys.exc_info()[0])
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

            img_path = self.download_images(img_urls, uuid_generated, img_filepath)
            data_dictionary.update({"Saved Images Path": img_path})
        except:
            data_dictionary.update({"Image Urls": "ERROR" + str(sys.exc_info()[0])})
            data_dictionary.update({"Saved Images Path": "ERROR" + str(sys.exc_info()[0])})
            print("Image ERROR:" + str(sys.exc_info()[0]))

        data_dictionary.update({"HTTP Request Status Code": self.page_http_status()})

        data_dictionary.update({"Location Listing is Found": [listing_location]})

        return data_dictionary



    def create_reset_json_file(self, data_collection_folder_name):
        """
        This method is used to create a JSON file. If JSON file already exists and has data,
        this method replaces contents fo the file with an empty list. It also creates a directory
        for the data collection run.

        Args:
            data_collection_folder_name (str): The data collection folder name. A name given to
                                                the data collection run.

        Returns:
            str: Filepath of JSON file created.
        """
        output =[]
        try:
            os.mkdir(os.path.join("./raw_data", data_collection_folder_name))
        except FileExistsError:
            pass
        filepath = os.path.join("./raw_data", data_collection_folder_name, "data.json")


        with open(filepath, "w") as outfile:
            json.dump(output, outfile)
        return filepath



    def add_data_json(self, new_data, json_filepath):
        """
        This method is used to add data to the JSON file.

        Args:
            new_data (dict): The data to add to the JSON file.
            filepath (str): file path of the JSON file.
        """

        with open(json_filepath, 'r') as file:
            file_data = json.load(file)
        
        file_data.append(new_data)
        
        with open(json_filepath, "w") as file:
            json.dump(file_data, file)



    def download_images(self, url_list, product_id, img_folder_name):
        """
        This method is used to download images from an image URL.

        Args:
            url_list (list): List containing URLs of images
            product_id (string): The ID used to identify products. Used here so that images
                                can be saved under their respective product ID folder.
            img_folder_name (str): The file path of the location to save folder of downloaded 
                                    images

        Returns:
            str: The file path of the folder containing image(s) saved.
        """
        
        img_path = img_folder_name+"/"+product_id
        os.mkdir(img_path)

        for i in range(len(url_list)):
            open(img_path+"/"+str(i)+".jpg", 'w').close()
            urllib.request.urlretrieve(url_list[i], img_path+"/"+str(i)+".jpg")


        return img_path
    


    def check_is_duplicate(self, json_filepath, listing_id):

        """
        This method checks whether the data from the product listing is has already been scraped.
        
        Args:
            json_filepath (str): The filepath of the JSON file.
            listing_id (str): The ID of the product listing to be scraped    
        """

        with open(json_filepath, "r") as json_file:
            json_data = json.load(json_file)
        
        for i in range(len(json_data)):
            if json_data[i]["Product ID"] == listing_id:
                return True, i

        return False, False



    def do_not_scrape(self, json_filepath):

        """
        This method is used to the json data file when the page to scrape cannot be reached.
        
        Args:
            data_collection_folder_name (str): The data collection folder name. A name given to
                                                the data collection run.

        """

        self.add_data_json({"HTTPS REQUEST ERROR WITH CODE": self.page_http_status()}, json_filepath)



    def listing_is_scraped(self, json_filepath, index, parent_page_url):

        """
        This method is used to update the existing JSON file, to show the location where the product listing was found.
        
        Args: 
            json_filepath (str): Location of the JSON file to update.
            index (int): Index of the data in the JSON file to update.
            parent_page_url (str): URL of the webpage where the scraped product listing was found.
        """

        print('REPEAT')
        with open(json_filepath, "r") as json_file:
            json_data = json.load(json_file)

        old_data = json_data[index]["Location Listing is Found"]

        if parent_page_url in old_data:
            pass
        else:
            json_data[index]["Location Listing is Found"].append(parent_page_url)
            with open(json_filepath, "w") as file:
                json.dump(json_data, file)



    def scrape_listing(self, number_of_listing, json_filepath, data_collection_folder_name):

        """
        This method is used to scrape data from product listings on a specific webpage, 
        eg.search webpage, store front webpage. It checks whether data from a product listing
        has already been scraped, if yes, the product listing will not be scraped.

        Args:
            number_of_listing (int): The number of product listing to scrape data from.
            json_filepath (str): The file path of the JSON file.
            data_collection_folder_name (str): The data collection folder name. A name given to
                                                the data collection run.

        """

        data_collection_folder_path = os.path.join("./raw_data", data_collection_folder_name)

        try:
            os.mkdir(data_collection_folder_path)
        except FileExistsError:
            pass

        img_filepath = os.path.join(data_collection_folder_path, "images")

        try:
            os.mkdir(img_filepath)
        except FileExistsError:
            pass

        scraped_data = {}
        parent_page_url = self.driver.current_url

        for i in range(number_of_listing):

            time.sleep(1)
            product_listing_found = True
            try:
                listing_url = self.listing_url(i)
            except IndexError:
                self.scroll_to_bottom()
                time.sleep(3)
                try:
                    listing_url = self.listing_url(i)
                except IndexError:
                    self.driver.get(parent_page_url)
                    time.sleep(3)
                    try:
                        listing_url = self.listing_url(i)
                    except IndexError:
                        product_listing_found == False
                        scraped_data = {"ERROR": "Can't find any product listing"}
                        print("CAN'T FIND ANY PRODUCT LISTING")


            
            if product_listing_found == True:
                print(listing_url)
                self.open_url_new_tab(listing_url)
                self.switch_tab(1)
                page_status = self.page_http_status()
                print(page_status)
                print(self.driver.current_url)
                if page_status >= 400:
                    print('hi')
                    time.sleep(3)
                    self.driver.refresh()

                is_data_duplicated, index = self.check_is_duplicate(json_filepath, self.driver.current_url)
                try:
                    rds_duplicate = self.check_duplicate_on_rds(self.driver.current_url, data_collection_folder_name)
                except:
                    rds_duplicate = False

               
                if is_data_duplicated == False and rds_duplicate == False:
                    self.scroll_to_bottom()
                    scraped_data = self.get_product_page_data(img_filepath, parent_page_url)
                    self.add_data_json(scraped_data, json_filepath)
                elif is_data_duplicated == True and rds_duplicate == False:
                    self.listing_is_scraped(json_filepath, index, parent_page_url)
                else:
                    self.duplicated_on_rds(parent_page_url, self.driver.current_url)


                self.close_tab()
                self.switch_tab(0)
            else:
                pass

    

    def scrape_shop(self, shops, data_collection_folder_name):
        
        """
        This method is used to scrape data from different depop store webpages.
        
        Args:
            shops [list of str]: List of username of stores to scrape data from
            data_collection_folder_name (str): The data collection folder name. A name given to
                                                the data collection run.
        """

        data_collection_folder_path = os.path.join("./raw_data", data_collection_folder_name)

        for shop in shops:
            self.nav_by_shop(shop)
            scraped_data = self.get_shop_data()
            self.add_data_json(scraped_data, os.path.join(data_collection_folder_path, "data.json"))



    def get_image_directory_name(self, data_collection_folder_name):
        """
        This method is used to get the parent directory names of images saved while scrapping.
        
        Args:
            data_collection_folder_name (str): The data collection folder name. A name given to
                                                the data collection run.
        
        Returns:
            list of str: List containing the parent directory names of images saved.
        """


        directory_list = []
        for root, dirs, files in os.walk(os.path.join("./raw_data", data_collection_folder_name, "images")):
            for dir in dirs:
                directory_list.append(dir)
        return directory_list



    def get_img_file_list(self, data_collection_folder_name, directory_list):

        """
        This method is used to obtain a list of lists containing image paths. It groups
        images with the same parent directory in the same list.

        Args:
            data_collection_folder_name (str): The data collection folder name. A name given to
                                                the data collection run.
            directory_list (list of str): Folder names of parent directory of images.
        
        Returns:
            list of (list of str): List of lists containing image paths, with the images of the 
                                    same parent directory grouped in the same list.
        """

        file_list_by_folder = []
        for i in directory_list:
            file_list = []
            dir_name = os.path.join("./raw_data", data_collection_folder_name, "images", i)
            for root, dirs, files in os.walk(dir_name):
                for file in files:

                    file_list.append(os.path.join(root, file))
            file_list_by_folder.append(file_list)
        
        return file_list_by_folder



    def upload_data_to_s3(self, data_collection_folder_name, local_json_file_path, upload_image):
        """
        This method uploads images into AWS S3.

        Args:
            data_collection_folder_name (str): The data collection folder name. A name given to
                                                the data collection run.
            local_json_file_path (str): File path of JSON file.
            upload_image (bool): If true, upload images to S3
        """

        img_directory_list = self.get_image_directory_name(data_collection_folder_name)
        img_file_list_by_folder = self.get_img_file_list(data_collection_folder_name, img_directory_list)

        if upload_image == True:
            self.upload_img_to_s3(data_collection_folder_name, img_directory_list, img_file_list_by_folder)
        else:
            pass
        self.upload_json_to_s3(data_collection_folder_name, local_json_file_path)



    def upload_img_to_s3(self, data_collection_folder_name, directory_list, img_file_list_by_folder):
        """
        This method uploads images into AWS S3.

        Args:
            data_collection_folder_name (str): The data collection folder name. A name given to
                                                the data collection run.
            directory_list (list of str): Folder names of parent directory of images.
            img_file_list_by_folder (list of (list of str)): List of lists containing image 
                                                            paths, with the images of the 
                                                            same parent directory grouped in 
                                                            the same list.

        """

        self.s3_client = boto3.client('s3')
        for i in range(len(img_file_list_by_folder)):
            
            for j in range(len(img_file_list_by_folder[i])):
                self.s3_client.upload_file(img_file_list_by_folder[i][j], 'datacollectionpipeline', os.path.join(data_collection_folder_name, 'images', directory_list[i], str(j)+".jpg"))



    def upload_json_to_s3(self, data_collection_folder_name, local_json_file_path):
        """
        This method uploads a JSON file into AWS S3.

        Args:
            data_collection_folder_name (str): The data collection folder name. A name given to
                                                the data collection run.
            local_json_file_path (str): File path of JSON file.

        """

        self.s3_client = boto3.client('s3')
        self.s3_client.upload_file(local_json_file_path, 'datacollectionpipeline', os.path.join(data_collection_folder_name, "data.json"))



    def upload_to_rds(self,json_filepath, data_collection_name):
        """
        This method is used to upload data from a JSON file to AWS.

        Args:
            json_filepath (str): File path of JSON file to upload.
            data_collection_folder_name (str): The data collection folder name. A name given to
                                                the data collection run.
        """
        with open(json_filepath, 'r') as file:
            data = json.load(file)

        df = pd.DataFrame(data)

        df.to_sql(data_collection_name, self.engine, if_exists='replace')



    def check_duplicate_on_rds(self, product_id, rds_table_name):
        """
        This method is used to check whether data scraped already exists on AWS RDS.

        Args:
            product_id (str): Unique string used to identify data.
            rds_table_name (str): Table name of the data in AWS RDS to check.
        """
        self.df = pd.read_sql_query("SELECT * FROM " + rds_table_name, self.engine)
        duplicate = False
        for index, row in self.df.iterrows():
            if row['Product ID'] == product_id:
                duplicate = True
            else:
                pass
        return duplicate



    def duplicated_on_rds(self, search_to_check, product_id):
        """
        This method is used to update AWS RDS data, if data scraped already exists. If the
        same product is found in two different search terms (eg. short skirt and mini skirt), it
        updates the exisitng column 'Location Listing is Found' to include the two searches.

        Args:
            search_to_check (str): Search term that the duplicated product listing showed up in.
            product_id (str): Unique string of the data duplicated.
        """
        for index, row in self.df.iterrows():
            if row['Product ID'] == product_id:
                search_locations = row['Location Listing is Found'][1:-1]
                search_location_seperator_index = []
                for char_index in range(len(search_locations)):
                    if search_locations[char_index] == ",":
                        search_location_seperator_index.append(char_index)
                search_location_seperator_index.append(len(search_locations))
                search_location_list = []
                search_location_num = len(search_location_seperator_index)
                if search_location_num == 1:
                    search_location_list.append(search_locations)
                else:
                    for i in range(search_location_num):
                        if i == 0:
                            search_location_list.append(search_locations[:search_location_seperator_index[i]])
                        else:
                            search_location_list.append(search_locations[search_location_seperator_index[i-1]+1:search_location_seperator_index[i]])

                if search_to_check not in search_location_list:
                    search_location_string = "{" + search_locations + "," + search_to_check + "}"
                    self.df.loc[index, "Location Listing is Found"] = search_location_string

        self.df.to_sql("skirt_search", self.engine, if_exists='replace', index=False)



    def download_rds(self, rds_table_name):
        """
        This method is used to download AWS RDS data in the dataframe format.

        Args:
            rds_table_name (str): Table name of the data in AWS RDS to download.
        """
        self.df = pd.read_sql_query("SELECT * FROM " + rds_table_name, self.engine)



if __name__ == "__main__":

    bot = Scrapper()

    skirt_search_data_collection = "skirt_search"
    skirt_search_json_path = bot.create_reset_json_file(skirt_search_data_collection)
    searches = ["black skirt", 'skirt black']
    for i in range(len(searches)):
        bot.nav_by_search(searches[i])
        is_page_working = bot.check_initiate_scraping()
        if is_page_working == True:
            bot.scrape_listing(5, skirt_search_json_path, skirt_search_data_collection)
        else:
            bot.do_not_scrape(skirt_search_json_path)
    bot.upload_to_rds(skirt_search_json_path, skirt_search_data_collection)



    cleopatress_listing_data_collection_name = "cleopatress_shop_listing"
    cleopatress_listing_json_file_path = bot.create_reset_json_file(cleopatress_listing_data_collection_name)
    bot.nav_by_shop("cleopatress")
    is_page_working = bot.check_initiate_scraping()
    if is_page_working == True:
        bot.scrape_listing(100, cleopatress_listing_json_file_path, cleopatress_listing_data_collection_name)
    else:
        bot.add_data_json({"HTTPS REQUEST ERROR WITH CODE": bot.page_http_status()}, cleopatress_listing_json_file_path)
    bot.upload_data_to_s3(cleopatress_listing_data_collection_name, cleopatress_listing_json_file_path, True)




    shop_front_data_collection_name = "store_front_data"
    shop_front_json_file_path = bot.create_reset_json_file(shop_front_data_collection_name)
    shops = ["cleopatress", "robinrebecca", "prettypiecess"]
    bot.scrape_shop(shops, shop_front_data_collection_name)
    bot.upload_data_to_s3(shop_front_data_collection_name, shop_front_json_file_path, False)




    header_data_collection_name = "header_listings"
    header_json_file_path = bot.create_reset_json_file(header_data_collection_name)
    header_url_list = bot.header_url_list()
    for header in header_url_list:
        bot.nav_by_url(header)
        is_page_working = bot.check_initiate_scraping()
        if is_page_working == True:
            bot.scrape_listing(1, header_json_file_path, header_data_collection_name)
        else:
            bot.add_data_json({"HTTPS REQUEST ERROR WITH CODE": bot.page_http_status()}, header_json_file_path)
    bot.upload_data_to_s3(header_data_collection_name, header_json_file_path, True)

    bot.close_browser()

    



