from flask import render_template, url_for, redirect, flash, request
from app import app, db, login
from app.forms import LoginForm, RegistrationForm
from app.models import User
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.dbfun import *
from app import aux_fun

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Notification': Notification}

@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        r = login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('notifications')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/accounts')
@login_required
def accounts():
    users =  db.session.query(User).all()
    print(users)
    return render_template('accounts.html', users=users, title='Accounts')

@app.route('/accounts/account_actions', methods=["POST", "GET"])
def account_actions():
    conn = get_users_connection()
    cursor = conn.cursor()
    if request.method == "POST":
        action = request.form['action']
        if action == 'delete':
            checked_list = list(map(int, request.form.getlist('checkbox[]')))
            print(checked_list)
            for i in checked_list:
                user = User.query.filter_by(id=i).first()
                print('i:', i, 'user:', user)
                db.session.delete(user)
                db.session.commit()
            #query = "DELETE FROM users_db WHERE id IN ({})".format(", ".join("?" * len(checked_list)))
            #cursor.execute(query, checked_list)
            #conn.commit()
            return redirect(url_for('accounts'))
        if action == 'register':
            return redirect(url_for('register'))

@app.route('/create_account', methods=['GET', 'POST'])
def register():
    if (current_user.is_authenticated and current_user == 'admin'):
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('create_account.html', title='Register', form=form)

@app.route('/notifications', methods=["POST", "GET"])
def notifications():
    conn_notifications = get_notifications_connection()
    notifications = conn_notifications.execute('SELECT * FROM notifications_db').fetchall()
    conn_rules = get_rules_connection()
    rules = conn_rules.execute('SELECT * FROM rules_db').fetchall()
    #rule_description = conn_rules.execute('SELECT rule FROM rules_db WHERE description = ?',
    #               (notification_id,)).fetchone()
    return render_template('notifications.html', notifications=notifications, rules=rules, title="Notifications")

@app.route('/notifications/notifications_actions', methods=["POST", "GET"])
@login_required
def notifications_actions():
    conn = get_notifications_connection()
    cursor = conn.cursor()
    action = request.form['action']
    if action == 'add':
        if request.method == "POST":
            return redirect(url_for('add_notification'))
    if action == 'del': 
        if request.method == "POST":
            checked_list = list(map(int, request.form.getlist('checkbox[]')))
            if len(checked_list) > 0:
                query = "DELETE FROM notifications_db WHERE id IN ({})".format(", ".join("?" * len(checked_list)))
                cursor.execute(query, checked_list)
                conn.commit()
            else:
                flash('Select at least one notification to delete')
        conn.close()
        return redirect(url_for('notifications'))
    if action == 'edit':
        if request.method == "POST":
            checked_list = list(map(int, request.form.getlist('checkbox[]')))
            if ((len(checked_list)>1)):
                flash('Select ONE notification to edit')
                return redirect(url_for('notifications'))
            elif (len(checked_list)==0):
                flash('Select one notification to edit')
                return redirect(url_for('notifications'))
            else: 
                #global idx
                id = checked_list[0]
                return redirect(url_for('edit_notification', id=id))


@app.route('/notifications/add_notification', methods=['GET','POST'])
@login_required
def add_notification():
    conn_rules = get_rules_connection()
    descriptions = conn_rules.execute('SELECT description FROM rules_db').fetchall()
    rules = conn_rules.execute('SELECT * FROM rules_db').fetchall()
    if request.method == 'POST':
        action = request.form['action']
        if action == 'accept':
            expiration = request.form['expiration']
            pv = request.form['pv']
            rule = request.form.get('rule')
            limits = request.form['limits']
            owner = request.form['owner']
            phone = request.form['phone']
            persistent = 'persistent' in request.form
            interval = request.form['interval']
            r = aux_fun.verifyPV(pv)
            if r:
                if interval.isnumeric():
                    if (int(interval) < 10):
                        interval = 10
                else:
                    interval = 10
                if expiration=='' or pv=='' or rule==None or limits=='' or phone=='':
                    flash("Please fill in empty field(s)")
                else:
                    conn = get_notifications_connection()
                    conn.execute('INSERT INTO notifications_db (expiration, pv, rule, limits, owner, \
                                phone, persistent, interval) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                                (expiration, pv, rule, limits, owner, phone, persistent, interval))
                    conn.commit()
                    conn.close()
                    return redirect(url_for('notifications'))
            else:
                flash("Please verify PV name")
        if action == 'cancel':
            return redirect(url_for('notifications'))
    return render_template('add_notification.html', descriptions=descriptions, rules=rules, title="Add Notification")

@app.route('/notifications/edit_notification/<int:id>', methods=['GET','POST'])
@login_required
def edit_notification(id):
    conn_rules = get_rules_connection()
    descriptions = conn_rules.execute('SELECT description FROM rules_db').fetchall()
    rules = conn_rules.execute('SELECT * FROM rules_db').fetchall()
    if request.method == 'POST':
        action = request.form['action']
        if action == 'accept':
            expiration = request.form['expiration']
            pv = request.form['pv']
            rule = request.form['rule']
            limits = request.form['limits']
            owner = request.form['owner']
            phone = request.form['phone']
            if request.form.getlist('sent'):
                sent = 1
            else:
                sent = 0
            interval = request.form['interval']
            if request.form.getlist('persistent'):
                persistent = 1
            else:
                persistent = 0
            r = aux_fun.verifyPV(pv)
            if r:
                if interval.isnumeric():
                    if (int(interval) < 10):
                        interval = 10
                else:
                    interval = 10
                if request.form.get('action'):
                    conn = get_notifications_connection()
                    conn.execute('UPDATE notifications_db SET expiration = ?, pv = ?, rule = ?, limits = ?, owner = ?, \
                                phone = ?, interval = ?, sent = ?, persistent = ?'
                                ' WHERE id = ?',
                                (expiration, pv, rule, limits, owner, phone, interval, sent, persistent, id))
                    conn.commit()
                    notification = conn.execute('SELECT * FROM notifications_db').fetchall()
                    conn.close()
                    return redirect(url_for('notifications'))
            else:
                flash("Please verify PV name")
        if action == 'cancel':
            return redirect(url_for('notifications'))
        if action == 'delete': 
            if request.method == "POST":
                conn = get_notifications_connection()
                conn.execute("DELETE FROM notifications_db WHERE id = ?", (id,))
                conn.commit()
                conn.close()
                return redirect(url_for('notifications'))
    notification = get_notification(id)
    return render_template('edit_notification.html', descriptions=descriptions, rules=rules, notification=notification, title="Edit Notification")

@app.route('/rules')
def rules():
    conn = get_rules_connection()
    rules = conn.execute('SELECT * FROM rules_db').fetchall()
    return render_template('rules.html', rules=rules, title='Rules')

@app.route('/rules/add_rule', methods=['GET','POST'])
@login_required
def add_rule():
    if request.method == 'POST':
        action = request.form['action']
        rule = request.form['rule']
        description = request.form['description']
        owner = request.form['owner']
        if action == 'accept':
            if request.form.get('action'):
                conn = get_rules_connection()
                conn.execute('INSERT INTO rules_db (rule, description, owner) VALUES (?, ?, ?)',
                            (rule, description, owner))
                conn.commit()
                conn.close()
                return redirect(url_for('rules'))
        if action == 'cancel':
            return redirect(url_for('rules'))
    return render_template('add_rule.html', title='Add Rule')

@app.route('/rules/edit_rule/<int:id>', methods=['GET','POST'])
@login_required
def edit_rule(id):
    if request.method == 'POST':
        action = request.form['action']
        if action == 'accept':
            rule = request.form['rule']
            description = request.form['description']
            owner = request.form['owner']
            conn = get_rules_connection()
            conn.execute('UPDATE rules_db SET rule = ?, description = ?, owner = ? WHERE id = ?', \
                            (rule, description, owner, id))
            conn.commit()
            conn.close()
            return redirect(url_for('rules'))
        if action == 'cancel':
            return redirect(url_for('rules'))
    rule = get_rule(id)
    return render_template('edit_rule.html', rule=rule, title='Edit Rule')

@app.route('/rules/rules_actions', methods=["POST", "GET"])
def rules_actions():
    conn = get_rules_connection()
    cursor = conn.cursor()
    action = request.form['action']
    if action == 'add':
        return redirect(url_for('add_rule'))
    if action == 'del':
        if request.method == "POST":
            checked_list = list(map(int, request.form.getlist('checkbox[]')))
            print(checked_list)
            #owner = get_rule(checked_list[0])[3]
            if len(checked_list) > 0:
                query = "DELETE FROM rules_db WHERE id IN ({})".format(", ".join("?" * len(checked_list)))
                cursor.execute(query, checked_list)
                conn.commit()
            else:
                flash('Select at least one rule to delete')
        conn.close()
        return redirect(url_for('rules'))
    if action == 'edit':
        if request.method == "POST":
            checked_list = list(map(int, request.form.getlist('checkbox[]')))
            if ((len(checked_list)>1)):
                flash('Select ONE rule to edit')
                return redirect(url_for('rules'))
            elif (len(checked_list)==0):
                flash('Select one rule to edit')
                return redirect(url_for('rules'))
            else: 
                #global idx
                id = checked_list[0]
                return redirect(url_for('edit_rule', id=id))