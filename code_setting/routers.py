from code_setting.middleware import db_ctx

from code_setting.settings import DATABASES, LOCAL_APPLICATIONS


class CodeMasterRouter:
    """
    A router to control all database operations on models in the ermm application.
    """

    @staticmethod
    def db_for_read(model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        try:
            if db_ctx.get() == 'default' and model._meta.app_label == 'xmaster':
                return 'default'
            return None
        except:
            return None

    @staticmethod
    def db_for_write(model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        try:
            if db_ctx.get() == 'default' and model._meta.app_label == 'xmaster':
                return 'default'
            return None
        except:
            return None

    @staticmethod
    def allow_relation(obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label == 'xmaster' or obj2._meta.app_label == 'xmaster':
            return True
        return None

    @staticmethod
    def allow_migrate(db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the 'auth_db' database.
        """
        if app_label == 'xmaster':
            return db == 'default'
        return None


class TycheToolCompaniesRouter:
    """
    A router to control all database operations on models in the code_setting app
    """

    @staticmethod
    def db_for_read(model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        try:
            db = db_ctx.get()
            if db != 'default' and model._meta.app_label in LOCAL_APPLICATIONS:
                return db
            return None
        except:
            return None

    @staticmethod
    def db_for_write(model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        try:
            db = db_ctx.get()
            if db != 'default' and model._meta.app_label in LOCAL_APPLICATIONS:
                return db
            return None
        except:
            return None

    @staticmethod
    def allow_relation(obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label in LOCAL_APPLICATIONS or obj2._meta.app_label in LOCAL_APPLICATIONS:
            return True
        return None

    @staticmethod
    def allow_migrate(db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the 'auth_db' database.
        """
        if app_label in LOCAL_APPLICATIONS:
            return db in [k for k in DATABASES.keys() if k != 'default']
        return None
