from app import create_app, db, User, Workout, Exercise
from sqlalchemy import inspect

def init_database():
    app = create_app()

    with app.app_context():
        print("📊 Creating database tables...")
        db.create_all()
        print("✅ Tables created successfully!")

        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📋 Tables: {tables}")

        for table in tables:
            columns = [c['name'] for c in inspector.get_columns(table)]
            print(f"   {table}: {columns}")

if __name__ == '__main__':
    init_database()