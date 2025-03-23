import sys  # Redirect print statements to GitHub Actions log
sys.stdout = sys.stderr

import time
import schedule
import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
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

# Timetable dictionary (Day -> Hour -> (Kod Subjek, Mod Kelas))
TIMETABLE = {
    "Sunday": {
        8: ("SM025 : MATHEMATICS 2 (SAINS)", "Tutorial"),
        9: ("KIMIA 2 (SDS)", "Kuliah"),
        10: ("FIZIK 2 (SDS)", "Amali"),
        11: ("FIZIK 2", "Amali"),
        12: ("BAHASA INGGERIS 2 (SDS)", "Tutorial"),
        14: ("BAHASA INGGERIS 2 (SDS)", "Tutorial"),
    },
    "Monday": {
        8: ("FIZIK 2 (SDS)", "Tutorial"),
        9: ("KIMIA 2", "Kuliah"),
        10: ("SM025 : MATHEMATICS 2 (SAINS)", "Tutorial"),
        12: ("SM025 : MATHEMATICS 2 (SAINS)", "Kuliah"),
        13: ("KIMIA 2 (SDS)", "Kuliah"),
        14: ("COMPUTER SCIENCE 2", "Kuliah"),
    },
    "Tuesday": {
        8: ("KIMIA 2 (SDS)", "Amali"),
        9: ("KIMIA 2 (SDS)", "Amali"),
        10: ("FIZIK 2 (SDS)", "Tutorial"),
        12: ("BAHASA INGGERIS 2 (SDS)", "Tutorial"),
        14: ("COMPUTER SCIENCE 2", "Amali"),
        15: ("COMPUTER SCIENCE 2", "Amali"),
    },
    "Wednesday": {
        8: ("FIZIK 2 (SDS)", "Tutorial"),
        9: ("FIZIK 2 (SDS)", "Kuliah"),
        10: ("KIMIA 2 (SDS)", "Kuliah"),
        11: ("SM025 : MATHEMATICS 2 (SAINS)", "Tutorial"),
        12: ("BAHASA INGGERIS 2 (SDS)", "Tutorial"),
    },
    "Thursday": {
        8: ("SM025 : MATHEMATICS 2 (SAINS)", "Kuliah"),
        9: ("COMPUTER SCIENCE 2", "Tutorial"),
        10: ("KIMIA 2 (SDS)", "Tutorial"),
        12: ("FIZIK 2 (SDS)", "Tutorial"),
    },
}

# Function to mark attendance
def mark_attendance():
    if not check_internet():
        print("❌ No internet! Skipping attendance marking.")
        return

    today = datetime.datetime.today().strftime('%A')  # Get current day
    current_hour = datetime.datetime.now().hour  # Get current hour

    if today in TIMETABLE and current_hour in TIMETABLE[today]:
        kod_subjek, mod_kelas = TIMETABLE[today][current_hour]
        print(f"📌 Marking attendance for {kod_subjek} ({mod_kelas}) at {current_hour}:00")

        # Set Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run without GUI
        chrome_options.add_argument("--no-sandbox")  # Required for cloud environments
        chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent crashes in limited resources
        chrome_options.add_argument("--remote-debugging-port=9222")  # Debugging

        # Initialize WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.phyvis2.com/hadirkmk")

        try:
            # Enter Matric Number
            matric_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "Masukkan no matrik"))
            )
            matric_input.send_keys(MATRIC_NO)

            # Select "Kod Subjek" from dropdown
            kod_subjek_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "Pilih Kod Subjek"))
            )
            select_kod_subjek = Select(kod_subjek_dropdown)
            select_kod_subjek.select_by_visible_text(kod_subjek)

            # Select "Mod Kelas" from dropdown
            mod_kelas_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "Pilih Mode Kelas"))
            )
            select_mod_kelas = Select(mod_kelas_dropdown)
            select_mod_kelas.select_by_visible_text(mod_kelas)

            # Click "Cari" button
            cari_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "Cari"))
            )
            cari_button.click()
            print("✅ 'Cari' button clicked.")

            # Click "Saya Hadir" button
            Saya_Hadir_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.NAME, "Saya Hadir"))
            )
            Saya_Hadir_button.click()
            print("✅ Attendance marked successfully!")

        except Exception as e:
            print(f"❌ Failed to mark attendance: {e}")
        finally:
            time.sleep(3)
            driver.quit()
    else:
        print(f"⏳ No class at {current_hour}:00, skipping attendance.")

# Run the scheduler (For max 5 hours)
start_time = datetime.datetime.now()
max_runtime = 5 * 60 * 60  # 5 hours in seconds

# Set your local time zone (e.g., "Asia/Kuala_Lumpur")
LOCAL_TZ = pytz.timezone("Asia/Kuala_Lumpur")

while (datetime.datetime.now() - start_time).total_seconds() < max_runtime:
    # Get the current local time
    now_local = datetime.datetime.now(LOCAL_TZ)
    now = now_local.strftime("%H:%M")
    current_hour = now_local.hour

    # Check attendance for the current hour
    for hour in range(8, 18):
        if now == f"{hour:02d}:00":
            mark_attendance()

    schedule.run_pending()
    print(f"⏳ Checking attendance at {now_local.strftime('%H:%M:%S')}")
    time.sleep(60)  # Check every 60 seconds

print("✅ Attendance script finished running after 5 hours.")


#cd C:\Users\Kim\PycharmProjects\pythonProject
#to run in control panel
