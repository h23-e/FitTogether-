from flask import Blueprint, render_template, abort, request, flash, redirect, url_for
from flask_login import current_user, login_required
from app import db, User, Workout, Exercise
from sqlalchemy import func

bp = Blueprint('social', __name__)


# ==================== PUBLIC PROFILE PAGE ====================
@bp.route('/u/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)

    is_owner = current_user.is_authenticated and current_user.id == user.id

    query = Workout.query.filter_by(user_id=user.id)
    if not is_owner:
        query = query.filter_by(is_public=True)
    workouts = query.order_by(Workout.date.desc()).all()

    total_workouts = len(workouts)
    total_volume = 0
    for w in workouts:
        for ex in w.exercises:
            if ex.sets and ex.reps and ex.weight:
                total_volume += ex.sets * ex.reps * ex.weight

    fav_exercise = None
    if workouts:
        workout_ids = [w.id for w in workouts]
        fav = (
            db.session.query(Exercise.name, func.count(Exercise.id).label('count'))
            .filter(Exercise.workout_id.in_(workout_ids))
            .group_by(Exercise.name)
            .order_by(func.count(Exercise.id).desc())
            .first()
        )
        if fav:
            fav_exercise = fav[0]

    recent_workouts = workouts[:10]

    is_following = False
    if current_user.is_authenticated and not is_owner:
        is_following = current_user.is_following(user)

    personal_records = []
    if is_owner:
        personal_records = user.personal_records()

    weekly_volume = []
    if is_owner:
        weekly_volume = user.weekly_volume(weeks=8)

    return render_template(
        'social/profile.html',
        user=user,
        is_owner=is_owner,
        workouts=recent_workouts,
        total_workouts=total_workouts,
        total_volume=round(total_volume, 1),
        fav_exercise=fav_exercise,
        is_following=is_following,
        follower_count=user.followers.count(),
        following_count=user.following.count(),
        personal_records=personal_records,
        weekly_volume=weekly_volume,
    )


# ==================== USER DISCOVERY PAGE ====================
@bp.route('/users')
@login_required
def users():
    search_query = request.args.get('q', '').strip()

    query = User.query
    if search_query:
        query = query.filter(User.username.ilike(f'%{search_query}%'))

    all_users = query.order_by(User.username.asc()).all()

    user_data = []
    for u in all_users:
        public_count = Workout.query.filter_by(user_id=u.id, is_public=True).count()
        user_data.append({
            'user': u,
            'public_workouts': public_count,
            'is_following': current_user.is_following(u),
        })

    return render_template(
        'social/users.html',
        user_data=user_data,
        search_query=search_query,
        total_users=len(user_data),
    )


# ==================== FOLLOW A USER ====================
@bp.route('/u/<username>/follow', methods=['POST'])
@login_required
def follow(username):
    target = User.query.filter_by(username=username).first()
    if not target:
        abort(404)

    if target.id == current_user.id:
        flash("You can't follow yourself.", 'warning')
        return redirect(url_for('social.profile', username=username))

    if not current_user.is_following(target):
        current_user.follow(target)
        db.session.commit()

    flash(f'You are now following {target.username}.', 'success')

    next_url = request.form.get('next') or request.referrer or url_for('social.profile', username=username)
    return redirect(next_url)


# ==================== UNFOLLOW A USER ====================
@bp.route('/u/<username>/unfollow', methods=['POST'])
@login_required
def unfollow(username):
    target = User.query.filter_by(username=username).first()
    if not target:
        abort(404)

    if current_user.is_following(target):
        current_user.unfollow(target)
        db.session.commit()
        flash(f'You unfollowed {target.username}.', 'info')

    next_url = request.form.get('next') or request.referrer or url_for('social.profile', username=username)
    return redirect(next_url)


# ==================== FOLLOWING PAGE ====================
@bp.route('/u/<username>/following')
@login_required
def following(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)

    users = user.following.order_by(User.username.asc()).all()

    return render_template(
        'social/follow_list.html',
        profile_user=user,
        users=users,
        list_type='following',
        total=len(users),
    )


# ==================== FOLLOWERS PAGE ====================
@bp.route('/u/<username>/followers')
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)

    users = user.followers.order_by(User.username.asc()).all()

    return render_template(
        'social/follow_list.html',
        profile_user=user,
        users=users,
        list_type='followers',
        total=len(users),
    )