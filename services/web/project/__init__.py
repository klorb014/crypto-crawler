from apscheduler.schedulers.background import BackgroundScheduler

import time
import atexit
import requests
import yaml
import json
import smtplib
import ssl
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, DateTime
import os


#from models import Result

app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)

port = 465  # For SSL


def print_date_time():
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))


@app.route("/")
def home():
    return jsonify(home="Crypto Market Cap & Pricing Data Provided By Nomics")


def handle_config(namespace):
    with open("config.yaml", 'r') as stream:
        try:
            config = yaml.safe_load(stream)[namespace]
            return config
        except yaml.YAMLError as exc:
            print(exc)


def get_crypto_value(send_email=False):
    config = handle_config("api")
    coins = ",".join(config["crypto"])
    query = {
        "key": config["key"], "ids": coins, "interval": config["interval"], "per-page": "100", "page": "1"}

    response = requests.get(config['url'], params=query)
    json_data = json.loads(response.text)

    print({"coin": json_data[0]['id'], "price": json_data[0]['price'],
          "timestamp": json_data[0]['price_timestamp']})

    db.session.add(Prices(crypto=json_data[0]['id'], price=json_data[0]['price'],
                   timestamp=json_data[0]['price_timestamp']))
    db.session.commit()

    # print(response["price"])
    # print(response["price_timestamp"])
    # if(send_email):
    #    send_alert_email(str({"coin": json_data[0]['id'], "price": json_data[0]['price'],
    #                          "timestamp": json_data[0]['price_timestamp']}))


def send_alert_email(msg):
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        config = handle_config("email")
        sender_email = "{0}@gmail.com".format(config["user"])
        password = config["password"]
        server.login(sender_email, password)
        # TODO: Send email here
        receiver_email = "ken.lorbetskie@gmail.com"
        message = """\
        Subject: CRYPTO PRICES

        {0}
        This message is sent from Python.""".format(msg)
        server.sendmail(sender_email, receiver_email, message)


scheduler = BackgroundScheduler()
scheduler.add_job(func=print_date_time, trigger="interval", seconds=180)
scheduler.add_job(func=get_crypto_value, trigger="interval", seconds=180)
scheduler.start()


class Prices(db.Model):
    __tablename__ = 'prices'

    id = db.Column(db.Integer, primary_key=True)
    crypto = db.Column(db.String())
    price = db.Column(db.Float())
    timestamp = db.Column(DateTime)

    def __init__(self, crypto, price, timestamp):
        self.crypto = crypto
        self.price = price
        self.timestamp = timestamp

    def __repr__(self):
        return '<id {}>'.format(self.id)


# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    app.run(debug=True)
