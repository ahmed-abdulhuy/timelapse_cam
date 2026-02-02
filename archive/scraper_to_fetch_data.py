import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



# Path to your ChromeDriver
driverPathLinux = "./chromedriver-linux64/chromedriver-linux64/chromedriver"
driverPathWindows = "./chromedriver-win64/chromedriver"

driver = webdriver.Chrome()
driver.get("http://192.168.8.100")

passwordElem = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'PasswordInput')]"))
)
username = driver.find_element(By.XPATH, "//*[@placeholder='Username']")

username.send_keys("admin")
passwordElem.send_keys('Aa@203040')

driver.find_element('css selector', 'button[type="submit"]').click()

backupDiv = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'Card_4')]"))
)
backupDiv.click()

time.sleep(1)

backupDir = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/div[2]/div/div/div/div/div[2]/div[2]/div[1]/div/div/div[3]/input'))
)

backupDir.send_keys('D:\\FFI_Work\\Timelapse Records\\unorganized_cam_raw_date')

time.sleep(0.1)

typeSelection = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/div[2]/div/div/div/div/div[2]/div[4]/div/div/div[3]'))
)
print(typeSelection)
typeSelection.click()

time.sleep(0.1)

PictureOption = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div/div/div/div[2]/div/div/div/div[8]'))
)
print(PictureOption)
PictureOption.click()



PeriodElem = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/div[2]/div/div/div/div/div[2]/div[5]/div/div[3]/div'))
)
print(PeriodElem)
PeriodElem.click()


time.sleep(0.1)


customElem = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.XPATH, '//*[@title="Custom"]'))
)
print(customElem.get_attribute('title'))
customElem.click()

startDateInput = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.XPATH, '//*[@placeholder="Start Time"]'))
)
print(startDateInput.get_attribute("value"))
# startDateInput.clear()
startDateInput.send_keys('2024-09-10 00:00:00')
print(startDateInput.get_attribute("value"))


endDateInput = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.XPATH, '//*[@placeholder="End Time"]'))
)
# endDateInput.clear()
endDateInput.send_keys('2024-09-10 05:00:00')
print(endDateInput.get_attribute("value"))

time.sleep(0.1)

PeriodAproveElem = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.XPATH, '//span[text()="OK"]'))
)
PeriodAproveElem.click()

time.sleep(0.1)

PeriodAproveElem = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.XPATH, '//div[text()="Search"]'))
)
PeriodAproveElem.click()




time.sleep(5)

PeriodAproveElem = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/div[2]/div/div/div/div/div[3]/div[1]/div/div/div/div/div/div/div[1]/table/thead/tr/th[1]'))
)
PeriodAproveElem.click()


time.sleep(20)

