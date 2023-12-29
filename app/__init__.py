from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager
from .users import User
from .config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, SECRET_KEY

app = Flask(__name__)
app.config.from_object(config)

#Configurates server and database

app.config["MYSQL_HOST"] = MYSQL_HOST
app.config["MYSQL_USER"] = MYSQL_USER
app.config["MYSQL_PASSWORD"] = MYSQL_PASSWORD
app.config["MYSQL_DB"] = MYSQL_DB
app.config["SECRET_KEY"] = SECRET_KEY

#Connects server to database
try:
    mysql = MySQL(app)
except Exception as e:
    print("Error connecting to the database:", e)
    # Add better error handling here


from .socket import socketio
from .views import views
from .routes import routes

socketio.init_app(app, async_mode="threading")

app.register_blueprint(views, url_prefix='/')
app.register_blueprint(routes, url_prefix='/')

login_manager = LoginManager(app)
login_manager.login_view = "routes.login"

#Loads user from database into User object
@login_manager.user_loader
def loadUser(userID):

    conn = mysql.connection
    cursor = conn.cursor()

    sql = "SELECT * FROM users WHERE UserID = %s"
    cursor.execute(sql, (userID,))
    user = cursor.fetchone()

    cursor.close()

    if user:
        return User(*user)
    else:
        return None


mysql = MySQL()