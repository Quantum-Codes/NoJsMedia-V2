from flask import Flask, redirect, render_template, request, make_response
import mysql.connector, os, re, secrets, dotenv
import bcrypt
#POETRY ADD REPLIT BACK IF ANY WEIRD ERROR 
#REMAKE DIV CONTAINING ERROR MESSAGE
#ONLY MAIN PAGE ACTUALLY VERIFIES SESSION. OTHERS SIMPLY CHECK THE PRESENCE OF SESSION COOKIE
dotenv.load_dotenv()
app = Flask('app')
uname = re.compile("^[A-Za-z0-9-_]{3,25}$")
passwd = re.compile("^[A-Za-z0-9-_\$@\&!#\?]{3,50}$")

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
  return bcrypt.checkpw(password.encode("utf-8"), bytes(hashed)) #convert bytearray by sql to bytes

def respond(page, cookiename, val, expiry=60*60*24*7): #1 week auto expire
  res = make_response(redirect(page))
  res.set_cookie(cookiename, val, expiry)
  return res

def get_session(request):
  sql.execute("SELECT username, display FROM Users WHERE session = %s;", params=(request.cookies.get("session"),))
  data = [i for i in sql]
  return data

"""CREATE TABLE Users (
id BIGINT UNSIGNED NOT NULL UNIQUE, #this became primary key automatically somehow
username varchar(25) NOT NULL UNIQUE,
display varchar(25),
password binary(60) NOT NULL,
session varchar(64) UNIQUE, #max 1 char = 2 byte for token urlsafe. so 32*2=64 max session len
bio TEXT,
about TEXT
);"""

@app.route('/')
def mainpage():
  loggedin = False 
  if request.cookies.get("session"):
    session = get_session(request)
    if not session:
      return respond("/", "session", "", 0) #delete session cookie
    loggedin = True
    username, displayname = session[0]
  else:
    username = displayname = "guest"
  return render_template("main.html", user = displayname, loggedin = loggedin)

@app.route("/login", methods=["GET", "POST"])
def loginpage():
  if request.method == "POST":
    if not (request.form["username"] and request.form["password"]):
      return respond("/login", "temp", "Username or password field was left empty.", 2)
    username = request.form["username"].strip().lower()
    if not uname.fullmatch(username): #saves a useless read
      return respond("/login", "temp", "No such user exists.", 2)
    if not passwd.fullmatch(request.form["password"]):
      return respond("/login", "temp", "Invalid password.", 2)
      
    sql.execute("SELECT password FROM Users WHERE username = %s;", params=(username,))
    password = [i for i in sql]
    if not password: #no user. so empty
      return respond("/login", "temp", "No such user exists.", 2)
    if not compareit(password[0][0], request.form["password"]):
      return respond("/login", "temp", "Incorrect password.", 2)

    #Verified user from here
    session = secrets.token_urlsafe(32)
    sql.execute("UPDATE Users SET session = %s WHERE username = %s", params = (session, username))
    db.commit()
    return respond("/", "session", session)
    
  return render_template("login.html", mode = "login", error = request.cookies.get("temp"), loggedin = request.cookies.get("session"))

@app.route("/signup", methods=["GET", "POST"])
def signuppage():
  if request.method == "POST":
    if not (request.form["username"] and request.form["password"]):
      return respond("/signup", "temp", "Username or password field was left empty.", 2)
    username = request.form["username"].strip()
    if not uname.fullmatch(username):
      return respond("/signup", "temp", "Username must have length of 3 to 25 and only characters A-Z, a-z, 0-9, '-', '_'", 2)
    if not passwd.fullmatch(request.form["password"]):
      return respond("/signup", "temp", "Password must have length of 3 to 50 and only characters A-Z, a-z, 0-9, &,#,₩,₹,£,€,&,!,@,?", 2)

    sql.execute("INSERT INTO Users (id, username, display, password) VALUES (UUID_SHORT(), %s, %s, %s)", params=(username.lower(), username, hashit(request.form["password"])))
    db.commit()
    return "Created user. Should add session and redirect to main site."
    
  return render_template("login.html", mode = "signup", error = request.cookies.get("temp"), loggedin = request.cookies.get("session"))

@app.route("/logout", methods=["POST"]) #don't GET as people could just put this as img url and it would get this and log them out.
def logoutpage(): #Logging out makes 1 read and 1 write query. Try reducing to 1 write
  if not request.cookies.get("session"):
    return redirect("/")
  user = get_session(request)
  if user:
    user = user[0][0]
    sql.execute("UPDATE Users SET session = NULL WHERE username = %s", params=(user,))
    db.commit()
  return respond("/", "session", "", 0)

@app.errorhandler(404)
def notfoundpage(e):
  return render_template("404.html")

app.run(host='0.0.0.0', port=8080)
