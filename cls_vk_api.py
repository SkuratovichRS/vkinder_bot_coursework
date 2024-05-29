import requests
import random
from typing import Any
from collections import deque


class VkApi:
    def __init__(self, token):
        self.token = token
        self.base_url = 'https://api.vk.com/method/'
        self.base_params = {'access_token': token, 'v': '5.131'}
        self.users_storage = deque()

    def get_random_pairs(self, data: list, count: int) -> list[Any]:
        chosen_users = []
        result = []
        attempts = count * 2
        attempt = 1
        while len(result) < count and attempt <= attempts:
            user = random.choice(data)
            if user not in chosen_users and self.has_three_photo(user.get("id")):
                result.append(user)
                chosen_users.append(user)
            attempt += 1
        return result

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

    def find_pairs(self, city: str, sex: int, age_from: int,
                   age_to: int, count: int = 5) -> (
            list[dict[str, str | list[Any] | Any]]):

        url = f"{self.base_url}users.search"
        self.base_params.update(
            {
                "count": 1000,
                "hometown": city,
                "sex": sex,
                "age_from": age_from,
                "age_to": age_to,
                "has_photo": 1,
                "is_closed": 0,
            }
        )
        response = requests.get(url=url, params=self.base_params)
        print(f"{self.find_pairs.__name__}-{response.status_code=}")
        response_json = response.json()
        if list(response_json.keys())[0] == 'error':
            raise Exception([response_json['error']['error_msg']])
        try:
            response_json.get("response").get("items")
        except Exception as e:
            print(f"{e}")
            return []
        random_users = (self.get_random_pairs
                        (response_json.get("response").get("items"), count))
        data = [
            {
                "id": user.get("id"),
                "link": f"https://vk.com/id{user.get("id")}",
                "first_last_name": f"{user.get("first_name")} "
                                   f"{user.get("last_name")}"
            }
            for user in random_users]

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

    def store_pairs_data(self, city: str, sex: int, age_from: int,
                         age_to: int, count: int = 5) -> None:

        raw_data = self.find_pairs(city, sex, age_from, age_to, count)
        for user in raw_data:
            user_id = user.get("id")
            photos_links = self.get_photos_links(user_id)
            self.users_storage.append(
                {
                    "first_last_name": user.get("first_last_name"),
                    "link": user.get("link"),
                    "photos_links": photos_links
                }
            )

    def get_pair_from_storage(self) -> dict[str, str | list[Any]]:
        return self.users_storage.popleft()
