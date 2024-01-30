from django.urls import path
from . import views


urlpatterns = [
    path('', views.login, name="login"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('logout', views.logout_route, name="logout"),
    path('Upload',views.Upload, name='Upload'),
    path('Notify', views.Notify, name= 'Notify'),
    path('Unknownfaces', views.Unknownfaces, name='Unknownfaces')
]