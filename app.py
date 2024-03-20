from flask import Flask, render_template, request,session,jsonify
from flask import redirect, url_for
from datetime import datetime

#import geocoder
import requests
import json
import pickle
import pytz
import bcrypt
import joblib
import warnings
warnings.filterwarnings("ignore")


import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("mgit-hack-c6060-firebase-adminsdk-1xvld-2f3c925e75.json")
firebase = firebase_admin.initialize_app(cred)

URL = "https://mgit-hack-c6060-default-rtdb.asia-southeast1.firebasedatabase.app/"
DB = db.reference(path="/", url=URL)

app = Flask(__name__)

app.secret_key = "mgit-hack-c6060"

def get_current_date():
    return datetime.now(pytz.timezone('Asia/Kolkata')).date()

def get_current_time():
    return datetime.now(pytz.timezone('Asia/Kolkata')).time()

class User:
    def __init__(self, email, password, age, gender):
        self.email = email
        self.password = password
        self.isAdmin = False
        self.age = age
        self.gender = gender

def create_user(username, email, password, age, gender):
    DB.child(username).set(User(email, password, age, gender).__dict__)

def Log_in(username, password):
    user = DB.child(username).get()
    if user:
        if user["password"] == password:
            return "Logged in successfully"
        return "Incorrect email or password"
    return "User not found"

def exists(username):
    user = DB.child(username).get()
    return user is not None

api_key = "0c6367c0ffc59182e0e17fbbe7ced418"
latitude = 0.0
longitude = 0.0


characterPickle = joblib.load('./models/Personality.joblib')
disorderPickle = joblib.load('./models/mental_disorder_model.joblib')
    

def celsius_to_fahrenheit(celsius):
    fahrenheit = (celsius * 9/5) + 32
    return fahrenheit

def get_weather(api_key, lat, lon):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}lat={lat}&lon={lon}&appid={api_key}"

    response = requests.get(complete_url)
    data = response.json()

    if data["cod"] != "404":
        if "main" in data:
            main_data = data["main"]
            temperature = main_data.get("temp", "N/A") - 273.15  # Convert Kelvin to Celsius
            humidity = main_data.get("humidity", "N/A")

            #print(f"Temperature: {temperature:.2f}°C")
            #print(f"Humidity: {humidity}%")
            return temperature, humidity
        else:
            return "Unexpected response structure. Data structure may have changed. Response:"
    else:
        return "Weather data not available for this location!"

@app.route('/')
def home():
    return render_template('./loginPage.html')

@app.route('/user_login', methods=['GET', 'POST'])
def login_form():
    username = request.form.get('username')
    password = request.form.get('password')
    if DB.child(username).get('isAdmin'):
        return redirect('/admin')
    var = Log_in(username, password)
    if var == "Logged in successfully":
        session["username"] = username
        return redirect(url_for('mainPage'))
    else:
        return render_template('./loginPage.html', error=var)

@app.route('/mainPage')
def mainPage():
    return render_template('./mainPage.html', username = session.get('username'))

@app.route('/register')
def register():
    return render_template('./signup.html')

@app.route('/register_form', methods=['GET', 'POST'])
def registerPage():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    age_str = request.form.get('age')
    gender = request.form.get('gender')

    age = int(age_str)
    
    if exists(username):
        return render_template('./signup.html',error="Username already exists")
    else:
        create_user(username, email, password, age, gender)
        session["username"] = username
        return redirect(url_for('mainPage'))
@app.route('/admin')
def admin_dashboard():
    db_val_ref=db.reference(path='/',url=URL)
    dv_val_value=db_val_ref.get()
    # users = []
    # for key, val in dv_val_value:
    #     for k, v in val["diagnosis"]["character"].__dict__:
    #         character = v
    #     for k, v in val["diagnosis"]["disorder"].__dict__:
    #         disorder = v
    #     users.append(key)

    return render_template('./admin_dashboard.html',username=session.get('username'),data=dv_val_value)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template('./loginPage.html')

@app.route('/character_form', methods=['GET', 'POST'])
def character_form():
    with open('character.json') as file:
        data = json.load(file)
        questions = data['questions']

    return render_template('./CharacterQuestions.html',questions = questions)

@app.route('/disorder_form', methods=['GET', 'POST'])
def disorder_form():
    with open('disorder.json') as file:
        data = json.load(file)
        questions = data['questions']

    return render_template('./DisorderQuestions.html',questions = questions)

@app.route('/character_submit', methods=['GET', 'POST'])
def character_submit():
    ans = json.loads(request.form.get('answers'))
    answers = [int(a) for a in ans]

    user = DB.child(session.get('username')).get()
    username = session.get('username')

    try:
        if len(answers) != 5:
            return "Error in number of questions with feature array"
        if user['gender'] == 'M' :
            features = [2, user['age']] + answers
        else :
            features = [1, user['age']] + answers
        result = characterPickle.predict([features])
        label_mapping = {
                          0 : 'dependable',
                          1 : 'extraverted',
                          2 :'lively',
                          3 :'responsible',
                          4 : 'serious'
                        }
        
        date = get_current_date()
        time = get_current_time()
        dateTime = f"{date} {time}"

        DB1 = db.reference(path=f"/{username}/diagnosis/character", url=URL)

        DB1.push(f"{dateTime} {label_mapping[result[0]]}")

        character_name = label_mapping[result[0]]
        result = f"you are probably {character_name} person"
        return render_template('./resultPage.html', result=result, Name=session.get('username'), gender=user['gender'])
    except Exception as e:
        print(e)
        return "Please enter valid numbers for the questions."

@app.route('/disorder_submit', methods=['GET', 'POST'])
def disorder_submit():
    ans = json.loads(request.form.get('answers'))

    answers = [int(a) for a in ans]

    user = DB.child(session.get('username')).get()
    username = session.get('username')

    try:
        if len(answers) != 26:
            return "Error in number of questions with feature array"
        features = answers + [user['age']]
        result = disorderPickle.predict([features])
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
        result_int = int(result)
        disorder_name = label_mapping[result_int]

        date = get_current_date()
        time = get_current_time()
        dateTime = f"{date} {time}"

        DB1 = db.reference(path=f"/{username}/diagnosis/disorder", url=URL)

        DB1.push(f"{dateTime} {disorder_name}")

        result = f"you might have risk of {disorder_name} disorder"
        return render_template('./resultPage.html',result=result,Name = session.get('username'), gender = user['gender'])
    except ValueError:
        return "Please enter valid numbers for the questions."

@app.route('/profile<string:username>')
def profile(username):
    DB1 = db.reference(path=f"/{session.get('username')}/diagnosis/character", url=URL)
    DB2 = db.reference(path=f"/{session.get('username')}/diagnosis/disorder", url=URL)

    character = DB1.get()
    disorder = DB2.get()
    ans1 = []
    if character is not None :
        for key, value in character.items():
            print(key, value)
            ans1.append((value.split()[0], value.split()[1], value.split()[2]))
    ans2 = []
    if disorder is not None:
        for key, value in disorder.items():
            print(key, value)
            ans2.append((value.split()[0], value.split()[1], value.split()[2]))
    
    user = DB.child(session.get('username')).get()
    return render_template('./profile.html', character = ans1, disorder = ans2, user = user, username = session.get('username'))

if __name__ == '__main__':
    app.run(debug=True)