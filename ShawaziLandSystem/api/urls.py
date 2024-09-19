from django.urls import path
from .views import LandListView,LandDetailView, LandMapDetailView, LandMapListView





urlpatterns = [
    path('land-details/', LandListView.as_view(), name='land-detail-list'),
    path('land-details/<int:pk>/', LandDetailView.as_view(), name='land-detail-detail'),
    path('map-url/<int:pk>/', LandMapDetailView.as_view(), name='land-map-url'),
    path('land-map/', LandMapListView.as_view({'get': 'list', 'post': 'create'}), name='land-map-view')  
  
]
