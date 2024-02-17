import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.upload import VkUpload
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from configurations.configuration import group_token, token, user_id
from random import randrange
from class_vk_api import VKAPIClient
from data_base.main_db import add_user, add_favorite, add_photo, open_favorite_list
import requests
from io import BytesIO
import time
import datetime


vk_session = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()
upload = VkUpload(vk)

keyboard = VkKeyboard()
keyboard.add_button("Начать поиск", color=VkKeyboardColor.POSITIVE)
keyboard.add_line()
keyboard.add_button("Открыть список избранных", color=VkKeyboardColor.PRIMARY)
keyboard2 = VkKeyboard()
keyboard2.add_button("Предыдущий пользователь", color=VkKeyboardColor.SECONDARY)
keyboard2.add_button("Следующий пользователь", color=VkKeyboardColor.SECONDARY)
keyboard2.add_line()
keyboard2.add_button("Добавить пользователя в список избранных", color=VkKeyboardColor.POSITIVE)
keyboard2.add_line()
keyboard2.add_button("Открыть список избранных", color=VkKeyboardColor.PRIMARY)


def upload_photo(upload, url):
    img = requests.get(url).content
    f = BytesIO(img)
    try:
        response = upload.photo_messages(f)[0]
    except Exception:
        pass

    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    return owner_id, photo_id, access_key


def send_photo(vk_, peer_id, owner_id, photo_id, access_key):
    attachment = f'photo{owner_id}_{photo_id}_{access_key}'
    vk_.messages.send(
        random_id=get_random_id(),
        peer_id=peer_id,
        attachment=attachment
    )


def calculate_age(resp):
    try:
        bdate = resp[0]['bdate']
        day, month, year = str(bdate).split('.')
        bdate = datetime.date(int(year), int(month), int(day))
        age_ = (datetime.datetime.now().date() - bdate).days // 365
    except KeyError:
        print(f'Дата рождения частично или полностью скрыта настройками приватности!')
        write_msg3(user_id, f"Дата рождения частично или полностью скрыта настройками приватности!\n"
                            f"Для поиска введите свой возраст (цифрами).")
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    try:
                        age_ = int(event.text)
                    except ValueError:
                        write_msg3(user_id, f"Вы ввели возраст не в числовом виде!\n"
                                            f"Пожалуйста введите возраст цифрами.")
                    else:
                        break
    return age_


def converted_sex(resp):
    sex_id = resp[0]['sex']
    converted_sex_dict = {1: 2, 2: 1, 0: 0}
    sex_id = converted_sex_dict[sex_id]
    return sex_id


def get_info_current_user(vkc, user_id):
    response = vkc.user_info()
    age_ = calculate_age(response)
    try:
        city_id_ = response[0]['city']['id']
    except KeyError:
        print(f'Город скрыт настройками приватности')
        write_msg3(user_id, f"Город скрыт настройками приватности!\n"
                            f"Поэтому введите город, в котором необходимо произвести поиск.")
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    city_name = event.text
                    try:
                        city_id_ = vkc.get_city_id(city_name)['items'][0]['id']
                    except IndexError:
                        write_msg3(user_id, f"Вы ввели несуществующий город!\n"
                                            f"Пожалуйста введите город корректно.")
                    else:
                        break
    sex_id = converted_sex(response)
    return response[0]['id'], response[0]['first_name'], response[0]['last_name'], age_, city_id_, sex_id


def find_user(vkc, age_, city_id_, sex_id_):
    user_info_list = []
    for user in vkc.user_search(age_, city_id_, sex_id_)['response']['items']:
        user_info = {'full_name': f"{user['first_name']} {user['last_name']}",
                     'id': user['id'],
                     'profile_link': f"https://vk.com/id{user['id']}",
                     'photo_url': vkc.get_list_foto_max_quality(user['id'])}
        user_info_list.append(user_info)
        time.sleep(0.25)
    return user_info_list


def write_msg(user_id, message):
    vk_session.method('messages.send', {'user_id': user_id, 'message': message,
                                        'random_id': randrange(10 ** 7), "keyboard": keyboard.get_keyboard()})


def write_msg2(user_id, message):
    vk_session.method('messages.send', {'user_id': user_id, 'message': message,
                                        'random_id': randrange(10 ** 7), "keyboard": keyboard2.get_keyboard()})


def write_msg3(user_id, message):
    vk_session.method('messages.send', {'user_id': user_id, 'message': message,
                                        'random_id': randrange(10 ** 7)})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if request.lower() == 'старт':
                write_msg(event.user_id,
                          f"Для запуска поиска людей для знакомства нажмите соответствующую кнопку")

            elif request == 'Начать поиск':
                write_msg(event.user_id, "Начинаю поиск людей, подходящих для знакомства...")
                vkclient = VKAPIClient(token, event.user_id)
                userid, first_name, last_name, age, city_id, gender = get_info_current_user(vkclient, event.user_id)
                try:
                    add_user(userid, first_name, last_name, age, city_id, gender, f"https://vk.com/id{userid}")
                except Exception:
                    pass
                found_users = find_user(vkclient, age, city_id, gender)
                i = 0
                write_msg2(event.user_id, f"{found_users[i]['full_name']}\n"
                                          f"{found_users[i]['profile_link']}")
                for url in found_users[i]['photo_url']:
                    send_photo(vk, event.user_id, *upload_photo(upload, url))
            elif request == 'Следующий пользователь':
                i += 1
                if i < len(found_users):
                    write_msg2(event.user_id, f"{found_users[i]['full_name']}\n"
                                              f"{found_users[i]['profile_link']}")
                    for url in found_users[i]['photo_url']:
                        send_photo(vk, event.user_id, *upload_photo(upload, url))
                else:
                    write_msg(event.user_id, "Список найденных пользователей закончился.\n"
                                             "Вы можете просмотреть список избранных или начать новый поиск.")
            elif request == 'Предыдущий пользователь':
                i -= 1
                if i >= 0:
                    write_msg2(event.user_id, f"{found_users[i]['full_name']}\n"
                                              f"{found_users[i]['profile_link']}")
                    for url in found_users[i]['photo_url']:
                        send_photo(vk, event.user_id, *upload_photo(upload, url))
                else:
                    i = 0
                    write_msg2(event.user_id, f"Вы перешли к началу списка.\n"
                                              f"{found_users[i]['full_name']}\n"
                                              f"{found_users[i]['profile_link']}")
                    for url in found_users[i]['photo_url']:
                        send_photo(vk, event.user_id, *upload_photo(upload, url))
            elif request == 'Добавить пользователя в список избранных':
                try:
                    add_favorite(found_users[i]['id'], found_users[i]['full_name'], found_users[i]['profile_link'],
                                 event.user_id)
                    for url in found_users[i]['photo_url']:
                        add_photo(url, found_users[i]['id'])
                    write_msg3(event.user_id, f"Пользователь {found_users[i]['full_name']} добавлен в "
                                              f"список избранных")
                except Exception:
                    write_msg3(event.user_id, f"Пользователь {found_users[i]['full_name']} уже в Вашем списке "
                                              f"избранных")
                i += 1
                if i < len(found_users):
                    write_msg2(event.user_id, f"{found_users[i]['full_name']}\n"
                                              f"{found_users[i]['profile_link']}")
                    for url in found_users[i]['photo_url']:
                        send_photo(vk, event.user_id, *upload_photo(upload, url))
                else:
                    write_msg(event.user_id, "Список найденных пользователей закончился.\n"
                                             "Вы можете просмотреть список избранных или начать новый поиск.")
            elif request == 'Открыть список избранных':
                write_msg(event.user_id, "Открываю Ваш список избранных для знакомства людей...")
                favorite_list = open_favorite_list(event.user_id)
                for index, favorite in enumerate(favorite_list):
                    write_msg(event.user_id, f"{index+1}. {favorite[1]} - {favorite[2]}")
                    for url in favorite[3]:
                        send_photo(vk, event.user_id, *upload_photo(upload, url))
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")
