from flask import Flask, render_template, request, redirect, session, url_for
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib
import mysql.connector
import datetime
from datetime import datetime
import time
from flask import jsonify

app = Flask(__name__)
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = os.environ.get('emailpageMySQL')
app.config['MYSQL_DB'] = 'emailpage'

mysql = MySQL(app)
app.secret_key = os.environ.get('groupKsecret')
sg_api = os.environ.get('SENDGRID_API_KEY')
sg = SendGridAPIClient(sg_api)

@app.route('/home', methods=['GET', 'POST'])
@app.route('/')

def home():
    if 'loggedin' in session:
        username = session.get('username')
        firstTag = 'Dashboard'
        firstTagRoute = '/dashboard'
        secondTag = 'Log Out'
        secondTagRoute = '/logout'
        thirdTag = 'Profile'
        thirdTagRoute = '/profile'
        return render_template('test.html', username=username, firstTag=firstTag, firstTagRoute=firstTagRoute, secondTag=secondTag, secondTagRoute=secondTagRoute, thirdTag=thirdTag, thirdTagRoute=thirdTagRoute)
    else:
        username = session.get('username')
        firstTag = 'Create Account'
        firstTagRoute = '/create_account_form'
        secondTag = 'Log In'
        secondTagRoute = '/login_function'
        return render_template('test.html', username=username, firstTag=firstTag, firstTagRoute=firstTagRoute, secondTag=secondTag, secondTagRoute=secondTagRoute)

@app.route('/issue_form', methods=['GET', 'POST'])
def issue_form():
    if 'loggedin' in session:
        username = session.get('username')
        firstTag = 'Dashboard'
        firstTagRoute = '/dashboard'
        secondTag = 'Log Out'
        secondTagRoute = '/logout'
        thirdTag = 'Profile'
        thirdTagRoute = '/profile'
        msg = session.pop('msg', None)
        if msg is None:
            return render_template('issue_form.html', username=username, firstTag=firstTag, firstTagRoute=firstTagRoute, secondTag=secondTag, secondTagRoute=secondTagRoute, thirdTag=thirdTag, thirdTagRoute=thirdTagRoute)
        else:
            return render_template('issue_form.html', username=username, firstTag=firstTag, firstTagRoute=firstTagRoute, secondTag=secondTag, secondTagRoute=secondTagRoute, thirdTag=thirdTag, thirdTagRoute=thirdTagRoute, msg=msg)



    else:
        firstTag = 'Create Account'
        firstTagRoute = '/create_account_form'
        secondTag = 'Log In'
        secondTagRoute = '/login_function'
        msg = session.pop('msg', None)
        if msg is None:
            return render_template('issue_form.html', firstTag=firstTag, firstTagRoute=firstTagRoute, secondTag=secondTag, secondTagRoute=secondTagRoute)
        else:
            return render_template('issue_form.html', firstTag=firstTag, firstTagRoute=firstTagRoute, secondTag=secondTag, secondTagRoute=secondTagRoute, msg=msg)









@app.route('/create_account_form', methods = ['GET', 'POST'] )
def create_account_form():
    return render_template('create_account.html')

@app.route('/login_function', methods=['POST', 'GET'])
def login_function():
    return render_template('login_page.html')

@app.route('/create_account', methods=['POST'])
def create_account():
    msg = ''
    username = request.form['username']
    password = request.form['password']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE login_username = %s', (username,))
    account = cursor.fetchone()
    if account:
        msg = 'Account already exists!'
    elif not username or not password:
        msg = 'Please fill out the form!'
    else:
        cursor.execute('INSERT INTO users (login_username, login_password) VALUES (%s, %s)', (username, password))
        mysql.connection.commit()
        msg = 'You have successfully registered!'

    return jsonify({'msg': msg}) # Return message as JSON


@app.route('/authenticate_user', methods=['POST', 'GET'])
def authenticate_user():
    username = request.form['username']
    password = request.form['password']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE login_username = %s AND login_password = %s', (username, password,))
    account = cursor.fetchone()

    if account:

        session['loggedin'] = True
        session['user_id'] = account['userID']
        session['username'] = account['login_username']


        return redirect(url_for('dashboard'))
    else:
        msg = 'Incorrect username/password!'
        return render_template('login_page.html', msg=msg)
    





def add_email_record(user_issue, userID, emailStatus):
    email_datetime = datetime.now()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO emailrequests (emailRequestDescription, emailRequestDT, emailRequestStatus, userID) VALUES (%s, %s, %s, %s)', (user_issue, email_datetime, emailStatus, userID))
    mysql.connection.commit()

def fetch_email_data(userID, username):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT emailRequestDescription, emailRequestDT, emailRequestStatus FROM emailrequests WHERE userID = %s', (userID,))
    emaildata = cursor.fetchall()
    dashboard(emaildata, username)


    





@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('user_id', None)
   session.pop('username', None)
   session.pop('password', None)
   session.pop('first_name', None)
   session.pop('last_name', None)
   session.pop('UWEemail', None)

   # Redirect to login page
   msg = 'You are now logged out'
   return render_template('login_page.html', msg=msg)

@app.route('/dashboard', methods={'GET', 'POST'})
def dashboard():
        userID = session.get('user_id')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT emailRequestDescription, emailRequestDT, emailRequestStatus FROM emailrequests WHERE userID = %s', (userID,))
        emaildata = cursor.fetchall()

        # Convert emaildata to a JSON serializable format
        emailArray = [dict(row) for row in emaildata]

        username = session.get('username')

        if emailArray == []:
            msg="You haven't submitted a request yet :("
            return render_template('main_dashboard.html', username=username, msg=msg)
        else: 
            erd = 'Email Request Description'
            erdt = 'Email Request Date and Time'
            ers = 'Email Request Status'
            return render_template('main_dashboard.html', emailArray=emailArray, username=username, erd=erd, erdt=erdt, ers=ers)



@app.route('/profile', methods=['GET'])
def profile():
    userID = session.get('user_id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT login_username, login_password, first_name, last_name, UWE_email FROM users WHERE userID = %s', (userID,))
    profiledata = cursor.fetchall()

    if profiledata:
        row = profiledata[0]
        session['username'] = row['login_username']
        session['password'] = row['login_password']
        session['first_name'] = row['first_name']
        session['last_name'] = row['last_name']
        session['UWEemail'] = row['UWE_email']


    username = session.get('username')
    password = session.get('password')
    fName = session.get('first_name')
    lName = session.get('last_name')
    UWEemail = session.get('UWEemail')

    

    if fName is None:
        fName = 'No First Name Given'

    if lName is None:
        lName = 'No Last Name Given'

    if UWEemail is None:
        UWEemail = 'No UWE email Given'
    return render_template('profile.html', fName=fName, lName=lName, username=username, password=password, UWEemail=UWEemail)









@app.route('/modify_details', methods=['GET', 'POST'])
def modify_details_page():
    return render_template('modify_details.html')






@app.route('/change_first', methods = ['GET'])
def change_first():
    First = 'New First Name'
    Second = 'Confirm New First Name:'
    verify = '/first_verify'
    message = session.pop('message', None)
    if message is None:
        return render_template('modify_details.html', First=First, Second=Second, verify=verify)
    else:
        return render_template('modify_details.html', First=First, Second=Second, verify=verify, message=message)

@app.route('/change_last', methods = ['GET'])
def change_last():
    First = 'New Last Name'
    Second = 'Confirm New Last Name:'
    verify = '/last_verify'
    message = session.pop('message', None)
    if message is None:
        return render_template('modify_details.html', First=First, Second=Second, verify=verify)
    else:
        return render_template('modify_details.html', First=First, Second=Second, verify=verify, message=message)

@app.route('/change_username', methods = ['GET'])
def change_username():
    First = 'Current Username:'
    Second = 'New Username:'
    verify = '/username_verify'
    message = session.pop('message', None)
    if message is None:
        return render_template('modify_details.html', First=First, Second=Second, verify=verify)
    else:
        return render_template('modify_details.html', First=First, Second=Second, verify=verify, message=message)

@app.route('/change_password', methods = ['GET'])
def change_password():
    First = 'Current Password:'
    Second = 'New Password:'
    verify = '/password_verify'
    message = session.pop('message', None)
    if message is None:
        return render_template('modify_details.html', First=First, Second=Second, verify=verify)
    else:
        return render_template('modify_details.html', First=First, Second=Second, verify=verify, message=message)

@app.route('/change_uwe', methods=['GET'])
def change_uwe():
    First = 'New UWE email:'
    Second = 'Confirm New UWE email:'
    verify = '/uwe_verify' 
    message = session.pop('message', None)
    if message is None:
        return render_template('modify_details.html', First=First, Second=Second, verify=verify)
    else:
        return render_template('modify_details.html', First=First, Second=Second, verify=verify, message=message)






@app.route('/first_verify', methods=['POST'])
def first_verify():
    userID = session.get('user_id')
    fName = session.get('first_name')
    first_entry = request.form['first_entry']
    last_entry = request.form['last_entry']
    if fName == first_entry or fName == last_entry:
        session['message'] = 'Please type in a new First Name'
        return redirect(url_for('change_first'))
    elif first_entry == last_entry:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE users SET first_name = %s WHERE userID = %s', (first_entry, userID,))
        mysql.connection.commit()
        session['message'] = 'Your information has been updated!'
        return redirect(url_for('change_first'))
    else:
        session['message'] = 'Your entries no not match. Please re-enter the fields above.'
        return redirect(url_for('change_first'))

@app.route('/last_verify', methods = ['POST'])
def last_verify():
    userID = session.get('user_id')
    lName = session.get('last_name')
    first_entry = request.form['first_entry']
    last_entry = request.form['last_entry']
    if lName == first_entry or lName == last_entry:
        session['message'] = 'Please type in a new Last Name'
        return redirect(url_for('change_last'))
    elif first_entry == last_entry:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE users SET last_name = %s WHERE userID = %s', (first_entry, userID,))
        mysql.connection.commit()
        session['message'] = 'Your information has been updated!'
        return redirect(url_for('change_last'))
    else:
        session['message'] = 'Your entries no not match. Please re-enter the fields above.'
        return redirect(url_for('change_last'))

@app.route('/username_verify', methods = ['POST'])
def username_verify():
    userID = session.get('user_id')
    username = session.get('username')
    first_entry = request.form['first_entry']
    last_entry = request.form['last_entry']
    if username == first_entry:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE users SET login_username = %s WHERE userID = %s', (last_entry, userID,))
        mysql.connection.commit()
        session['message'] = 'Your information has been updated!'
        return redirect(url_for('change_username'))
    else:
        session['message'] = 'Your current username is incorrect. Please re-enter the fields above correctly.'
        return redirect(url_for('change_username'))

@app.route('/password_verify', methods = ['POST'])
def password_verify():
    userID = session.get('user_id')
    password = session.get('password')
    first_entry = request.form['first_entry']
    last_entry = request.form['last_entry']
    if password == first_entry:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE users SET login_password = %s WHERE userID = %s', (last_entry, userID,))
        mysql.connection.commit()
        session['message'] = 'Your information has been updated!'
        return redirect(url_for('change_password'))
    else:
        session['message'] = 'Your current password is incorrect. Please re-enter the fields above correctly.'
        return redirect(url_for('change_password'))

@app.route('/uwe_verify', methods = ['POST'])
def uwe_verify():
    userID = session.get('user_id')
    UWEemail = session.get('UWE_email')
    first_entry = request.form['first_entry']
    last_entry = request.form['last_entry']
    if '@live.uwe.ac.uk' in first_entry and last_entry:
        if UWEemail == first_entry or UWEemail == last_entry:
            session['message'] = 'Please type in a new UWE email'
            return redirect(url_for('change_uwe'))
        elif first_entry == last_entry:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE users SET UWE_email = %s WHERE userID = %s', (first_entry, userID,))
            mysql.connection.commit()
            session['message'] = 'Your information has been updated!'
            return redirect(url_for('change_uwe'))
        else:
            session['message'] = 'Your entries no not match. Please re-enter the fields above.'
            return redirect(url_for('change_uwe'))
    else:
        session['message'] = 'Please type in a UWE email'
        return redirect(url_for('change_uwe'))
    





def send_email(user_firstname, user_lastname, user_issue, user_email, template_id):
    substitution_data = {
        'user_firstname': user_firstname,
        'user_lastname': user_lastname, 
        'user_issue': user_issue
    }
    message = Mail(from_email='uweitstestemail@gmail.com',
               to_emails=user_email,
               )
    message.template_id = template_id
    message.dynamic_template_data = substitution_data

    response = sg.send(message)

def send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id):
    substitution_data = {
        'user_firstname': user_firstname,
        'user_lastname': user_lastname,
        'user_spec_issue': user_spec_issue
    }
    message = Mail(from_email='uweitstestemail@gmail.com',
               to_emails=user_email,
               )
    message.template_id = template_id
    message.dynamic_template_data = substitution_data

    response = sg.send(message)








@app.route('/process_form', methods=['POST'])
def process_form():
    user_email = request.form['UWEemail']

    if 'live.uwe.ac.uk' in user_email:
        user_firstname = request.form['firstname']
        user_lastname = request.form['lastname']
        user_issue = request.form['issue']
        user_spec_issue = request.form['specissue']
        username = request.form['username']
        wordMatch = request.form['wordMatch']
        if username != "":
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE login_username = %s', (username,))
            account = cursor.fetchone()
            if account:
                session['user_id'] = account['userID']
                userID = session['user_id']
                if user_issue == 'Reset Password':
                    resetpassword_email(user_email, user_firstname, user_lastname, user_issue)
                    emailStatus = 'Solution sent'
                    add_email_record(user_issue, userID, emailStatus)
                    session['msg'] = 'The email has been sent. Please check your junk if it has not appeared in your inbox. A record of this request has been saved on your account'
                    return redirect(url_for('issue_form'))
                elif user_issue == 'MFA not working':
                    mfa_email(user_email, user_firstname, user_lastname, user_issue)
                    emailStatus = 'Solution sent'
                    add_email_record(user_issue, userID, emailStatus)
                    session['msg'] = 'The email has been sent. Please check your junk if it has not appeared in your inbox. A record of this request has been saved on your account'
                    return redirect(url_for('issue_form'))
                elif user_issue == 'How to access marks':
                    marks_email(user_email, user_firstname, user_lastname, user_issue)
                    emailStatus = 'Solution sent'
                    add_email_record(user_issue, userID, emailStatus)
                    session['msg'] = 'The email has been sent. Please check your junk if it has not appeared in your inbox. A record of this request has been saved on your account'
                    return redirect(url_for('issue_form'))
                elif user_issue == 'How to connect to UWEs WiFi':
                    wifi_email(user_email, user_firstname, user_lastname, user_issue)
                    emailStatus = 'Solution sent'
                    add_email_record(user_issue, userID, emailStatus)
                    session['msg'] = 'The email has been sent. Please check your junk if it has not appeared in your inbox. A record of this request has been saved on your account'
                    return redirect(url_for('issue_form'))
                elif user_issue == 'How to order a new ID card':
                    id_card(user_email, user_firstname, user_lastname, user_issue)
                    emailStatus = 'Solution sent'
                    add_email_record(user_issue, userID, emailStatus)
                    session['msg'] = 'The email has been sent. Please check your junk if it has not appeared in your inbox. A record of this request has been saved on your account'
                    return redirect(url_for('issue_form'))
                elif user_issue == 'How to print things off':
                    printing_help(user_email, user_firstname, user_lastname, user_issue)
                    emailStatus = 'Solution sent'
                    add_email_record(user_issue, userID, emailStatus)
                    session['msg'] = 'The email has been sent. Please check your junk if it has not appeared in your inbox. A record of this request has been saved on your account'
                    return redirect(url_for('issue_form'))
                elif (user_issue == 'Not Specified') and (user_spec_issue != "Not Specified") and (wordMatch != ""):
                    spec_email(user_email, user_firstname, user_lastname, user_spec_issue, wordMatch)
                    emailStatus = 'Solution suggestions sent'
                    add_email_record(user_issue, userID, emailStatus)
                    session['msg'] = 'The email has been sent. Please check your junk if it has not appeared in your inbox'
                    return redirect(url_for('issue_form'))
                elif (user_issue == 'Not Specified') and (user_spec_issue != "Not Specified") and (wordMatch == ""):
                    session['msg'] = 'Due to the lack of information given, we cannot send you a solution directly. Feel free to explore our other page or contact ITS via their help desk or by phone.'
                    return redirect(url_for('issue_form'))
                else:
                    session['msg'] = "You have not selected a option in second option box. Please select 'Not Specified' in the first box and pick a related issue from the box below."
                    return redirect(url_for('issue_form'))

            else: 
                session['msg'] = 'The username you have entered is not on our system. Please fill out the form again with a valid username'
                return redirect(url_for('issue_form'))
        else:
            if user_issue == 'Reset Password':
                resetpassword_email(user_email, user_firstname, user_lastname, user_issue)
                session['msg'] = 'The email has been sent. Please check your junk if it has not appeared in your inbox'
                return redirect(url_for('issue_form'))
            elif user_issue == 'MFA not working':
                mfa_email(user_email, user_firstname, user_lastname, user_issue)
                session['msg'] = 'The email has been sent. Please check your junk if it has not appeared in your inbox'
                return redirect(url_for('issue_form'))
            elif user_issue == 'How to access marks':
                marks_email(user_email, user_firstname, user_lastname, user_issue)
                session['msg'] = 'The email has been sent. Please check your junk if it has not appeared in your inbox'
                return redirect(url_for('issue_form'))
            elif user_issue == 'How to connect to UWEs WiFi':
                wifi_email(user_email, user_firstname, user_lastname, user_issue)
                session['msg'] = 'The email has been sent. Please check your junk if it has not appeared in your inbox'
                return redirect(url_for('issue_form'))
            elif user_issue == 'How to order a new ID card':
                id_card(user_email, user_firstname, user_lastname, user_issue)
                session['msg'] = 'The email has been sent. Please check your junk if it has not appeared in your inbox'
                return redirect(url_for('issue_form'))
            elif user_issue == 'How to print things off':
                printing_help(user_email, user_firstname, user_lastname, user_issue)
                session['msg'] = 'The email has been sent. Please check your junk if it has not appeared in your inbox'
                return redirect(url_for('issue_form'))
            elif (user_issue == 'Not Specified') and (user_spec_issue != "Not Specified") and (wordMatch != ""):
                spec_email(user_email, user_firstname, user_lastname, user_spec_issue, wordMatch)
                session['msg'] = 'The email has been sent. Please check your junk if it has not appeared in your inbox'
                return redirect(url_for('issue_form'))
            elif (user_issue == 'Not Specified') and (user_spec_issue != "Not Specified") and (wordMatch == ""):
                session['msg'] = 'Due to the lack of information given, we cannot send you a solution directly. Feel free to explore our other page orcontact ITS via their help desk or by phone.'
                return redirect(url_for('issue_form'))
            else:
                session['msg'] = "You have not selected a option in second option box. Please select 'Not Specified' in the first box and pick a related issue from the box below."
                return redirect(url_for('issue_form'))
    else:
        session['msg'] = 'The email entered is not a UWE email. Please re-enter the correct credentials.'
        return redirect(url_for('issue_form'))





def resetpassword_email(user_email, user_firstname, user_lastname, user_issue):
    template_id = 'd-4930ad3e308640758e9cdb2ad98e9213'
    send_email(user_firstname, user_lastname, user_issue, user_email, template_id)

def mfa_email(user_email, user_firstname, user_lastname, user_issue):
    template_id = 'd-abb4f313296042669342b604f85472b1'
    send_email(user_firstname, user_lastname, user_issue, user_email, template_id)

def marks_email(user_email, user_firstname, user_lastname, user_issue):
    template_id = 'd-7d38a881b35940fd8dde35f66a9a7cab'
    send_email(user_firstname, user_lastname, user_issue, user_email, template_id)

def wifi_email(user_email, user_firstname, user_lastname, user_issue):
    template_id = 'd-18d79409b8ca4ec9b087836244110ae6'
    send_email(user_firstname, user_lastname, user_issue, user_email, template_id)

def id_card(user_email, user_firstname, user_lastname, user_issue):
    template_id = 'd-d98ac1d8ddbe4de0ba6fc343a0765ce0'
    send_email(user_firstname, user_lastname, user_issue, user_email, template_id)

def printing_help(user_email, user_firstname, user_lastname, user_issue):
    template_id = 'd-e529669747f14af7bc55894a234d705f'
    send_email(user_firstname, user_lastname, user_issue, user_email, template_id)







def spec_email(user_email, user_firstname, user_lastname, user_spec_issue, wordMatch):
    if (user_spec_issue == 'Passwords'):
        passwords_spec_email(user_email, user_firstname, user_lastname, user_spec_issue, wordMatch)
    elif (user_spec_issue == 'Blackboard'):
        blackboard_spec_email(user_email, user_firstname, user_lastname, user_spec_issue, wordMatch)
    elif (user_spec_issue == 'Finance'):
        finance_spec_email(user_email, user_firstname, user_lastname, user_spec_issue, wordMatch)
    elif (user_spec_issue == 'Timetable'):
        timetable_spec_email(user_email, user_firstname, user_lastname, user_spec_issue, wordMatch)
    elif (user_spec_issue == 'Personal Information'):
        personal_spec_email(user_email, user_firstname, user_lastname, user_spec_issue, wordMatch)
    elif (user_spec_issue == 'Attendance'):
        attendance_spec_email(user_email, user_firstname, user_lastname, user_spec_issue, wordMatch)
    elif (user_spec_issue == 'UWE Software'):
        software_spec_email(user_email, user_firstname, user_lastname, user_spec_issue, wordMatch)
    else:
        misc_email(user_email, user_firstname, user_lastname, user_spec_issue, wordMatch)

def passwords_spec_email(user_email, user_firstname, user_lastname, user_spec_issue, wordMatch):
    if "Change" or "Edit" in wordMatch:
        template_id = 'd-2f71b112084f4f819842d7919f2c50f2'  
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    else:
        template_id = 'd-848f54277dfb4b779b5087ccd621e5aa'  
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)

def blackboard_spec_email(user_email, user_firstname, user_lastname, user_spec_issue, wordMatch):
    if ("Access" or "Find") and ("Module" or "Modules") in wordMatch:
        template_id = 'd-633d008aae2f4f709b5e3c9ae0d5a2bf'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    elif ("Access" or "Find") and ("Lecture" or "Lectures") in wordMatch:
        template_id = 'd-cc215040640346f2a716ffa4ba032225'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    elif ("Access" or "Find") and ("Assignment" or "Assessment" or "Assignments" or "Assessments") in wordMatch:
        template_id = 'd-09ae903139094dc7b3debe41fbd0f040'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    else:
        template_id = 'd-41344086a1ca492f9e17585c955895e4'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)


def finance_spec_email(user_email, user_firstname, user_lastname, user_spec_issue, wordMatch):
    if ("Review" or "Check") and ("Payment" or "Fees") in wordMatch:
        template_id = 'd-467b069f8f1a46ab9616136bb7b16e3f'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    elif "Loan" in wordMatch:
        template_id = 'd-8929c127e45249c8b6b29cf0244444dc'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    else:
        template_id = 'd-689fb1acb3b74b13a4a9968f450e3559'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)


def timetable_spec_email(user_email, user_firstname, user_lastname, user_spec_issue, wordMatch):
    if ("See" or "View") and "Timetable" in wordMatch:
        template_id = 'd-d1a0f86069f44c72a38e33fb0a07c5d4'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    elif ("Add" and "Timetable") in wordMatch:
        template_id = 'd-480d24466c3d4af18f6f1854dc5933ac'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    else:
        template_id = 'd-dda3e801fe754ad9ab7fdf0ba8f54625'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)

def personal_spec_email(user_email, user_firstname, user_lastname, user_spec_issue, wordMatch):
    if ("Edit" or "Change") and ("Email" or "E-mail") in wordMatch:
        template_id = 'd-58a2862b6d7b4ce38a212bf869a198aa'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    elif ("Edit" or "Change") and ("Phone" or "Number" or "Phone Number") in wordMatch:
        template_id = 'd-58a2862b6d7b4ce38a212bf869a198aa'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    elif ("Edit" or "Change" or "Add") and "Address" in wordMatch:
        template_id = 'd-af9843461625406ab58cf990da13c812'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    else:
        template_id = 'd-ea3fa9aa103f4c89ad983737b81e57c5'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)


def attendance_spec_email(user_email, user_firstname, user_lastname, user_spec_issue, wordMatch):
    if ("View" or "See") and "Attendance" in wordMatch:
        template_id = 'd-84647951eb394ee1bbb44e2a53f853d4'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    elif ("Record" or "Mark") and "Attendance" in wordMatch:
        template_id = 'd-e04bd42fcde241839bb3967cbe4f3381'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    elif ("View" and "See") and "Engagement" in wordMatch:
        template_id = 'd-1a72edafd79b43feb99fb11657cc532b'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    else:
        template_id = 'd-3f74090f29e3407eaa596e4b977daf9f'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)

def software_spec_email(user_email, user_firstname, user_lastname, user_spec_issue, wordMatch):
    if "Access" and "AppsAnywhere" in wordMatch:
        template_id = 'd-71cf700b1be946d7baf2888894685a64'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    elif "Microsoft Office" or "Office 365" in wordMatch:
        template_id = 'd-8113ee70eb544995b59d0b70ea108a2e'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    else:
        template_id = 'd-d6edc185f5eb4b42b308dc5e26549788'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)

def misc_email(user_email, user_firstname, user_lastname, user_spec_issue, wordMatch):
    if ("Find" or "Access") and ("Library" and "Search") in wordMatch:
        template_id = 'd-213cd1b41c6a432384bf7f398c4d9f2c'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    elif ("Create" or "Schedule") and "Teams" in wordMatch:
        template_id = 'd-98f7c65438e44defa169dcaedde239dd '
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    elif "Borrow" and "Library" in wordMatch:
        template_id = 'd-02e7a98988784ce5999634bcab366e90'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    elif ("Book" or "Find" or "Register") and ("Events" or "Fairs" or "Event") in wordMatch:
        template_id = 'd-69c1446b279b48e0ae9a62957447a253'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)
    else:
        template_id = 'd-52df8406b0704c84ae755068de1466e0'
        send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)

        
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)