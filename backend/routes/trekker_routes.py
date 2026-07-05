from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from ..controllers.trekker_controller import TrekkerController
from ..decorators.trekker_required import trekker_required

trekker_bp = Blueprint("trekker", __name__, url_prefix="/api/trekker")
trekker_controller = TrekkerController()


@trekker_bp.route("/dashboard", methods=["GET"])
@trekker_required
def dashboard():
    trekker_user_id = int(get_jwt_identity())
    response, status_code = trekker_controller.get_dashboard(trekker_user_id)
    return jsonify(response), status_code


@trekker_bp.route("/treks", methods=["GET"])
@trekker_required
def open_treks():
    trekker_user_id = int(get_jwt_identity())
    response, status_code = trekker_controller.get_open_treks(trekker_user_id, request.args.to_dict())
    return jsonify(response), status_code


@trekker_bp.route("/bookings", methods=["POST"])
@trekker_required
def book_trek():
    trekker_user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    response, status_code = trekker_controller.book_trek(trekker_user_id, data)
    return jsonify(response), status_code


@trekker_bp.route("/bookings", methods=["GET"])
@trekker_required
def my_bookings():
    trekker_user_id = int(get_jwt_identity())
    response, status_code = trekker_controller.get_my_bookings(trekker_user_id)
    return jsonify(response), status_code


@trekker_bp.route("/bookings/<int:booking_id>", methods=["GET"])
@trekker_required
def booking_details(booking_id):
    trekker_user_id = int(get_jwt_identity())
    response, status_code = trekker_controller.get_booking_details(trekker_user_id, booking_id)
    return jsonify(response), status_code


@trekker_bp.route("/bookings/<int:booking_id>/cancel", methods=["PUT"])
@trekker_required
def cancel_booking(booking_id):
    trekker_user_id = int(get_jwt_identity())
    response, status_code = trekker_controller.cancel_booking(trekker_user_id, booking_id)
    return jsonify(response), status_code


@trekker_bp.route("/history", methods=["GET"])
@trekker_required
def history():
    trekker_user_id = int(get_jwt_identity())
    response, status_code = trekker_controller.get_history(trekker_user_id)
    return jsonify(response), status_code


@trekker_bp.route("/profile", methods=["GET", "PUT"])
@trekker_required
def profile():
    trekker_user_id = int(get_jwt_identity())
    if request.method == "GET":
        response, status_code = trekker_controller.get_profile(trekker_user_id)
        return jsonify(response), status_code

    data = request.get_json(silent=True) or {}
    response, status_code = trekker_controller.update_profile(trekker_user_id, data)
    return jsonify(response), status_code
