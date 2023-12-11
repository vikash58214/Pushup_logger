from datetime import datetime
import os
from flask import Flask,render_template,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user, UserMixin

app=Flask(__name__)
app.secret_key="343434oflksdjglkt4454l"
db=SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///pushup.db"
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20))
    email=db.Column(db.String(100),unique=True)
    password=db.Column(db.String(100))
    workouts=db.relationship('Workout',backref='author',lazy=True)
    workoutSplits=db.relationship('WorkoutSplit',backref='author',lazy=True)
with app.app_context():
    db.create_all()

class Workout(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    pushups=db.Column(db.Integer,nullable=False)
    date_posted=db.Column(db.DateTime,nullable=False,default=datetime.utcnow())
    comment=db.Column(db.Text,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
with app.app_context():
    db.create_all()

class WorkoutSplit(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    monday=db.Column(db.Text,nullable=False)
    tuesday=db.Column(db.Text,nullable=False)
    wednesday=db.Column(db.Text,nullable=False)
    thursday=db.Column(db.Text,nullable=False)
    friday=db.Column(db.Text,nullable=False)
    saturday=db.Column(db.Text,nullable=False)
    sunday=db.Column(db.Text,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template('index.html',account=current_user)

@app.route("/profile")
@login_required
def profile():

    return render_template('profile.html',name=current_user.name)

@app.route("/signup",methods=['GET','POST'])
def signup():
    if request.method=="POST":
        hashed_password=generate_password_hash(request.form["password"],method= 'pbkdf2:sha256',salt_length=8)
        user=User.query.filter_by(email=request.form["email"]).first()
        print(user)
        if user:
            print("already exist")
        new_user = User(
            name=request.form["name"],
            email=request.form["email"],
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()


    return render_template('signup.html')

@app.route("/login",methods=["GET","POST"])
def login():

    if request.method=='POST':
        email = request.form.get('email')
        password=request.form.get('password')


        result= db.session.execute(db.select(User).where(User.email == email))
        user=result.scalar()
        if not user:
            return redirect(url_for('login'))
        elif not check_password_hash(user.password,password):
            return redirect(url_for('login'))
        else:
            login_user(user,remember=True,duration=None)
            return redirect(url_for('home'))

    return render_template('login.html')
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('signup')

@app.route("/new",methods=['GET','POST'])
@login_required
def new_workout():
    if request.method=='POST':
        workout=Workout(
            pushups=request.form.get('pushups'),
            comment=request.form.get('comment'),
            author=current_user,
        )
        db.session.add(workout)
        db.session.commit()
        return redirect(url_for('all_workout'))



    return render_template('create_workout.html')
@app.route('/all')
@login_required
def all_workout():
    user=User.query.filter_by(email=current_user.email).first_or_404()
    workouts=user.workouts

    return render_template('all_workout.html',workouts=workouts)

@app.route('/workout/<int:workout_id>/update',methods=['GET','POST'])
def edit_workout(workout_id):
    workout=Workout.query.get_or_404(workout_id)
    if request.method=='POST':
        workout.pushups=request.form.get('pushups')
        workout.comment=request.form.get('comment')
        db.session.commit()
        return redirect(url_for('all_workout'))
    return render_template('edit_workout.html',workout=workout )


@app.route('/workout/<int:workout_id>/delete',methods=['GET','POST'])
@login_required
def delete_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    db.session.delete(workout)
    db.session.commit()
    return redirect(url_for('all_workout'))
@app.route('/new-workoutSplit',methods=['GET','POST'])
@login_required
def new_workout_split():
    if request.method=='POST':
        workoutSplit=WorkoutSplit(
            monday=request.form.get('monday'),
            tuesday = request.form.get('tuesday'),
            wednesday=request.form.get('wednesday'),
            thursday=request.form.get('thursday'),
            friday=request.form.get('friday'),
            saturday=request.form.get('saturday'),
            sunday=request.form.get('sunday'),
            author=current_user

        )
        db.session.add(workoutSplit)
        db.session.commit()

    return render_template('workoutSplit_form.html')

@app.route('/view-workoutsplit')
@login_required
def view_workoutsplit():
    user=User.query.filter_by(email=current_user.email).first_or_404()
    workoutsplit=user.workoutSplits
    return render_template('Workout_split.html',splits=workoutsplit)

if __name__=='__main__':
    app.run(debug=True)