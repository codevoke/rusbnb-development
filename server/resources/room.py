from http import HTTPStatus
from datetime import datetime as create_date
from flask import request, abort
from flask_restful import Resource, reqparse
from models import RoomModel, RoomLocations, RoomTypes, HostFreeDatesModel

const_rooms_args = [
    "offset", "size", 
    "location", "type", 
    "rooms_count", "max_cost", "min_rate",
    "sort_by_cost"
]


def _str2date(str_date):
    separated_date = str_date.split('/')
    try:
        [dd, mm, yy] = [int(el) for el in separated_date]
        return create_date(yy, mm, dd)
    except IndexError:
        raise ValueError(f"incorrect date format: {str_date}")


def parse_dates(dates_array):
    dates = []
    for date in dates_array:
        if _str2date(date['date_from']) > _str2date(date['date_to']):
            raise ValueError("date from must be earlier than date_to")
        dates.append((
            _str2date(date['date_from']),
            _str2date(date['date_to'])
        ))
    return dates


def validate_room_location(value):
    try:
        return RoomLocations(value)
    except ValueError as error:
        abort(400, message=error)


def validate_room_type(value):
    value_list = value.split(" ")
    try:
        return [RoomTypes(value) for value in value_list]
    except ValueError as error:
        abort(400, message=error)


room_obj_args_parser = reqparse.RequestParser()
room_obj_args_parser.add_argument(
    "host_id", type=int, required=True, help="id of host user is required arg"
)
room_obj_args_parser.add_argument(
    "title", type=str, required=True, help="title of room is required arg"
)
room_obj_args_parser.add_argument(
    "subtitle", type=str, required=True, help="subtitle of room is required arg"
)
room_obj_args_parser.add_argument(
    "description", type=str, required=True, help="description of room is required arg"
)
room_obj_args_parser.add_argument(
    "price", type=int, required=True, help="price of room is required arg"
)
room_obj_args_parser.add_argument(
    "location", type=RoomLocations, required=True, help='{error_msg}'
)
room_obj_args_parser.add_argument(
    "type", type=RoomTypes, required=True, help="{error_msg}"
)
room_obj_args_parser.add_argument(
    "rooms_count", type=int, required=True, help="rooms_count is required arg"
)
room_obj_args_parser.add_argument(
    "room_dates", type=parse_dates, required=True, help="{error_msg}"
)


def get_args(*params):
    return {param: request.args.get(param) for param in params}


class Rooms(Resource):
    # /rooms

    @classmethod
    def get(cls):
        if request.args:
            kwargs = get_args(*const_rooms_args)
            
            if kwargs['type']:
                kwargs['type'] = validate_room_type(kwargs['type'])
            if kwargs['location']:
                kwargs['location'] = validate_room_location(kwargs['location'])

            response_list = RoomModel.find_with_params(**kwargs)

        else:
            response_list = RoomModel.find_all()

        if not response_list:
            return {"message": "Rooms not found"}, HTTPStatus.NOT_FOUND
        else:
            return {"rooms": [room_object.json() for room_object in response_list]}

    @classmethod
    def post(cls):
        args = room_obj_args_parser.parse_args()

        dates = args['room_dates']

        room = RoomModel(
            title=args['title'],
            subtitle=args['subtitle'],
            description=args['description'],
            location=args['location'],
            type=args['type'],
            price=args['price'],
            rooms_count=args['rooms_count'],
            host_id=args['host_id']
        )

        room.save_to_db()

        [HostFreeDatesModel(
            host_id=args['host_id'], date_from=date[0], date_to=date[1], room_id=room.id  # noqa: E501
            ).save_to_db() for date in dates]

        return {"message": f"Successfully created room", "room_id": room.id}, HTTPStatus.CREATED


class Room(Resource):
    # /rooms/{ room_id }

    @classmethod
    def get(cls, room_id):
        room = RoomModel.find_by_id(room_id)
        if room:
            return room.json(), HTTPStatus.OK
        return {"message": "Room not found"}, HTTPStatus.NOT_FOUND

    @classmethod
    def put(cls, room_id):
        req_data = room_obj_args_parser.parse_args()

        room = RoomModel.find_by_id(room_id)
        room.update(
            title=req_data['title'],
            subtitle=req_data['subtitle'],
            description=req_data['description'],
            price=req_data['price']
        )
        room.save_to_db()
        return {"message": "Successfully updated room"}, HTTPStatus.ACCEPTED

    @classmethod
    def delete(cls, room_id):
        room = RoomModel.find_by_id(room_id)
        room.delete_from_db()
        return {"message": "Successfully deleted room"}, HTTPStatus.OK
