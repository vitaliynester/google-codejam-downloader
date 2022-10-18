import json
import math
import os
import time
from collections import Counter

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


n = 10
k = 0


def split_list(data_list):
    per_list = math.floor(len(data_list) / n)
    chunks = [data_list[x:x + per_list] for x in range(0, len(data_list), per_list)]
    return chunks


if __name__ == '__main__':
    with open('./data.json', 'r') as f:
        data = json.load(f)

    # Получение всех пользователей (ID)
    user_ids = []
    for d in data:
        for challenge in d['challenges']:
            if challenge['user_scores'] is None:
                continue
            for user_score in challenge['user_scores']:
                user_ids.append(user_score['competitor']['id'])
    print(f'Всего участников за все время: {len(user_ids)} шт.')
    print(f'Всего уникальных участников за все время: {len(list(set(user_ids)))} шт.')

    c = Counter(user_ids)
    target_ids = [key for key in c.keys() if c[key] > 4]
    print(f'Количество участников в пяти и более соревнованиях: {len(target_ids)} шт.')

    filtered_result = []
    for it1, d in enumerate(data):
        filtered_result.append({
            "adventure_name": d['adventure_name'],
            "adventure_id": d['adventure_id'],
            "challenges": []
        })
        print(f"data: {it1 + 1}/{len(data)}")
        for it2, challenge in enumerate(d['challenges']):
            filtered_result[-1]['challenges'].append(
                {
                    "challenge": {
                        "id": challenge['challenge']['id'],
                        "title": challenge['challenge']['title'],
                    },
                    "user_scores": []
                }
            )
            print(f'challenges: {it2 + 1}/{len(d["challenges"])}')
            if challenge['user_scores'] is None:
                continue
            for it3, user_score in enumerate(challenge['user_scores']):
                if user_score['competitor']['id'] in target_ids:
                    filtered_result[-1]['challenges'][-1]['user_scores'].append(
                        {
                            "competitor": {
                                "displayname": user_score['competitor']['displayname'],
                                "id": user_score['competitor']['id']
                            }
                        }
                    )
    with open('filtered_data.json', 'w', encoding='utf-8') as file:
        json.dump(filtered_result, file, indent=4, ensure_ascii=False)

    data = filtered_result
    options = uc.ChromeOptions()
    prefs = {
        "download.default_directory": "/Users/vitaly_posadnev/Develop/PythonProjects/google-codejam-webview/uploads",
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

            user_scores = split_list(challenge['user_scores'])
            for it3, user_score in enumerate(user_scores[k]):
                print(f"Парсинг результатов {it3 + 1}/{len(user_scores[k])}: {(it3 + 1) / len(user_scores[k])}%")
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
