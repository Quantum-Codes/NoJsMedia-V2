from flask import Flask, redirect, render_template, request 
import mysql.connector, os

app = Flask('app')
"""
db = mysql.connector.connect( 
  host = os.environ["Host"],
  user = os.environ["User"],
  password = os.environ["Pass"],
  database = os.environ["User"]
)
sql = db.cursor()

def result():
  for x in sql:
    print(x)

def execute(query):
  sql.execute(query)
  result()
"""

@app.route('/')
def mainpage():
  if True: #check login
    return redirect("/login")
  
  return render_template("main.html")

@app.route("/login", methods=["GET", "POST"])
def loginpage():
  if request.method == "POST":
    if not (request.form["username"] and request.form["password"]):
      return render_template("login.html", mode = "login", error = "Username or password field was left empty")
    
  return render_template("login.html", mode = "login", error = False)

@app.route("/signup", methods=["GET", "POST"])
def signuppage():
  return render_template("login.html", mode = "signup", error = False)

@app.errorhandler(404)
def notfoundpage(e):
  return render_template("404.html")

app.run(host='0.0.0.0', port=8080)
