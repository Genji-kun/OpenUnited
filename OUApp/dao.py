import os

from flask_login import current_user

from OUApp import app, db
from OUApp.models import RoomType, Room, Reservation, ReservationDetails, ReservationDetailsGuest, Guest
from sqlalchemy import or_, and_, not_, func, extract
import json


def load_policy():
    my_dir = os.getcwd()
    json_file_path = os.path.join(my_dir, 'static/json/policy.json')
    with open(json_file_path, encoding='utf-8') as f:
        return json.load(f)


def save_policy(data):
    my_dir = os.getcwd()
    json_file_path = os.path.join(my_dir, 'static/json/policy.json')
    with open(json_file_path, mode='w', encoding='utf-8') as f:
        return json.dump(data, f, ensure_ascii=False, indent=4)


def load_room_types(kw=None, min_price=None, max_price=None, num_of_guests=None, id=None):
    room_types = RoomType.query
    if kw:
        room_types = room_types.filter(RoomType.name.contains(kw))
    if min_price:
        room_types = room_types.filter(RoomType.price >= float(min_price))
    if max_price:
        room_types = room_types.filter(RoomType.price <= float(max_price))
    if num_of_guests:
        room_types = room_types.filter(RoomType.max_people >= float(num_of_guests))
    if id:
        room_types = room_types.filter(RoomType.id.__eq__(id))

    return room_types.all()


def get_roomtype_by_id(roomtype_id):
    return RoomType.query.filter_by(id=roomtype_id).all()


def save_reservation(details, date, orderer, rent=None):
    if details and date and orderer:
        if rent:
            r = Reservation(check_in=date["check-in"], check_out=date["check-out"],
                            orderer_name=orderer["name"], orderer_email=orderer["email"], did_guests_check_in=True)
        else:
            r = Reservation(check_in=date["check-in"], check_out=date["check-out"],
                            orderer_name=orderer["name"], orderer_email=orderer["email"], did_guests_check_in=False)
        db.session.add(r)
        for d in details.values():
            room = get_available_room(date["check-in"], date["check-out"], d['room_type_id']).first()
            rd = ReservationDetails(reservation=r, room_id=room.id, price=d['total'])
            db.session.add(rd)
            for g in d['guests'].values():
                gst = get_guest(g["name"], g["identity_number"], int(g["type"]))
                if gst:
                    rdg = ReservationDetailsGuest(reservation_details=rd, guest_id=gst.id)
                else:
                    gst = Guest(name=g["name"], gender=g["gender"], identity_number=g["identity_number"],
                                address=g["address"], guest_type=g["type"])
                    db.session.add(gst)
                    rdg = ReservationDetailsGuest(reservation_details=rd, guest=gst)
                db.session.add(rdg)
        db.session.commit()


def get_available_room(start, end, room_type_id):
    subquery = db.session.query(ReservationDetails.room_id) \
        .join(Reservation, Reservation.id.__eq__(ReservationDetails.reservation_id)) \
        .filter(or_(and_(Reservation.check_in >= start, Reservation.check_in <= end),
                    and_(Reservation.check_out >= start, Reservation.check_out <= end),
                    and_(Reservation.check_in <= start, Reservation.check_out >= end)))
    query = db.session.query(Room.id) \
        .filter(Room.room_type_id.__eq__(room_type_id)) \
        .filter(Room.id.notin_(subquery))
    return query


def get_unavailable_room(start, end, room_type_id):
    subquery = db.session.query(ReservationDetails.room_id) \
        .join(Reservation, Reservation.id.__eq__(ReservationDetails.reservation_id)) \
        .filter(or_(and_(Reservation.check_in >= start, Reservation.check_in <= end),
                    and_(Reservation.check_out >= start, Reservation.check_out <= end),
                    and_(Reservation.check_in <= start, Reservation.check_out >= end)))
    query = db.session.query(Room.id) \
        .filter(Room.room_type_id.__eq__(room_type_id)) \
        .filter(Room.id.in_(subquery))
    return query


def get_guest(name=None, identity_number=None, guest_type=None, id=None):
    guest = Guest.query
    if name:
        guest = guest.filter(Guest.name.__eq__(name))
    if identity_number:
        guest = guest.filter(Guest.identity_number.__eq__(identity_number))
    if guest_type:
        guest = guest.filter(Guest.guest_type.__eq__(guest_type))
    if id:
        guest = guest.filter(Guest.id.__eq__(id))
    if guest.first():
        return guest.first()
    else:
        return None


def revenue_stats_by_month(month):
    query = db.session.query(RoomType.id, RoomType.name, func.sum(ReservationDetails.price)) \
        .join(Reservation, Reservation.id.__eq__(ReservationDetails.reservation_id)) \
        .join(Room, Room.id.__eq__(ReservationDetails.room_id)) \
        .join(RoomType, RoomType.id.__eq__(Room.room_type_id)) \
        .filter(Reservation.is_paid.__eq__(True)) \
        .filter(extract('month', Reservation.created_date) == month) \
        .group_by(RoomType.id, RoomType.name)

    return query.all()


def total_by_month(month):
    query = db.session.query(func.sum(ReservationDetails.price)) \
        .join(Reservation, Reservation.id.__eq__(ReservationDetails.reservation_id)) \
        .filter(Reservation.is_paid.__eq__(True)) \
        .filter(extract('month', Reservation.created_date) == month)

    return query.first()


def frequency_room_type(month):
    subquery = db.session.query(func.count(Room.room_type_id)). \
        join(ReservationDetails, ReservationDetails.room_id.__eq__(Room.id)). \
        join(Reservation, Reservation.id.__eq__(ReservationDetails.reservation_id)). \
        filter(Room.room_type_id.__eq__(RoomType.id)). \
        filter(Reservation.did_guests_check_in.__eq__(True)). \
        filter(extract('month', Reservation.created_date) == month).label('số lần xuất hiện')

    query = db.session.query(RoomType.id, RoomType.name, subquery)

    return query.all()


def total_reservation_details(month):
    query = db.session.query(ReservationDetails.id). \
        join(Reservation, Reservation.id.__eq__(ReservationDetails.reservation_id)). \
        filter(Reservation.did_guests_check_in.__eq__(True)). \
        filter(extract('month', Reservation.created_date) == month)

    return query.count()


def get_reservation(check_in=None, check_out=None, orderer_name=None, orderer_email=None, is_paid=None,
                    did_guests_check_in=None, id=None):
    query = Reservation.query
    if check_in:
        query = query.filter(Reservation.check_in.__eq__(check_in))
    if check_out:
        query = query.filter(Reservation.check_out.__eq__(check_out))
    if orderer_name:
        query = query.filter(Reservation.orderer_name.contains(orderer_name))
    if orderer_email:
        query = query.filter(Reservation.orderer_email.contains(orderer_email))
    if is_paid is not None and is_paid == False:
        query = query.filter(Reservation.is_paid.__eq__(False))
    if is_paid is not None and is_paid == True:
        query = query.filter(Reservation.is_paid.__eq__(True))
    if did_guests_check_in is not None and did_guests_check_in == False:
        query = query.filter(Reservation.did_guests_check_in.__eq__(False))
    if did_guests_check_in is not None and did_guests_check_in == True:
        query = query.filter(Reservation.did_guests_check_in.__eq__(True))
    if id:
        query = query.filter(Reservation.id.__eq__(id))

    return query.all()


def get_reservation_details(reservation_id=None):
    query = db.session.query(ReservationDetails, Room.id, RoomType.name).join(Room, Room.id.__eq__(
        ReservationDetails.room_id)). \
        join(RoomType, RoomType.id.__eq__(Room.room_type_id))

    if reservation_id:
        query = query.filter(ReservationDetails.reservation_id.__eq__(reservation_id))

    return query.all()


def get_reservation_details_guests(reservation_details_id=None):
    query = ReservationDetailsGuest.query

    if reservation_details_id:
        query = query.filter(ReservationDetailsGuest.reservation_details_id.__eq__(reservation_details_id))

    return query.all()


def change_reservation(reservation_id):
    r = Reservation.query.filter(Reservation.id.__eq__(reservation_id)).first()
    r.did_guests_check_in = True
    db.session.commit()


def pay_reservation(reservation_id):
    r = Reservation.query.filter(Reservation.id.__eq__(reservation_id)).first()
    r.is_paid = True
    r.user = current_user
    db.session.commit()


