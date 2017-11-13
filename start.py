from flask import Flask, current_app
import logging
import os
import sys
import json
from kafka import KafkaConsumer, TopicPartition
from threading import Thread
import eventlet
import requests

from context import app, logbook_db, roles_db, socketio

from pages import pages_blueprint

from services.business_service import business_service_blueprint
from services.socket_service import socket_service_blueprint, kafka_2_websocket

__author__ = 'mshankar@slac.stanford.edu'


# Initialize application.
app = Flask("psdm_ws_template")
app.secret_key = "This is a secret key that is somewhat temporary."
app.debug = bool(os.environ.get('DEBUG', "False"))

if app.debug:
    print("Sending all debug messages to the console")
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    logging.getLogger('kafka').setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

# Set the expiration for static files
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300; 

# Register routes.
app.register_blueprint(pages_blueprint, url_prefix="")
app.register_blueprint(business_service_blueprint, url_prefix="/ws/business")
app.register_blueprint(socket_service_blueprint, url_prefix="/ws/socket")

logbook_db.init_app(app)
roles_db.init_app(app)

# Socket Initialization
eventlet.monkey_patch()
socketio.init_app(app, async_mode="eventlet")

kafka_2_websocket(["elog"])

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)
