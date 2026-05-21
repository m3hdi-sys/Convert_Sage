from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('convertisseur.urls')), # C'est cette ligne qui branche ton application !
]