from pprint import pprint
from class_vk_api import VKAPIClient
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


def get_info_current_user(vkc):
    response = vkc.user_info()
    age = calculate_age(response)
    city_id = response[0]['city']['id']
    sex_id = converted_sex(response)
    return age, city_id, sex_id


def find_user(vkc,age_, city_id_, sex_id_):
    user_info_list = []
    for user in vkc.user_search(age_, city_id_, sex_id_)['response']['items']:
        owner_id = user['id']
        user_info = {'full_name': f"{user['first_name']} {user['last_name']}",
                     'profile_link': f"https://vk.com/id{user['id']}",
                     'photo_url': vkc.get_list_foto_max_quality(owner_id)}
        user_info_list.append(user_info)
        time.sleep(0.25)
    return user_info_list


if __name__ == '__main__':
    vk = VKAPIClient(token, user_id)
    found_users = find_user(vk, *get_info_current_user(vk))
    pprint(found_users, width=120)
    print(len(found_users))
