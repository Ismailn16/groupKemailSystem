from flask import Flask, render_template, request
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'UWEITSTestEmail@gmail.com'
app.config['MAIL_PASSWORD'] = 'ITPtesting2024'

@app.route('/home')
@app.route('/')

def home():
    return render_template('test.html')

#def send_email():
#    user_firstname = request.form('firstname')
#    user_lastname = request.form('lastname')
#    user_email = request.form('UWEemail')
 #   user_issue = request.form('issue')
 #   user_info = request.form('furtherinfo')

 #   if 'live.uwe.ac.uk' in user_email:
  #      if user_issue == 'issue1':
  #          if 'password' & 'forgot' in user_info:
                


if __name__ == '__main__':
    app.run(debug=True)