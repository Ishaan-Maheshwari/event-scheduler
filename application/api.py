from datetime import datetime
from flask import request
from flask_restful import Resource
from application.database import db
from application.models import Event, Recurrence
from flask_restful import reqparse

class EventList(Resource):
    def get(self, event_id=None):
        if event_id:
            event = Event.query.filter_by(event_id=event_id).first()
            if not event:
                return {'message': 'Event not found'}, 404
            res = {
                    "event_id": event.event_id,
                    "title": event.title,
                    "description": event.description,
                    "start_date": event.start_date.strftime('%Y-%m-%d %H:%M'),
                    "end_date": event.end_date.strftime('%Y-%m-%d %H:%M'),
                    "is_active": event.is_active
                }
            return res, 200
        all_events = []
        events = Event.query.order_by(Event.start_date).all()
        for event in events:
            all_events.append(
                {
                    "event_id": event.event_id,
                    "title": event.title,
                    "description": event.description,
                    "start_date": event.start_date.strftime('%Y-%m-%d %H:%M'),
                    "end_date": event.end_date.strftime('%Y-%m-%d %H:%M'),
                    "is_active": event.is_active
                }
            )
        return all_events, 200

    def post(self):
        data = request.get_json()
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True, help='Title is required')
        parser.add_argument('description', type=str, required=True, help='Description is required')
        parser.add_argument('start_date', type=str)
        parser.add_argument('end_date', type=str)
        args = parser.parse_args()
        if args['start_date'] == None:
            args['start_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        if args['end_date'] == None:
            args['end_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        start_date = datetime.strptime(args['start_date'], '%Y-%m-%d %H:%M')
        end_date = datetime.strptime(args['end_date'], '%Y-%m-%d %H:%M')
        if args['start_date'] > args['end_date']:
            return {"status": "Error", "message" : "Start date cannot be greater than end date"}, 400
        event = Event(title=args['title'], description=args['description'], start_date=start_date, end_date=end_date)
        db.session.add(event)
        db.session.commit()
        return {"status": "Success", "message" : "Event created successfully"}, 201
    
    def put(self):
        data = request.get_json()
        parser = reqparse.RequestParser()
        parser.add_argument('event_id', type=int, required=True, help='Event ID is required')
        parser.add_argument('title', type=str)
        parser.add_argument('description', type=str)
        parser.add_argument('start_date', type=str)
        parser.add_argument('end_date', type=str)
        args = parser.parse_args()
        event = Event.query.filter_by(event_id=args['event_id']).first()
        if not event:
            return {'message': 'Event not found'}, 404
        if args['title']:
            event.title = args['title']
        if args['description']:
            event.description = args['description']
        if args['start_date']:
            event.start_date = args['start_date']
        if args['end_date']:
            event.end_date = args['end_date']
        db.session.commit()
        return event.to_dict(), 200
    
    def delete(self, event_id):
        # check if event_id is mot null or an int
        if event_id == None:
            return {"Status": "Error", "message": "event id is required"},400
        event = Event.query.filter_by(event_id=event_id).first()
        if not event:
            return {'message': 'Event not found'}, 404
        db.session.delete(event)
        db.session.commit()
        return {"Status": "Success", "message": "event deleted successfully"}, 200

class ReccuringEvent(Resource):
    def get(self, event_id=None):
        # get all event that is recurring with latest recurrence from today
        if event_id:
            event = Event.query.filter_by(event_id=event_id).first()
            if not event:
                return {'message': 'Event not found'}, 404
            recurrence = Recurrence.query.filter_by(event_id=event_id).first()
            if not recurrence:
                return {'message': 'Recurrence not found'}, 404
            res = {
                    "event_id": event.event_id,
                    "title": event.title,
                    "description": event.description,
                    "start_date": event.start_date.strftime('%Y-%m-%d %H:%M'),
                    "end_date": event.end_date.strftime('%Y-%m-%d %H:%M'),
                    "is_active": event.is_active,
                    "recurrence_id": recurrence.recurrence_id,
                    "type": recurrence.type,
                    "interval": recurrence.interval,
                    "day_of_week": recurrence.day_of_week,
                    "month_of_year": recurrence.month_of_year,
                    "end_date": recurrence.end_date.strftime('%Y-%m-%d %H:%M')
                }
            return res, 200
        all_events = []
        events = Event.query.filter_by(is_recurring=True).all()
        for event in events:
            recurrence = Recurrence.query.filter_by(event_id=event.event_id).first()
            all_events.append(
                {
                    "event_id": event.event_id,
                    "title": event.title,
                    "description": event.description,
                    "start_date": event.start_date.strftime('%Y-%m-%d %H:%M'),
                    "end_date": event.end_date.strftime('%Y-%m-%d %H:%M'),
                    "is_active": event.is_active,
                    "recurrence_id": recurrence.recurrence_id,
                    "type": recurrence.type,
                    "interval": recurrence.interval,
                    "day_of_week": recurrence.day_of_week,
                    "month_of_year": recurrence.month_of_year,
                    "end_date": recurrence.end_date.strftime('%Y-%m-%d %H:%M')
                }
            )
        return all_events, 200

    def post(self):
        data = request.get_json()
        parser = reqparse.RequestParser()
        parser.add_argument('event_id', type=int, required=True, help='Event ID is required')
        parser.add_argument('type', type=str, required=True, help='Type is required')
        parser.add_argument('interval', type=int, default=1, help='Interval is required')
        parser.add_argument('day_of_week', type=int)
        parser.add_argument('month_of_year', type=int)
        parser.add_argument('end_date', type=str)
        args = parser.parse_args()
        event = Event.query.filter_by(event_id=args['event_id']).first()
        if not event:
            return {'message': 'Event not found'}, 404
        if args['type'] == 'daily':
            day_of_week = None
            month_of_year = None
        if args['type'] == 'weekly':
            day_of_week = args['day_of_week']
            month_of_year = None
        if args['type'] == 'monthly':
            day_of_week = None
            month_of_year = args['month_of_year']
        if args['end_date']:
            end_date = datetime.strptime(args['end_date'], '%Y-%m-%d %H:%M')
        recurrence = Recurrence(event_id=args['event_id'], type=args['type'], interval=args['interval'], day_of_week=day_of_week, month_of_year=month_of_year, end_date=end_date)
        event.is_recurring = True
        db.session.add(recurrence)
        db.session.commit()
        return {"status": "Success", "message" : "Recurrence created successfully"}, 201
    
    def put(self, recurrence_id):
        if recurrence_id == None:
            return {"Status": "Error", "message": "recurrence id is required"},400
        data = request.get_json()
        parser = reqparse.RequestParser()
        parser.add_argument('type', type=str)
        parser.add_argument('interval', type=int)
        parser.add_argument('day_of_week', type=int)
        parser.add_argument('month_of_year', type=int)
        parser.add_argument('end_date', type=str)
        args = parser.parse_args()
        recurrence = Recurrence.query.filter_by(recurrence_id=args['recurrence_id']).first()
        if not recurrence:
            return {'message': 'Recurrence not found'}, 404
        if args['type']:
            recurrence.type = args['type']
        if args['interval']:
            recurrence.interval = args['interval']
        if args['day_of_week']:
            recurrence.day_of_week = args['day_of_week']
        if args['month_of_year']:
            recurrence.month_of_year = args['month_of_year']
        if args['end_date']:
            recurrence.end_date = args['end_date']
        db.session.commit()
        return recurrence.to_dict(), 200
    
    def delete(self, recurrence_id):
        # check if recurrence_id is mot null or an int
        if recurrence_id == None:
            return {"Status": "Error", "message": "recurrence id is required"},400
        recurrence = Recurrence.query.filter_by(recurrence_id=recurrence_id).first()
        if not recurrence:
            return {'message': 'Recurrence not found'}, 404
        db.session.delete(recurrence)
        db.session.commit()
        return {"Status": "Success", "message": "recurrence deleted successfully"}, 200