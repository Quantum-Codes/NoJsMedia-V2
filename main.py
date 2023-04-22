from flask import Flask, redirect, render_template
import mysql.connector, os

app = Flask('app')
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
 

@app.route('/')
def mainpage():
  if  True: #check login
    return redirect("/login")
  
  return "hey"

@app.route("/login")
def loginpage():
  return "login"

app.run(host='0.0.0.0', port=8080)
