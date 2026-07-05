from ..services.staff_service import StaffService


class StaffController:
    def __init__(self):
        self.staff_service = StaffService()

    def get_dashboard(self, staff_user_id):
        return self.staff_service.get_dashboard(staff_user_id)

    def get_my_treks(self, staff_user_id):
        return self.staff_service.get_my_treks(staff_user_id)

    def get_trek_participants(self, staff_user_id, trek_id):
        return self.staff_service.get_trek_participants(staff_user_id, trek_id)

    def update_trek_status(self, staff_user_id, trek_id, payload):
        return self.staff_service.update_trek_status(staff_user_id, trek_id, payload)

    def complete_trek(self, staff_user_id, trek_id):
        return self.staff_service.complete_trek(staff_user_id, trek_id)

    def update_trek_slots(self, staff_user_id, trek_id, payload):
        return self.staff_service.update_trek_slots(staff_user_id, trek_id, payload)
