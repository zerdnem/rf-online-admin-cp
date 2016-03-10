from flask import Blueprint, render_template, url_for, request, session, flash, redirect, jsonify
from .models import GMRegistrationForm, RegistrationForm, connection_rfuser, connection_rfworld, login_required
from passlib.hash import sha256_crypt
import gc


cp = Blueprint('cp', __name__, template_folder='templates', static_folder='static')


@cp.route('/login')
def login_session():
    if 'logged_in' in session:
        return redirect(url_for('cp.dashboard'))
    else:
        return render_template('main.html')


@cp.route('/login', methods=["GET", "POST"])
def login():
    cur, conn = connection_rfuser()
    if request.method == "POST":
        cur.execute("SELECT ID,PW FROM dbo.tbl_StaffAccount \
                WHERE ID = convert(binary, ?) AND \
                PW = CONVERT(BINARY, ?)", (request.form['username']),(request.form['password']))
        row = cur.fetchone()

        if row:
            session['logged_in'] = True
            session['username'] = request.form['username']
            return redirect(url_for("cp.dashboard"))

        else:
            flash("Invalid credentials...try again!", 'error')

    gc.collect()
    return render_template("main.html")


@cp.route('/unban_user', methods=["GET", "POST"])
@login_required
def unban_user():
    cur, conn = connection_rfuser()
    cursor, con = connection_rfworld()
    serial = []
    if request.method == "POST":
        user = request.form['unbanUser']
        for users in cursor.execute("SELECT Name, AccountSerial FROM dbo.tbl_base"):
            if user == str(users.Name):
                serial.append(users.AccountSerial)
                try:
                    cur.execute("DELETE FROM dbo.tbl_UserBan WHERE nAccountSerial=?", serial[0])
                    conn.commit()
                    print("User successfully banned.")
                except:
                    print("Can't unban the account!")

    return redirect(url_for('cp.ban_list'))


@cp.route('/ban_user', methods=["GET","POST"])
@login_required
def ban_user():
    cur, conn = connection_rfuser()
    cursor, con = connection_rfworld()
    serial = []
    if request.method == "POST":
        user = request.form['banUser']
        for users in cursor.execute("SELECT Name, AccountSerial FROM dbo.tbl_base"):
            if user == str(users.Name):
                serial.append(users.AccountSerial)
                try:
                    cur.execute("INSERT INTO dbo.tbl_UserBan (nAccountSerial, nPeriod, szReason, GMReason) \
                            VALUES(?, 99999, 'Naughty playah!', 'Naughty playah!')", serial[0])
                    conn.commit()
                except:
                    print("Account is already banned!")
    return redirect(url_for("cp.ban_list"))


@cp.route('/ban_list', methods=["GET"])
@login_required
def ban_list():
    data = []
    cur, conn = connection_rfuser()
    cursor, con = connection_rfworld()
    serials = [str(item[0]) for item in cur.execute("SELECT nAccountSerial FROM dbo.tbl_UserBan")]
    for i in serials:
        for users in cursor.execute("SELECT Name, AccountSerial FROM dbo.tbl_base"):
            if i == str(users.AccountSerial):
                data.append(users.Name)
    return render_template('ban.html', data=data)


@cp.route('/gm', methods=["GET", "POST"])
def gm_register():
    try:
        form = GMRegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            username = form.username.data
            password = form.password.data
            cur, conn = connection_rfuser()
            cur.execute("select ID from dbo.tbl_StaffAccount where ID = CONVERT(binary, ?)", (username))
            row = cur.fetchone()
            if row:
                flash('That username is already taken, please try another one.', 'error')
                print("Username is already taken!")
                return render_template('gm.html', form=form)

            else:
                cur.execute("insert into dbo.tbl_StaffAccount \
                        (ID,PW,Grade,Depart,RealName,SubGrade,Birthday,ComClass) \
                        values(convert(binary, ?),convert(binary, ?),'2', 'none', ?, '4', '01/01/1991', 'GM')", 
                        username, password, username.strip('!'))
                conn.commit()
                flash('Registration successful!', 'success')
                print("Registration Successful!")
                cur.close()
                gc.collect()
        return render_template('gm.html', form=form)

    except Exception as e:
        return str(e)


@cp.route('/register', methods=["GET", "POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = form.password.data
            cur, conn = connection_rfuser()
            cur.execute("select id from dbo.tbl_RFTestAccount where id = CONVERT(binary, ?)", (username))
            row = cur.fetchone()
            if row:
                flash(u'That username is already taken, please try another one.', 'error')
                print("Username is already taken!")
                return render_template('register.html', form=form)

            else:
                cur.execute("insert into dbo.tbl_RFTestAccount(id, password, email)  \
                        values(convert(binary(13), ?),convert(binary(13), ?), ?)", username, password, email)
                conn.commit()
                flash(u'Registration successful!', 'success')
                print("Registration Successful!")
                cur.close()
                gc.collect()

        return render_template('register.html', form=form)

    except Exception as e:
        return(str(e))


@cp.route('/online', methods=["GET"])
@login_required
def online_users():
    cur, conn = connection_rfuser()
    return render_template('online.html')


@cp.route('/', methods=["GET"])
def main_page():
    if not 'logged_in' in session:
        return render_template('main.html')
    else:
        return redirect(url_for('cp.dashboard'))


@cp.route('/dashboard', methods=["GET"])
@login_required
def dashboard():
    return render_template('dashboard.html')


@cp.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('cp.main_page'))


@cp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
