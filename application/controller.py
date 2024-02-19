from flask import current_app as app
from sqlalchemy import or_
from .models import Event

@app.route('/search/<keyword>', methods=['GET'])
def search(keyword):
    search_results = []

    events = Event.query.filter(or_(Event.title.contains(keyword), Event.description.contains(keyword))).all()
    for event in events:
        search_results.append(
            {
                "event_id": event.event_id,
                "title": event.title,
                "description": event.description,
                "start_date": event.start_date.strftime('%Y-%m-%d %H:%M'),
                "end_date": event.end_date.strftime('%Y-%m-%d %H:%M'),
                "is_active": event.is_active
            }
        )
    return search_results, 200