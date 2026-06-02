from django.apps import AppConfig


class RestauranteConfig(AppConfig):
    name = 'restaurante'
    
    def ready(self):
        import restaurante.signals
