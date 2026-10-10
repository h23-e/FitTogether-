from app import create_app, db, User

app = create_app()

with app.app_context():
    u1 = User.query.filter_by(username='user').first()
    u2 = User.query.filter_by(username='user2').first()

    print("user2 follows user?", u2.is_following(u1))
    print("user follows user2?", u1.is_following(u2))
    print("user's followers count:", u1.followers.count())
    print("user2's following count:", u2.following.count())