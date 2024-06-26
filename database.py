from typing import Any
import psycopg2


class Database:
    def __init__(self, name, user, password, host, port):
        self.name = name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None
        self.cursor = None
        self.create_tables()

    def connect(self) -> None:
        self.connection = (psycopg2.connect(
            database=self.name, user=self.user, password=self.password,
            host=self.host, port=self.port))
        self.cursor = self.connection.cursor()

    def disconnect(self) -> None:
        self.connection.commit()
        self.connection.close()

    def create_tables(self) -> None:
        self.connect()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
            user_id SERIAL PRIMARY KEY,
            city VARCHAR(40) NOT NULL,
            sex VARCHAR(20) NOT NULL,
            age INT NOT NULL);
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pairs(
            id SERIAL PRIMARY KEY,
            user_vk_id INT NOT NULL,
            first_last_name VARCHAR(70) NOT NULL,
            vk_link VARCHAR(2048) NOT NULL,
            FOREIGN KEY(user_vk_id) REFERENCES users(user_id));
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS photos(
            id SERIAL PRIMARY KEY,
            pair_id INT NOT NULL,
            photo_link VARCHAR(2048) NOT NULL,
            FOREIGN KEY(pair_id) REFERENCES pairs(id));
            """
        )
        self.disconnect()

    def fetch_all(self, query, params=None) -> list[tuple]:
        self.connect()
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        result = self.cursor.fetchall()
        self.disconnect()
        return result

    def fetch_one(self, query, params=None) -> tuple:
        self.connect()
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        result = self.cursor.fetchone()
        self.disconnect()
        return result

    def execute_query(self, query, params=None) -> None:
        self.connect()
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        self.disconnect()

    @staticmethod
    def generator(data):
        for item in data:
            yield item

    def authentication(self, user_id: int) -> tuple:
        return self.fetch_one("SELECT user_id FROM users WHERE user_id = %s",
                              (user_id,))

    def get_settings_for_search(self, user_id: int) -> list[tuple]:
        self.connect()
        return self.fetch_all(
            "SELECT city, sex, age, user_id FROM users WHERE user_id= %s",
            (user_id,))

    def insert_settings_for_search(self, user_id: int, city: str,
                                   selected_gender: str, age: int) -> None:
        self.connect()
        self.cursor.execute("INSERT INTO users (user_id, city, sex, age) VALUES (%s, %s, %s, %s)",
                            (user_id, city, selected_gender, age,))
        self.disconnect()

    def update_settings_for_search(self, city: str, selected_gender: str,
                                   age: int, user_id: int) -> None:
        self.connect()
        self.cursor.execute("""UPDATE users 
                                SET city = %s, sex = %s, age = %s
                                WHERE user_id = %s""",
                            (city, selected_gender, age, user_id))
        self.disconnect()

    def add_into_favorites(self, user_id: int, first_last_name: str,
                           vk_link: str) -> None:
        self.connect()
        self.cursor.execute(
            """
            INSERT INTO pairs (user_vk_id, first_last_name, vk_link)
            VALUES (%s, %s, %s);
            """, (user_id, first_last_name, vk_link,))
        self.disconnect()

    def get_pair_id(self, vk_link: str):
        return self.fetch_one("SELECT id FROM pairs WHERE vk_link = %s",
                              (vk_link,))[0]

    def add_into_photos(self, pair_id: int, photo_link: str) -> None:
        self.connect()
        self.cursor.execute(
            """
            INSERT INTO photos (pair_id, photo_link)
            VALUES (%s, %s);
            """, (pair_id, photo_link,))
        self.disconnect()

    def get_favorites(self, user_id: int) -> list[tuple]:
        return self.fetch_all(
            """
            SELECT first_last_name, vk_link, photo_link FROM pairs 
            JOIN photos ON pairs.id = photos.pair_id
            WHERE user_vk_id = %s;
            """, (user_id,)
        )

    def create_favorites_data(self, user_id: int) -> list[dict[str, list[Any] | Any]]:
        data = []
        count = 0
        ind = 0
        for item in self.generator(self.get_favorites(user_id)):
            if count == 0:
                data.append({"first_last_name": item[0],
                             "link": item[1],
                             "photos_links": [item[2]]})
                count += 1
            else:
                data[ind].get("photos_links").append(item[2])
                count += 1
            if count == 3:
                count = 0
                ind += 1
        return data
