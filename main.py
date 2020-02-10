import csv
import sqlite3
import random
from flask import Flask,g, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
import traceback
import configparser

config = configparser.ConfigParser()
config.read('config.ini')


app = Flask(__name__)
app.secret_key = config.get('flask', 'secret_key')

# File name and Path 
SQLITE_DB_PATH = config.get('path', 'SQLITE_DB_PATH')
SQLITE_DB_SCHEMA = config.get('path', 'SQLITE_DB_SCHEMA')
MEMBER_CSV_PATH = config.get('path', 'MEMBER_CSV_PATH')

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'
login_manager.login_message = 'Please Log In ~'



@app.route('/')
def index():
    return render_template('index.html')

class User(UserMixin):
        pass



users = {'ShangWei': {'password': '00000000'}}




@login_manager.user_loader
def user_loader(login_name):
    if login_name not in users:
        return

    user = User()
    user.id = login_name
    return user

@login_manager.request_loader
def request_loader(request):
    login_name = request.form.get('user_id')
    if login_name not in users:
        return

    user = User()
    user.id = login_name
    user.is_authenticated = request.form['password'] == users[login_name]['password']
    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    login_name = request.form['user_id']
    if (login_name in users) and (request.form['password'] == users[login_name]['password']):
        user = User()
        user.id = login_name
        login_user(user)
        flash(f'Welcome Log In !!')
        return render_template('index.html')
    flash('Login Failure...')
    return render_template('login.html')

@app.route('/logout')        
def logout():
    login_name = current_user.get_id()
    logout_user()
    
    return render_template('index.html')
                                                                                                                                                
# SQLITE3-related operations
def get_db():
    db = getattr(g,'_database',None)
    if db is None:
        db = g._database = sqlite3.connect(SQLITE_DB_PATH)
        # Enable foreign key check
        db.execute("PRAGMA foreign_keys = ON")

    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g,'_database',None)
    if db is not None:
        db.close()

@app.route('/addmember')
@login_required
def addmember():
    return render_template('addmember.html')

@app.route('/registermember')
def getAddMemberRequest():
    # Get the database connection
    db = get_db()

    cursor = db.cursor()

    sql = "INSERT INTO members(name,gender) VALUES('%s','%s')" % (request.args.get('name'),request.args.get('gender'))
    print("\n\n")
    print(request.args.get('gender'))
    try:
        cursor.execute(sql)
        db.commit()

        return render_template('index.html')
        
    except:
        traceback.print_exc()
        db.rollback()
        return 'Add Members Failure'

    # add check whether the added data is already in database

    db.close()
   


@app.route('/showmember')
def showmember():
    db = get_db()
    c = db.execute(
        'SELECT m.name, m.gender '
        'FROM members as m '
        'ORDER BY m.gender DESC '
    ).fetchall()

    members = []
    for row in c:
        members.append({
            'name':row[0],
            'gender':row[1],
        })
    
    return render_template(
        'showmember.html',
        members = members
    )
   



@app.route('/draw',methods=['POST'])
def draw():
    # Get the database connection
    db = get_db()

    # Draw member ids from given group
    # If ALL is given then draw from all members
    gender = request.form.get('gender', 'ALL')
    valid_members_sql = 'SELECT id FROM members '
    if gender == 'ALL':
        cursor = db.execute(valid_members_sql)
    else:
        valid_members_sql += 'WHERE gender = ?'
        cursor = db.execute(valid_members_sql, (gender, ))
    
    valid_member_ids = [
        row[0] for row in cursor
    ]

    # If no valid members return 404 (unlikely)
    if not valid_member_ids:
        err_msg = "<p>No member in gender '%s'</p>" % gender
        return err_msg, 404

    # Randomly choice a member
    chosen_id = random.choice(valid_member_ids)

    # Obtain the lucy member's information
    member_name, member_gender = db.execute(
        'SELECT name, gender FROM members WHERE id = ?',
        (chosen_id, )
    ).fetchone()
    # fetchone(): get one data only

    with db:
        db. execute('INSERT INTO draw_histories (memberid) VALUES (?)',
                    (chosen_id, ))
                    
    return render_template(
        'draw.html',
        name=member_name,
        gender=member_gender,
        )

@app.route('/history')
def history():
    db = get_db()
    c = db.execute(
        'SELECT m.name, m.gender, d.time '
        'FROM draw_histories AS d, members as m '
        'WHERE m.id == d.memberid '
        'ORDER BY d.time DESC '
        'LIMIT 10 '
    ).fetchall()

    recent_histories = []
    for row in c:
        recent_histories.append({
            'name':row[0],
            'gender':row[1],
            'draw_time': datetime.strptime(row[2],'%Y-%m-%d %H:%M:%S'),
        })

    return render_template(
        'history.html',
        recent_histories = recent_histories
    )


def reset_db():
    with open(SQLITE_DB_SCHEMA,'r') as f:
        create_db_sql = f.read()
    
    db = get_db()
    # reset database
    with db:
        db.execute("DROP TABLE IF EXISTS draw_histories")
        db.execute("DROP TABLE IF EXISTS members")
        db.executescript(create_db_sql)

    # read members csv data
    with open('./members.csv', newline='') as f:
        csv_reader = csv.DictReader(f)
        members = [ (row['Name'], row['Gender'])   for row in csv_reader]

    # write members into database
    with db:
        db.executemany('INSERT INTO members (name,gender) VALUES(?,?)',members)

@app.route('/reset')
@login_required
def reset():
    with app.app_context():
        reset_db()

    return render_template('index.html')



if __name__ =="__main__":
    app.run(debug=True)

