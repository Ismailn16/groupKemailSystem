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

    
    return render_template('create_account.html', msg=msg)


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
                elif (user_issue == 'Not Specified') and (user_spec_issue != "Not Specified"):
                    spec_email(user_email, user_firstname, user_lastname, user_spec_issue)
                    emailStatus = 'Broad solution suggestions sent'
                    add_email_record(user_issue, userID, emailStatus)
                    session['msg'] = 'The email has been sent. Please check your junk if it has not appeared in your inbox'
                    return redirect(url_for('issue_form'))
                elif (user_issue == 'Not Specified') and (user_spec_issue == 'Not Specified'):
                    session['msg'] = 'As you have not selected either option, we cannot assist you. Please contact ITS via their help desk or by phone.'
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
            elif (user_issue == 'Not Specified') and (user_spec_issue != "Not Specified"):
                spec_email(user_email, user_firstname, user_lastname, user_spec_issue)
                session['msg'] = 'The email has been sent. Please check your junk if it has not appeared in your inbox'
                return redirect(url_for('issue_form'))
            elif (user_issue == 'Not Specified') and (user_spec_issue == 'Not Specified'):
                session['msg'] = 'As you have not selected either option, we cannot assist you. Please contact ITS via their help desk or by phone.'
                return redirect(url_for('issue_form'))
            else:
                session['msg'] = "You have not selected a option in second option box. Please select 'Not Specified'in the first box and pick a related issue from the box below."
                return redirect(url_for('issue_form'))
    else:
        session['msg'] = 'The email entered is not a UWE email. Please re-enter the correct credentials.'
        return redirect(url_for('issue_form'))





def resetpassword_email(user_email, user_firstname, user_lastname, user_issue):
    template_id = 'd-ffa70cf693e74289894e9305175a58f1'
    send_email(user_firstname, user_lastname, user_issue, user_email, template_id)

def mfa_email(user_email, user_firstname, user_lastname, user_issue):
    template_id = 'd-7ddb1ea78ad54e29b1836974946f2d1f'
    send_email(user_firstname, user_lastname, user_issue, user_email, template_id)

def marks_email(user_email, user_firstname, user_lastname, user_issue):
    template_id = 'd-57fd53429b1a4dc184e4847bd57f1ba5'
    send_email(user_firstname, user_lastname, user_issue, user_email, template_id)

def wifi_email(user_email, user_firstname, user_lastname, user_issue):
    template_id = 'd-a197450e4ab6457da1e02305eff33e7c'
    send_email(user_firstname, user_lastname, user_issue, user_email, template_id)







def spec_email(user_email, user_firstname, user_lastname, user_spec_issue):
    if (user_spec_issue == 'Passwords'):
        passwords_spec_email(user_email, user_firstname, user_lastname, user_spec_issue)
    elif (user_spec_issue == 'Blackboard'):
        blackboard_spec_email(user_email, user_firstname, user_lastname, user_spec_issue)
    elif (user_spec_issue == 'Finance'):
        finance_spec_email(user_email, user_firstname, user_lastname, user_spec_issue)
    elif (user_spec_issue == 'Timetable'):
        timetable_spec_email(user_email, user_firstname, user_lastname, user_spec_issue)
    elif (user_spec_issue == 'Personal Information'):
        personal_spec_email(user_email, user_firstname, user_lastname, user_spec_issue)
    elif (user_spec_issue == 'WiFi'):
        wifi_spec_email(user_email, user_firstname, user_lastname, user_spec_issue)
    elif (user_spec_issue == 'Attendance'):
        attendance_spec_email(user_email, user_firstname, user_lastname, user_spec_issue)
    elif (user_spec_issue == 'UWE Software'):
        software_spec_email(user_email, user_firstname, user_lastname, user_spec_issue)

def passwords_spec_email(user_email, user_firstname, user_lastname, user_spec_issue):
    template_id = 'euibhckdalihc;kns-9'
    send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)

def blackboard_spec_email(user_email, user_firstname, user_lastname, user_spec_issue):
    template_id = 'euibhckdalihc;kns-9'
    send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)

def finance_spec_email(user_email, user_firstname, user_lastname, user_spec_issue):
    template_id = 'euibhckdalihc;kns-9'
    send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)

def timetable_spec_email(user_email, user_firstname, user_lastname, user_spec_issue):
    template_id = 'euibhckdalihc;kns-9'
    send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)

def personal_spec_email(user_email, user_firstname, user_lastname, user_spec_issue):
    template_id = 'euibhckdalihc;kns-9'
    send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)

def wifi_spec_email(user_email, user_firstname, user_lastname, user_spec_issue):
    template_id = 'euibhckdalihc;kns-9'
    send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)

def attendance_spec_email(user_email, user_firstname, user_lastname, user_spec_issue):
    template_id = 'euibhckdalihc;kns-9'
    send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)

def software_spec_email(user_email, user_firstname, user_lastname, user_spec_issue):
    template_id = 'euibhckdalihc;kns-9'
    send_spec_email(user_firstname, user_lastname, user_spec_issue, user_email, template_id)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)