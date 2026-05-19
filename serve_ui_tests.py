import pytest
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture(scope="session")
def driver():
	#Add ChromeOptions to disable 'password breach' error
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_experimental_option("detach", True) # keeps the browser window open
	prefs = {
	        "credentials_enable_service": False,
	        "profile.password_manager_enabled": False,
	        "profile.password_manager_leak_detection": False
	}
	chrome_options.add_experimental_option("prefs", prefs)

	#Initialize driver and navigate to url
	driver = webdriver.Chrome(options=chrome_options)
	driver.get("https://www.saucedemo.com/")

	yield driver

	driver.quit()

#login vars
username = "standard_user"
pw = "secret_sauce"

#util functions
def add_to_cart(driver, item_title, title_xpath):
	#turns title into id format
	item_id = re.sub(r' ', '-', item_title.lower())
	add_button = WebDriverWait(driver, 10).until(
	    EC.visibility_of_element_located((By.ID, f"add-to-cart-{item_id}"))
	)
	add_button.click()
	cart_button = WebDriverWait(driver, 10).until(
	    EC.visibility_of_element_located((By.ID, "shopping_cart_container"))
	)
	cart_button.click()
	cart_item_title = WebDriverWait(driver, 10).until(
	    EC.visibility_of_element_located((By.XPATH, title_xpath))
	)
	#asserts item is in cart
	assert cart_item_title.text == item_title
	#returns to Products page
	continue_shopping_button = driver.find_element(By.ID, "continue-shopping")
	continue_shopping_button.click()

def remove_from_cart(driver, item_title):
	cart_button = driver.find_element(By.ID, "shopping_cart_container")
	cart_button.click()
	remove_id = re.sub(r' ', '-', item_title.lower())
	remove_button = driver.find_element(By.ID, f"remove-{remove_id}")
	remove_button.click()


def test_login(driver):
	username_field = driver.find_element(By.ID, "user-name")
	pw_field = driver.find_element(By.ID, "password")
	login_button = driver.find_element(By.ID, "login-button")

	username_field.send_keys(username)
	pw_field.send_keys(pw)
	login_button.click()
	cart_button = driver.find_element(By.ID, "shopping_cart_container")
	assert cart_button.is_displayed()

def test_order_by_price(driver):
	sort_button = driver.find_element(By.CLASS_NAME, "product_sort_container")
	price_low_high = driver.find_element(By.XPATH, "//*[@value='lohi']")
	inventory_list = driver.find_element(By.CLASS_NAME, "inventory_list")
	inventory_item = driver.find_elements(By.CLASS_NAME, "inventory_item")

	sort_button.click()
	price_low_high.click()
	#asserts each item price is less than or equal to the next
	for i in range((len(inventory_item) - 1)):
		price_current = (driver.find_element(By.XPATH, f"(//div[@class='inventory_item_price'])[{i+1}]").text).replace("$", "")
		price_next = (driver.find_element(By.XPATH, f"(//div[@class='inventory_item_price'])[{i+2}]").text).replace("$", "")
		assert float(price_current) <= float(price_next)

def test_add_item_to_cart(driver):
	item_to_add = "Sauce Labs Fleece Jacket"
	first_title_xpath = "//div[@class='cart_item']/div[2]/a/div"
	add_to_cart(driver, item_to_add, first_title_xpath)

def test_add_second_item_to_cart(driver):
	item_to_add = "Sauce Labs Onesie"
	second_title_xpath = "//div[@class='cart_item'][2]/div[2]/a/div"
	add_to_cart(driver, item_to_add, second_title_xpath)

def test_cart_items(driver):
	cart_badge = driver.find_element(By.CLASS_NAME, "shopping_cart_badge")
	cart_count = int(cart_badge.text)
	assert cart_count == 2

def test_remove_item(driver):
	item_to_remove = "Sauce Labs Onesie"
	remove_from_cart(driver, item_to_remove)
	cart_badge = driver.find_element(By.CLASS_NAME, "shopping_cart_badge")
	cart_count = int(cart_badge.text)
	assert cart_count == 1

