import os
from flask import Flask
from flask import redirect
from flask import request
from flask import url_for
from flask import session
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "movies.db"))

app = Flask(__name__)
app.secret_key = "123"

# app.config['SQLALCHEMY_DATABASE_URI'] = database_file
# app.config['DATABASE_URL'] = database_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '123'

ENV = 'pro'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = database_file
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://qmcqivjqsmyrbx:24b7d20d1b3e270c938ddf7297a277c3a91fc12d1e445964194d026895e1577f@ec2-54-242-120-138.compute-1.amazonaws.com:5432/dcfm38290mgo56'

db = SQLAlchemy(app)

class Movie(db.Model):
    title = db.Column(db.String(80), nullable=False, primary_key=True)
    genre = db.Column(db.String(80), nullable=False)
    human = db.Column(db.String(80), nullable=False)

    def __init__(self, title, genre, human):
        self.title = title
        self.genre = genre
        self.human = human
    
    def __repr__(self):
        return f"{self.title},{self.genre},{self.human}"

@app.route("/", methods=["GET", "POST"])
def default():
    return redirect(url_for("index"))

@app.route("/add.html", methods=["GET", "POST"])
def add():
    if request.form:
        print(request.form["human"])
        try:
            exists = bool(Movie.query.filter_by(title=request.form["title"]).first())
            if exists:
                error = "Movie exists!"
                return render_template("add.html", error=error)
            else:
                movie = Movie(title=request.form["title"], \
                            genre=request.form["genre"], \
                            human=request.form["human"])
                db.session.add(movie)
                db.session.commit()
                return redirect(url_for("index"))
        except Exception as e:
            print("Failed to add movie"+str(e))
    return render_template("add.html")

@app.route("/index.html", methods=["GET","POST"])
def index():
    movies = []
    try: 
        movies = Movie.query.all()
    except Exception as e:
        print("Failed to fetch books"+str(e))
    return render_template("index.html", movies = movies)

@app.route("/admin.html", methods=["GET","POST"])
def admin():
    error = ""
    if request.form:
        print(request.form["user"],request.form["pass"],"is the data")
        if(request.form["user"]=="admin" and \
           request.form["pass"]=="1234"):
            print("Access granted!")
            session['logged_in'] = True
            return redirect(url_for("table"))
        else:
            error = "Invalid login!"
            return render_template("admin.html", error = error)
    return render_template("admin.html")
    
@app.route("/table.html", methods=["GET", "POST"])
def table():
    if session['logged_in'] != True:
        return redirect(url_for("admin"))
    else:
        movies = []
        try: 
            movies = Movie.query.all()
        except Exception as e:
            print("Failed to fetch books"+str(e))
        return render_template("table.html", movies = movies)
        

@app.route("/delete", methods=["GET", "POST"])
def delete():
    try:
        if request.form:
            title = request.form["title"]
            print(title)
            movie = Movie.query.filter_by(title=title).one()
            db.session.delete(movie)
            db.session.commit()
            print("Deleted!")
    except Exception as e:
        print(e)
    return redirect(url_for("table"))

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session['logged_in'] = False
    return redirect(url_for("index"))

@app.errorhandler(404)  
def notFound(*args):
    return render_template("404.html")

if __name__=="main":
    db.create_all()
    app.run()