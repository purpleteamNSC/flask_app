from flask import request, Flask, render_template, redirect   # Import these flask functions
import sqlite3
import os
from flask.helpers import flash, url_for

if  "mydb.db" not in os.listdir():
        conn = sqlite3.connect("mydb.db")
        db = conn.cursor()
        db.execute("CREATE TABLE posts (title TEXT, content TEXT, date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        conn.commit()
        conn.close()

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret key"

@app.route("/")
def main():
        return render_template("./site/index.html")

@app.route('/create', methods=["GET", "POST"]) # Allowing Post requests
def create_post():
    if request.method.upper() == "POST":
        title = request.form.get("title")
        content = request.form.get("content")

        if title == None or content == None or title.strip() == "" or content.strip() == "":
            # flashes a message to tell the user to fill all the fields
            flash("Please fill all the fields")
            return render_template("create.html")

        conn = sqlite3.connect("mydb.db")
        cur = conn.cursor()
        # Adding the post to the database
        cur.execute("INSERT INTO posts (title, content) VALUES(?, ?)", (title, content))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("display_posts")) # redirect user
    return render_template("create.html")

@app.route("/posts")
def display_posts():
        conn = sqlite3.connect("mydb.db")
        cur = conn.cursor()
        cur.execute("SELECT *, rowid FROM posts") # Getting all the posts from the sqlite3 database
        posts = cur.fetchall() # fetching all the posts from the database and assigning them to the posts variable
        cur.close()
        conn.close()
        return render_template("./site/posts.html", posts=posts)  # Passing the posts variable ( which is a list ) to the front-end so that jinja2 can loop over it and display all the posts

@app.route("/posts/<int:post_id>")
def display_post(post_id):
    conn = sqlite3.connect("mydb.db")
    cur = conn.cursor()
    post = cur.execute("SELECT * FROM posts WHERE rowid = ?", (str(post_id))).fetchone() # Notice the fetchone() fucntion

    return render_template("./site/post.html", post=post, post_id=post_id)

@app.route("/posts/<int:post_id>/delete")
def delete_post(post_id):
    conn = sqlite3.connect("mydb.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM posts WHERE rowid = ?", (str(post_id)))
    conn.commit()

    return redirect(url_for("./site/display_posts"))

@app.route("/posts/<int:post_id>/edit", methods=["POST", "GET"])
def edit_post(post_id):
    conn = sqlite3.connect("mydb.db")
    cur = conn.cursor()
    post = cur.execute("SELECT * FROM posts WHERE rowid = ?", (str(post_id))).fetchone()

    if request.method.upper() == "POST":
        title = request.form.get("title")
        content = request.form.get("content")

        if title == None or content == None or title.strip() == "" or content.strip() == "":
            flash("Please fill all the fields")
            return render_template("./site/edit.html", post=post)

        cur.execute("UPDATE posts SET title = ?, content = ? WHERE rowid = ?", (title, content, post_id))
        conn.commit()

        return redirect(url_for("display_posts"))

    return render_template("./site/edit.html", post=post)

#admin
@app.route("/admin")
def admin():
    return render_template("./admin/index.html")

if __name__ == "__main__":
    app.run(debug=True)