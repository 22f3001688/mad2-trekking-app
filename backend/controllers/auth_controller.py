from flask import jsonify, request

from ..services.auth_service import AuthService


class AuthController:
    def __init__(self):
        self.auth_service = AuthService()

    def register(self):
        data = request.get_json(silent=True) or {}
        response, status_code = self.auth_service.register(data)
        return jsonify(response), status_code

    def login(self):
        data = request.get_json(silent=True) or {}
        response, status_code = self.auth_service.login(data)
        return jsonify(response), status_code

    def logout(self):
        return jsonify({"success": True, "message": "Logout not implemented"}), 200

    def get_profile(self):
        return jsonify({"success": True, "message": "Profile not implemented"}), 200
