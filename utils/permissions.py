from rest_framework import permissions

from code_setting.middleware import db_ctx


class IsAuthorized(permissions.BasePermission):
    """
    Custom permission to check Company-User relation
    """
    def has_permission(self, request, view):
        try:
            # to have access to master db
            db = db_ctx.get()
            if db == 'default':
                return True

            # to have access to specific db
            user = request.user
            if user.is_superuser:
                return True
            else:
                return user.companyuser_set.filter(company__db=db).exists()
        except Exception as ex:
            print(ex.__str__())
            return False