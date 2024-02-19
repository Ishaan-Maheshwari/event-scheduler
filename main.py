import os
from flask import Flask
from flask_restful import Api
from application.config import LocalDevelopmentConfig
from application.database import db

app = None
api = None

def create_app():
    app = Flask(__name__, template_folder="templates")
    if os.getenv('ENV', "development") == "production":
      raise Exception("Currently no production config is setup.")
    else:
      print("Staring Local Development")
      app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    api = Api(app)
    app.app_context().push()  
    return app, api

app, api = create_app()

@app.route('/')
def index():
  return "Hello World"

@app.route('/do_init_setup')
def do_init_setup():
  with app.app_context():
    db.create_all()
  return "Database setup complete"

from application.api import EventList
from application.api import ReccuringEvent

api.add_resource(EventList, '/events', '/event/<int:event_id>')
api.add_resource(ReccuringEvent, '/recurrences', '/recurrence/<int:recurrence_id>')

from application.controller import *


if __name__ == '__main__':
  # Run the Flask app
  app.run(host='0.0.0.0',port=8080)
