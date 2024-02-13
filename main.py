from flask import Flask, render_template, request
import sendgrid
from sendgrid.helpers.mail import *

app = Flask(__name__)
sg = sendgrid.SendGridAPIClient('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')

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

    if 'live.uwe.ac.uk' in user_email:
        result = send_email(user_email, user_firstname, user_lastname)
        return result
    else:
        return "This email isn't a UWE Email, Goodbye."

app.route('/send_email', methods=['POST'])
def send_email(user_email, user_firstname, user_lastname):
    from_email = 'uweitstestemail@gmail.com'
    to_email = To(user_email)
    subject = "UWE ITS Test Email"
    content = Content("text/plain", "Hi " + user_firstname + " " + user_lastname + ", This is a test email as we are currently prototyping this system. Thank you for your support!")
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return "The email has been sent. Please check your junk if it has not appeared in your inbox."



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)