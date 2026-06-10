from django.urls import path
from . import views

urlpatterns = [
    path("", views.learn_page, name="learn_page"),
    path("api/save-progress/", views.save_progress, name="save_progress"),
    path("api/load-progress/", views.load_progress, name="load_progress"),
]
