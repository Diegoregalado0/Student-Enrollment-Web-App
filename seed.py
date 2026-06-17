from app import app, db, User, Course, Enrollment
from werkzeug.security import generate_password_hash

def make_hash(password):
    return generate_password_hash(password, method='pbkdf2:sha256')

with app.app_context():
    db.drop_all()
    db.create_all()

    # create users
    admin = User(name='Admin User', username='admin', role='admin', password_hash=make_hash('password123'))
    chuck = User(name='Chuck Norris', username='cnorris', role='student', password_hash=make_hash('password123'))
    mindy = User(name='Mindy White', username='mwhite', role='student', password_hash=make_hash('password123'))
    s3 = User(name='Jake Torres', username='jtorres', role='student', password_hash=make_hash('password123'))
    s4 = User(name='Aisha Patel', username='apatel', role='student', password_hash=make_hash('password123'))
    s5 = User(name='Leo Kim', username='lkim', role='student', password_hash=make_hash('password123'))
    s6 = User(name='Sara Chen', username='schen', role='student', password_hash=make_hash('password123'))
    s7 = User(name='Marcus Webb', username='mwebb', role='student', password_hash=make_hash('password123'))
    s8 = User(name='Nina Brooks', username='nbrooks', role='student', password_hash=make_hash('password123'))
    susan = User(name='Susan Walker', username='swalker', role='teacher', password_hash=make_hash('password123'))
    ammon = User(name='Ammon Hepworth', username='ahepworth', role='teacher', password_hash=make_hash('password123'))
    ralph = User(name='Ralph Jenkins', username='rjenkins', role='teacher', password_hash=make_hash('password123'))

    db.session.add_all([admin, chuck, mindy, s3, s4, s5, s6, s7, s8, susan, ammon, ralph])
    db.session.commit()

    # create courses
    physics = Course(name='Physics 121', teacher_id=susan.id, time='TR 11:00-11:50 AM', capacity=10)
    cs106 = Course(name='CS 106', teacher_id=ammon.id, time='MWF 2:00-2:50 PM', capacity=10)
    math = Course(name='Math 101', teacher_id=ralph.id, time='MWF 10:00-10:50 AM', capacity=8)
    cs162 = Course(name='CS 162', teacher_id=ammon.id, time='TR 3:00-3:50 PM', capacity=4)

    db.session.add_all([physics, cs106, math, cs162])
    db.session.commit()

    # create enrollments
    enrollments = [
        Enrollment(student_id=chuck.id, course_id=physics.id, grade=92),
        Enrollment(student_id=mindy.id, course_id=physics.id, grade=78),
        Enrollment(student_id=s3.id, course_id=physics.id),
        Enrollment(student_id=s4.id, course_id=physics.id),
        Enrollment(student_id=s5.id, course_id=physics.id),
        Enrollment(student_id=chuck.id, course_id=cs106.id, grade=95),
        Enrollment(student_id=s3.id, course_id=cs106.id, grade=76),
        Enrollment(student_id=s6.id, course_id=cs106.id),
        Enrollment(student_id=s7.id, course_id=cs106.id),
        Enrollment(student_id=mindy.id, course_id=math.id),
        Enrollment(student_id=s4.id, course_id=math.id),
        Enrollment(student_id=s5.id, course_id=math.id),
        Enrollment(student_id=s6.id, course_id=math.id),
        Enrollment(student_id=s4.id, course_id=cs162.id),
        Enrollment(student_id=s5.id, course_id=cs162.id),
        Enrollment(student_id=s7.id, course_id=cs162.id),
        Enrollment(student_id=s8.id, course_id=cs162.id),
    ]

    db.session.add_all(enrollments)
    db.session.commit()

    print("Done! All accounts use password: password123")
