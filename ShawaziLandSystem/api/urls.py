from django.urls import path
from .views import LandListView,LandDetailView, LandMapDetailView, LandMapListView
from .views import AgreementsView,AgreementDetailView,CheckBlockchainView,NotificationsListView, TransactionsDetailView,SellerNotificationView, PropertyListView





urlpatterns = [
    path('land-details/', LandListView.as_view(), name='land-detail-list'),
    path('land-details/<int:pk>/', LandDetailView.as_view(), name='land-detail-detail'),
    path('map-url/<int:pk>/', LandMapDetailView.as_view(), name='land-map-url'),
    path('land-map/', LandMapListView.as_view({'get': 'list', 'post': 'create'}), name='land-map-view') 
    path('agreements/', AgreementsView.as_view(), name='agreements_list'),
    path('agreements/<int:id>/', AgreementDetailView.as_view(), name='agreement_detail'),
    path('api/agreements/edit/<int:pk>/', AgreementEditView.as_view(), name='agreement-edit'), 
    path("transactions/",TransactionsListView.as_view(), name="transactions_list_view"),
    path('check-blockchain/', CheckBlockchainView.as_view(), name='check_blockchain'),
    path("express-interest/",NotificationsListView.as_view(), name="send_notification"),
    path("transactions/<int:id>/", TransactionsDetailView.as_view(), name="transactions_detail_view"),
    path("property/<int:land_id>/", NotificationsListView.as_view(), name='property_details'),
    path('interested/', SellerNotificationView.as_view(), name='seller_notifications'),
    path('properties/', PropertyListView.as_view(), name='property_list'),
  
]


 

