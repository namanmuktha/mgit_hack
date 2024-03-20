
import firebase_admin
from firebase_admin import credentials, db
import random
import string

cred = credentials.Certificate("mgit-hack-c6060-firebase-adminsdk-1xvld-2f3c925e75.json")
firebase = firebase_admin.initialize_app(cred)

URL = "https://mgit-hack-c6060-default-rtdb.asia-southeast1.firebasedatabase.app/"
DB = db.reference(path="/", url=URL)


class User:
    def __init__(self, email, password, age, gender):
        self.email = email
        self.password = password
        self.isAdmin = False
        self.age = age
        self.gender = gender

from datetime import datetime
import pytz

def get_current_date():
    return datetime.now(pytz.timezone('Asia/Kolkata')).date()

def get_current_time():
    return datetime.now(pytz.timezone('Asia/Kolkata')).time()

def generate_random_email(name, domain='example.com'):
    return f'{name}@{domain}'

def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

def generate_random_age(min_age=15, max_age=30):
    return random.randint(min_age, max_age)

def generate_random_gender():
    return random.choice(['M', 'F'])

def create_user(username, email, password, age, gender):
    DB.child(username).set(User(email, password, age, gender).__dict__)

def generate_random_character():
    label_mapping = {
                          0 : 'dependable',
                          1 : 'extraverted',
                          2 :'lively',
                          3 :'responsible',
                          4 : 'serious'
                        }
    random_number = random.randint(0, 4)

    return label_mapping[random_number]

def generate_random_disorder():
    label_mapping = { 0 : '89+gfADHD',
                          1 : 'ASD',
                          2 : 'Loneliness',
                          3 : 'MDD',
                          4 : 'OCD',
                          5 : 'PDD',
                          6 : 'PTSD',
                          7 : 'anexiety',
                          8 : 'bipolar',
                          9 : 'eating disorder',
                         10 : 'psychotic deprission',
                         11 :'sleeping disorder'
                        }
    random_number = random.randint(0, 11)

    return label_mapping[random_number]
def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))
def create_data():
    for i in range(100):
        print(i,"th User added")
        name = "user" + str(i)
        email = generate_random_email(name)
        password = generate_random_password()
        age = generate_random_age()
        gender = generate_random_gender()

        create_user(name, email, password,age,gender)

        for i in range(10):
            dt = f"{get_current_date()} {get_current_time()}"
            res = f"{dt} {generate_random_character()} character"
            DB.child(name).child("diagnosis").child("character").child(generate_random_string()).set(res)

        for i in range(10):
            dt = f"{get_current_date()} {get_current_time()}"
            res = f"{dt} {generate_random_disorder()} disorder"
            DB.child(name).child("diagnosis").child("disorder").child(generate_random_string()).set(res)




def delete_complete_users():
    users = DB.get()
    for user in users:
        DB.child(user).delete()
    

#create_data()    

def test():
    
    user = DB.child("user0").get()
    #how to add child character to db with another chid by character
    DB.child("user0").child("character").child("result1").set("dependable")
    DB.child("user0").child("character").child("result2").set("extraverted")

create_data()