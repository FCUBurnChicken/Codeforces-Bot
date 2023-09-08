from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    
    def login(self): # 登入 codeforces
        self.browser.get("https://codeforces.com")
        element = WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.XPATH, "//a[@href='/enter?back=%2F']")))
        element.click()
        element = WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.XPATH, "//input[@name='handleOrEmail']")))
        element.send_keys(self._round["email"])
        element = self.browser.find_element(By.XPATH, "//input[@name='password']")
        element.send_keys(self._round["password"])
        element = self.browser.find_element(By.XPATH, "//input[@value='Login']")
        element.click()
        WebDriverWait(self.browser, 20).until(EC.url_to_be(f"https://codeforces.com/"))
        element = WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='lang-chooser']/div[2]/a[2]")))
        return element.get_attribute('innerText') == 'Logout'

    def write_round_info(self): # 寫入基本資料
        self.move("https://codeforces.com/mashup/new/")
        element = WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.XPATH, "//input[@name='contestName']")))
        element.send_keys(self._round["name"])
        element = self.browser.find_element(By.XPATH, "//input[@name='contestDuration']")
        element.send_keys(self._round["time"])
    
    def add_problems(self, problem): # 加入題目
        query = WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.XPATH, "//input[@name='problemQuery']")))
        query.send_keys(f"{problem[0]}-{problem[1]}")
        element = self.browser.find_element(By.XPATH, "//img[@alt='Add problem']")
        element.click()
        WebDriverWait(self.browser, 30).until(lambda browser: query.get_attribute('value') == '')
    
    def create(self): # 創建 contest
        element = self.browser.find_element(By.XPATH, "//input[@value='Create Mashup Contest']")
        element.click()
        WebDriverWait(self.browser, 20).until(EC.url_contains("gym"))

    def setupTime(self): # 設定舉辦時間
        self.contestId = self.browser.current_url.split("/")[-1]
        self.move(f"https://codeforces.com/gym/edit/{self.contestId}")
        element = WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.XPATH, "//input[@name='startDay']")))
        day = self._round["startDay"].split("/")
        element.send_keys(f"{month[day[1]]}/{day[2]}/{day[0]}")
        element = self.browser.find_element(By.XPATH, "//input[@name='startTime']")
        element.send_keys(self._round["startTime"])
        element = self.browser.find_element(By.XPATH, "//input[@value='Save changes']")
        element.click()
    
    def add_to_group(self): # 將 contest 加入 codeforces group 中
        WebDriverWait(self.browser, 20).until(EC.url_to_be(f"https://codeforces.com/gym/{self.contestId}"))
        self.move("https://codeforces.com/group/GFWL4cNHNj/contests/add")
        element = WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.XPATH, "//input[@name='contestIdAndName']")))
        element.send_keys(self.contestId)
        element = self.browser.find_element(By.XPATH, "//input[@value='Add']")
        element.click()
        element = WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.XPATH, "//input[@value='Yes']")))
        element.click()
        WebDriverWait(self.browser, 20).until(EC.url_contains(f"https://codeforces.com/group"))
    
    def close(self):
        self.browser.close()
