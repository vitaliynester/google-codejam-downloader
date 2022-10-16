import json
import os
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

if __name__ == '__main__':
    with open('./data.json', 'r') as f:
        data = json.load(f)

    options = uc.ChromeOptions()
    prefs = {
        "download.default_directory": "/home/vitaly/PycharmProjects/google-codejam-downloader/uploads/",
        "profile.default_content_settings.popups": 0,
    }
    options.add_experimental_option("prefs", prefs)
    driver = uc.Chrome(debug=True, options=options)
    driver.get('chrome://settings/')
    driver.execute_script('chrome.settingsPrivate.setDefaultZoom(0.25);')

    prefix = ''
    result = []
    flag = False
    for it1, d in enumerate(data):
        print(f'Парсинг {it1 + 1}/{len(data)} соревнования: {(it1 + 1) / len(data)}%')
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

        if str(d['adventure_name']).count('2018') != 0:
            flag = True

        if not flag:
            continue

        adventure_id = d['adventure_id']
        adventure_name = d['adventure_name']

        for it2, challenge in enumerate(d['challenges']):
            challenge_id = challenge['challenge']['id']
            challenge_name = challenge['challenge']['title']
            print(f"Парсинг результатов этапа {it2 + 1}/{len(d['challenges'])}: {(it2 + 1) / len(d['challenges'])}%")

            for it3, user_score in enumerate(challenge['user_scores']):
                print(
                    f"Парсинг результатов {it3 + 1}/{len(challenge['user_scores'])}: {(it3 + 1) / len(challenge['user_scores'])}%")
                user_id = user_score['competitor']['id']
                user_name = user_score['competitor']['displayname']

                url = f'https://codingcompetitions.withgoogle.com/{prefix}/submissions/{challenge_id}/{user_id}'
                driver.get(url)
                try:
                    wait = WebDriverWait(driver, 20)
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ranking-table__row--header")))
                except Exception as e:
                    print("Не дождались загрузки...")
                    continue
                buttons = driver.find_elements(By.CLASS_NAME, "download-button")
                if len(buttons) == 0:
                    break
                for button in buttons:
                    try:
                        before = os.listdir('/home/vitaly/Downloads')
                        button.click()
                        time.sleep(4)
                        after = os.listdir('/home/vitaly/Downloads')
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
                            print(request)
                    except Exception as e:
                        print("Ошибка!!!")
    with open('result.json', 'w', encoding='utf-8') as file:
        json.dump(result, file, indent=4, ensure_ascii=False)
