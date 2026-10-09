from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db, Workout, Exercise, Like, Comment
from datetime import datetime

bp = Blueprint('workouts', __name__, url_prefix='/workouts')


# ==================== REDIRECT /workouts/ → /workouts/history ====================
@bp.route('/')
@login_required
def index():
    return redirect(url_for('workouts.history'))


# ==================== LOG WORKOUT (CREATE SESSION) ====================
@bp.route('/log', methods=['GET', 'POST'])
@login_required
def log_workout():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        duration = request.form.get('duration', 0)
        notes = request.form.get('notes', '')
        is_public = 'is_public' in request.form

        ex_names     = request.form.getlist('exercise_name[]')
        ex_sets      = request.form.getlist('exercise_sets[]')
        ex_reps      = request.form.getlist('exercise_reps[]')
        ex_weights   = request.form.getlist('exercise_weight[]')
        ex_durations = request.form.getlist('exercise_duration[]')
        ex_distances = request.form.getlist('exercise_distance[]')

        if not name:
            flash('Workout name is required!', 'danger')
            return render_template('workouts/log.html')

        if not ex_names or not any(n.strip() for n in ex_names):
            flash('Add at least one exercise!', 'danger')
            return render_template('workouts/log.html')

        workout = Workout(
            user_id=current_user.id,
            name=name,
            date=datetime.utcnow(),
            duration=int(duration) if duration else 0,
            notes=notes,
            is_public=is_public
        )
        db.session.add(workout)
        db.session.flush()

        # Create exercises
        new_exercises = []
        for i, ex_name in enumerate(ex_names):
            ex_name = ex_name.strip()
            if not ex_name:
                continue

            exercise = Exercise(
                workout_id=workout.id,
                name=ex_name,
                sets=int(ex_sets[i]) if i < len(ex_sets) and ex_sets[i] else 0,
                reps=int(ex_reps[i]) if i < len(ex_reps) and ex_reps[i] else 0,
                weight=float(ex_weights[i]) if i < len(ex_weights) and ex_weights[i] else 0,
                duration=int(ex_durations[i]) if i < len(ex_durations) and ex_durations[i] else 0,
                distance=float(ex_distances[i]) if i < len(ex_distances) and ex_distances[i] else 0,
            )
            db.session.add(exercise)
            new_exercises.append(exercise)

        db.session.flush()

        # Detect PRs
        pr_names = [ex.name for ex in new_exercises if ex.is_pr_for(current_user)]

        db.session.commit()

        # Flash message
        if pr_names:
            if len(pr_names) == 1:
                flash(f'🏆 New PR on {pr_names[0]}!', 'success')
            else:
                flash(f'🏆 {len(pr_names)} new PRs: {", ".join(pr_names)}', 'success')
        else:
            flash(f'💪 "{name}" logged with {len(new_exercises)} exercise(s)!', 'success')

        return redirect(url_for('workouts.history'))

    return render_template('workouts/log.html')


# ==================== VIEW WORKOUT HISTORY (READ ALL) ====================
@bp.route('/history')
@login_required
def history():
    workouts = Workout.query.filter_by(user_id=current_user.id)\
        .order_by(Workout.date.desc()).all()

    return render_template(
        'workouts/history.html',
        workouts=workouts,
        total_workouts=len(workouts)
    )


# ==================== VIEW SINGLE WORKOUT (READ ONE) ====================
@bp.route('/<int:workout_id>')
def view_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)

    is_owner = current_user.is_authenticated and current_user.id == workout.user_id

    if not is_owner and not workout.is_public:
        flash('This workout is private.', 'danger')
        return redirect(url_for('main.index'))

    comments = Comment.query.filter_by(workout_id=workout.id)\
        .order_by(Comment.created_at.desc()).all()

    return render_template(
        'workouts/view.html',
        workout=workout,
        is_owner=is_owner,
        comments=comments,
    )


# ==================== EDIT WORKOUT (UPDATE) ====================
@bp.route('/<int:workout_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    if workout.user_id != current_user.id:
        flash('You do not have permission to edit this workout.', 'danger')
        return redirect(url_for('workouts.history'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        duration = request.form.get('duration', 0)
        notes = request.form.get('notes', '')
        is_public = 'is_public' in request.form

        ex_names     = request.form.getlist('exercise_name[]')
        ex_sets      = request.form.getlist('exercise_sets[]')
        ex_reps      = request.form.getlist('exercise_reps[]')
        ex_weights   = request.form.getlist('exercise_weight[]')
        ex_durations = request.form.getlist('exercise_duration[]')
        ex_distances = request.form.getlist('exercise_distance[]')

        if not name:
            flash('Workout name is required!', 'danger')
            return redirect(url_for('workouts.edit_workout', workout_id=workout.id))

        if not ex_names or not any(n.strip() for n in ex_names):
            flash('Add at least one exercise!', 'danger')
            return redirect(url_for('workouts.edit_workout', workout_id=workout.id))

        workout.name = name
        workout.duration = int(duration) if duration else 0
        workout.notes = notes
        workout.is_public = is_public

        for old_exercise in workout.exercises:
            db.session.delete(old_exercise)

        db.session.flush()

        for i, ex_name in enumerate(ex_names):
            ex_name = ex_name.strip()
            if not ex_name:
                continue

            exercise = Exercise(
                workout_id=workout.id,
                name=ex_name,
                sets=int(ex_sets[i]) if i < len(ex_sets) and ex_sets[i] else 0,
                reps=int(ex_reps[i]) if i < len(ex_reps) and ex_reps[i] else 0,
                weight=float(ex_weights[i]) if i < len(ex_weights) and ex_weights[i] else 0,
                duration=int(ex_durations[i]) if i < len(ex_durations) and ex_durations[i] else 0,
                distance=float(ex_distances[i]) if i < len(ex_distances) and ex_distances[i] else 0,
            )
            db.session.add(exercise)

        db.session.commit()
        flash(f'✅ "{name}" updated successfully!', 'success')
        return redirect(url_for('workouts.view_workout', workout_id=workout.id))

    return render_template('workouts/edit.html', workout=workout)


# ==================== DELETE WORKOUT ====================
@bp.route('/<int:workout_id>/delete', methods=['POST'])
@login_required
def delete_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    if workout.user_id != current_user.id:
        flash('You do not have permission to delete this workout.', 'danger')
        return redirect(url_for('workouts.history'))

    name = workout.name
    db.session.delete(workout)
    db.session.commit()
    flash(f'🗑️ "{name}" deleted.', 'info')
    return redirect(url_for('workouts.history'))


# ==================== LIKE A WORKOUT ====================
@bp.route('/<int:workout_id>/like', methods=['POST'])
@login_required
def like_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)

    is_owner = current_user.id == workout.user_id
    if not is_owner and not workout.is_public:
        flash('You cannot like a private workout.', 'danger')
        return redirect(url_for('main.index'))

    existing = Like.query.filter_by(
        user_id=current_user.id,
        workout_id=workout.id
    ).first()

    if not existing:
        like = Like(user_id=current_user.id, workout_id=workout.id)
        db.session.add(like)
        db.session.commit()

    next_url = request.form.get('next') or request.referrer or url_for('workouts.view_workout', workout_id=workout.id)
    return redirect(next_url)


# ==================== UNLIKE A WORKOUT ====================
@bp.route('/<int:workout_id>/unlike', methods=['POST'])
@login_required
def unlike_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)

    existing = Like.query.filter_by(
        user_id=current_user.id,
        workout_id=workout.id
    ).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()

    next_url = request.form.get('next') or request.referrer or url_for('workouts.view_workout', workout_id=workout.id)
    return redirect(next_url)


# ==================== POST A COMMENT ====================
@bp.route('/<int:workout_id>/comment', methods=['POST'])
@login_required
def add_comment(workout_id):
    workout = Workout.query.get_or_404(workout_id)

    is_owner = current_user.id == workout.user_id
    if not is_owner and not workout.is_public:
        flash('You cannot comment on a private workout.', 'danger')
        return redirect(url_for('main.index'))

    content = request.form.get('content', '').strip()

    if not content:
        flash('Comment cannot be empty.', 'warning')
        return redirect(url_for('workouts.view_workout', workout_id=workout.id))

    comment = Comment(
        user_id=current_user.id,
        workout_id=workout.id,
        content=content,
    )
    db.session.add(comment)
    db.session.commit()

    flash('Comment posted.', 'success')
    return redirect(url_for('workouts.view_workout', workout_id=workout.id))