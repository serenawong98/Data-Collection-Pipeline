import time
import unittest
import scrapper_class
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import json
import os
import shutil


class ScrapperTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.bot = scrapper_class.Scrapper()
        pass
    

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
        flag = True
        url_list = self.bot.header_url_list()
        print(url_list)
        for i in url_list:
            self.bot.driver.get(i)
            try:
                self.bot.driver.find_element(by=By.CSS_SELECTOR, value="p[data-testid='invalidUrlError__message']")
                print(i)
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


    def test_get_shop_data(self):
        self.bot.driver.get("https://www.depop.com/cleopatress/")
        shop_data = self.bot.get_shop_data()
        self.assertEqual(len(shop_data), 6)
        self.assertIsInstance(shop_data, dict)
        self.assertEqual(shop_data["Username"][0], "@")
        self.assertEqual(shop_data["Items Sold"][-4:], "sold")
        self.assertEqual(shop_data["Last Active Date"][:6], "Active")
        self.assertIsInstance(int(shop_data["Followers"][0]), int)
        self.assertIsInstance(int(shop_data["Following"][0]), int)

        self.bot.driver.get("https://www.depop.com/alannahh_04/")
        shop_data = self.bot.get_shop_data()
        self.assertEqual(len(shop_data), 6)
        self.assertIsInstance(shop_data, dict)
        self.assertEqual(shop_data["Username"][0], "@")
        self.assertEqual(shop_data["Items Sold"][-4:], "sold")
        self.assertEqual(shop_data["Last Active Date"][:6], "Active")
        self.assertIsInstance(int(shop_data["Followers"][0]), int)
        self.assertIsInstance(int(shop_data["Following"][0]), int)

        self.bot.driver.get("https://www.depop.com/itsourlaura/")
        shop_data = self.bot.get_shop_data()
        self.assertEqual(len(shop_data), 6)
        self.assertIsInstance(shop_data, dict)
        self.assertEqual(shop_data["Username"][0], "@")
        self.assertEqual(shop_data["Items Sold"][-4:], "sold")
        self.assertEqual(shop_data["Last Active Date"][:6], "Active")
        self.assertIsInstance(int(shop_data["Followers"][0]), int)
        self.assertIsInstance(int(shop_data["Following"][0]), int)


    def test_product_availability(self):
        self.bot.driver.get("https://www.depop.com/products/suzy_a-colourblock-ribbed-tank-top/")
        self.assertEqual(self.bot.product_availability(), False)

        self.bot.driver.get('https://www.depop.com/products/suzy_a-long-flare-pants-in-black/')
        self.assertEqual(self.bot.product_availability(), True)


    def test_get_product_page_data(self):
        self.bot.driver.get("https://www.depop.com/products/chlloeharrison-topshop-washed-out-greyblack-mom/")
        os.mkdir('./raw_data/test')
        product_data = self.bot.get_product_page_data('./raw_data/test')
        self.assertEqual(len(product_data), 20)
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
        shutil.rmtree('./raw_data/test')

        self.bot.driver.get("https://www.depop.com/products/elizabeth_todd-geandmacore-blue-and-white-winter/")
        os.mkdir('./raw_data/test')
        product_data = self.bot.get_product_page_data('./raw_data/test')
        self.assertEqual(len(product_data), 20)
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
        shutil.rmtree('./raw_data/test')

        self.bot.driver.get("https://www.depop.com/products/bebelxl-brandy-melville-blue-and-white-9e65/")
        os.mkdir('./raw_data/test')
        product_data = self.bot.get_product_page_data('./raw_data/test')
        self.assertEqual(len(product_data), 20)
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
        shutil.rmtree('./raw_data/test')


    def test_reset_json_file(self):

        self.bot.reset_json_file('./raw_data/test.json')
        with open('./raw_data/test.json', "r") as f:
            f_data = json.load(f)

        self.assertIsInstance(f_data, list)
        os.remove('./raw_data/test.json')


    def test_add_data(self):
        filepath = './raw_data/test.json'
        with open(filepath, "w") as f:
            json.dump([], f)
        self.bot.add_data({"hi":"hello", "heh": "haha"}, filepath)
        self.bot.add_data({"bye":"goodbye"}, filepath)
        self.bot.add_data({"wow":"pop"}, filepath)

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
        image_path = self.bot.download_images(['https://i.ytimg.com/vi/RQkWvoES_uQ/maxresdefault.jpg','https://pbs.twimg.com/profile_images/1353075738358910977/0N3HhghG_400x400.jpg','https://i.pinimg.com/736x/f1/06/d7/f106d70f41c3d9e7db1f404adc93df38.jpg'], "cute_animals", './raw_data/images/')
        self.assertEqual(os.path.isfile(image_path+"/0.jpg"), True)
        self.assertEqual(os.path.isfile(image_path+"/1.jpg"), True)
        self.assertEqual(os.path.isfile(image_path+"/2.jpg"), True)


    def test_scrape_listing(self):

        output =[]
        filepath = "./raw_data/test.json"

        self.bot.driver.get("https://www.depop.com/cleopatress/")
        n = 26

        with open(filepath, "w") as f:
            json.dump(output, f)

        self.bot.scrape_listing(n, filepath)

        with open(filepath, "r") as f:
            file_data = json.load(f)
        
        self.assertEqual(len(file_data), n)
        self.assertIsInstance(file_data, list)
        for i in range(n):
            self.assertIsInstance(file_data[i], dict)

        self.bot.driver.get("https://www.depop.com/search/?q=skirt")

        n = 30

        with open(filepath, "w") as f:
            json.dump(output, f)

        self.bot.scrape_listing(n, filepath)

        with open(filepath, "r") as f:
            file_data = json.load(f)
        
        self.assertEqual(len(file_data), n)
        self.assertIsInstance(file_data, list)
        for i in range(n):
            self.assertIsInstance(file_data[i], dict)

        os.remove('./raw_data/test.json')


    @classmethod
    def tearDownClass(cls):
        cls.bot.driver.quit()
        # try:
        #     shutil.rmtree('./raw_data/test')
        # except:
        #     pass


if __name__ == "__main__":
    unittest.main()
