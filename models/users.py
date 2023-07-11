from main.db import db
from flask_login import UserMixin

ACCESS = {
    'user' : 0,
    'admin' : 1
}

class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True) 
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(120))
    name = db.Column(db.String(70))
    access =db.Column(db.Integer)

    def is_admin(self):
        return self.access == ACCESS['admin']
    
    def is_user(self):
        return self.access == ACCESS['user']
