import time
import os
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
aic_file_path = r"C:\Users\humay\Desktop\AIC.txt"
download_dir = r"C:\Users\humay\Desktop\aifa_pdfs"
chromedriver_path = r"C:\Users\humay\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

# --- LOAD AICs ---
with open(aic_file_path, "r") as file:
    raw_aics = [line.strip() for line in file if line.strip().isdigit()]
    aic_search_list = [f"0{aic}" for aic in raw_aics]
    aic_original_list = raw_aics

# --- SETUP DOWNLOAD FOLDER ---
os.makedirs(download_dir, exist_ok=True)

# --- CHROME OPTIONS ---
options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', {
    "download.prompt_for_download": False,
    "download.default_directory": download_dir,
    "plugins.always_open_pdf_externally": True
})
options.add_argument("--start-maximized")

# --- START WEBDRIVER ---
driver = webdriver.Chrome(service=ChromeService(executable_path=chromedriver_path), options=options)
wait = WebDriverWait(driver, 20)

# --- LOG ATC INFO ---
atc_log = []

# --- LOOP THROUGH AICs ---
for index, (search_aic, true_aic) in enumerate(zip(aic_search_list, aic_original_list), 1):
    try:
        print(f"[{index}/{len(aic_search_list)}] Processing AIC: {true_aic}")
        url = f"https://medicinali.aifa.gov.it/it/#/it/risultati?query={search_aic}&spellingCorrection=true"
        driver.get(url)
        time.sleep(4)

        # Click first result
        result = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
            "#main-content > app-content > div > div > app-results-page > div:nth-child(3) > div.row.pt-4 > div.col-12.col-xl-8"
        )))
        result.click()
        time.sleep(4)

        # Extract Codice ATC
        atc_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
            "#main-content > app-content > div > div > app-details-page > div > div.details-main > div:nth-child(2) > div.col-sm-12.col-lg-8.text-black > div > div:nth-child(2) > div:nth-child(3)"
        )))
        codice_atc = atc_elem.text.strip()

        # Get list of files before download
        files_before = set(os.listdir(download_dir))

        # Click download button
        pdf_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
            "#main-content > app-content > div > div > app-details-page > div > div.details-main > div:nth-child(2) > div.col-sm-12.col-lg-8.text-black > div > div:nth-child(1) > div:nth-child(2)"
        )))
        pdf_button.click()
        print(f"✅ Download triggered for AIC {true_aic}")
        time.sleep(6)

        # Get new file by comparing file lists
        files_after = set(os.listdir(download_dir))
        new_files = list(files_after - files_before)
        if not new_files:
            raise Exception("No new PDF detected after download.")
        downloaded_file = os.path.join(download_dir, new_files[0])

        # Rename to true AIC (e.g., 35691359.pdf)
        new_name = os.path.join(download_dir, f"{true_aic}.pdf")
        if os.path.exists(new_name):
            os.remove(new_name)
        os.rename(downloaded_file, new_name)

        # Log AIC + ATC
        atc_log.append([true_aic, codice_atc])

    except Exception as e:
        print(f"❌ Failed for AIC {true_aic}: {e}")
        atc_log.append([true_aic, "Errore o non trovato"])
        continue

# --- CLEANUP ---
driver.quit()

# --- SAVE CSV ---
csv_path = os.path.join(download_dir, "atc_codes.csv")
with open(csv_path, mode="w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["AIC", "Codice ATC"])
    writer.writerows(atc_log)

print(f"\n🎉 Done! All PDFs downloaded and saved in:\n📁 {download_dir}")
print(f"📄 Codici ATC saved to:\n{csv_path}")
