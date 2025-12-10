from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'all_app.users'

    def ready(self):
        import all_app.users.users_signals
        
