from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pandas as pd
import os
import shutil
import time


driver = webdriver.Chrome()

url = 'https://www.lumiproxy.com/free-proxy/'
driver.get(url)

download_folder = "C:\\Users\\frien\\Downloads"

try:

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#__layout'))
    )

    csv_radio_button = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[value="csv"]'))
    )
    csv_label = csv_radio_button.find_element(By.XPATH, './ancestor::label')
    print("CSV radio button found, scrolling into view.")
    driver.execute_script("arguments[0].scrollIntoView(true);", csv_label)

    print("Clicking the CSV radio button.")
    driver.execute_script("arguments[0].click();", csv_label)

    get_proxies_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#__layout > div > div.page.nuxt > div.content > div.groups > div.item-export > div.box > div.get-p'))
    )
    print("'Get Proxies' button found, clicking it.")
    driver.execute_script("arguments[0].scrollIntoView(true);", get_proxies_button)
    driver.execute_script("arguments[0].click();", get_proxies_button)

    action_chains = ActionChains(driver)
    action_chains.context_click(get_proxies_button).perform()

    action_chains.send_keys(Keys.ARROW_DOWN).perform()
    action_chains.send_keys(Keys.ARROW_DOWN).perform()
    action_chains.send_keys(Keys.RETURN).perform()

    desired_folder = os.path.join(os.getcwd(), "lumiproxy")

    params = {'behavior': 'allow', 'downloadPath': desired_folder}
    driver.execute_cdp_cmd('Page.setDownloadBehavior', params)

    get_proxies_button.click()

    print("Waiting for the CSV file to download...")
    time.sleep(10)

    params = {'behavior': 'allow', 'downloadPath': download_folder}
    driver.execute_cdp_cmd('Page.setDownloadBehavior', params)

    csv_file = None
    for file in os.listdir(desired_folder):
        if file.endswith('.csv'):
            csv_file = file
            break

    if csv_file:
        csv_file_path = os.path.join(desired_folder, csv_file)
        print(f"CSV file '{csv_file_path}' found.")

        with open("last_downloaded_csv.txt", "w") as file:
            file.write(csv_file)

        df = pd.read_csv(csv_file_path)

        print("Column names in the CSV file:")
        print(df.columns)

        if 'ip' in df.columns and 'port' in df.columns:
            protocol_mapping = {
                1: 'http',
                2: 'https',
                4: 'socks4',
                8: 'socks5'
            }

            df['Proxy'] = df.apply(
                lambda row: f"{protocol_mapping.get(row['protocol'], 'Unknown')}://{row['ip']}:{row['port']}", axis=1)

            formatted_csv_path = os.path.join(desired_folder, 'formatted_proxies.csv')
            df.to_csv(formatted_csv_path, columns=['Proxy'], index=False)

            print(f"Formatted proxies saved to {formatted_csv_path}")

        else:
            print("Required columns not found in the CSV file. Unable to format proxies.")
    else:
        print("No CSV file found in the specified folder.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
