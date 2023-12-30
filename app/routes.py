from flask import Blueprint, redirect, render_template, request, flash, jsonify, session
from flask_login import login_user, login_required, logout_user, current_user
from . import mysql
from .queries import *
from .users import User
from .encryption import encryptionManager


class RoutesManager():
    def __init__(self, encryptionManager):
        self.encryptionManager = encryptionManager

    def userExists(self, username):
        if getUser(username):
            flash("Username already exists", category="error")
            return True
        return False

    def validateLength(self, length, maxLength, errorMessage):
        if len(length) > maxLength:
            flash(error_message, category="error")
            return True
        return False

    def signup(self, firstName, lastName, username, password):

        existingUser = getUser(username)

        #If any existing checks return true, flashes message and returns out of signup function
        if (
            self.userExists(username) or
            self.validateLength(username, 15, "Username must be 15 characters or less.") or
            self.validateLength(password, 50, "Password must be 50 characters or less.") or
            self.validateLength(firstName, 25, "First name must be 25 characters or less.") or
            self.validateLength(lastName, 25, "Last name must be 25 characters or less.")
        ):
            return

        hashedPassword = self.encryptionManager.hashPassword(password)

        #Inserts user into user database
        insertUser(username, hashedPassword, firstName, lastName)
        
        #Logs user into account and redirects user to dashboard page if user inserted into database
        newUser = getUser(username)

        if newUser:
            objUser = User(*newUser)
            login_user(objUser)
            flash("Account created!", category="success")
            return True
        else:
            flash("Error creating account.", category="error")
            return False

    def login(self, username, password):

            #Hashes password inputted
            loginHashedPassword = self.encryptionManager.hashPassword(password)
            user = getUser(username)

            if user is None:
                flash("Username not found.", category="error")
            #Checks if inputted password doesn't equal to passsword stored in user database
            elif loginHashedPassword != user[2]:
                flash("Incorrect password.", category="error")
            #Logs user into account and redirects user to dashboard page
            else:
                objUser = User(*user)
                login_user(objUser)
                flash("Logged in successfully!", category="success")
                return True
            return False

    def logout(self):
        logout_user()
        return True

    def addUser(self, username):
        recipient = getUser(username)
        senderID = current_user.id

        #Prerequisite checks for validation for adding a new user
        if recipient is None:
            flash("Username not found.", category="error")
        else:
            #Gets the recipientID from 'recipient' user object
            recipientID = recipient[0]

            if connectionExists(senderID, recipientID) == True:
                flash("User already exists in your chat list.", category="error")
            elif senderID == recipientID:
                flash("You cannot add yourself.", category="error")
            #Inserts new user into connections database
            else:
                insertConnection(senderID, recipientID)
                flash("Successfully added user!", category="success")
                return True
        return False

    def changeName(self, firstName, lastName):
        if (
            self.validateLength(firstName, 25, "First name must be 25 characters or less.") or
            self.validateLength(lastName, 25, "Last name must be 25 characters or less.")
        ):
            return

        updateName(current_user.id, firstName, lastName)
        flash("Successfully updated user's name!", category="success")
        return True

    def changeUsername(self, username):
        existingUser = getUser(username)

        if (
            self.userExists(username) or
            self.validateLength(username, 15, "Last name must be 25 characters or less.")
        ):
            return

        updateUsername(current_user.id, username)
        flash("Successfully updated username!", category="success")
        return True

    def changePassword(self, currentPassword, newPassword):

        currentHashedPassword = self.encryptionManager.hashPassword(currentPassword)

        if currentHashedPassword != current_user.password:
            flash("Your current password is incorrect.", category="error")
        elif len(newPassword) > 50:
            flash("Password must be 50 characters or less.", category="error")
        else:
            updatePassword(current_user.id, newPassword)
            flash("Successfully updated password!", category="success")
            return True
        
        return False

class RoutesBlueprint(Blueprint):
    def __init__(self, name, importName, routesManager):
        super().__init__(name, importName)
        self.routesManager = routesManager
        self.add_url_rule("/", "default", self.default)
        self.add_url_rule("/signup", "sign_up", self.signup, methods=["GET", "POST"])
        self.add_url_rule("/login", "login", self.login, methods=["GET", "POST"])
        self.add_url_rule("/logout", "logout", self.logout)
        self.add_url_rule("/dashboard", "dashboard", self.dashboard, methods=["GET", "POST"])
        self.add_url_rule("/profile", "profile", self.profile, methods=["GET", "POST"])

    def default(self):
        return redirect("/login")

    def signup(self):
        if request.method == "POST":
            firstName = request.form.get("firstName")
            lastName = request.form.get("lastName")
            username = request.form.get("username")
            password = request.form.get("password")

            if self.routesManager.signup(firstName, lastName, username, password):
                return redirect("/dashboard")

        return render_template("signup.html", user=current_user)


    def login(self):
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            if self.routesManager.login(username, password):
                return redirect("/dashboard")

        return render_template("login.html", user=current_user)

    @login_required
    def logout(self):
        if self.routesManager.logout():
            return redirect("/login")

    @login_required
    def dashboard(self):
        if request.method == "POST":
            if "username" in request.form:
                username = request.form.get("username")
                self.routesManager.addUser(username)
        
        return render_template("dashboard.html", user=current_user)

    @login_required
    def profile(self):
        if request.method == "POST":
            if "changeName" in request.form:
                firstName = request.form.get("firstName")
                lastName = request.form.get("lastName")

                if self.routesManager.changeName(firstName, lastName):
                    return redirect("/profile")

            elif "changeUsername" in request.form:
                username = request.form.get("username")

                if self.routesManager.changeUsername(username):
                    return redirect("/profile")


            elif "changePassword" in request.form:
                currentPassword = request.form.get("currentPassword")
                newPassword = request.form.get("newPassword")

                if self.routesManager.changePassword(password):
                    return redirect("/profile")

        return render_template("profile.html", user=current_user)

routesManager = RoutesManager(encryptionManager)
routes = RoutesBlueprint("routes", __name__, routesManager)