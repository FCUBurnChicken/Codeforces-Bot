import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

month = {
    "01":"Jan",
    "02":"Feb",
    "03":"Mar",
    "04":"Apr",
    "05":"May",
    "06":"Jun",
    "07":"Jul",
    "08":"Aug",
    "09":"Sep",
    "10":"Oct",
    "11":"Nov",
    "12":"Dec"
}

class build_round():
    def __init__(self, _round: dict) -> None:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self._round = _round
        self.contestId = None

    def move(self, url): # 網址移動
        self.browser.get(url)
        time.sleep(2)
    
    def login(self): # 登入 codeforces
        self.browser.get("https://codeforces.com")
        element = self.browser.find_element(By.XPATH, "//a[@href='/enter?back=%2F']")
        element.click()
        time.sleep(2)
        element = self.browser.find_element(By.XPATH, "//input[@name='handleOrEmail']")
        element.send_keys(self._round["email"])
        element = self.browser.find_element(By.XPATH, "//input[@name='password']")
        element.send_keys(self._round["password"])
        element = self.browser.find_element(By.XPATH, "//input[@value='Login']")
        element.click()
        time.sleep(2)
        
    def add_to_group(self): # 將 contest 加入 codeforces group 中
        self.move("https://codeforces.com/group/GFWL4cNHNj/contests/add")
        element = self.browser.find_element(By.XPATH, "//input[@name='contestIdAndName']")
        element.send_keys(self.contestId)
        element = self.browser.find_element(By.XPATH, "//input[@value='Add']")
        element.click()
        time.sleep(1)
        element = self.browser.find_element(By.XPATH, "//input[@value='Yes']")
        element.click()

    def write_round_info(self): # 寫入基本資料
        element = self.browser.find_element(By.XPATH, "//input[@name='contestName']")
        element.send_keys(self._round["name"])
        element = self.browser.find_element(By.XPATH, "//input[@name='contestDuration']")
        element.send_keys("180")

    def setupTime(self): # 設定舉辦時間
        self.contestId = self.browser.current_url.split("/")[-1]
        self.move(f"https://codeforces.com/gym/edit/{self.contestId}")
        element = self.browser.find_element(By.XPATH, "//input[@name='startDay']")
        day = self._round["startDay"].split("/")
        element.send_keys(f"{month[day[1]]}/{day[2]}/{day[0]}")
        element = self.browser.find_element(By.XPATH, "//input[@name='startTime']")
        element.send_keys(self._round["startTime"])
        element = self.browser.find_element(By.XPATH, "//input[@value='Save changes']")
        element.click()
        time.sleep(2)

    def add_problems(self, problem): # 加入題目
        element = self.browser.find_element(By.XPATH, "//input[@name='problemQuery']")
        element.send_keys(f"{problem[0]}-{problem[1]}")
        element = self.browser.find_element(By.XPATH, "//img[@alt='Add problem']")
        element.click()
        time.sleep(5)

    def create(self): # 創建 contest
        element = self.browser.find_element(By.XPATH, "//input[@value='Create Mashup Contest']")
        element.click()
        time.sleep(2)
    
    def close(self):
        self.browser.close()
