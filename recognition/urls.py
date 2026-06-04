from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path("", views.landing_page, name="landing"),
    path("recognize/", views.recognize_page, name="recognize"),
    path("text-to-isl/", views.text_to_isl_page, name="text_to_isl"),
    path("learn/", views.learn_isl_page, name="learn_isl"),
    path("login/", views.login_page, name="login_page"),
    path("register/", views.register_page, name="register_page"),
    path("gesture/", views.gesture_page, name="gesture"),
    # APIs
    path("predict/", views.predict, name="predict"),
    path("predict-gesture/", views.predict_gesture, name="predict_gesture"),
    path("process-text/", views.process_text, name="process_text"),
]