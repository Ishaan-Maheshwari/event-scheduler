from datetime import datetime
from flask import request
from flask_restful import Resource
from application.database import db
from application.models import Event
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

