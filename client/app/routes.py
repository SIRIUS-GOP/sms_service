from flask import render_template, url_for, redirect, flash, request, jsonify
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

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('q')
    conn_fullpvlist = get_fullpvlist_connection()
    conn_fullpvlist.create_function("REGEXP", 2, regexp)
    results = conn_fullpvlist.execute('SELECT * FROM fullpvlist_db WHERE pv REGEXP ?',(search,))
    #results = conn_fullpvlist.execute('SELECT * FROM fullpvlist_db WHERE pv LIKE ?', ('%' + search + '%',))
    m = []
    for row in results:
        for i in row:
            m.append(i)
    return jsonify(matching_results=m)

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
        r = login_user(user, remember=False) #form.remember_me.data)
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

@app.route('/delete_notification', methods=['POST', 'GET'])
@login_required
def delete_notification():
    checked_list = request.args.getlist('checked_list')
    conn = get_notifications_connection()
    cursor = conn.cursor()
    for item in checked_list:
        query = cursor.execute("SELECT owner FROM notifications_db WHERE id = ?", (item,))
        owner = query.fetchall()[0][0]
        if current_user.username == owner or current_user.username == "admin" :
            cursor.execute("DELETE FROM notifications_db WHERE id = ?", (item,))
        else:
            flash("Cannot delete notifications you don't own")
    conn.commit()
    conn.close()
    return redirect(url_for('notifications'))

@app.route('/notifications/notifications_actions', methods=["POST", "GET"])
def notifications_actions():
    #conn = get_notifications_connection()
    #cursor = conn.cursor()
    action = request.form['action']
    if action == 'add':
        if request.method == "POST":
            return redirect(url_for('add_notification'))
    if action == 'del': 
        if request.method == "POST":
            checked_list = list(map(int, request.form.getlist('checkbox[]')))
            if len(checked_list) > 0:
                return redirect(url_for('delete_notification', checked_list=checked_list))
            else:
                flash('Select at least one notification to delete')
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
                id = checked_list[0]
                return redirect(url_for('edit_notification', id=id))

@app.route('/notifications/add_notification', methods=['GET','POST'])
@login_required
def add_notification():
    conn_fullpvlist = get_fullpvlist_connection()
    conn_rules = get_rules_connection()
    fullpvlist_rows = conn_fullpvlist.execute('SELECT pv FROM fullpvlist_db').fetchall()
    fullpvlist = [] 
    for row in fullpvlist_rows:
        for i in row:
            fullpvlist.append(i)
    descriptions = conn_rules.execute('SELECT description FROM rules_db').fetchall()
    rules = conn_rules.execute('SELECT * FROM rules_db').fetchall()
    if request.method == 'POST':
        action = request.form['action']
        if action == 'accept':
            expiration = request.form['expiration']
            owner = request.form['owner']
            phone = request.form['phone']
            pv1 = request.form['pv1']
            rule1 = request.form.get('rule1')
            limits1 = request.form['limits1']
            addsubrule1 = (request.form.get('addsubrule1')).lower()
            pv2 = request.form['pv2']
            rule2 = request.form.get('rule2')
            limits2 = request.form['limits2']
            addsubrule2 = ''#(request.form.get('addsubrule2')).lower()
            pv3 = ''#request.form['pv3']
            rule3 = 0#request.form.get('rule3')
            limits3 = ''#request.form['limits3']
            hidden1 = request.form['hidden1']
            hidden2 = request.form['hidden2']
            L1 = limits1.find('L=')
            LL1 = limits1.find('LL=')
            LU1 = limits1.find('LU=')
            L2 = limits2.find('L=')
            LL2 = limits2.find('LL=')
            LU2 = limits2.find('LU=')
            L3 = limits3.find('L=')
            LL3 = limits3.find('LL=')
            LU3 = limits3.find('LU=')
            #print(addsubrule1, addsubrule2)
            if (L1 and LL1 and LU1) == -1:
                #print("case1")
                flash('Please use format L=<value>, LL=<value> and/or LU=<value> for Limit(s)')
            elif (hidden1 == 1):
                if ((L2 and LL2 and LU2) == -1):
                    #print("case2", L2, LL2, LU2)
                    flash('Please use format L=<value>, LL=<value> and/or LU=<value> for Limit(s)')
            elif (hidden2 == 1):
                if ((L3 and LL3 and LU3) == -1):
                    #print("case3", L3, LL3, LU3)
                    flash('Please use format L=<value>, LL=<value> and/or LU=<value> for Limit(s)')
            else:
                #return render_template('add_notification.html', descriptions=descriptions, rules=rules, title="Add Notification", fullpvlist=fullpvlist)
                persistent = 'persistent' in request.form
                interval = request.form['interval']
                if interval.isnumeric():
                    if (int(interval) < 10):
                        interval = 10
                else:
                    interval = 10
                if expiration=='' or pv1=='' or rule1==None or limits1=='' or phone=='':
                    flash("Please fill in empty field(s)")
                else:
                    conn = get_notifications_connection()
                    conn.execute('INSERT INTO notifications_db (expiration, owner, phone, pv1, rule1, limits1, subrule1, pv2, rule2, \
                                limits2, subrule2, pv3, rule3, limits3, persistent, interval) \
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                (expiration, owner, phone, pv1, rule1, limits1, addsubrule1, pv2, rule2, limits2, addsubrule2, \
                                    pv3, rule3, limits3, persistent, interval))
                    conn.commit()
                    conn.close()
                    return redirect(url_for('notifications'))
        if action == 'cancel':
            return redirect(url_for('notifications'))
    return render_template('add_notification.html', descriptions=descriptions, rules=rules, title="Add Notification", fullpvlist=fullpvlist)

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
            owner = request.form['owner']
            phone = request.form['phone']
            pv1 = request.form['pv1']
            rule1 = request.form.get('rule1')
            limits1 = request.form['limits1']
            addsubrule1 = (request.form.get('addsubrule1')).lower()
            pv2 = request.form['pv2']
            rule2 = request.form.get('rule2')
            limits2 = request.form['limits2']
            addsubrule2 = ''#(request.form.get('addsubrule2')).lower()
            pv3 = ''#request.form['pv3']
            rule3 = 0#request.form.get('rule3')
            limits3 = ''#request.form['limits3']
            hidden1 = request.form['hidden1']
            hidden2 = request.form['hidden2']
            L1 = limits1.find('L=')
            LL1 = limits1.find('LL=')
            LU1 = limits1.find('LU=')
            L2 = limits2.find('L=')
            LL2 = limits2.find('LL=')
            LU2 = limits2.find('LU=')
            L3 = limits3.find('L=')
            LL3 = limits3.find('LL=')
            LU3 = limits3.find('LU=')
            #print(addsubrule1, addsubrule2)
            if (L1 and LL1 and LU1) == -1:
                #print("case1")
                flash('Please use format L=<value>, LL=<value> and/or LU=<value> for Limit(s)')
            elif (hidden1 == 1):
                if ((L2 and LL2 and LU2) == -1):
                    #print("case2", L2, LL2, LU2)
                    flash('Please use format L=<value>, LL=<value> and/or LU=<value> for Limit(s)')
            elif (hidden2 == 1):
                if ((L3 and LL3 and LU3) == -1):
                    #print("case3", L3, LL3, LU3)
                    flash('Please use format L=<value>, LL=<value> and/or LU=<value> for Limit(s)')
            else:
                if request.form.getlist('sent'):
                    sent = 1
                else:
                    sent = 0
                interval = request.form['interval']
                if request.form.getlist('persistent'):
                    persistent = 1
                else:
                    persistent = 0
                if interval.isnumeric():
                    if (int(interval) < 10):
                        interval = 10
                else:
                    interval = 10
                if request.form.get('action'):
                    conn = get_notifications_connection()
                    conn.execute('UPDATE notifications_db SET expiration = ?, owner = ?, phone = ?, pv1 = ?, rule1 = ?, limits1 = ?, \
                                subrule1 = ?, pv2 = ?, rule2 = ?, limits2 = ?, subrule2 = ?, pv3 = ?, rule3 = ?, limits3 = ?, \
                                persistent = ?, interval = ?, sent = ? WHERE id = ?',
                                (expiration, owner, phone, pv1, rule1, limits1, addsubrule1, pv2, rule2, limits2, addsubrule2, \
                                pv3, rule3, limits3, persistent, interval, sent, id))
                    conn.commit()
                    notification = conn.execute('SELECT * FROM notifications_db').fetchall()
                    conn.close()
                    return redirect(url_for('notifications'))
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
        if action == 'delete': 
            if request.method == "POST":
                conn = get_rules_connection()
                conn.execute("DELETE FROM rules_db WHERE id = ?", (id,))
                conn.commit()
                conn.close()
                return redirect(url_for('rules'))
    rule = get_rule(id)
    return render_template('edit_rule.html', rule=rule, title='Edit Rule')

@app.route('/delete_rule', methods=['POST', 'GET'])
@login_required
def delete_rule():
    checked_list = request.args.getlist('checked_list')
    conn = get_rules_connection()
    cursor = conn.cursor()
    if len(checked_list) > 0:
        for item in checked_list:
            query = cursor.execute("SELECT owner FROM rules_db WHERE id = ?", (item,))
            owner = query.fetchall()[0][0]
            if current_user.username == owner or current_user.username == "admin":
                cursor.execute("DELETE FROM rules_db WHERE id = ?", (item,))
            else:
                flash("Cannot delete rules you do not own")
        conn.commit()
    else:
        flash('Select at least one rule to delete')
    conn.close()
    return redirect(url_for('rules'))

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
            print('checked_list:', type(checked_list))
            return redirect(url_for('delete_rule', checked_list=checked_list))
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