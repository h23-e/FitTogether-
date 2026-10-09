from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from config import Config
from datetime import datetime, timedelta

# ==================== INITIALIZE EXTENSIONS ====================
db = SQLAlchemy()
login_manager = LoginManager()


# ==================== FOLLOW ASSOCIATION TABLE ====================
follows = db.Table('follows',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id'), nullable=False),
    db.Column('following_id', db.Integer, db.ForeignKey('users.id'), nullable=False),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


# ==================== USER MODEL ====================
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text, default='')
    profile_pic = db.Column(db.String(200), default='default.jpg')
    fitness_goal = db.Column(db.String(200), default='')
    height = db.Column(db.Float, default=0)
    weight = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)

    following = db.relationship(
        'User',
        secondary=follows,
        primaryjoin=(follows.c.follower_id == id),
        secondaryjoin=(follows.c.following_id == id),
        lazy='dynamic'
    )

    followers = db.relationship(
        'User',
        secondary=follows,
        primaryjoin=(follows.c.following_id == id),
        secondaryjoin=(follows.c.follower_id == id),
        lazy='dynamic',
        overlaps="following"
    )

    def follow(self, user):
        if not self.is_following(user):
            self.following.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        return self.following.filter(
            follows.c.following_id == user.id
        ).count() > 0

    def personal_records(self):
        """
        Return a list of dicts, one per exercise name, with the user's
        best weight and the date it was achieved.
        Sorted alphabetically by exercise name.
        """
        names = (
            db.session.query(Exercise.name)
            .join(Workout, Exercise.workout_id == Workout.id)
            .filter(Workout.user_id == self.id)
            .filter(Exercise.weight > 0)
            .distinct()
            .all()
        )

        records = []
        for (name,) in names:
            best = (
                Exercise.query
                .join(Workout, Exercise.workout_id == Workout.id)
                .filter(Workout.user_id == self.id)
                .filter(Exercise.name == name)
                .order_by(Exercise.weight.desc(), Workout.date.asc())
                .first()
            )
            if best:
                records.append({
                    'name': name,
                    'weight': best.weight,
                    'date': best.workout.date,
                })

        records.sort(key=lambda r: r['name'].lower())
        return records

    def weekly_volume(self, weeks=8):
        """
        Return a list of dicts with:
          - 'week_start': date string (e.g., 'Sep 25')
          - 'volume': total volume for that week in kg
        For the last `weeks` weeks.
        Week starts on Sunday (Kuwait convention).
        """
        today = datetime.utcnow().date()
        # Sunday is the first day of the week in Kuwait
        days_since_sunday = (today.weekday() + 1) % 7
        start_of_this_week = today - timedelta(days=days_since_sunday)

        result = []
        for i in range(weeks - 1, -1, -1):
            week_start = start_of_this_week - timedelta(weeks=i)
            week_end = week_start + timedelta(days=7)

            workouts = (
                Workout.query
                .filter(Workout.user_id == self.id)
                .filter(Workout.date >= datetime.combine(week_start, datetime.min.time()))
                .filter(Workout.date < datetime.combine(week_end, datetime.min.time()))
                .all()
            )

            total = 0
            for w in workouts:
                for ex in w.exercises:
                    if ex.sets and ex.reps and ex.weight:
                        total += ex.sets * ex.reps * ex.weight

            result.append({
                'week_start': week_start.strftime('%b %d'),
                'volume': round(total, 1),
            })

        return result

    def __repr__(self):
        return f'<User {self.username}>'


# ==================== WORKOUT MODEL (Session) ====================
class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text, default='')
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='workouts')
    exercises = db.relationship(
        'Exercise',
        backref='workout',
        cascade='all, delete-orphan'
    )

    def is_liked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return Like.query.filter_by(
            user_id=user.id,
            workout_id=self.id
        ).first() is not None

    def like_count(self):
        return Like.query.filter_by(workout_id=self.id).count()

    def __repr__(self):
        return f'<Workout {self.name} - {self.user.username}>'


# ==================== LIKE MODEL ====================
class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'workout_id', name='unique_user_workout_like'),
    )

    user = db.relationship('User', backref='likes')
    workout = db.relationship('Workout', backref=db.backref('likes', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<Like user={self.user_id} workout={self.workout_id}>'


# ==================== COMMENT MODEL ====================
class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='comments')
    workout = db.relationship('Workout', backref=db.backref('comments', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<Comment by user={self.user_id} on workout={self.workout_id}>'


# ==================== EXERCISE MODEL ====================
class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    sets = db.Column(db.Integer, default=0)
    reps = db.Column(db.Integer, default=0)
    weight = db.Column(db.Float, default=0)
    duration = db.Column(db.Integer, default=0)
    distance = db.Column(db.Float, default=0)
    notes = db.Column(db.Text, default='')

    def is_pr_for(self, user):
        """
        Return True if this exercise is the user's personal record
        (highest weight) for its exercise name.
        On ties, the earliest workout wins.
        """
        if not self.weight or not user:
            return False

        best = (
            Exercise.query
            .join(Workout, Exercise.workout_id == Workout.id)
            .filter(Workout.user_id == user.id)
            .filter(Exercise.name == self.name)
            .order_by(Exercise.weight.desc(), Workout.date.asc())
            .first()
        )

        if best is None:
            return False

        return best.id == self.id

    def __repr__(self):
        return f'<Exercise {self.name}>'


# ==================== USER LOADER ====================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ==================== CREATE APP ====================
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    from app.routes import main, auth, workouts, social

    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(workouts.bp)
    app.register_blueprint(social.bp)

    with app.app_context():
        db.create_all()

    return app