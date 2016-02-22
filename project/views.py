#import sqlite3
from functools import wraps
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, \
    session, url_for
from forms import AddTaskForm, LoginForm, RegisterForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

# Config
app = Flask(__name__)
app.config.from_object('_config')
db = SQLAlchemy(app)

# *** I don't like this - line has to be after db =SQL.. otherwise fails!!!
from models import Task, User


# helper functions
# def connect_db():
#   return sqlite3.connect(app.config['DATABASE_PATH'])

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" %(getattr(form, field).label.text, error), 'error')


def open_tasks():
    return db.session.query(Task).filter_by(status='1').order_by(Task.due_date.asc())


def closed_tasks():
    return db.session.query(Task).filter_by(status='0').order_by(Task.due_date.asc())


@app.route('/register/', methods=['GET', 'POST'])
def register():
    error = None
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            print "processes validatied on submit"
            new_user = User(
                form.name.data,
                form.email.data,
                form.password.data,
            )
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('thanks for registering. Now log in')
                return redirect(url_for('login'))
            except IntegrityError:
                error = "User already exists with that name"
                return render_template('register.html', form=form, error=error)
    return render_template('register.html', form=form, error=error)


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first')
            return redirect(url_for('login'))
    return wrap


# route handlers
@app.route('/logout/')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('role', None)
    flash('Goodbye')
    return redirect(url_for('login'))


# def login():
#     error = None
#     if request.method == 'POST':
#         if request.form['username'] != app.config['USERNAME'] \
#             or request.form['password'] != app.config['PASSWORD']:
#             error = 'Invalid credentials. Try again'
#             return render_template('login.html', error=error)
#         else:
#             session['logged_in'] = True
#             flash('Welcome')
#             return redirect(url_for('tasks'))
#     return render_template('login.html')
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(name=request.form['name']).first()
            if user is not None and user.password == request.form['password']:
                session['logged_in'] = True
                session['user_id'] = user.id
                session['role'] = user.role
                flash('Welcome')
                return redirect(url_for('tasks'))
            else:
                error = 'Invalid login credentials'
        else:
            error = 'Both fields are required'
    return render_template('login.html', form=form, error=error)


@app.route('/tasks/')
@login_required
def tasks():
    # g.db = connect_db()
    # cur = g.db.execute(""" select name, due_date, priority, task_id
    #                     from tasks where status = 1""")
    # open_tasks = [dict(name=row[0], due_date=row[1],
    #              priority=row[2], task_id=row[3]) for row in cur.fetchall()]
    # cur = g.db.execute("""select name, due_date, priority, task_id
    #                     from tasks where status=0""")
    # closed_tasks = [dict(name=row[0], due_date=row[1],
    #                 priority=row[2], task_id=row[3]) for row in cur.fetchall()]
    # g.db.close()

    # this is the object oriented way way with an ORM
    
    # open_tasks = db.session.query(Task)\
    #     .filter_by(status='1').order_by(Task.due_date.asc())
    # closed_tasks = db.session.query(Task)\
    #     .filter_by(status='0').order_by(Task.due_date.asc())

    return render_template(
        'tasks.html',
        form=AddTaskForm(request.form),
        open_tasks=open_tasks(),
        closed_tasks=closed_tasks()
    )


# add new tasks
@app.route('/add/', methods=['GET', 'POST'])
@login_required
def new_task():
    # g.db = connect_db()
    # name = request.form['name']
    # date = request.form['due_date']
    # priority = request.form['priority']
    # if not name or not date or not priority:
    #     flash('all fields are required. Try again')
    #     return redirect(url_for('tasks'))
    # else:
    #     g.db.execute("""insert into tasks (name, due_date, priority, status)
    #                  values(?, ?, ?, 1)""", [
    #                  request.form['name'],
    #                  request.form['due_date'],
    #                  request.form['priority']
    #                  ]
    #                  )
    #     g.db.commit()
    #     g.db.close()
    #     flash('New entry successfully posted.')
    #     return redirect(url_for('tasks'))
    error = None
    form = AddTaskForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_task = Task(
                form.name.data,
                form.due_date.data,
                form.priority.data,
                datetime.utcnow(),
                '1',
                session['user_id']
            )
            db.session.add(new_task)
            db.session.commit()
            flash('New entry successfully posted')
            return redirect(url_for('tasks'))
    return render_template(
        'tasks.html',
        form=form,
        error=error,
        open_tasks=open_tasks(),
        closed_tasks=closed_tasks())


# Mark tests as complete
@app.route('/complete/<int:task_id>/')
@login_required
def complete(task_id):
    # g.db   = connect_db()
    # g.db.execute('update tasks set status = 0 where task_id='+str(task_id))
    # g.db.commit()
    # g.db.close()

    new_id = task_id
    task = db.session.query(Task).filter_by(task_id=new_id)
    if session['user_id'] == task.first().user_id or\
            session['role'] == "admin":
        task.update({"status": "0"})
        db.session.commit()
        flash('task was marked as complete')
        return redirect(url_for('tasks'))
    else:
        flash('You can only update tasks that belong to you')
        return redirect(url_for('tasks'))


@app.route('/delete/<int:task_id>/')
@login_required
def delete_entry(task_id):
    # g.db = connect_db()
    # g.db.execute('delete from tasks where task_id='+str(task_id))
    # g.db.commit()
    # g.db.close()

    new_id = task_id
    task = db.session.query(Task).filter_by(task_id=new_id)
    if session['user_id'] == task.first().user_id or\
            session['role'] == "admin":
        task.delete()
        db.session.commit()
        flash('task was deleted')
        return redirect((url_for('tasks')))
    else:
        flash('You can only delete tasks that belong to you')
        return redirect(url_for('tasks'))
