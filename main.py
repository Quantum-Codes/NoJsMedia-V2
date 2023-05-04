from flask import Flask, redirect, render_template, request 
import mysql.connector, os, re
import bcrypt
#REMAKE DIV CONTAINING ERROR MESSAGE
app = Flask('app')
uname = re.compile("^[A-Za-z0-9-_]{3,25}$")
passwd = re.compile("^[A-Za-z0-9-_\$@\&!£#€₹₩\?]{3,50}$")

"""regex tester 
x = lambda y: print("\n".join([str(uname.fullmatch(i)) for i in y]))
x([
  "abchfyyfyf",
  "srhtsthth\n097dbt",
  "dthhtddththdtdhthdthdthdyhdyhddyhydhyhdyhdhycchy",
  "tr64fy6rdt-txtx__"
])
exit()
#"""
#"""uncomment to remove connection
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
  #print(bytes(password, "utf-8"))
  return bcrypt.checkpw(password.encode("utf-8"), bytes(hashed)) #convert bytearray by sql to bytes

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
    username = request.form["username"].strip().lower()
    if not uname.fullmatch(username): #saves a useless read
      return render_template("login.html", mode = "login", error = "No such user exists.")
    if not passwd.fullmatch(request.form["password"]):
      return render_template("login.html", mode = "login", error = "Invalid password.")
      
    sql.execute("SELECT password FROM Users WHERE username = %s;", params=(username,))
    password = [i for i in sql]
    if not password: #no user. so empty
      return render_template("login.html",  mode="login", error="No such user exists.")
    if not compareit(password[0][0], request.form["password"]):
      return render_template("login.html", mode = "login", error = "Incorrect password.")

    #Verified user from here
    return "True. now should add session cookie and redirect to main site"
    
  return render_template("login.html", mode = "login", error = False)

@app.route("/signup", methods=["GET", "POST"])
def signuppage():
  if request.method == "POST":
    if not (request.form["username"] and request.form["password"]):
      return render_template("login.html", mode = "signup", error = "Username or password field was left empty")
    username = request.form["username"].strip()
    if not uname.fullmatch(username):
      return render_template("login.html", mode="signup", error = "Username must have length of 3 to 25 and only characters A-Z, a-z, 0-9, '-', '_'")
    if not passwd.fullmatch(request.form["password"]):
      return render_template("login.html", mode = "login", error = "Password must have length of 3 to 50 and only characters A-Z, a-z, 0-9, &,#,₩,₹,£,€,&,!,@,?") #auto sanitized by flask

    sql.execute("INSERT INTO Users (id, username, display, password) VALUES (UUID_SHORT(), %s, %s, %s)", params=(username.lower(), username, hashit(request.form["password"])))
    db.commit()
    return "Created user. Should add session and redirect to main site."
    
  return render_template("login.html", mode = "signup", error = False)

@app.errorhandler(404)
def notfoundpage(e):
  return render_template("404.html")

app.run(host='0.0.0.0', port=8080)
