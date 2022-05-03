import sqlite3

DB_NAME = "Users.db"
testDB = "Test.db"
SALT = "SV175926392"

def get_database_connection():
    con = sqlite3.connect(DB_NAME)
    return con


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit() # ensures the query is durable and will remain in the database
        print("Query executed successfully")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")
        return False


def create_database(connection):
    try:
        file = open("schema.sql")
        query = file.read()
        connection.executescript(query)
        print("database created")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")

class UserDatabase():

    def __init__(self):
        '''
        Creates a database based on the schema if not already existent
        '''
        con = get_database_connection()
        create_database(con)

    def add_user(self, username, password, phone, ability):
        self.username = username
        self.password = password
        self.phone = phone
        self.ability = ability

        qry = f'INSERT INTO users (username,password,phone,ability) VALUES("{self.username}","{self.password}","{self.phone}","{self.ability}");'
        try:
            c = get_database_connection()
            print("inserting...")
            execute_query(c, qry)
        except sqlite3.Error as e:
            print(e)
        finally:
            c.close()

    def update_ability(self,ability,user):
        try:
            con = get_database_connection()
            query = f'UPDATE users SET ability = "{ability}" WHERE username = "{user}"'
            execute_query(con,query)
            print("Update has taken place")
            results = self.find_user(user)
            print(results)
        except:
            print("Except statement executed: update_ability")
            return None


    def find_user(self,user):
        '''
        Locates the user's credentials in the database searching the column username
        :param user: Submitted username used by the user to identify their account
        :return: Database row with the user's credentials
        '''
        try:
            con = get_database_connection()
            cur = con.cursor()
            query = f'SELECT * FROM users WHERE username= ?'
            cur.execute(query,(user,))
            result = cur.fetchone()
            print(result)
            print("Try statement executed: find_user")  #debugging purposes
            return result
        except:
            print("Except statement executed: find_user")
            return None

    def find_all(self):
        try:
            con = get_database_connection()
            query = f'SELECT username FROM users'
            data = execute_query(con, query)
            names = []
            for name in data:
                names.append(name[0])
            return names
        except:
            print("Except statement executed: find_all")

    @property
    def phone(self):
        return self.__phone

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    @property
    def ID(self):
        return self.__ID

    @property
    def ability(self):
        return self.__ability

    @ability.setter
    def ability(self,ability):
        if ability == "Standard" or ability == "Advanced":
            self.__ability = ability
        else:
            raise ValueError("ability must be either Standard or Advanced")

    @username.setter
    def username(self, username):
        if len(username) > 15:
            raise ValueError("username must be between 2 and 15 characters long")
        else:
            self.__username = username

    @phone.setter
    def phone(self,phone):
        if len(phone) != 11:
            raise ValueError("Phone number must have contain 11 digits")
        elif type(phone) != str:
            raise TypeError("Phone number must be of type: string")
        else:
            self.__phone = phone

    @password.setter
    def password(self, password):
        '''
        Validates the password and once validated, enables the password to be added to the database
        :param password:
        :return:
        '''
        if type(password) != str:
            raise TypeError("Password must be a string")
        elif len(password) < 8:
            raise ValueError("Password is too short must be at least 8 characters")
        else:
            self.__password = password

if __name__ == '__main__':
    con = get_database_connection()
    db = UserDatabase()
    db.find_all()