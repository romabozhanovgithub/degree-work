import smtplib

sender = "anymail@anymail.com"
receiver = "roma.bozhanov2017.11@gmail.com"

message = f"""\
Subject: Hi Mailtrap
To: {receiver}
From: {sender}

This is a test e-mail message."""

with smtplib.SMTP("smtp-relay.sendinblue.com", 587) as server:
    server.login("roma.bozhanov2017.11@gmail.com", "xVTGaD9OPg2dZvMA")
    server.sendmail(sender, receiver, message)
