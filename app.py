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
#loding models

# atmospherePickle = joblib.load('./Models/atmosphereModel.joblib')
# characterPickle = joblib.load('./Models/characterModel.joblib')
# disorderPickle = joblib.load('./Models/disorderModel.joblib')

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

# def get_user_location():
#     g = geocoder.ip('me')
#     return g.latlng



@app.route('/')
def home():
    return render_template('./loginPage.html')

@app.route('/user_login', methods=['GET', 'POST'])
def login_form():
    username = request.form.get('username')
    password = request.form.get('password')
    var = Log_in(username, password)
    if var == "Logged in successfully":
        return redirect(url_for('mainPage'))
    else:
        return render_template('./loginPage.html', error=var)

@app.route('/mainPage')
def mainPage():
    return render_template('./mainPage.html')

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
        return redirect(url_for('mainPage'))
    
# @app.route('/account', methods=['GET', 'POST'])
# def account():
#     try:
#         user_email = session.get('user_email')
#         user = UserDetails.query.get(user_email)
#         if user_email == 'eligetivignesh@gmail.com':
#             return redirect(url_for('adminPage'))
#         charResult = CharacterResult.query.filter_by(email=user_email).all()
#         disResult = DisorderResult.query.filter_by(email=user_email).all()
#         return render_template('./account.html',user = user,
#                                charResult = charResult,
#                                disResult = disResult
#                                )
#     except Exception as e:
#         return jsonify(error=str(e)), 500

# @app.route('/logout')
# def logout():
#     session.pop('user_email', None)
#     return render_template('./loginPage.html')


# @app.route('/adminPage', methods=['GET', 'POST'])
# def adminPage():
#     user_email = session.get('user_email')
#     user = UserDetails.query.get(user_email)
#     CharQuestions = CharacterQuestions.query.all()
#     users = UserDetails.query.all()
#     DisQuestions = DisorderQuestions.query.all()
#     return render_template('./adminPage.html',user=user, users=users,CharacterQuestions=CharQuestions,DisorderQuestions=DisQuestions)
    
    
# # delete user from database
# @app.route('/delete_user/<int:user_id>', methods=['DELETE'])
# def delete_user(user_id):
#     user = UserDetails.query.get(user_id)
#     if not user:
#         return jsonify({"error": "User not found"}), 404

#     db.session.delete(user)  # pass the user object
#     db.session.commit()

#     return jsonify({"message": "User deleted successfully"}), 200



# @app.route('/character_form', methods=['GET', 'POST'])
# def character_form():
#     questions  = CharacterQuestions.query.all()
#     #for i in range (0,len(questions)):
#     #    print(questions[i].question)

#     return render_template('./CharacterQuestions.html',questions = questions)

# @app.route('/disorder_form', methods=['GET', 'POST'])
# def disorder_form():
#     questions  = DisorderQuestions.query.all()
#     #for i in range (0,len(questions)):
#     #    print(questions[i].question)

#     return render_template('./DisorderQuestions.html',questions = questions)

# @app.route('/character_submit', methods=['GET', 'POST'])	
# def characterSubmit():
#     user_email = session.get('user_email')
#     user = UserDetails.query.get(user_email)
#     questions = CharacterQuestions.query.all()
#     noOfQuestions = len(questions)
#     question_array = [0] * noOfQuestions
#     try:
#         for i in range (0,noOfQuestions):
#             question_array[i] = int(request.form.get("question "+str(questions[i].id)))

#         if len(question_array) != 5:
#             return "Error in number of questions with feature array"
#         if user.gender == 'male' :
#             features = [2, user.age] + question_array
#         else :
#             features = [1, user.age] + question_array
#         result = characterPickle.predict([features])
#         label_mapping = {
#                           0 : 'dependable',
#                           1 : 'extraverted',
#                           2 :'lively',
#                           3 :'responsible',
#                           4 : 'serious'
#                         }
        
#         #storing the result in the database
#         new_result = CharacterResult(
#             email=user_email,
#             result=label_mapping[result[0]],
#         )
#         db.session.add(new_result)
#         db.session.commit()
#         character_name = label_mapping[result[0]]
#         result = f"you are probably {character_name} person"
#         return render_template('./resultPage.html', result=result, Name=user.name, gender=user.gender)
#     except ValueError:
#         return "Please enter valid numbers for the questions."

# @app.route('/disorder_submit', methods=['GET', 'POST'])
# def disorderSubmit():
#     user_email = session.get('user_email')  
#     latest_user = UserDetails.query.get(user_email)
#     questions = DisorderQuestions.query.all()
#     noOfQuestions = len(questions)
#     question_array = [0] * noOfQuestions
#     try:
#         for i in range(0,noOfQuestions):
#             question_array[i] = int(request.form.get("question"+str(questions[i].id)))
#         if len(question_array) != 26:
#             return "Error in number of questions with feature array"
#         features = question_array + [latest_user.age]
#         result = disorderPickle.predict([features])
#         label_mapping = { 0 : '89+gfADHD',
#                           1 : 'ASD',
#                           2 : 'Loneliness',
#                           3 : 'MDD',
#                           4 : 'OCD',
#                           5 : 'PDD',
#                           6 : 'PTSD',
#                           7 : 'anexiety',
#                           8 : 'bipolar',
#                           9 : 'eating disorder',
#                          10 : 'psychotic deprission',
#                          11 :'sleeping disorder'
#                         }
#         result_int = int(result)
#         disorder_name = label_mapping[result_int]

#         #storing the result in the database
#         new_result = DisorderResult(
#             email=user_email,
#             result=disorder_name,
#         )
#         db.session.add(new_result)
#         db.session.commit()

#         result = f"you might have risk of {disorder_name} disorder"
#         return render_template('./resultPage.html',result=result,Name = latest_user.name, gender = latest_user.gender)
#     except ValueError:
#         return "Please enter valid numbers for the questions."



if __name__ == '__main__':
    app.run(debug=True)