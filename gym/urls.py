from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('add-member/', views.add_member, name='add_member'),
    path('record-payment/<int:member_id>/', views.record_payment, name='record_payment'),
    path('delete-member/<int:member_id>/', views.delete_member, name='delete_member'),
]

