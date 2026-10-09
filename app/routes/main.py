from flask import Blueprint, render_template
from flask_login import current_user
from app import db, Workout
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    # --- If not logged in, show the landing page ---
    if not current_user.is_authenticated:
        return render_template('index.html')

    # --- Logged in: gather dashboard data ---

    # 1. All of the user's workouts (newest first)
    user_workouts = Workout.query.filter_by(user_id=current_user.id)\
        .order_by(Workout.date.desc()).all()

    # 2. Total volume across all user workouts
    total_volume = 0
    for w in user_workouts:
        for ex in w.exercises:
            if ex.sets and ex.reps and ex.weight:
                total_volume += ex.sets * ex.reps * ex.weight

    # 3. Workouts in the last 7 days
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    week_workouts = [w for w in user_workouts if w.date >= one_week_ago]

    # 4. The user's 3 most recent workouts
    recent_workouts = user_workouts[:3]

    # 5. Community feed: prioritize people you follow, then fill with others
    followed_ids = [u.id for u in current_user.following.all()]

    community_workouts = []

    # First: pull up to 3 public workouts from people you follow
    if followed_ids:
        followed_workouts = (
            Workout.query
            .filter(Workout.is_public == True)
            .filter(Workout.user_id.in_(followed_ids))
            .order_by(Workout.date.desc())
            .limit(3)
            .all()
        )
        community_workouts.extend(followed_workouts)

    # Then: if we don't have 3 yet, fill with workouts from anyone else
    if len(community_workouts) < 3:
        needed = 3 - len(community_workouts)
        excluded_ids = followed_ids + [current_user.id]

        filler_workouts = (
            Workout.query
            .filter(Workout.is_public == True)
            .filter(~Workout.user_id.in_(excluded_ids))
            .order_by(Workout.date.desc())
            .limit(needed)
            .all()
        )
        community_workouts.extend(filler_workouts)

    return render_template(
        'index.html',
        total_workouts=len(user_workouts),
        total_volume=round(total_volume, 1),
        week_workouts=len(week_workouts),
        recent_workouts=recent_workouts,
        community_workouts=community_workouts,
        follower_count=current_user.followers.count(),
        following_count=current_user.following.count(),
    )