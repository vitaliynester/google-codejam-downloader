import json
import os
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

if __name__ == '__main__':
    with open('./data.json', 'r') as f:
        data = json.load(f)

    options = uc.ChromeOptions()
    prefs = {
        "download.default_directory": "./uploads",
        "profile.default_content_settings.popups": 0,
    }
    options.add_experimental_option("prefs", prefs)
    driver = uc.Chrome(debug=True, options=options)
    driver.get('chrome://settings/')
    driver.execute_script('chrome.settingsPrivate.setDefaultZoom(0.01);')

    prefix = ''
    result = []
    for d in data:
        if 'Code Jam' in d['adventure_name'] and 'Code Jam to' not in d['adventure_name']:
            prefix = 'codejam'
        elif 'Hash Code' in d['adventure_name']:
            prefix = 'hashcode'
        elif 'Kick Start' in d['adventure_name']:
            prefix = 'kickstart'
        elif 'Code Jam to' in d['adventure_name']:
            prefix = 'codejamio'
        else:
            continue

        challenge_id = d['challenge_id']
        challenge_name = d['challenge_name']

        adventure_id = d['adventure_id']
        adventure_name = d['adventure_name']
        for user_score in d['user_scores']:
            user_name = user_score['competitor']['displayname']
            user_id = user_score['competitor']['id']

            url = f'https://codingcompetitions.withgoogle.com/{prefix}/submissions/{challenge_id}/{user_id}'
            driver.get(url)
            time.sleep(20)
            buttons = driver.find_elements(By.CLASS_NAME, "download-button")
            for button in buttons:
                try:
                    before = os.listdir('./uploads')
                    button.click()
                    time.sleep(5)
                    after = os.listdir('./uploads')
                    change = set(after) - set(before)
                    if len(change) == 1:
                        file_name = change.pop()
                        request = {
                            "file_name": file_name,
                            "user_id": user_id,
                            "user_name": user_name,
                            "challenge_id": challenge_id,
                            "challenge_name": challenge_name,
                            "adventure_id": adventure_id,
                            "adventure_name": adventure_name
                        }
                        result.append(request)
                except:
                    continue
