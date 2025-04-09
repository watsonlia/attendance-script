import sys  # Redirect print statements to GitHub Actions log
sys.stdout = sys.stderr

import time
import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import pytz

print("✅ Attendance script is running on GitHub Actions...")

# Your matric number
MATRIC_NO = "MS2418123549"

# Function to check internet connection
def check_internet():
    for _ in range(3):  # Retry 3 times
        try:
            requests.get("https://www.google.com", timeout=5)
            return True
        except requests.ConnectionError:
            print("⚠️ No internet! Retrying in 5 seconds...")
            time.sleep(5)
    return False

# Function to mark attendance by trying all dropdown combinations
def mark_attendance():
    if not check_internet():
        print("❌ No internet! Skipping attendance marking.")
        return

    print("📌 Trying to mark attendance...")

    # Set Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")

    # Initialize WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.phyvis2.com/hadirkmk")

            try:
            # Enter Matric Number
            matric_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "Masukkan no matrik"))
            )
            matric_input.send_keys(MATRIC_NO)

            # Loop through dropdown options
            kod_subjek_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "Pilih Kod Subjek"))
            )
            select_kod = Select(kod_subjek_dropdown)
            kod_options = select_kod.options

            mod_kelas_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "Pilih Mode Kelas"))
            )
            select_mod = Select(mod_kelas_dropdown)
            mod_options = select_mod.options

            for kod in kod_options:
                for mod in mod_options:
                    try:
                        select_kod.select_by_visible_text(kod.text)
                        select_mod.select_by_visible_text(mod.text)

                        # Click "Cari"
                        cari_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.NAME, "Cari"))
                        )
                        cari_button.click()
                        time.sleep(1)

                        # Try to find "Saya Hadir" button
                        hadir_button = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.NAME, "Saya Hadir"))
                        )
                        hadir_button.click()
                        print(f"✅ Attendance marked for {kod.text} ({mod.text})!")
                        driver.quit()
                        return  # Exit after success

                    except:
                        continue  # Try next combination

            print("⚠️ No valid attendance combo found, skipping this hour.")
            driver.quit()

        except Exception as e:
            print(f"❌ Failed to mark attendance: {e}")
            driver.quit()

#cd C:\Users\Kim\PycharmProjects\pythonProject
#to run in control panel
