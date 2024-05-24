import requests


class VK:
    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token

        self.id = user_id

        self.version = version

        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self):

        url = 'https://api.vk.com/method/users.get'

        params = {'user_ids': self.id}

        response = requests.get(url, params={**self.params, **params})

        return response.json()


access_token = 'vk1.a.Hl8ScOL_JqzXzpXZjqnjX2jfaUOZxpksPVqAjcky8kYVO6XEwnahu9gzX1Xo9Gotbxn3wcp3fHrrrvM7dfLx9Ck1O-8TWpE-BUQ796-OnEP1-ONb7zapubJ5TaFx4q4TZa3x7kNF54eLa4dVSHm-UwbHMkprCdtAcwIiJZ9dj2uyEiGFuau68jvkE2LMrvvf'
user_id = '842545206'
vk = VK(access_token, user_id)

print(vk.users_info())


# token_vk = 'https://oauth.vk.com/authorize?client_id=51857420
# &display=page&redirect_uri=https://example.com/
# callback&scope=friends,photos&response_type=token&v=5.131&state=123456'


# token_group = 'vk1.a.1Ju1eKhG7yqQZ8RgAqfuAjUEEA8zO-DTcHM8FZkqhpyzkEPlqyhl
# wJNZyRam-eZl_EVNGd68qBNXcEbXQwvC2_gz6ZxW4VDgpAnXefMQ6532OPs4xwIifVnmCDUZaK4wZGeZ2n2
# 8rxEFiCWSM4CQy153hnKbzPdnQRI_217US9vFpxv2iY1ab-PNpj9dJmddxQro69uldNYgOk8xddLWXw'

'vk1.a.1Ju1eKhG7yqQZ8RgAqfuAjUEEA8zO-DTcHM8FZkqhpyzkEPlqyhlwJNZyRam-eZl_EVNGd68qBNXcEbXQwvC2_gz6ZxW4VDgpAnXefMQ6532OPs4xwIifVnmCDUZaK4wZGeZ2n2 8rxEFiCWSM4CQy153hnKbzPdnQRI_217US9vFpxv2iY1ab-PNpj9dJmddxQro69uldNYgOk8xddLWXw'