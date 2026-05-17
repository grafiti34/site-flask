from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)
app.secret_key = "change-moi"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

users = {}

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(20), unique=True, nullable=False)

    password_hash = db.Column(db.String(200), nullable=False)

    email = db.Column(db.String(120), default="")

    description = db.Column(db.String(300), default="")

    public = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        password_hash = generate_password_hash(password)

        nouvel_utilisateur = User(
            username=username,
            password_hash=password_hash
        )

        db.session.add(nouvel_utilisateur)
        db.session.commit()

        flash("Compte créé avec succès")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Identifiants invalides")
        return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("profil.html")

@app.route("/modifier", methods=["GET", "POST"])
@login_required
def modifier():

    if request.method == "POST":

        current_user.email = request.form["email"]
        current_user.description = request.form["description"]

        if "public" in request.form:
            current_user.public = True
        else:
            current_user.public = False

        return redirect(url_for("dashboard"))

    return render_template("modifier.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))
@app.route("/supprimer")
@login_required
def supprimer():

    users.pop(current_user.id)

    logout_user()

    return redirect(url_for("home"))
@app.route("/public/<id>")
def public(id):

    user = users.get(id)

    if user and user.public:
        return render_template("public.html", user=user)

    return "Profil privé ou inexistant"
if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)