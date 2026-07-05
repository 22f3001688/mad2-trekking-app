from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from ..controllers.staff_controller import StaffController
from ..decorators.staff_required import staff_required

staff_bp = Blueprint("staff", __name__, url_prefix="/api/staff")
staff_controller = StaffController()


@staff_bp.route("/dashboard", methods=["GET"])
@staff_required
def dashboard():
    staff_user_id = int(get_jwt_identity())
    response, status_code = staff_controller.get_dashboard(staff_user_id)
    return jsonify(response), status_code


@staff_bp.route("/my-treks", methods=["GET"])
@staff_required
def my_treks():
    staff_user_id = int(get_jwt_identity())
    response, status_code = staff_controller.get_my_treks(staff_user_id)
    return jsonify(response), status_code


@staff_bp.route("/treks/<int:trek_id>/participants", methods=["GET"])
@staff_required
def trek_participants(trek_id):
    staff_user_id = int(get_jwt_identity())
    response, status_code = staff_controller.get_trek_participants(staff_user_id, trek_id)
    return jsonify(response), status_code


@staff_bp.route("/treks/<int:trek_id>/status", methods=["PUT"])
@staff_required
def update_trek_status(trek_id):
    staff_user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}
    response, status_code = staff_controller.update_trek_status(staff_user_id, trek_id, payload)
    return jsonify(response), status_code


@staff_bp.route("/treks/<int:trek_id>/complete", methods=["PUT"])
@staff_required
def complete_trek(trek_id):
    staff_user_id = int(get_jwt_identity())
    response, status_code = staff_controller.complete_trek(staff_user_id, trek_id)
    return jsonify(response), status_code


@staff_bp.route("/treks/<int:trek_id>/slots", methods=["PUT"])
@staff_required
def update_trek_slots(trek_id):
    staff_user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}
    response, status_code = staff_controller.update_trek_slots(staff_user_id, trek_id, payload)
    return jsonify(response), status_code
