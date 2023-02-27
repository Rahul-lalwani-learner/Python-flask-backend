from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
app = Flask(__name__)
app.secret_key = 'my_super_secret_key_123'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Songfiles.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = 'static/music'

db = SQLAlchemy(app)


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    album = db.Column(db.String(100), nullable=False)

    def __repr__(self) -> str:
        return f"{self.id}- {self.title},{self.album},{self.artist}"


with app.app_context():
    db.create_all()


@app.route("/", methods=['GET', 'POST'])
def Main():
    allSong = Song.query.all()
    if request.method == "POST":
        Title = request.form['search']
        flag = Song.query.filter(Song.title.ilike(f"%{Title}%")).all()
        return render_template("index.html", allSong=allSong, flag=flag, Title=Title)
    else:
        return render_template("index.html", allSong=allSong)


@app.route("/upload", methods=['GET', 'POST'])
def upload_song():
    if request.method == "POST":
        Title = request.form['title']
        Artist = request.form['artist']
        Album = request.form['album']
        song_file = request.files['song']
        song_file.save(os.path.join(
            app.config['UPLOAD_FOLDER'], f"{Title}.mp3"))
        AddSong = Song(title=Title, artist=Artist, album=Album)
        db.session.add(AddSong)
        db.session.commit()
        if song_file:
            flash("Song uploaded successfully", "success")
    Allsongs = Song.query.all()
    print(Allsongs)
    return render_template("upload.html")


@app.route('/delete/<int:id>')
def delete(id):
    song = Song.query.filter_by(id=id).first()
    file_to_delete = os.path.join(
        app.config['UPLOAD_FOLDER'], f"{song.title}.mp3")
    try:
        os.remove(file_to_delete)
    except OSError:
        pass
    db.session.delete(song)
    db.session.commit()
    flash('Song Deleted Successfully!', 'success')

    return redirect("/")


@app.route("/play/<int:id>")
def play_song(id):
    song = Song.query.filter_by(id=id).first()
    return render_template("player.html", song=song)


@app.route("/view")
def view_songs():
    allSong = Song.query.all()
    return render_template("view.html", allSong=allSong)


if __name__ == "__main__":
    app.run(debug=True)
