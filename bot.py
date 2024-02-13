import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.upload import VkUpload
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from configurations.configuration import group_token, token
from random import randrange
from class_vk_api import VKAPIClient
from main import get_info_current_user, find_user
import requests
from io import BytesIO


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


def upload_photo(upload, url):
    img = requests.get(url).content
    f = BytesIO(img)

    response = upload.photo_messages(f)[0]

    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    return owner_id, photo_id, access_key


def send_photo(vk, peer_id, owner_id, photo_id, access_key):
    attachment = f'photo{owner_id}_{photo_id}_{access_key}'
    vk.messages.send(
        random_id=get_random_id(),
        peer_id=peer_id,
        attachment=attachment
    )


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

            if request == 'привет':
                write_msg(event.user_id,
                          f"Для запуска поиска людей для знакомства нажмите соответствующую кнопку")

            elif request == 'Начать поиск':
                write_msg(event.user_id, "Начинаю поиск людей, подходящих для знакомства...")
                vkclient = VKAPIClient(token, event.user_id)
                found_users = find_user(vkclient, *get_info_current_user(vkclient))
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
                write_msg3(event.user_id, f"Пользователь {found_users[i]['full_name']} добавлен в "
                                         f"список избранных")
                i += 1
                write_msg2(event.user_id, f"{found_users[i]['full_name']}\n"
                                          f"{found_users[i]['profile_link']}")
                for url in found_users[i]['photo_url']:
                    send_photo(vk, event.user_id, *upload_photo(upload, url))

            elif request == 'Открыть список избранных':
                write_msg(event.user_id, "Открываю список Ваш список избранных для знакомства людей...")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")
