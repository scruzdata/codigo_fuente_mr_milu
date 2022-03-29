from _contextvars import ContextVar

from django.utils.deprecation import MiddlewareMixin

db_ctx = ContextVar('var')


class WhichDatabaseToUseMIddleware(MiddlewareMixin):
    """
        Middleware to update the context var with the correct db to be routed to
    """
    @staticmethod
    def process_request(request):
        try:
            path = request.path.split('/')
            db = 'default' if path[1] in ['master', 'docs', 'auth'] else path[1]
            db_ctx.set(db)
        except Exception:
            db_ctx.set('')
