import requests


class VKAPIClient:
    api_base_url = 'https://api.vk.com/method'

    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def get_common_params(self):
        return {
            'access_token': self.token,
            'v':'5.199'
        }

    def _build_url(self, api_metod):
        return f'{self.api_base_url}/{api_metod}'

    def user_info(self):
        url = 'https://api.vk.com/method/users.get'
        params = self.get_common_params()
        params.update({'fields': 'bdate, city, sex'})
        response = requests.get(url, params=params)
        return response.json()['response']

    def user_search(self, age, city_id, sex_id):
        url = 'https://api.vk.com/method/users.search'
        params = self.get_common_params()
        params.update({'count': 1000, 'city': city_id, 'sex': sex_id, 'status': 6, 'age_from': age, 'age_to':age})
        response = requests.get(url, params=params)
        return response.json()

    def _get_photos(self, owner_id):
        params = self.get_common_params()
        params.update({'owner_id': owner_id, 'album_id': 'profile', 'extended': '1'})
        response = requests.get(self._build_url('photos.get'), params=params)
        return response

    def get_list_foto_max_quality(self, owner_id):
        reply = self._get_photos(owner_id)
        foto_list_for_download = []
        try:
            list_foto_all_info = reply.json()['response']['items']
        except:
            status = 'error'
            print(f'\n'
                  f'Ошибка: {reply.json()["error"]["error_msg"]}')
        else:
            status = 'success'
            vk_photo_sizes = {'s': 1, 'm': 2, 'o': 3, 'p': 4, 'q': 5, 'r': 6, 'x': 7, 'y': 8, 'z': 9, 'w': 10}
            for foto_all_info in list_foto_all_info:
                max_photo_size = max(foto_all_info['sizes'], key= lambda x: vk_photo_sizes[x['type']])
                max_photo_size['count_likes'] = foto_all_info["likes"]["count"]
                foto_list_for_download.append(max_photo_size)
        return self.get_url_photos(self.get_popular_photos(foto_list_for_download))

    def get_popular_photos(self, photo_list: list):
        photo_list.sort(key=lambda x: x['count_likes'], reverse=True)
        return photo_list[:3]

    def get_url_photos(self, photo_list: list):
        final_photo_list = []
        for photo in photo_list:
            final_photo_list.append(photo['url'])
        return final_photo_list
