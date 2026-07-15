from ..services.admin_service import AdminService


class AdminController:
    def __init__(self):
        self.admin_service = AdminService()

    def get_dashboard(self):
        return self.admin_service.get_dashboard_stats()

    def get_staff(self):
        return self.admin_service.get_all_staff()

    def get_users(self, filters=None):
        return self.admin_service.get_all_users_summary(filters)

    def create_staff(self, payload):
        return self.admin_service.create_staff(payload)

    def update_staff(self, staff_id, payload):
        return self.admin_service.update_staff(staff_id, payload)

    def delete_staff(self, staff_id):
        return self.admin_service.delete_staff(staff_id)

    def get_treks(self, filters=None):
        return self.admin_service.get_all_treks(filters)

    def get_booking_history(self, filters=None):
        return self.admin_service.get_booking_history(filters)

    def get_trek(self, trek_id):
        return self.admin_service.get_trek_by_id(trek_id)

    def update_trek(self, trek_id, payload):
        return self.admin_service.update_trek(trek_id, payload)

    def get_available_staff(self):
        return self.admin_service.get_available_staff()

    def assign_staff(self, trek_id, payload):
        return self.admin_service.assign_staff_to_trek(trek_id, payload)

    def create_trek(self, payload):
        return self.admin_service.create_trek(payload)
