from app import create_app, Exercise, db

app = create_app()
app.app_context().push()

fixed = 0
for ex in Exercise.query.all():
    if ex.weight and ex.weight > 0:
        if not ex.sets:
            ex.sets = 3
        if not ex.reps:
            ex.reps = 10
        fixed += 1

db.session.commit()
print(f"✅ Fixed {fixed} exercises (default 3 sets × 10 reps)")