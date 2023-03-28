from todoapp import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Benutzermodell
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    lists = db.relationship('List', backref='owner', lazy=True)

    def __repr__(self):
        return f"User('{self.username}')"

    # Passwort setzen    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Passwort überprüfen
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
   # Favoritenlisten abrufen    
    @property
    def favorite_lists(self):
        return List.query.join(FavoriteList).filter(FavoriteList.user_id == self.id).all()
    
    def to_dict(self):
        user_dict = {
            'id': self.id,
            'username': self.username,
            'lists': [{'id': lst.id, 'title': lst.title} for lst in self.lists]
        }
        return user_dict

# Listenmodell
class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    items = db.relationship('Item', backref='list', lazy=True)
    public = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    favorites = db.relationship('FavoriteList', backref='list', lazy=True)

    def __repr__(self):
        return f"List('{self.title}')"
    
    @property
    def owner(self):
        return User.query.filter_by(id=self.user_id).first()
    
    @property
    def item_count(self):
        return len(self.items)
    
    def favorited_by(self, user):
        return FavoriteList.query.filter_by(user_id=user.id, list_id=self.id).first()
    
# Favoritenlistenmodell
class FavoriteList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), nullable=False)

    def __repr__(self):
        return f"FavoriteList('{self.user_id}', '{self.list_id}')"
    
    @property
    def user(self):
        return User.query.filter_by(id=self.user_id).first()
    
    @property
    def list(self):
        return List.query.filter_by(id=self.list_id).first()

# Itemmodell
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    deadline = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='Not Started')
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), nullable=False)

    def __repr__(self):
        return f"Item('{self.description}', '{self.completed}', '{self.deadline}', '{self.status}')"

    @property
    def list(self):
        return List.query.filter_by(id=self.list_id).first()

# Benutzerlader für Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
