from flask import Flask, redirect, render_template, request 
import mysql.connector, os
import bcrypt

app = Flask('app')
#"""
db = mysql.connector.connect( 
  host = os.environ["Host"],
  user = os.environ["User"],
  password = os.environ["Pass"],
  database = "testdb"
)
sql = db.cursor()

def result():
  for x in sql:
    print(x)

def execute(query):
  sql.execute(query)
  result()
#"""
def hashit(password):
  return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()) #don't need to save salts
  
def compareit(hashed, password):
  return bcrypt.checkpw(password, hashed)

"""CREATE TABLE Users (
id BIGINT UNSIGNED NOT NULL UNIQUE, #this became primary key automatically somehow
username varchar(25) NOT NULL UNIQUE,
display varchar(25),
password binary(60) NOT NULL,
bio TEXT,
about TEXT
);"""

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

    sql.execute("SELECT password FROM Users WHERE username = %s;", params=(request.form["username"].strip().lower(),))
    password = [i for i in sql]
    if not password: #no user. so empty
      return render_template("login.html",  mode="login", error="No user exists")
    if compareit(password[0], request.form["password"]):
      return True
    else: 
      return False
    
  return render_template("login.html", mode = "login", error = False)

@app.route("/signup", methods=["GET", "POST"])
def signuppage():
  if request.method == "POST":
    if not (request.form["username"] and request.form["password"]):
      return render_template("login.html", mode = "signup", error = "Username or password field was left empty")
    username = request.form["username"].strip()
    sql.execute("INSERT INTO Users (id, username, display, password) VALUES (UUID_SHORT(), %s, %s, %s)", params=(username.lower(), username, hashit(request.form["password"])))
    db.commit()
  return render_template("login.html", mode = "signup", error = False)

@app.errorhandler(404)
def notfoundpage(e):
  return render_template("404.html")

app.run(host='0.0.0.0', port=8080)
