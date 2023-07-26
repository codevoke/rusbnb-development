from db import db
from sqlalchemy import ARRAY


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(87), nullable=False)
    name_image = db.Column(db.String(80), nullable=True, default='Default.png')
    booked_rooms = db.Column(db.String(), nullable=False)

    def json(self):
        return {
            'id': self.id,
            'username': self.username,
            'name_image': self.name_image,
            'booked_rooms': self.booked_rooms 
        }

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, username, password):
        self.username = username
        self.password = password

    def add_booked_room(self, room_id: int):
        if self.booked_rooms:
            self.booked_rooms += f" {room_id}"
        else:
            self.booked_rooms = str(room_id)

    def get_booked_rooms(self):
        if self.booked_rooms:
            return [int(x) for x in self.booked_rooms.split(' ')]
