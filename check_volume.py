from app import create_app, User, Workout, Exercise, db

app = create_app()
app.app_context().push()

u = User.query.first()
print(f"User: {u.username}\n")

for w in Workout.query.filter_by(user_id=u.id).all():
    print(f"Workout: {w.name}")
    for ex in w.exercises:
        counted = "✅ counted" if (ex.sets and ex.reps and ex.weight) else "❌ NOT counted"
        print(f"  {ex.name}: sets={ex.sets}, reps={ex.reps}, weight={ex.weight}  {counted}")
    print()