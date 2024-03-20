from flask import Flask, request, render_template, jsonify
import json

app = Flask(__name__)

# Sample questions
questions = [
    {'id': 1, 'question': 'Feeling nervous: Do you often feel nervous?'},
    {'id': 2, 'question': 'Panic: Have you ever experienced a panic attack?'},
    {'id': 3, 'question': 'Breathing rapidly: Do you find yourself breathing rapidly in certain situations?'},
    {'id': 4, 'question': 'Sweating: Do you experience excessive sweating, even when it'},
    {'id': 5, 'question': 'Trembling: Do you find yourself trembling in certain situations?'},


]

@app.route('/')
def index():
    return render_template('./DisorderQuestions.html', questions=questions)

@app.route('/disorder_submit', methods=['POST'])
def disorder_submit():
    answers = json.loads(request.form.get('answers'))
    print(answers)
    return jsonify({'status': 'success', 'answers': answers})

if __name__ == '__main__':
    app.run(debug=True)
