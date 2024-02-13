import sendgrid
import os
from sendgrid.helpers.mail import *

sg = sendgrid.SendGridAPIClient('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')
from_email = Email('uweitstestemail@gmail.com')
to_email = To('ismailnoor.102@gmail.com')
subject = "Sending with SendGrid is Fun"
content = Content("text/plain", "and easy to do anywhere, even with Python")
mail = Mail(from_email, to_email, subject, content)
response = sg.client.mail.send.post(request_body=mail.get())
print(response.status_code)
print(response.body)
print(response.headers)