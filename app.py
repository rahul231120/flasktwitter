from flask import Flask, render_template, flash, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from forms import RegistrationForm, LoginForm, TweetForm
from database import db
from models import Tweet,User,Retweet,Like
from flask import request, jsonify
from flask_migrate import Migrate
from models import Follow

# ...



print("Creating app instance")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
from flask_migrate import Migrate

# ...

migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
db.init_app(app)
print("db initialized with app")



# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(20), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(60), nullable=False)
#     tweets = db.relationship('Tweet', backref='author', lazy=True)

# class Tweet(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.Text, nullable=False)
#     date_posted = db.Column(db.DateTime, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route("/")
@app.route("/home")
@login_required
def home():
    tweets = Tweet.query.all()
    return render_template('home.html', title='Home', tweets=tweets)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html', title='Profile')

@app.route("/post", methods=['GET', 'POST'])
@login_required
def post():
    form = TweetForm()
    if form.validate_on_submit():
        tweet = Tweet(content=form.content.data, author=current_user, date_posted=db.func.current_timestamp())
        db.session.add(tweet)
        db.session.commit()
        flash('Your tweet has been posted!', 'success')
        return redirect(url_for('home'))
    return render_template('post.html', title='Post', form=form)

@app.route("/timeline/<username>")
@login_required
def timeline(username):
    user = User.query.filter_by(username=username).first_or_404()
    tweets = Tweet.query.filter_by(author=user).all()
    return render_template('timeline.html', title=f"{username}'s Timeline", tweets=tweets)
@app.route("/like/<int:tweet_id>", methods=['POST'])
@login_required
def like_tweet(tweet_id):
    tweet = Tweet.query.get_or_404(tweet_id)

    # Check if the user has already liked the tweet
    if current_user in tweet.likes:
        return jsonify({'message': 'You already liked this tweet!'}), 400

    like = Like(user=current_user, tweet=tweet)
    db.session.add(like)
    db.session.commit()

    return jsonify({'message': 'Tweet liked successfully'}), 200

# New route to handle retweet requests
@app.route("/retweet/<int:tweet_id>", methods=['POST'])
@login_required
def retweet(tweet_id):
    tweet = Tweet.query.get_or_404(tweet_id)

    # Check if the user has already retweeted the tweet
    if current_user in tweet.retweets:
        return jsonify({'message': 'You already retweeted this tweet!'}), 400

    retweet = Retweet(user=current_user, tweet=tweet)
    db.session.add(retweet)
    db.session.commit()
    return jsonify({'message': 'Tweet retweeted successfully'}), 200

@app.route("/profile/<username>")
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    tweets = Tweet.query.filter_by(author=user).all()
    return render_template('profile.html', title=f"{username}'s Profile", user=user, tweets=tweets)

@app.route("/follow/<int:user_id>", methods=['POST'])
@login_required
def follow_user(user_id):
    if user_id == current_user.id:
        return jsonify({'message': 'You cannot follow yourself!'}), 400

    user_to_follow = User.query.get_or_404(user_id)

    if current_user.is_following(user_to_follow):
        return jsonify({'message': 'You are already following this user!'}), 400

    follow = Follow(follower_id=current_user.id, following_id=user_id)
    db.session.add(follow)
    db.session.commit()

    return jsonify({'message': 'You are now following this user!'}), 200

@app.route("/unfollow/<int:user_id>", methods=['POST'])
@login_required
def unfollow_user(user_id):
    user_to_unfollow = User.query.get_or_404(user_id)

    follow = Follow.query.filter_by(follower_id=current_user.id, following_id=user_id).first()

    if not follow:
        return jsonify({'message': 'You are not following this user!'}), 400

    db.session.delete(follow)
    db.session.commit()

    return jsonify({'message': 'You have unfollowed this user!'}), 200

@app.route("/followers/<int:user_id>")
@login_required
def followers(user_id):
    user = User.query.get_or_404(user_id)
    followers = user.followers.all()
    return render_template('followers.html', title=f"{user.username}'s Followers", user=user, followers=followers)

@app.route("/following/<int:user_id>")
@login_required
def following(user_id):
    user = User.query.get_or_404(user_id)
    following = user.following.all()
    return render_template('following.html', title=f"{user.username}'s Following", user=user, following=following)

    
if __name__ == "__main__":
    app.run(debug=True)