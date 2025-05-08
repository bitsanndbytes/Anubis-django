from django.urls import path
from . import views


urlpatterns = [
    path('', views.login, name="login"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('logout', views.logout_route, name="logout"),
    path('Upload',views.Upload, name='Upload'),
    path('Notify', views.Notify, name= 'Notify'),
    path('Unknownfaces', views.Unknownfaces, name='Unknownfaces'),
    path('save_camera/', views.save_camera, name='save_camera'),
    path('stop_stream/<int:camera_id>/', views.stop_stream, name='stop_stream'),
    path('settings/', views.settings_view, name='settings'),
    path('activity-log/', views.activity_log, name='activity_log'),
    path('change-password/', views.change_password, name='change_password'),
]