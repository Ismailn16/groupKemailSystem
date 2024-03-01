from flask import Flask, render_template, request, redirect
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)
sg_api = os.environ.get('SENDGRID_API_KEY')
sg = SendGridAPIClient(sg_api)

@app.route('/home', methods=['GET', 'POST'])
@app.route('/')

def home():
    return render_template('test.html')

@app.route('/postemail', methods = ['GET', 'POST'])
def postemail():
    return render_template('postemail.html')

@app.route('/noinfo', methods = ['GET', 'POST'])
def noinfo():
    return render_template('noinfo.html')

@app.route('/fakeemail', methods = ['GET', 'POST'])
def failemail():
    return render_template('fakeemail.html')

@app.route('/process_form', methods=['POST'])
def process_form():
    user_email = request.form['UWEemail']

    if 'live.uwe.ac.uk' in user_email:
        user_firstname = request.form['firstname']
        user_lastname = request.form['lastname']
        user_issue = request.form['issue']
        user_spec_issue = request.form['specissue']
        if user_issue == 'Reset Password':
            resetpassword_email(user_email, user_firstname, user_lastname, user_issue)
            return redirect('/postemail')
        elif user_issue == 'MFA not working':
            mfa_email(user_email, user_firstname, user_lastname, user_issue)
            return redirect('/postemail')
        elif user_issue == 'How to access marks':
            marks_email(user_email, user_firstname, user_lastname, user_issue)
            return redirect('/postemail')
        elif user_issue == 'How to connect to UWEs WiFi':
            wifi_email(user_email, user_firstname, user_lastname, user_issue)
        elif (user_issue == 'Not Specified') and (user_spec_issue != ""):
            spec_email(user_email, user_firstname, user_lastname, user_spec_issue)
            return redirect('/postemail')
        else:
            return redirect('/noinfo')
    else:
        return redirect('/fakeemail')

def resetpassword_email(user_email, user_firstname, user_lastname, user_issue):
    template_id = 'd-ffa70cf693e74289894e9305175a58f1'
    
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
    return "The email has been sent. Please check your junk if it has not appeared in your inbox."

def mfa_email(user_email, user_firstname, user_lastname, user_issue):
    template_id = 'd-7ddb1ea78ad54e29b1836974946f2d1f'
    
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
    return "The email has been sent. Please check your junk if it has not appeared in your inbox."

def marks_email(user_email, user_firstname, user_lastname, user_issue):
    template_id = 'd-57fd53429b1a4dc184e4847bd57f1ba5'
    
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
    return "The email has been sent. Please check your junk if it has not appeared in your inbox."

def wifi_email(user_email, user_firstname, user_lastname, user_issue):
    template_id = 'd-57fd53429b1a4dc184e4847bd57f1ba5'
    
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
    return "The email has been sent. Please check your junk if it has not appeared in your inbox."

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
    return "The email has been sent. Please check your junk if it has not appeared in your inbox."

def blackboard_spec_email(user_email, user_firstname, user_lastname, user_spec_issue):
    template_id = 'euibhckdalihc;kns-9'
    
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
    return "The email has been sent. Please check your junk if it has not appeared in your inbox."

def finance_spec_email(user_email, user_firstname, user_lastname, user_spec_issue):
    template_id = 'euibhckdalihc;kns-9'
    
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
    return "The email has been sent. Please check your junk if it has not appeared in your inbox."

def timetable_spec_email(user_email, user_firstname, user_lastname, user_spec_issue):
    template_id = 'euibhckdalihc;kns-9'
    
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
    return "The email has been sent. Please check your junk if it has not appeared in your inbox."

def personal_spec_email(user_email, user_firstname, user_lastname, user_spec_issue):
    template_id = 'euibhckdalihc;kns-9'
    
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
    return "The email has been sent. Please check your junk if it has not appeared in your inbox."

def wifi_spec_email(user_email, user_firstname, user_lastname, user_spec_issue):
    template_id = 'euibhckdalihc;kns-9'
    
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
    return "The email has been sent. Please check your junk if it has not appeared in your inbox."

def attendance_spec_email(user_email, user_firstname, user_lastname, user_spec_issue):
    template_id = 'euibhckdalihc;kns-9'
    
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
    return "The email has been sent. Please check your junk if it has not appeared in your inbox."

def software_spec_email(user_email, user_firstname, user_lastname, user_spec_issue):
    template_id = 'euibhckdalihc;kns-9'
    
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
    return "The email has been sent. Please check your junk if it has not appeared in your inbox."


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)