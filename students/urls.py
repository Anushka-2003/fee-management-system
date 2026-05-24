from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list, name='list'),
    path('add/', views.student_add, name='add'),
    path('<int:pk>/', views.student_detail, name='detail'),
    path('<int:pk>/edit/', views.student_edit, name='edit'),
    path('<int:pk>/delete/', views.student_delete, name='delete'),
    path('years/', views.year_list, name='year_list'),
    path('years/add/', views.year_add, name='year_add'),
    path('years/<int:pk>/set-current/', views.year_set_current, name='year_set_current'),
    path('years/<int:pk>/carry-forward/', views.year_carry_forward, name='year_carry_forward'),
    path('classes/', views.class_list, name='class_list'),
    path('classes/add/', views.class_add, name='class_add'),
]
