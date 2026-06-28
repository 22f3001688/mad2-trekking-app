class Roles:
    ADMIN = "admin"
    STAFF = "staff"
    TREKKER = "trekker"


class TrekStatus:
    PENDING = "pending"
    APPROVED = "approved"
    OPEN = "open"
    CLOSED = "closed"
    COMPLETED = "completed"


class BookingStatus:
    BOOKED = "booked"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Difficulty:
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"


class PaymentStatus:
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    NOT_APPLICABLE = "not_applicable"
