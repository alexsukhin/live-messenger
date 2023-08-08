from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager
from .models import User
from . import config

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'Xn828h!#Wg#MpYJg'
    app.config['MYSQL_DB'] = 'messenger'  

    try:
        mysql = MySQL(app)
    except Exception as e:
        print("Error connecting to the database:", e)
        #create better error handling

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'

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


    return app

mysql = MySQL()