class DatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'open5gs':
            return 'open5gs_db'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'open5gs':
            return 'open5gs_db'
        return 'default'

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'open5gs_db':
            return False
        return db == 'default'
