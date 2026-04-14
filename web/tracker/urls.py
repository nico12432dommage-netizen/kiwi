from django.urls import path
from . import views

urlpatterns = [
    # Páginas HTML
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('pallets/', views.pallets_page, name='pallets'),
    path('ventas/', views.ventas_page, name='ventas'),
    path('reportes/', views.reportes_page, name='reportes'),
    path('usuarios/', views.usuarios_page, name='usuarios'),

    # API — Pallets
    path('api/pallets/', views.api_pallets, name='api_pallets'),
    path('api/pallets/<int:pallet_id>/', views.api_pallet_detail, name='api_pallet_detail'),

    # API — Ventas
    path('api/ventas/', views.api_ventas, name='api_ventas'),
    path('api/ventas/<int:venta_id>/', views.api_venta_detail, name='api_venta_detail'),

    # API — Usuarios
    path('api/usuarios/', views.api_usuarios, name='api_usuarios'),
    path('api/usuarios/<int:user_id>/', views.api_usuario_detail, name='api_usuario_detail'),

    # API — Reportes
    path('api/reportes/por-dia/', views.api_reportes_por_dia, name='api_reportes_por_dia'),
    path('api/reportes/por-mes/', views.api_reportes_por_mes, name='api_reportes_por_mes'),
    path('api/estadisticas/', views.api_estadisticas, name='api_estadisticas'),

    # Exportar a Excel
    path('api/export/ventas/', views.export_ventas, name='export_ventas'),
    path('api/export/pallets/', views.export_pallets, name='export_pallets'),
]
