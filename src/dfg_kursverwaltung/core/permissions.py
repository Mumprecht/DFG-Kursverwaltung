from enum import StrEnum

from dfg_kursverwaltung.core.models import User, UserRole


class Permission(StrEnum):
    PERSON_READ = "person_read"
    PERSON_WRITE = "person_write"

    COURSE_TYPE_READ = "course_type_read"
    COURSE_TYPE_WRITE = "course_type_write"

    COURSE_READ = "course_read"
    COURSE_WRITE = "course_write"

    COURSE_DAY_READ = "course_day_read"
    COURSE_DAY_WRITE = "course_day_write"

    LOCATION_READ = "location_read"
    LOCATION_WRITE = "location_write"

    ASSIGNMENT_READ = "assignment_read"
    ASSIGNMENT_WRITE = "assignment_write"

    EXAM_RESULT_READ = "exam_result_read"
    EXAM_RESULT_WRITE = "exam_result_write"

    SEARCH = "search"

    IMPORT = "import"
    EXPORT = "export"

    BACKUP = "backup"
    RESTORE = "restore"
    DATABASE_RESET = "database_reset"

    USER_ADMIN = "user_admin"
    SETTINGS = "settings"

    CHANGE_OWN_PASSWORD = "change_own_password"


ROLE_PERMISSIONS: dict[
    UserRole,
    frozenset[Permission],
] = {
    UserRole.ADMINISTRATOR: frozenset(
        Permission
    ),

    UserRole.COURSE_MANAGEMENT: frozenset(
        {
            Permission.PERSON_READ,
            Permission.PERSON_WRITE,

            Permission.COURSE_TYPE_READ,

            Permission.COURSE_READ,
            Permission.COURSE_WRITE,

            Permission.COURSE_DAY_READ,
            Permission.COURSE_DAY_WRITE,

            Permission.LOCATION_READ,
            Permission.LOCATION_WRITE,

            Permission.ASSIGNMENT_READ,
            Permission.ASSIGNMENT_WRITE,

            Permission.EXAM_RESULT_READ,
            Permission.EXAM_RESULT_WRITE,

            Permission.SEARCH,

            Permission.IMPORT,
            Permission.EXPORT,

            Permission.BACKUP,

            Permission.CHANGE_OWN_PASSWORD,
        }
    ),

    UserRole.INSTRUCTOR: frozenset(
        {
            Permission.PERSON_READ,

            Permission.COURSE_TYPE_READ,

            Permission.COURSE_READ,
            Permission.COURSE_DAY_READ,
            Permission.LOCATION_READ,

            Permission.ASSIGNMENT_READ,
            Permission.ASSIGNMENT_WRITE,

            Permission.EXAM_RESULT_READ,
            Permission.EXAM_RESULT_WRITE,

            Permission.SEARCH,

            Permission.CHANGE_OWN_PASSWORD,
        }
    ),

    UserRole.READER: frozenset(
        {
            Permission.PERSON_READ,

            Permission.COURSE_TYPE_READ,

            Permission.COURSE_READ,
            Permission.COURSE_DAY_READ,
            Permission.LOCATION_READ,

            Permission.ASSIGNMENT_READ,
            Permission.EXAM_RESULT_READ,

            Permission.SEARCH,

            Permission.CHANGE_OWN_PASSWORD,
        }
    ),

    UserRole.INACTIVE: frozenset(),
}


def permissions_for_role(
    role: UserRole | str,
) -> frozenset[Permission]:
    role = UserRole(role)

    return ROLE_PERMISSIONS[role]


def has_permission(
    user_or_role: User | UserRole | str,
    permission: Permission | str,
) -> bool:
    permission = Permission(permission)

    if isinstance(user_or_role, User):
        role = user_or_role.rolle
    else:
        role = UserRole(user_or_role)

    return (
        permission
        in permissions_for_role(role)
    )


def require_permission(
    user_or_role: User | UserRole | str,
    permission: Permission | str,
) -> None:
    permission = Permission(permission)

    if has_permission(
        user_or_role,
        permission,
    ):
        return

    raise PermissionError(
        "Für diese Aktion fehlt die "
        f"Berechtigung: {permission.value}"
    )
