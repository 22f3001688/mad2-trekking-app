from ..services.trekker_service import TrekkerService


class TrekkerController:
    def __init__(self):
        self.trekker_service = TrekkerService()

    def get_dashboard(self, trekker_user_id):
        return self.trekker_service.get_dashboard(trekker_user_id)

    def get_open_treks(self, trekker_user_id, filters=None):
        return self.trekker_service.get_open_treks(trekker_user_id, filters)

    def book_trek(self, trekker_user_id, data):
        return self.trekker_service.book_trek(trekker_user_id, data)

    def get_my_bookings(self, trekker_user_id):
        return self.trekker_service.get_my_bookings(trekker_user_id)

    def get_booking_details(self, trekker_user_id, booking_id):
        return self.trekker_service.get_booking_details(trekker_user_id, booking_id)

    def cancel_booking(self, trekker_user_id, booking_id):
        return self.trekker_service.cancel_booking(trekker_user_id, booking_id)

    def get_history(self, trekker_user_id):
        return self.trekker_service.get_history(trekker_user_id)

    def get_profile(self, trekker_user_id):
        return self.trekker_service.get_profile(trekker_user_id)

    def update_profile(self, trekker_user_id, data):
        return self.trekker_service.update_profile(trekker_user_id, data)
