from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

DEBUG = False
SEE_BROWSER_ACTIONS = False

chrome_profile_path = r"C:\Users\gty65\AppData\Local\Google\Chrome\User Data" # ВАШ ПУТЬ ЗДЕСЬ
profile_directory = "Default" # ВАШ ПРОФИЛЬ ЗДЕСЬ : СЕЙЧАС СТОИТ Default

def log(s):
    if DEBUG:
        print(s)

def add_arguments(chrome_profile_path, profile_directory):
    options = Options()
    
    options.add_argument(f"--user-data-dir={chrome_profile_path}")
    options.add_argument(f"--profile-directory={profile_directory}")

    options.add_argument("--restore-last-session")
    
    # оптимизации
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-features=TranslateUI")
    
    options.page_load_strategy = "eager"
    options.add_argument("--blink-settings=imagesEnabled=false")
    
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_argument("--log-level=3")
    
    # Для Windows
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    return options


def create_service():
    service = Service(
        ChromeDriverManager().install(),
        service_args=['--silent'],
        popen_kw={"creation_flags": 134217728}  # ВИНДА
        # popen_kw={"startupinfo": None, "stdin": subprocess.DEVNULL} # Linux/Mac
    )

    return service



try:
    options = add_arguments(chrome_profile_path, profile_directory)

    if not SEE_BROWSER_ACTIONS:
        options.add_argument('--headless')

    log("Starting...")
    service = create_service()

    driver = webdriver.Chrome(
        service=service,
        options=options
    )

    # таймауты
    driver.set_page_load_timeout(20)
    driver.implicitly_wait(7)

    driver.switch_to.new_window('tab')
    
    log("Opening website...")
    driver.get("https://kompege.ru/lk")
    
    # загрузка основного контента
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body'))
    )
    log("Website loaded successfully")
    
    # клик по кнопке статистики
    log("Searching for statistics button...")
    stats_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//p[contains(text(), 'Моя статистика')]"))
    )
    stats_button.click()
    log("Statistics button clicked")
    
    
    # сбор данных
    log("Processing data...")
    time.sleep(1.2)  # краткая пауза для стабилизации
    
    all_text = driver.find_element(By.TAG_NAME, 'body').text.splitlines()
    score = 0

    for cur_num in range(len(all_text)):
        if cur_num > 6 and (cur_num - 7) % 4 == 3:
            try:
                points = all_text[cur_num].split()
                score += int(points[0])
            except (IndexError, ValueError) as e:
                log(f"Error parsing line {cur_num}: {str(e)}")
    
    # вывод результата
    print("\n" + "#" * 50)
    print(f"Your current score: {score} points".center(50))
    print("#" * 50)
    print("Keep going!".center(50))
    print("#" * 50 + "\n")

    # закрытие только новой вкладки
    log("Closing work tab...")
    driver.close()


except Exception as global_error:
    print(f"Global error: {str(global_error)}")

finally:
    # закрытие браузера
    if 'driver' in locals():
        log("Closing browser...")
        try:
            driver.quit()
        except Exception as quit_error:
            print(f"Browser quit error: {str(quit_error)}")

    log("Process completed")