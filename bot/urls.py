from django.urls import path
from . import views

urlpatterns = [
    path("zarinpal/verify/", views.verify_zarinpal, name="verify_zarinpal"),
]