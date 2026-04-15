from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

@app.route("/")
def home():
    # Renders Tailwind dashboard (dashboard.html)
    return render_template("dashboard.html")

@app.route("/api/live")
def api_live():
    return jsonify({
        "colleges": random.randint(5, 5),
        "total_students": random.randint(30, 50),
        "streams": random.randint(4, 5),

        "line": [random.randint(20, 30) for _ in range(7)],
        "bar": [random.randint(20, 30) for _ in range(5)],
        "pie": [
            random.randint(20, 30),   # Pass
            random.randint(20, 30),   # Fail
            random.randint(10, 20)    # Backlog
        ]
    })

if __name__ == "__main__":
    app.run(debug=True)

#   form app

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def form():
    return render_template("form.html")

app.run(debug=True)

@app.route("/form")
def student_form():
    return render_template("form.html")

# from flask import Flask, render_template

# @app.route('/form')
# def form():
#     return render_template("form.html")
