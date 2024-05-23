import requests
import configparser
import random
from typing import Any, List, Dict

config = configparser.ConfigParser()
config.read("token.ini")


class VkApi:
    def __init__(self, token):
        self.token = token
        self.base_url = 'https://api.vk.com/method/'
        self.base_params = {'access_token': token, 'v': '5.131'}

    def has_three_photo(self, user_id: int) -> bool:

        url = f"{self.base_url}photos.get"
        self.base_params.update(
            {
                "owner_id": user_id,
                "album_id": "profile"
            }
        )
        response = requests.get(url=url, params=self.base_params)
        print(f"{self.has_three_photo.__name__}-{response.status_code=}")
        response_json = response.json()
        try:
            response_json.get("response").get("items")
        except Exception as e:
            print(f"{e}")
            return False

        return len(response_json.get("response").get("items")) >= 3

    def find_users(self, city: str, sex: int, age_from: int,
                   age_to: int, count: int = 10) -> (
            list)[dict[str, str | list[Any] | Any]]:

        url = f"{self.base_url}users.search"
        self.base_params.update(
            {
                "count": count,
                "hometown": city,
                "sex": sex,
                "age_from": age_from,
                "age_to": age_to,
                "has_photo": 1,
                # "offset": random.randint(0, 1000 - count)
            }
        )
        response = requests.get(url=url, params=self.base_params)
        print(f"{self.find_users.__name__}-{response.status_code=}")
        response_json = response.json()
        if list(response_json.keys())[0] == 'error':
            raise Exception([response_json['error']['error_msg']])

        try:
            data = [
                {
                    "id": user.get("id"),
                    "link": f"https://vk.com/id{user.get("id")}",
                    "first_last_name": f"{user.get("first_name")} "
                                       f"{user.get("last_name")}"
                }
                for user in response_json.get("response").get("items")
                if self.has_three_photo(user.get("id"))]
        except Exception as e:
            data = []
            print(f"{e}")

        return data

    def get_photos_links(self, user_id: int) -> list[Any]:

        url = f"{self.base_url}photos.get"
        self.base_params.update({"owner_id": user_id,
                                 "album_id": "profile",
                                 "extended": 1}
                                )
        response = requests.get(url=url, params=self.base_params)
        print(f"{self.get_photos_links.__name__}-{response.status_code=}")
        response_json = response.json()
        try:
            items = response_json.get("response").get("items")
        except Exception as e:
            items = []
            print(f"{e}")
        top_three_photos = sorted(items, key=lambda item: item.get("likes").
                                  get("count"), reverse=True)[0:3]
        links = [photo_data.get("sizes")[-1].get("url")
                 for photo_data in top_three_photos]

        return links

    def get_users_data(self, city: str, sex: int, age_from: int,
                       age_to: int, count: int = 5) -> (
            list)[dict[str, str | list[Any] | None | Any]]:

        raw_data = self.find_users(city, sex, age_from, age_to, count)
        valid_data = []
        for user in raw_data[:count + 1]:
            user_id = user.get("id")
            photos_links = self.get_photos_links(user_id)
            valid_data.append(
                {
                    "first_last_name": user.get("first_last_name"),
                    "link": user.get("link"),
                    "photos_links": photos_links
                }
            )

        return valid_data


api = VkApi(config['TOKEN']['vk_token'])
print(api.get_users_data("Москва", 1, 20, 30))
