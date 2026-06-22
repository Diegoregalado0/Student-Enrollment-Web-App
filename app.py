from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///enrollment.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(200))
    role = db.Column(db.String(20))  # 'student', 'teacher', 'admin'


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    time = db.Column(db.String(50))
    capacity = db.Column(db.Integer)


class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    grade = db.Column(db.Integer)


admin = Admin(app, name='UC Merced Admin')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Course, db.session))
admin.add_view(ModelView(Enrollment, db.session))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.role == 'student':
                return redirect(url_for('student_dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            else:
                return redirect('/admin')
        flash('Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/student')
@login_required
def student_dashboard():
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    my_courses = []
    for e in enrollments:
        course = Course.query.get(e.course_id)
        teacher = User.query.get(course.teacher_id)
        count = Enrollment.query.filter_by(course_id=course.id).count()
        my_courses.append({'course': course, 'teacher': teacher, 'count': count})
    return render_template('student_dashboard.html', my_courses=my_courses)


@app.route('/student/courses')
@login_required
def all_courses():
    courses = Course.query.all()
    enrolled_ids = []
    for e in Enrollment.query.filter_by(student_id=current_user.id).all():
        enrolled_ids.append(e.course_id)
    course_list = []
    for course in courses:
        teacher = User.query.get(course.teacher_id)
        count = Enrollment.query.filter_by(course_id=course.id).count()
        course_list.append({'course': course, 'teacher': teacher, 'count': count, 'enrolled': course.id in enrolled_ids})
    return render_template('all_courses.html', course_list=course_list)


@app.route('/student/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll(course_id):
    course = Course.query.get(course_id)
    count = Enrollment.query.filter_by(course_id=course_id).count()
    already = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
    if already:
        flash('You are already enrolled in this class')
    elif count >= course.capacity:
        flash('This class is full')
    else:
        enrollment = Enrollment(student_id=current_user.id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
        flash('Successfully enrolled!')
    return redirect(url_for('all_courses'))


@app.route('/teacher')
@login_required
def teacher_dashboard():
    courses = Course.query.filter_by(teacher_id=current_user.id).all()
    course_list = []
    for course in courses:
        count = Enrollment.query.filter_by(course_id=course.id).count()
        course_list.append({'course': course, 'count': count})
    return render_template('teacher_dashboard.html', course_list=course_list)


@app.route('/teacher/course/<int:course_id>')
@login_required
def teacher_course(course_id):
    course = Course.query.get(course_id)
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    students = []
    for e in enrollments:
        student = User.query.get(e.student_id)
        students.append({'enrollment': e, 'student': student})
    return render_template('teacher_course.html', course=course, students=students)


@app.route('/teacher/grade/<int:enrollment_id>', methods=['POST'])
@login_required
def edit_grade(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)
    enrollment.grade = int(request.form['grade'])
    db.session.commit()
    return redirect(url_for('teacher_course', course_id=enrollment.course_id))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
