from pprint import pprint
from vk_api import VKAPIClient
from configurations.configuration import token, user_id
import time
import datetime


def calculate_age(resp):
    bdate = resp[0]['bdate']
    day, month, year = str(bdate).split('.')
    bdate = datetime.date(int(year), int(month), int(day))
    delta = (datetime.datetime.now().date() - bdate).days // 365
    return delta


def converted_sex(resp):
    sex_id = resp[0]['sex']
    converted_sex_dict = {1: 2, 2: 1, 0: 0}
    sex_id = converted_sex_dict[sex_id]
    return sex_id


if __name__ == '__main__':
    vk = VKAPIClient(token, user_id)

    response = vk.user_info()
    age = calculate_age(response)
    city_id = response[0]['city']['id']
    sex_id = converted_sex(response)

    user_info_list = []
    for user in vk.user_search(age, city_id, sex_id)['response']['items']:
        owner_id = user['id']
        user_info = {'full_name': f"{user['first_name']} {user['last_name']}",
                     'profile_link': f"https://vk.com/id{user['id']}",
                     'photo_url': vk.get_list_foto_max_quality(owner_id)}
        user_info_list.append(user_info)
        time.sleep(0.25)

    pprint(user_info_list, width=120)
