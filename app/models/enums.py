import enum


class UserRole(str, enum.Enum):
    WORKER = "WORKER"
    FIELD_INSPECTOR = "FIELD_INSPECTOR"
    MINE_MANAGER = "MINE_MANAGER"
    CORPORATE_ADMIN = "CORPORATE_ADMIN"
    AUDITOR = "AUDITOR"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"


class ComplianceCategory(str, enum.Enum):
    SAFETY = "SAFETY"
    ENVIRONMENT = "ENVIRONMENT"
    LABOUR = "LABOUR"
    PRODUCTION = "PRODUCTION"


class ComplianceStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    OVERDUE = "OVERDUE"


class InspectionStatus(str, enum.Enum):
    REPORTED = "REPORTED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    AWAITING_VERIFICATION = "AWAITING_VERIFICATION"
    RESOLVED = "RESOLVED"


class SeverityLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class GrievanceCategory(str, enum.Enum):
    WORKPLACE_SAFETY = "WORKPLACE_SAFETY"
    ATTENDANCE = "ATTENDANCE"
    WAGE = "WAGE"
    CONTRACTOR = "CONTRACTOR"
    FACILITIES = "FACILITIES"
    OTHER = "OTHER"


class GrievanceStatus(str, enum.Enum):
    PENDING = "PENDING"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"


class GrievancePriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class ActionStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"


class DocumentOCRStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SyncStatus(str, enum.Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CONFLICT = "CONFLICT"


class NotificationChannel(str, enum.Enum):
    IN_APP = "IN_APP"
    EMAIL = "EMAIL"
    FCM = "FCM"
