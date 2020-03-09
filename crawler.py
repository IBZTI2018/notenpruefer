from selenium.common.exceptions import *
from selenium import webdriver
import requests
import json
import time
import sys

_debug = True
_interval = 600

class notenpruefer():
  def __init__(self):
    self.__init_setup_webdriver()
    self.__init_load_credentials()
    self.__init_slack_webhook()

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

  def __init_slack_webhook(self):
    try:
      f = open("/shared/webhook.txt")
      webhook = f.read().strip()
      self.webhook = webhook
    except FileNotFoundError:
      print("No webhook link provided!")
      sys.exit(1)

  def crawl_loop(self):
    self.crawl_cache = {}
    self.crawl_index = 0

    #while True:
    print("starting crawl round " + str(self.crawl_index) + "...")
    grades = self.crawl_grades()

    #if crawl_index != 0:
    print(grades)

    self.crawl_cache = grades # REMOVE THIS AFTER TESTING
    self.send_message_to_slack("no") # REMOVE
    
    print("finished crawl round " + str(self.crawl_index) + ", waiting...")
    self.crawl_cache = grades
    #time.sleep(_interval)

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

    return self.fetch_grades_from_overview2()

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
    time.sleep(5) # TODO: wait for actual load event instead of arbitrarily

  def fetch_grades_from_overview(self):
    grades = {}
    grade_list = self.driver.find_elements_by_class_name("x-grid3-scroller")[0]
    grade_entries = grade_list.find_elements_by_tag_name("table")
    for grade_entry in grade_entries:
      entry_fields = grade_entry.find_elements_by_tag_name("td")
      if (len(entry_fields) != 9):
        continue

      name = entry_fields[4].find_elements_by_tag_name("div")[0].text
      grade = entry_fields[7].find_elements_by_tag_name("div")[0].text
      grades[name] = grade

    return grades

  def fetch_grades_from_overview2(self):
    import re
    # Intercept all XHR requests.
    # If url contains 'SearchService'(URL for fetching grades) then save response to a variable named as rawInterceptedData
    self.driver.execute_script("""
      (function (XHR) {
        "use strict";

        var element = document.createElement('div');
        element.id = "interceptedResponse";
        element.appendChild(document.createTextNode(""));
        document.body.appendChild(element);

        var open = XHR.prototype.open;
        var send = XHR.prototype.send;

        XHR.prototype.open = function (method, url, async, user, pass) {
          this._url = url; // want to track the url requested
          open.call(this, method, url, async, user, pass);
        };

        XHR.prototype.send = function (data) {
          var self = this;
          var oldOnReadyStateChange;
          var url = this._url;

          function onReadyStateChange() {
            if (self.status === 200 && self.readyState == 4 /* complete */) {
              if (url.indexOf("SearchService") !== -1) {
                window.rawInterceptedData = self.responseText;
              }
            }
            if (oldOnReadyStateChange) {
              oldOnReadyStateChange();
            }
          }

          if (this.addEventListener) {
            this.addEventListener("readystatechange", onReadyStateChange,
              false);
          } else {
            oldOnReadyStateChange = this.onreadystatechange;
            this.onreadystatechange = onReadyStateChange;
          }
          send.call(this, data);
        }
      })(XMLHttpRequest);
    """)

    # Run again the grades fetch function
    # Since it is nested on a very deep object, it's almost impossible to run the fetch function with our own custom response handler.
    self.driver.execute_script("""
                Ext.onReady(function () {
      var cfg = {};
      cfg.widgetName = "user_grades";
      cfg.widgetKey = "c6a67a56-b570-0001-903a-11f911e0114c";
      nice2.flows.publicflows.PublicFlow.run("nice2.optional.qualification.publicflows.usergrades.UserGradesFlow", cfg);
    });
    """)

    time.sleep(5)

    rawInterceptedData = self.driver.execute_script(
      "return window.rawInterceptedData")
    regexWonder = "({createdEntities.+)\)\);"
    cleanedInterceptedData = re.search(
      regexWonder, rawInterceptedData).group(1)
    grades = self.driver.execute_script("""
                var cleanedInterceptedData = % s;
    window.ibz_noten = [];
    for (var row in cleanedInterceptedData.returnValue.rows) {
      row = cleanedInterceptedData.returnValue.rows[row];
      if ("cells" in row) {
        var fach = row["cells"]["relInput.relInput_node.short"].cellValues[0].value;
        var veranstaltung = row["cells"]["event"].cellValues[0].value;
        var note = row["cells"]["rating"].cellValues[0].value;
        ibz_noten.push([fach, veranstaltung, note]);
      }
    }
    return window.ibz_noten;
    """ % cleanedInterceptedData)

    return grades


  def send_message_to_slack(self, grade_for):
    data = {
      'text': 'Testy.',
      'username': 'gradebot',
      'icon_emoji': ':robot_face:'
    }

    requests.post(self.webhook, data=json.dumps(data), headers={'Content-Type': 'application/json'})


gradebot = notenpruefer()
gradebot.crawl_loop()
