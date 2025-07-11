from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy 
from flask_login import UserMixin, login_user, login_required, logout_user, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '7169dec5fb54a733a218324b16a6b3d3057ca42f56f67b27c15e9bab11ed41fc'

# Initialize
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Models
class GFGBLOG(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    author = db.Column(db.String(20))
    post_date = db.Column(db.DateTime)
    content = db.Column(db.Text)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

# Create DB
with app.app_context():
    db.create_all()

# Routes
@app.route("/")
def hello_world():
    article = GFGBLOG.query.order_by(GFGBLOG.post_date.desc()).all()
    return render_template('index.html', article=article)

@app.route('/profile')
@login_required
def profile():
    posts = GFGBLOG.query.filter_by(author=current_user.username).order_by(GFGBLOG.post_date.desc()).all()
    return render_template('profile.html', posts=posts)

@app.route('/addpost', methods=['POST', 'GET'])
@login_required
def addpost():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        post = GFGBLOG(title=title, author=current_user.username, content=content, post_date=datetime.now())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template('add.html')

@app.route('/update/<int:id>', methods=['POST', 'GET'])
@login_required
def update(id):
    post = GFGBLOG.query.get_or_404(id)

    if post.author != current_user.username:
        flash("You are not authorized to edit this post.", "danger")
        return redirect(url_for('profile'))

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        flash("Post updated successfully.", "success")
        return redirect(url_for('profile'))

    return render_template('update.html', edit=post)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = GFGBLOG.query.get_or_404(id)

    if post.author != current_user.username:
        flash("You are not authorized to delete this post.", "danger")
        return redirect(url_for('profile'))

    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.", "info")
    return redirect(url_for('profile'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password.', 'danger')
            return render_template('login.html')
        login_user(user)
        return redirect(url_for('hello_world'))
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists.', 'warning')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('hello_world'))

# Run App
if __name__ == '__main__':
    app.run(debug=True)
