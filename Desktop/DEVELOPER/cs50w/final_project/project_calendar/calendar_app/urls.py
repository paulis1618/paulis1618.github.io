from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("/login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_event", views.create_event, name="create_event"),
    path("settings", views.settings, name="settings"),
    path("allevents", views.allevents, name="allevents"),
    path("getevent/<str:name>/<str:start>/<str:end>/", views.get_event, name="getevent"),
    path("gettomorrowsevents", views.get_tomorrows_events, name="get_tomorrows_events"),
]
