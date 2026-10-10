from app import create_app, db, User, Workout, Exercise

app = create_app()

with app.app_context():
    u = User.query.first()
    if not u:
        print("No users in DB. Register one first via the app.")
    else:
        print(f"User: {u.username}")
        workouts = Workout.query.filter_by(user_id=u.id).all()
        if not workouts:
            print("No workouts for this user")
        else:
            for w in workouts:
                print(f"\nWorkout: {w.name} ({w.date.strftime('%Y-%m-%d')})")
                for ex in w.exercises:
                    pr = ex.is_pr_for(u)
                    marker = "🏆 PR" if pr else "   "
                    print(f"  {marker}  {ex.name}: {ex.weight} kg")