import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from configurations.configuration import group_token, token
from random import randrange
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from class_vk_api import VKAPIClient
from main import get_info_current_user, find_user

vk = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk)

keyboard = VkKeyboard()
keyboard.add_button("Начать поиск", color=VkKeyboardColor.POSITIVE)
keyboard.add_line()
keyboard.add_button("Открыть список избранных", color=VkKeyboardColor.PRIMARY)
keyboard2 = VkKeyboard()
keyboard2.add_button("Следующий пользователь", color=VkKeyboardColor.SECONDARY)
keyboard2.add_button("Предыдущий пользователь", color=VkKeyboardColor.SECONDARY)
keyboard2.add_line()
keyboard2.add_button("Добавить пользователя в список избранных", color=VkKeyboardColor.POSITIVE)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7),
                                "keyboard": keyboard.get_keyboard()})


def write_msg2(user_id, message, attachments):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7),
                                'attachment': ','.join(attachments), "keyboard": keyboard2.get_keyboard()})


def write_msg3(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})


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
                                          f"{found_users[i]['profile_link']}", found_users[i]['photo_url'])
            elif request == 'Следующий пользователь':
                i += 1
                if i < len(found_users):
                    write_msg2(event.user_id, f"{found_users[i]['full_name']}\n"
                                              f"{found_users[i]['profile_link']}", found_users[i]['photo_url'])
                else:
                    write_msg(event.user_id, "Список найденных пользователей закончился.\n"
                                             "Вы можете просмотреть список избранных или начать новый поиск.")
            elif request == 'Предыдущий пользователь':
                i -= 1
                if i >= 0:
                    write_msg2(event.user_id, f"{found_users[i]['full_name']}\n"
                                              f"{found_users[i]['profile_link']}", found_users[i]['photo_url'])
                else:
                    i = 0
                    write_msg2(event.user_id, f"Вы перешли к началу списка.\n"
                                              f"{found_users[i]['full_name']}\n"
                                              f"{found_users[i]['profile_link']}", found_users[i]['photo_url'])
            elif request == 'Добавить пользователя в список избранных':
                write_msg3(event.user_id, f"Пользователь {found_users[i]['full_name']} добавлен в "
                                         f"список избранных")
                i += 1
                write_msg2(event.user_id, f"{found_users[i]['full_name']}\n"
                                          f"{found_users[i]['profile_link']}", found_users[i]['photo_url'])

            elif request == 'Открыть список избранных':
                write_msg(event.user_id, "Открываю список Ваш список избранных для знакомства людей...")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")
