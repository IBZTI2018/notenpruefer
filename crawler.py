from selenium import webdriver
import time
import sys

_debug = True

class notenpruefer():
  def __init__(self):
    self.__init_setup_webdriver()
    self.__init_load_credentials()

  def __init_setup_webdriver(self):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    self.driver = webdriver.Chrome(options=options)

  def __init_load_credentials(self):
    try:
      f = open("/shared/credentials.txt")
      credentials = f.read().split("::")
      self.username = credentials[0].strip()
      self.password = credentials[1].strip()
    except FileNotFoundError:
      print("No credentials provided!")
      sys.exit(1)

  def crawl_loop(self):
    self.crawl_index = 0

    print("starting crawl round {self.crawl_index}...")
    self.crawl_grades()

  def crawl_grades(self):
    self.driver.set_window_size(1280, 720)
    self.driver.get("https://campus.ibz.ch/unterricht/studierende/noteneinsicht")
    if _debug:
      print("opening ibz grade page, saving as ibz1.png")
      self.driver.save_screenshot("/shared/ibz1.png")

    if self.is_login_form_present():
      self.perform_login_and_wait()

    if _debug:
      print("should be logged in now, saving as ibz3.png")
      self.driver.save_screenshot("/shared/ibz3.png")
    
    print("check teh grades m8")

  def is_login_form_present(self):
    try:
      self.driver.find_element_by_id("login")
    except NoSuchElementException:
      return False
    return True

  def perform_login_and_wait(self):
    login_form = self.driver.find_element_by_id("login")
    login_form.find_element_by_name("user").send_keys(self.username)
    login_form.find_element_by_name("password").send_keys(self.password)

    if _debug:
      print("sending login information to site, saving as ibz2.png")
      self.driver.save_screenshot("/shared/ibz2.png")

    login_form.find_element_by_css_selector("button[type=submit]").click()
    time.sleep(10) # TODO: wait for actual load event instead of arbitrarily

gradebot = notenpruefer()
gradebot.crawl_loop()
