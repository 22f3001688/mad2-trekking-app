from flask import Blueprint, jsonify, request

from ..controllers.admin_controller import AdminController
from ..decorators.admin_required import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")
admin_controller = AdminController()


@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard():
    response = admin_controller.get_dashboard()
    return jsonify(response), 200


@admin_bp.route("/staff", methods=["GET"])
@admin_required
def get_staff():
    response = admin_controller.get_staff()
    return jsonify(response), 200


@admin_bp.route("/staff", methods=["POST"])
@admin_required
def create_staff():
    payload = request.get_json(silent=True) or {}
    response, status_code = admin_controller.create_staff(payload)
    return jsonify(response), status_code


@admin_bp.route("/treks", methods=["GET"])
@admin_required
def get_treks():
    filters = {
        "search": request.args.get("search", ""),
        "difficulty": request.args.get("difficulty", ""),
        "status": request.args.get("status", ""),
    }
    response = admin_controller.get_treks(filters)
    return jsonify(response), 200


@admin_bp.route("/bookings/history", methods=["GET"])
@admin_required
def get_booking_history():
    filters = {
        "search": request.args.get("search", ""),
        "status": request.args.get("status", "historical"),
    }
    response, status_code = admin_controller.get_booking_history(filters)
    return jsonify(response), status_code


@admin_bp.route("/treks/<int:trek_id>", methods=["GET"])
@admin_required
def get_trek(trek_id):
    response, status_code = admin_controller.get_trek(trek_id)
    return jsonify(response), status_code


@admin_bp.route("/treks/<int:trek_id>", methods=["PUT"])
@admin_required
def update_trek(trek_id):
    payload = request.get_json(silent=True) or {}
    response, status_code = admin_controller.update_trek(trek_id, payload)
    return jsonify(response), status_code


@admin_bp.route("/staff/available", methods=["GET"])
@admin_required
def get_available_staff():
    response = admin_controller.get_available_staff()
    return jsonify(response), 200


@admin_bp.route("/treks/<int:trek_id>/assign-staff", methods=["PUT"])
@admin_required
def assign_staff(trek_id):
    payload = request.get_json(silent=True) or {}
    response, status_code = admin_controller.assign_staff(trek_id, payload)
    return jsonify(response), status_code


@admin_bp.route("/treks", methods=["POST"])
@admin_required
def create_trek():
    payload = request.get_json(silent=True) or {}
    response, status_code = admin_controller.create_trek(payload)
    return jsonify(response), status_code


@admin_bp.route("/staff/<int:staff_id>", methods=["PUT"])
@admin_required
def update_staff(staff_id):
    payload = request.get_json(silent=True) or {}
    response, status_code = admin_controller.update_staff(staff_id, payload)
    return jsonify(response), status_code


@admin_bp.route("/staff/<int:staff_id>", methods=["DELETE"])
@admin_required
def delete_staff(staff_id):
    response, status_code = admin_controller.delete_staff(staff_id)
    return jsonify(response), status_code
