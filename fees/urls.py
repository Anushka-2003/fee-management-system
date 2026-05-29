from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('entry/', views.fee_entry_select, name='fee_entry_select'),
    path('entry/<int:student_pk>/', views.fee_entry, name='fee_entry'),
    path('record/<int:pk>/', views.fee_record_detail, name='record_detail'),
    path('record/<int:pk>/receipt/', views.receipt_html, name='receipt_html'),
    path('record/<int:pk>/receipt/pdf/', views.receipt_pdf, name='receipt_pdf'),
    path('batch/<uuid:batch_id>/receipt/', views.batch_receipt_html, name='batch_receipt_html'),
    path('batch/<uuid:batch_id>/receipt/pdf/', views.batch_receipt_pdf, name='batch_receipt_pdf'),
    path('reports/monthly/', views.monthly_report, name='monthly_report'),
    path('reports/total/', views.total_collection, name='total_collection'),
    path('reports/defaulters/', views.defaulters, name='defaulters'),
    path('structure/', views.fee_structure_list, name='structure_list'),
    path('structure/edit/<int:year_pk>/<int:class_pk>/', views.fee_structure_edit, name='structure_edit'),
    path('api/fee-structure/', views.api_fee_structure, name='api_fee_structure'),
]
