import time
import unittest
from aiohttp import ClientConnectorSSLError, ClientError
import scrapper_class
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import json
import os
import shutil
import boto3
import urllib


class ScrapperTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.bot = scrapper_class.Scrapper()
        pass



    def test_nav_by_url(self):
        self.bot.nav_by_url("https://www.google.com")
        self.assertEqual(self.bot.driver.current_url, "https://www.google.com/")
        self.bot.nav_by_url("https://www.depop.com")
        self.assertEqual(self.bot.driver.current_url, "https://www.depop.com/")



    def test_nav_by_search(self):
        self.bot.nav_by_search("black jeans")
        self.assertEqual(self.bot.driver.current_url, "https://www.depop.com/search/?q=black%20jeans")
        self.bot.nav_by_search("croptop")
        self.assertEqual(self.bot.driver.current_url, "https://www.depop.com/search/?q=croptop")
        self.bot.nav_by_search("Rave outfit")
        self.assertEqual(self.bot.driver.current_url, "https://www.depop.com/search/?q=rave%20outfit")
        self.bot.nav_by_search("fairy_top")
        self.assertEqual(self.bot.driver.current_url, "https://www.depop.com/search/?q=fairy_top")
        self.bot.nav_by_search("black%20jeans")
        self.assertEqual(self.bot.driver.current_url, "https://www.depop.com/search/?q=black%20jeans")
        self.bot.nav_by_search("black=-qf")
        self.assertEqual(self.bot.driver.current_url, "https://www.depop.com/search/?q=black=-qf")



    def test_nav_by_shop(self):
        self.bot.nav_by_shop("cleopatress")
        self.assertEqual(self.bot.driver.current_url, "https://www.depop.com/cleopatress/")
        self.bot.nav_by_shop("robinrebecca")
        self.assertEqual(self.bot.driver.current_url, "https://www.depop.com/robinrebecca/")
        self.bot.nav_by_shop("oiwefn")
        self.assertEqual(self.bot.driver.current_url, "https://www.depop.com/oiwefn/")
        self.bot.nav_by_shop("re_mass")
        self.assertEqual(self.bot.driver.current_url, "https://www.depop.com/re_mass/")



    def test_header_url_list(self):
        self.bot.driver.get("https://www.depop.com")
        flag = True
        url_list = self.bot.header_url_list()
        # print(url_list)
        for i in url_list:
            self.bot.driver.get(i)
            try:
                self.bot.driver.find_element(by=By.CSS_SELECTOR, value="p[data-testid='invalidUrlError__message']")
                # print(i)
                flag = False
            except NoSuchElementException:
                pass
        if len(url_list)<1:
            flag = False
        self.assertEqual(flag, True)



    def test_listing_url(self):
        self.bot.driver.get('https://www.depop.com/search/?q=black%20jeans')
        time.sleep(2)
        url = self.bot.listing_url(1)
        self.bot.driver.get(url)
        self.assertEqual(self.bot.driver.current_url[:31], 'https://www.depop.com/products/')



    def test_scroll_to_bottom(self):
        webpage_height = self.bot.driver.execute_script("return document.body.scrollHeight")
        self.bot.scroll_to_bottom()
        current_height = self.bot.driver.execute_script("return window.pageYOffset")
        self.assertAlmostEqual(current_height, webpage_height, delta=800)



    def test_back_page(self):
        initial_url = self.bot.driver.current_url
        self.bot.driver.get('https://www.depop.com/cleopatress/')
        current_url = self.bot.driver.current_url
        self.bot.back_page()
        previous_url = self.bot.driver.current_url
        self.assertEqual(previous_url, initial_url)
        self.assertNotEqual(previous_url, current_url)



    def test_open_url_new_tab(self):
        initial_tab_count = len(self.bot.driver.window_handles)
        self.bot.open_url_new_tab("https://www.depop.com/")
        second_tab_count = len(self.bot.driver.window_handles)
        self.bot.open_url_new_tab("https://www.depop.com/")
        thrid_tab_count = len(self.bot.driver.window_handles)
        self.assertEqual(second_tab_count, initial_tab_count+1)
        self.assertEqual(thrid_tab_count, second_tab_count+1)
        for i in range(2, 0, -1):
            self.bot.driver.switch_to.window(self.bot.driver.window_handles[i])
            self.bot.driver.close()
        self.bot.driver.switch_to.window(self.bot.driver.window_handles[0])



    def test_close_tab(self):
        self.bot.driver.execute_script("window.open('https://www.depop.com/');")
        initial_tab_count = len(self.bot.driver.window_handles)
        self.bot.close_tab()
        final_tab_count = len(self.bot.driver.window_handles)
        self.assertEqual(final_tab_count, initial_tab_count-1)
        self.bot.driver.switch_to.window(self.bot.driver.window_handles[0])
    


    def test_switch_tab(self):
        self.bot.driver.execute_script("window.open('https://www.depop.com/');")
        self.bot.driver.execute_script("window.open('https://www.depop.com/');")
        self.bot.driver.execute_script("window.open('https://www.depop.com/');")
        tab_list = self.bot.driver.window_handles
        for i in range(len(tab_list)-1, 0, -1):
            self.bot.switch_tab(i)
            tab_index = tab_list.index(self.bot.driver.current_window_handle)
            self.assertEqual(tab_index, i)
            self.bot.driver.close()
        self.bot.driver.switch_to.window(self.bot.driver.window_handles[0])
        
        

    def test_close_browser(self):
        pass



    def test_page_http_status(self):
        self.bot.driver.get("https://www.google.com")
        status_code = self.bot.page_http_status()
        self.assertIsInstance(status_code, int)
        self.assertLess(status_code, 400)

        self.bot.driver.get("https://www.depop.com/osaijonvewuvkbv")
        status_code = self.bot.page_http_status()
        self.assertIsInstance(status_code, int)
        self.assertGreater(status_code, 400)




    def test_check_initiate_scraping(self):
        self.bot.driver.get("https://www.depop.com/cleopatress")
        page_working = self.bot.check_initiate_scraping()
        self.assertEqual(page_working, True)

        self.bot.driver.get("https://www.depop.com/cleosavnwuoebp")
        page_working = self.bot.check_initiate_scraping()
        self.assertEqual(page_working, False)



    def test_get_shop_data(self):
        self.bot.driver.get("https://www.depop.com/cleopatress/")
        shop_data = self.bot.get_shop_data()
        self.assertEqual(len(shop_data), 7)
        self.assertIsInstance(shop_data, dict)
        self.assertEqual(shop_data["Username"][0], "@")
        self.assertEqual(shop_data["Items Sold"][-4:], "sold")
        self.assertEqual(shop_data["Last Active Date"][:6], "Active")
        self.assertIsInstance(int(shop_data["Followers"][0]), int)
        self.assertIsInstance(int(shop_data["Following"][0]), int)
        self.assertIsInstance(int(shop_data["HTTP Request Status Code"]), int)

        self.bot.driver.get("https://www.depop.com/alannahh_04/")
        shop_data = self.bot.get_shop_data()
        self.assertEqual(len(shop_data), 7)
        self.assertIsInstance(shop_data, dict)
        self.assertEqual(shop_data["Username"][0], "@")
        self.assertEqual(shop_data["Items Sold"][-4:], "sold")
        self.assertEqual(shop_data["Last Active Date"][:6], "Active")
        self.assertIsInstance(int(shop_data["Followers"][0]), int)
        self.assertIsInstance(int(shop_data["Following"][0]), int)
        self.assertIsInstance(int(shop_data["HTTP Request Status Code"]), int)

        self.bot.driver.get("https://www.depop.com/itsourlaura/")
        shop_data = self.bot.get_shop_data()
        self.assertEqual(len(shop_data), 7)
        self.assertIsInstance(shop_data, dict)
        self.assertEqual(shop_data["Username"][0], "@")
        self.assertEqual(shop_data["Items Sold"][-4:], "sold")
        self.assertEqual(shop_data["Last Active Date"][:6], "Active")
        self.assertIsInstance(int(shop_data["Followers"][0]), int)
        self.assertIsInstance(int(shop_data["Following"][0]), int)
        self.assertIsInstance(int(shop_data["HTTP Request Status Code"]), int)



    def test_product_availability(self):
        self.bot.driver.get("https://www.depop.com/products/suzy_a-colourblock-ribbed-tank-top/")
        self.assertEqual(self.bot.product_availability(), False)

        self.bot.driver.get('https://www.depop.com/products/suzy_a-long-flare-pants-in-black/')
        self.assertEqual(self.bot.product_availability(), True)



    def test_get_product_page_data(self):
        self.bot.driver.get("https://www.depop.com/products/chlloeharrison-topshop-washed-out-greyblack-mom/")
        try:
            os.mkdir('./raw_data/test')
        except FileExistsError:
            shutil.rmtree('./raw_data/test')
            os.mkdir('./raw_data/test')
        product_data = self.bot.get_product_page_data('./raw_data/test', "ha")
        self.assertEqual(len(product_data), 22)
        self.assertIsInstance(product_data, dict)
        self.assertEqual(product_data["Product ID"][:31], "https://www.depop.com/products/")
        for char in product_data["Shop Name"]:
            self.assertNotEqual(char, " ")
        self.assertIsInstance(int(product_data["No. of Reviews"]), int)
        self.assertEqual(product_data["No. of Items Sold"][-4:], "sold")
        self.assertEqual(product_data["Last Active Date"][:6], "Active")
        self.assertEqual(product_data["No. of Likes"][-5:], "likes")
        self.assertIsInstance(float(product_data["Price"][1:]), float)
        self.assertIsInstance(product_data["Discount"], bool)
        self.assertEqual(product_data["Last Update"][:6], "LISTED")
        for url in product_data['Image Urls']:
            self.assertEqual(url[:31], "https://media-photos.depop.com/")
        self.assertIsInstance(int(product_data["HTTP Request Status Code"]), int)
        shutil.rmtree('./raw_data/test')

        self.bot.driver.get("https://www.depop.com/products/suzy_a-cami-lace-mesh-translucent-nightie-ae5d/")
        os.mkdir('./raw_data/test')
        product_data = self.bot.get_product_page_data('./raw_data/test', "ha")
        self.assertEqual(len(product_data), 22)
        self.assertIsInstance(product_data, dict)
        self.assertEqual(product_data["Product ID"][:31], "https://www.depop.com/products/")
        for char in product_data["Shop Name"]:
            self.assertNotEqual(char, " ")
        self.assertIsInstance(int(product_data["No. of Reviews"]), int)
        self.assertEqual(product_data["No. of Items Sold"][-4:], "sold")
        self.assertEqual(product_data["Last Active Date"][:6], "Active")
        self.assertEqual(product_data["No. of Likes"][-5:], "likes")
        self.assertIsInstance(float(product_data["Price"][1:]), float)
        self.assertIsInstance(product_data["Discount"], bool)
        self.assertEqual(product_data["Last Update"][:6], "LISTED")
        for url in product_data['Image Urls']:
            self.assertEqual(url[:31], "https://media-photos.depop.com/")
        self.assertIsInstance(int(product_data["HTTP Request Status Code"]), int)
        shutil.rmtree('./raw_data/test')

        self.bot.driver.get("https://www.depop.com/products/bebelxl-brandy-melville-blue-and-white-9e65/")
        os.mkdir('./raw_data/test')
        product_data = self.bot.get_product_page_data('./raw_data/test', "ha")
        self.assertEqual(len(product_data), 22)
        self.assertIsInstance(product_data, dict)
        self.assertEqual(product_data["Product ID"][:31], "https://www.depop.com/products/")
        for char in product_data["Shop Name"]:
            self.assertNotEqual(char, " ")
        self.assertIsInstance(int(product_data["No. of Reviews"]), int)
        self.assertEqual(product_data["No. of Items Sold"][-4:], "sold")
        self.assertEqual(product_data["Last Active Date"][:6], "Active")
        self.assertEqual(product_data["No. of Likes"][-5:], "likes")
        self.assertIsInstance(float(product_data["Price"][1:]), float)
        self.assertIsInstance(product_data["Discount"], bool)
        self.assertEqual(product_data["Last Update"][:6], "LISTED")
        for url in product_data['Image Urls']:
            self.assertEqual(url[:31], "https://media-photos.depop.com/")
        self.assertIsInstance(int(product_data["HTTP Request Status Code"]), int)
        shutil.rmtree('./raw_data/test')



    def test_create_reset_json_file(self):

        self.bot.create_reset_json_file("test")
        with open('./raw_data/test/data.json', "r") as f:
            f_data = json.load(f)

        self.assertIsInstance(f_data, list)
        shutil.rmtree('./raw_data/test')



    def test_add_data_json(self):
        filepath = './raw_data/test.json'
        with open(filepath, "w") as f:
            json.dump([], f)
        self.bot.add_data_json({"hi":"hello", "heh": "haha"}, filepath)
        self.bot.add_data_json({"bye":"goodbye"}, filepath)
        self.bot.add_data_json({"wow":"pop"}, filepath)

        with open(filepath, 'r') as file:
            file_data = json.load(file)
        
        self.assertIsInstance(file_data, list)
        self.assertIsInstance(file_data[0], dict)
        self.assertIsInstance(file_data[1], dict)
        self.assertIsInstance(file_data[2], dict)
        self.assertEqual(len(file_data), 3)
        self.assertEqual(len(file_data[0]), 2)
        self.assertEqual(file_data[0]["hi"], "hello")
        self.assertEqual(file_data[0]["heh"], "haha")
        self.assertEqual(file_data[1]["bye"], "goodbye")
        self.assertEqual(file_data[2]["wow"], "pop")

        os.remove('./raw_data/test.json')



    def test_download_images(self):
        try:
            os.mkdir('./raw_data/images')
        except:
            shutil.rmtree('./raw_data/images')
            os.mkdir('./raw_data/images')
        image_path = self.bot.download_images(['https://i.ytimg.com/vi/RQkWvoES_uQ/maxresdefault.jpg','https://pbs.twimg.com/profile_images/1353075738358910977/0N3HhghG_400x400.jpg','https://i.pinimg.com/736x/f1/06/d7/f106d70f41c3d9e7db1f404adc93df38.jpg'], "cute_animals", './raw_data/images')
        self.assertEqual(os.path.isfile(image_path+"/0.jpg"), True)
        self.assertEqual(os.path.isfile(image_path+"/1.jpg"), True)
        self.assertEqual(os.path.isfile(image_path+"/2.jpg"), True)
        shutil.rmtree('./raw_data/images')



    def test_scrape_listing(self):

        output =[]
        data_collection_folder_name = "test"
        try:
            os.mkdir(os.path.join("./raw_data", "test"))
        except FileExistsError:
            shutil.rmtree('./raw_data/images')
            os.mkdir('./raw_data/images')
        json_filepath = "./raw_data/test/data.json"

        self.bot.driver.get("https://www.depop.com/cleopatress")
        n = 26

        with open(json_filepath, "w") as f:
            json.dump(output, f)

        self.bot.scrape_listing(n, json_filepath, data_collection_folder_name)

        with open(json_filepath, "r") as f:
            file_data = json.load(f)
        
        self.assertEqual(len(file_data), n)
        self.assertIsInstance(file_data, list)
        for i in range(n):
            self.assertIsInstance(file_data[i], dict)

        self.bot.driver.get("https://www.depop.com/search/?q=skirt")

        n = 30

        with open(json_filepath, "w") as f:
            json.dump(output, f)

        self.bot.scrape_listing(n, json_filepath, data_collection_folder_name)

        with open(json_filepath, "r") as f:
            file_data = json.load(f)
       
        self.assertEqual(len(file_data), n)
        self.assertIsInstance(file_data, list)
        for i in range(n):
            self.assertIsInstance(file_data[i], dict)

        shutil.rmtree('./raw_data/test')



    def test_scrape_shop(self):
        output =[]
        data_collection_folder_name = "test"
        try:
            os.mkdir(os.path.join("./raw_data", "test"))
        except FileExistsError:
            shutil.rmtree(os.path.join("./raw_data", "test"))
            os.mkdir(os.path.join("./raw_data", "test"))
        json_filepath = "./raw_data/test/data.json"

        shops = ["cleopatress", "robinrebecca", "prettypiecess"]

        with open(json_filepath, "w") as f:
            json.dump(output, f)

        self.bot.scrape_shop(shops, data_collection_folder_name)

        with open(json_filepath, "r") as f:
            file_data = json.load(f)

        self.assertEqual(len(file_data), len(shops))
        self.assertIsInstance(file_data, list)
        for i in range(len(shops)):
            self.assertIsInstance(file_data[i], dict)

        shutil.rmtree('./raw_data/test')



    def test_get_image_directory_name(self):
        data_collection_folder_path = os.path.join("./raw_data", "test")
        try:
            os.mkdir(data_collection_folder_path)
        except:
            shutil.rmtree(data_collection_folder_path)
            os.mkdir(data_collection_folder_path)
        img_folder_path = os.path.join(data_collection_folder_path, "images")
        os.mkdir(img_folder_path)
        os.mkdir(os.path.join(img_folder_path, "folder_one"))
        os.mkdir(os.path.join(img_folder_path, "folder_two"))
        os.mkdir(os.path.join(img_folder_path, "folder_three"))
        os.mkdir(os.path.join(img_folder_path, "folder_four"))

        directory_list = self.bot.get_image_directory_name("test")
        is_folder_in_list = True
        if "folder_one" not in directory_list:
            is_folder_in_list = False
        if "folder_two" not in directory_list:
            is_folder_in_list = False
        if "folder_three" not in directory_list:
            is_folder_in_list = False
        if "folder_four" not in directory_list:
            is_folder_in_list = False
        self.assertEqual(is_folder_in_list, True)

        shutil.rmtree(data_collection_folder_path)



    def test_get_img_file_list(self):

        data_collection_folder_path = os.path.join("./raw_data", "test")
        try:
            os.mkdir(data_collection_folder_path)
        except:
            shutil.rmtree(data_collection_folder_path)
            os.mkdir(data_collection_folder_path)
        img_folder_path = os.path.join(data_collection_folder_path, "images")
        os.mkdir(img_folder_path)
        os.mkdir(os.path.join(img_folder_path, "a"))
        os.mkdir(os.path.join(img_folder_path, "b"))
        os.mkdir(os.path.join(img_folder_path, "c"))
        os.mkdir(os.path.join(img_folder_path, "d"))

        open("./raw_data/test/images/a/1.txt", 'w').close()
        open("./raw_data/test/images/a/2.txt", 'w').close()
        open("./raw_data/test/images/b/1.txt", 'w').close()
        open("./raw_data/test/images/b/2.txt", 'w').close()
        open("./raw_data/test/images/c/1.txt", 'w').close()
        open("./raw_data/test/images/c/2.txt", 'w').close()
        open("./raw_data/test/images/c/3.txt", 'w').close()
        open("./raw_data/test/images/d/1.txt", 'w').close()
        open("./raw_data/test/images/d/2.txt", 'w').close()
        open("./raw_data/test/images/d/3.txt", 'w').close()
        open("./raw_data/test/images/d/4.txt", 'w').close()

        file_list_by_folder = self.bot.get_img_file_list("test", ["a", "b", "c", "d"])

        self.assertEqual(len(file_list_by_folder), 4)
        self.assertEqual(len(file_list_by_folder[0]), 2)
        self.assertEqual(file_list_by_folder[0][0], "./raw_data/test/images/a/2.txt")
        self.assertEqual(file_list_by_folder[0][1], "./raw_data/test/images/a/1.txt")
        self.assertEqual(len(file_list_by_folder[1]), 2)
        self.assertEqual(file_list_by_folder[1][0], "./raw_data/test/images/b/2.txt")
        self.assertEqual(file_list_by_folder[1][1], "./raw_data/test/images/b/1.txt")
        self.assertEqual(len(file_list_by_folder[2]), 3)
        self.assertEqual(file_list_by_folder[2][0], "./raw_data/test/images/c/3.txt")
        self.assertEqual(file_list_by_folder[2][1], "./raw_data/test/images/c/2.txt")
        self.assertEqual(file_list_by_folder[2][2], "./raw_data/test/images/c/1.txt")
        self.assertEqual(len(file_list_by_folder[3]), 4)
        self.assertEqual(file_list_by_folder[3][0], "./raw_data/test/images/d/4.txt")
        self.assertEqual(file_list_by_folder[3][1], "./raw_data/test/images/d/3.txt")
        self.assertEqual(file_list_by_folder[3][2], "./raw_data/test/images/d/2.txt")
        self.assertEqual(file_list_by_folder[3][3], "./raw_data/test/images/d/1.txt")

        shutil.rmtree(data_collection_folder_path)



    def test_upload_data_to_s3(self):
        pass


    
    def test_check_is_duplicate(self):
        list_of_dictionary = [{"Product ID": 'hi'}, {"Product ID": 'hello'}, {"Product ID": 'bye'}]
        with open("./test.json", "w") as file:
            json.dump(list_of_dictionary, file)
        
        is_hi_in_datafile, index = self.bot.check_is_duplicate("./test.json", "hi")
        self.assertEqual(is_hi_in_datafile, True)
        self.assertIsInstance(index, int)
        is_hello_in_datafile, index = self.bot.check_is_duplicate("./test.json", "hello")
        self.assertEqual(is_hello_in_datafile, True)
        self.assertIsInstance(index, int)
        is_bye_in_datafile, index = self.bot.check_is_duplicate("./test.json", "bye")
        self.assertEqual(is_bye_in_datafile, True)
        self.assertIsInstance(index, int)
        is_goodbye_in_datafile, index = self.bot.check_is_duplicate("./test.json", "goodbye")
        self.assertEqual(is_goodbye_in_datafile, False)
        self.assertIsInstance(index, bool)
        os.remove("./test.json")



    def test_do_not_scrape(self):
        output = []
        with open("test.json", "w") as file:
            json.dump(output, file)

        self.bot.do_not_scrape("test.json")

        with open("test.json", "r") as file:
            file_data = json.load(file)

        self.assertEqual(len(file_data), 1)
        os.remove("./test.json")



    def test_listing_is_scraped(self):
        output = [{"Location Listing is Found": ["blablabla"]}]
        with open("./test.json", "w") as file:
            json.dump(output, file)

        self.bot.listing_is_scraped("test.json", 0, "blablabla")
        
        with open("./test.json", "r") as file:
            file_data = json.load(file)

        self.assertEqual(len(file_data[0]["Location Listing is Found"]), 1)

        self.bot.listing_is_scraped("test.json", 0, "hahhaha")
        
        with open("./test.json", "r") as file:
            file_data = json.load(file)
        
        self.assertEqual(len(file_data[0]["Location Listing is Found"]), 2)

        self.bot.listing_is_scraped("test.json", 0, "lalala")
        
        with open("./test.json", "r") as file:
            file_data = json.load(file)
        
        self.assertEqual(len(file_data[0]["Location Listing is Found"]), 3)
        os.remove("./test.json")

            

    def test_upload_img_to_s3(self):
        data_collection_folder_path = os.path.join("./raw_data", "test")
        try:
            os.mkdir(data_collection_folder_path)
        except:
            shutil.rmtree(data_collection_folder_path)
            os.mkdir(data_collection_folder_path)
        img_folder_path = os.path.join(data_collection_folder_path, "images")
        os.mkdir(img_folder_path)
        folder_a = os.path.join(img_folder_path, "a")
        os.mkdir(folder_a)
        folder_b = os.path.join(img_folder_path, "b")
        os.mkdir(folder_b)

        image_url = ["https://media-photos.depop.com/b0/19500478/1068425541_25628b1ceb3d4eb2b2c7704092b0b0d9/P0.jpg", "https://media-photos.depop.com/b0/19500478/1068425557_af91ce704e194c67b8de78b5a0a86658/P0.jpg"]
        folder_a_file = []
        folder_b_file = []
        for i in range(len(image_url)):
            open(folder_a+"/"+str(i)+".jpg", 'w').close()
            a_file = os.path.join(folder_a, str(i)+".jpg")
            urllib.request.urlretrieve(image_url[i], a_file)
            folder_a_file.append(a_file)
            open(folder_b+"/"+str(i)+".jpg", 'w').close()
            b_file = os.path.join(folder_b, str(i)+".jpg")
            urllib.request.urlretrieve(image_url[i], b_file)
            folder_b_file.append(b_file)
        file_by_folder = [folder_a_file, folder_b_file]

        self.bot.upload_img_to_s3("test", ["a", "b"], file_by_folder)
        self.s3 = boto3.client('s3')

        is_file_on_S3 = True

        try:
            self.s3.download_file('datacollectionpipeline', 'test/images/a/0.jpg', 'test_a_0')
            self.s3.download_file('datacollectionpipeline', 'test/images/a/1.jpg', 'test_a_1')
            self.s3.download_file('datacollectionpipeline', 'test/images/b/0.jpg', 'test_b_0')
            self.s3.download_file('datacollectionpipeline', 'test/images/b/1.jpg', 'test_b_1')
        except ClientError:
            is_file_on_S3 = False
        
        self.assertEqual(is_file_on_S3, True)

        self.s3_resource = boto3.resource('s3')
        bucket = self.s3_resource.Bucket('datacollectionpipeline')
        bucket.objects.filter(Prefix="test").delete()
        os.remove("test_a_0")
        os.remove("test_a_1")
        os.remove("test_b_0")
        os.remove("test_b_1")




    def test_upload_json_to_s3(self):
        output =[]
        data_collection_folder_name = "test"
        try:
            os.mkdir(os.path.join("./raw_data", data_collection_folder_name))
        except FileExistsError:
            shutil.rmtree(os.path.join("./raw_data", data_collection_folder_name))
            os.mkdir(os.path.join("./raw_data", data_collection_folder_name))
        json_filepath = "./raw_data/test/data.json"

        with open(json_filepath, "w") as f:
            json.dump(output, f)

        self.bot.upload_json_to_s3(data_collection_folder_name, json_filepath)

        self.s3 = boto3.client('s3')
        self.s3.download_file('datacollectionpipeline', 'test/data.json', 'test_upload_json_to_s3')

        with open("test_upload_json_to_s3", "r") as s3file:
            file_data = json.load(s3file)

        self.assertEqual(output, file_data)

        self.s3_resource = boto3.resource('s3')
        bucket = self.s3_resource.Bucket('datacollectionpipeline')
        bucket.objects.filter(Prefix="test").delete()

        os.remove("test_upload_json_to_s3")



    @classmethod
    def tearDownClass(cls):
        cls.bot.driver.quit()
        try:
            shutil.rmtree('./raw_data/test')
        except:
            pass


if __name__ == "__main__":
    unittest.main()
