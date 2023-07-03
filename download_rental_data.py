from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import datetime

rental_dir = os.getcwd() + '\\rental_csv'
download_dir = os.getcwd() + '\\download_csv'

PATH = os.getcwd() + 'chromedriver.exe'

def extract_date(filename):
    date_str = filename.split("_")[1].split(".")[0]
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

def scroll_down(driver):
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight/4);')

def download_rental(base_url,download_dir,date):
    # Initialising the chrome webdriver by adding certain options 
    options = Options()
    options.add_experimental_option('prefs',  {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True,
    "pdfjs.disabled": True
    }
    )
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications") # to open the window fully
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(PATH, service=service, options=options) # Initialising the driver by giving out the PATH to chromedriver.exe

    # Getting Todays Date and Month to use while filling out the form
    day = date.strftime('%d')
    next_day = int(day) + 1
    month_int = int(date.strftime('%m'))
    month = str(month_int - 1)
    year = date.strftime('%Y')

    driver.get(base_url)
    driver.implicitly_wait(1.5) 

    # Switching the navbar to Rents tab if necessary
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.LINK_TEXT, "Rents")))
    rental_element = driver.find_element(By.LINK_TEXT, 'Rents')
    driver.implicitly_wait(1)
    rental_element.click()
    time.sleep(4)


    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "rent_pFromDate")))
    # Finding the from date form element to enter the date
    from_date_picker = driver.find_element(By.ID, 'rent_pFromDate')
    from_date_picker.click()
    driver.implicitly_wait(1)
    from_date_picker.clear()
    from_date_picker.send_keys(f'{day}/{month_int}/{year}')
    driver.implicitly_wait(1)

    # Selecting the current month in the datepicker UI
    select_month_from_date = Select(driver.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]/div/div/select[1]'))
    select_month_from_date.select_by_value(month)


    # Finding the to date form element to enter the date
    to_date_picker = driver.find_element(By.ID, 'rent_pToDate')
    to_date_picker.click()
    to_date_picker.clear()
    to_date_picker.send_keys(f'{next_day}/{month_int}/{year}')
    select_month_to_date = Select(driver.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]/div/div/select[1]'))
    select_month_to_date.select_by_value(month)
    
    scroll_down(driver)
    search_csv = driver.find_element(By.XPATH, '//*[@id="rentFilter"]/div/div[10]/div/button[1]')
    time.sleep(2)
    search_csv.click()
    time.sleep(10)
    scroll_down(driver)
    time.sleep(2)
    WebDriverWait(driver,100).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.cs-loader-inner')))
    WebDriverWait(driver,100).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="rent"]/div[2]/div/div[1]/div/div/button')))
    #WebDriverWait(driver,100).until(EC.presence_of_element_located((By.XPATH, '//*[@id="rentFilter"]/div/div[10]/div/button[1]')))
    download_csv = driver.find_element(By.XPATH, '//*[@id="rent"]/div[2]/div/div[1]/div/div/button')
    #driver.execute_script("arguments[0].scrollIntoView();", download_csv)
    time.sleep(3)
    download_csv.click()
    WebDriverWait(driver,150).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.cs-loader-inner')))
    time.sleep(10)
    driver.quit()
    for file in os.listdir('download_csv'):
        if file.endswith('csv'):
            os.rename(os.path.join(download_dir,file),os.path.join(rental_dir,f'data_{date}.csv'))

base_url = 'https://dubailand.gov.ae/en/open-data/real-estate-data/#/'
 # Replace with the actual path to your folder
files = os.listdir(rental_dir)
dates = [extract_date(filename) for filename in files if "data_" in filename]

start_date = datetime.date(2023, 7, 1)

all_dates = set(   # Using this we can search upto 2 weeks from todays date
    start_date + datetime.timedelta(days=x)
    for x in range((datetime.date.today() - start_date).days + 1)
)

missing_dates = sorted(all_dates - set(dates))
print(len(missing_dates))
for date in missing_dates:
        print(date.strftime("%Y-%m-%d"))
        download_rental(base_url,download_dir,date)