from flask import jsonify, request
from todoapp.models import User, List, Item
from todoapp import db
from . import api

# Alle Benutzer abrufen
@api.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([user.username for user in users])

# Benutzerattribute abrufen
@api.route('/user/<username>', methods=['GET'])
def get_user_attributes(username):
    user = User.query.filter_by(username=username).first()
    if user is not None:
        return jsonify(user.to_dict())
    else:
        return jsonify({"error": "User not found"}), 404

# Anzahl der Benutzer abrufen
@api.route('/users/count', methods=['GET'])
def get_total_users_count():
    count = User.query.count()
    return jsonify({"count": count})

# Anzahl der Listen abrufen
@api.route('/lists/count', methods=['GET'])
def get_total_lists_count():
    count = List.query.count()
    return jsonify({"count": count})

# Anzahl abgeschlossener Tasks des Benutzers abrufen
@api.route('/user/<username>/completed/count', methods=['GET'])
def get_completed_items_count(username):
    user = User.query.filter_by(username=username).first()
    if user is not None:
        completed_items = sum([item.completed for lst in user.lists for item in lst.items])
        return jsonify({"count": completed_items})
    else:
        return jsonify({"error": "User not found"}), 404

# Anzahl der Tasks "in Bearbeitung" des Benutzers abrufen
@api.route('/user/<username>/in_progress/count', methods=['GET'])
def get_in_progress_items_count(username):
    user = User.query.filter_by(username=username).first()
    if user is not None:
        in_progress_items = sum([item.status == 'In Progress' for lst in user.lists for item in lst.items])
        return jsonify({"count": in_progress_items})
    else:
        return jsonify({"error": "User not found"}), 404

# Anzahl der nicht gestarteten Tasks des Benutzers abrufen
@api.route('/user/<username>/not_started/count', methods=['GET'])
def get_not_started_items_count(username):
    user = User.query.filter_by(username=username).first()
    if user is not None:
        not_started_items = sum([item.status == 'Not Started' for lst in user.lists for item in lst.items])
        return jsonify({"count": not_started_items})
    else:
        return jsonify({"error": "User not found"}), 404
