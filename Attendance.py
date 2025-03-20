from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
import schedule
import datetime
import requests

print("✅ Attendance script is running...")

# Your matric number
MATRIC_NO = "MS2418123549"

# Path to ChromeDriver (Manually specify location)
CHROMEDRIVER_PATH = "./chromedriver"  # Windows users may need "chromedriver.exe"

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
    "Sunday": {8: ("MATHEMATICS 2 (SAINS)", "Tutorial"), 9: ("KIMIA 2 (SDS)", "Kuliah"), 10: ("FIZIK 2 (SDS)", "Amali"), 11: ("FIZIK 2", "Amali"),
               12: ("BAHASA INGGERIS 2 (SDS)", "Tutorial"), 2: ("BAHASA INGGERIS 2 (SDS)", "Tutorial")},
    "Monday": {8: ("FIZIK 2 (SDS)", "Tutorial"), 9: ("KIMIA 2", "Kuliah"), 10: ("MATHEMATICS 2 (SAINS)", "Tutorial"),
               12: ("MATHEMATICS 2 (SAINS)", "Kuliah"), 1: ("KIMIA 2 (SDS)", "Kuliah"), 2: ("COMPUTER SCIENCE 2", "Kuliah")},
    "Tuesday": {8: ("KIMIA 2 (SDS)", "Amali"), 9: ("KIMIA 2 (SDS)", "Amali"), 10: ("FIZIK 2 (SDS)", "Tutorial"),
                12: ("BAHASA INGGERIS 2 (SDS)", "Tutorial"), 2: ("COMPUTER SCIENCE 2", "Amali"), 3: ("COMPUTER SCIENCE 2", "Amali")},
    "Wednesday": {8: ("FIZIK 2 (SDS)", "Tutorial"), 9: ("FIZIK 2 (SDS)", "Kuliah"), 10: ("KIMIA 2 (SDS)", "Kuliah"),
                  11: ("MATHEMATICS 2 (SAINS)", "Tutorial"), 12: ("BAHASA INGGERIS 2 (SDS)", "Tutorial")},
    "Thursday": {8: ("MATHEMATICS 2 (SAINS)", "Kuliah"), 9: ("COMPUTER SCIENCE 2", "Tutorial"), 10: ("KIMIA 2 (SDS)", "Tutorial"),
                 12: ("FIZIK 2 (SDS)", "Tutorial")},
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

        # Start Selenium WebDriver
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service)
        driver.get("https://www.phyvis2.com/hadirkmk")

        try:
            # Enter Matric Number
            matric_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "Masukkan no matrik"))
            )
            matric_input.send_keys(MATRIC_NO)

            # Enter "Kod Subjek"
            kod_subjek_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "Pilih Kod Subjek"))
            )
            kod_subjek_input.send_keys(kod_subjek)

            # Enter "Mod Kelas"
            mod_kelas_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "pilih mode kelas"))
            )
            mod_kelas_input.send_keys(mod_kelas)

            # Click "Hadir" if available
            try:
                Saya_Hadir_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.NAME, "saya hadir"))
                )
                Saya_Hadir_button.click()
                print("✅ Attendance marked successfully!")
            except:
                print("⚠️ No 'Hadir' button found. Skipping this session.")

        except Exception as e:
            print(f"❌ Failed to mark attendance: {e}")
        finally:
            time.sleep(3)
            driver.quit()
    else:
        print(f"⏳ No class at {current_hour}:00, skipping attendance.")

# Run the scheduler
while True:
    now = datetime.datetime.now().strftime("%H:%M")
    for hour in range(8, 18):
        if now == f"{hour:02d}:00":
            mark_attendance()
    schedule.run_pending()
    print(f"⏳ Checking attendance at {datetime.datetime.now().strftime('%H:%M:%S')}")
    time.sleep(60)  # Check every 60 seconds
#cd C:\Users\Kim\PycharmProjects\pythonProject
#to run in control panel