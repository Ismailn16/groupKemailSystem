from flask import Flask, render_template, request
from flask_mail import Mail, Message
import os

app = Flask(__name__)
mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'uweitstestemail@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('its_password')
#os.environ.get('its_password')
mail = Mail(app)

@app.route('/home', methods=['GET', 'POST'])
@app.route('/')

def home():
    return render_template('test.html')

@app.route('/process_form', methods=['POST'])
def process_data():
    user_firstname = request.form['firstname']
    user_lastname = request.form['lastname']
    user_email = request.form['UWEemail']
    user_issue = request.form['issue']
    user_info = request.form['furtherinfo']

    result = send_email(user_email, user_firstname, user_lastname)

    if 'live.uwe.ac.uk' in user_email:
        result = send_email(user_email, user_firstname, user_lastname)
        return result
    else:
        return "This email isn't a UWE Email, Goodbye."

app.route('/send_email', methods=['POST'])
def send_email(user_email, user_firstname, user_lastname):
    msg = Message("UWE ITS Help Service", sender = 'uweitstestemail@gmail.com', recipients = [user_email])
    msg.body = "Hi " + user_firstname + " " + user_lastname + ", This is a test email as we are currently prototyping. Thank you for your support."
    mail.send(msg)
    return "The email has been sent. Please check your junk if it has not appeared in your inbox."



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)