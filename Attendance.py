import sys
sys.stdout = sys.stderr

import time
import datetime
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pytz
import subprocess
import re

print("✅ Attendance script is running on GitHub Actions...")

MATRIC_NO = "MS2418123549"

def get_chrome_version():
    try:
        output = subprocess.check_output(
            "chromium-browser --version || chromium --version || google-chrome --version",
            shell=True
        ).decode()
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
        if match:
            version = match.group(1)
            major_version = version.split(".")[0]
            print(f"🌐 Detected Chrome version: {version}")
            return major_version
    except Exception as e:
        print(f"⚠️ Failed to detect Chrome version: {e}")
    return None

def check_internet():
    for _ in range(3):
        try:
            requests.get("https://www.google.com", timeout=5)
            return True
        except requests.ConnectionError:
            print("⚠️ No internet! Retrying in 5 seconds...")
            time.sleep(5)
    return False

def mark_attendance():
    if not check_internet():
        print("❌ No internet! Skipping.")
        return False

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    chrome_version = get_chrome_version()

    try:
        if chrome_version:
            try:
                driver_path = ChromeDriverManager(version=chrome_version).install()
            except ValueError as e:
                print(f"⚠️ Error with ChromeDriverManager: {e}")
                print("⚠️ Falling back to the latest available driver...")
                driver_path = ChromeDriverManager().install()  # Fallback to latest available driver
        else:
            print("⚠️ Chrome version could not be detected. Using latest driver.")
            driver_path = ChromeDriverManager().install()
    except Exception as e:
        print(f"⚠️ Error installing ChromeDriver: {e}")
        return False

    try:
        if chrome_version:
            try:
                driver_path = ChromeDriverManager(version=chrome_version).install()
            except ValueError as e:
                print(f"⚠️ Error with ChromeDriverManager: {e}")
                driver_path = ChromeDriverManager().install()  # Fallback to latest available driver
        else:
            print("⚠️ Chrome version could not be detected. Using latest driver.")
            driver_path = ChromeDriverManager().install()
    except Exception as e:
        print(f"⚠️ Error installing ChromeDriver: {e}")
        return False

    driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
    driver.get("https://www.phyvis2.com/hadirkmk")

    try:
        matric_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "Masukkan no matrik"))
        )
        matric_input.send_keys(MATRIC_NO)

        kod_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "Pilih Kod Subjek"))
        )
        mod_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "Pilih Mode Kelas"))
        )

        select_kod = Select(kod_dropdown)
        select_mod = Select(mod_dropdown)

        kod_options = [o.text for o in select_kod.options if o.text.strip()]
        mod_options = [o.text for o in select_mod.options if o.text.strip()]

        for kod in kod_options:
            for mod in mod_options:
                try:
                    driver.get("https://www.phyvis2.com/hadirkmk")

                    matric_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.NAME, "Masukkan no matrik"))
                    )
                    matric_input.send_keys(MATRIC_NO)

                    kod_dropdown = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.NAME, "Pilih Kod Subjek"))
                    )
                    select_kod = Select(kod_dropdown)
                    select_kod.select_by_visible_text(kod)

                    mod_dropdown = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.NAME, "Pilih Mode Kelas"))
                    )
                    select_mod = Select(mod_dropdown)
                    select_mod.select_by_visible_text(mod)

                    cari_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.NAME, "Cari"))
                    )
                    cari_button.click()
                    print(f"🔍 Tried {kod} | {mod}")

                    try:
                        hadir_button = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.NAME, "Saya Hadir"))
                        )
                        hadir_button.click()
                        print("✅ Attendance marked successfully!")
                        driver.quit()
                        return True
                    except Exception as e:
                        print(f"⚠️ Error marking attendance for {kod} | {mod}: {e}")
                        continue
                except Exception as e:
                    print(f"⚠️ Error with {kod} / {mod}: {e}")
                    continue

        print("❌ No valid combination found. Skipping.")
    except Exception as e:
        print(f"❌ Failed to load page: {e}")
    finally:
        driver.quit()

    return False

# Run every hour for 5 hours
start_time = datetime.datetime.now()
max_runtime = 5 * 60 * 60
LOCAL_TZ = pytz.timezone("Asia/Kuala_Lumpur")

while (datetime.datetime.now() - start_time).total_seconds() < max_runtime:
    now_local = datetime.datetime.now(LOCAL_TZ)
    print(f"🕒 Checking attendance at {now_local.strftime('%H:%M:%S')}")

    success = mark_attendance()

    if success:
        print("🛌 Sleeping for 1 hour...")
        time.sleep(3600)
    else:
        print("⏳ Will retry in 5 minutes...")
        time.sleep(300)

print("✅ Script completed after 5 hours.")
