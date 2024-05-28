import configparser

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

    def fetch_all(self, query, params=None):
        """
        Выполняет SQL-запрос и возвращает все полученные строки.

        Параметры
        ----------
        query: str
            SQL-запрос.
        params: tuple, optional
            Кортеж с параметрами для запроса.

        Возвращает
        -------
        list
            Список кортежей с данными.
        """
        self.connect()
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        result = self.cursor.fetchall()
        self.disconnect()
        return result

    def fetch_one(self, query, params=None):
        """
        Выполняет SQL-запрос и возвращает первую полученную строку.

        Параметры
        ----------
        query: str
            SQL-запрос.
        params: tuple, optional
            Кортеж с параметрами для запроса.

        Возвращает
        -------
        tuple
            Кортеж с данными.
        """
        self.connect()
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        result = self.cursor.fetchone()
        self.disconnect()
        return result

    def execute_query(self, query, params=None):
        self.connect()
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        self.connection.commit()
        self.disconnect()

    def add_into_favorites(self, user_id, first_last_name, vk_link):
        self.connect()
        self.cursor.execute(
            """
            INSERT INTO pairs (user_vk_id, first_last_name, vk_link)
            VALUES (%s, %s, %s);
            """, (user_id, first_last_name, vk_link, ))
        self.disconnect()

    def add_into_photos(self, pair_id, photo_link):
        self.connect()
        self.cursor.execute(
            """
            INSERT INTO photos (pair_id, photo_link)
            VALUES (%s, %s);
            """, (pair_id, photo_link, ))
        self.disconnect()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("settings.ini")
    db = Database(config['DATABASE']['name'], config['DATABASE']['user'],
                  config['DATABASE']['password'], '127.0.0.1', 5432)
    print(db.fetch_all('SELECT city, sex, age, user_id FROM users '))
    print(db.fetch_one('SELECT city FROM users')[0])