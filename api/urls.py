from turtle import home
from django.urls import path
from agreements import views
from .views import AgreementDetailView, Create_Room, RoomCreateView, Index_View, Login_View, Message_View,otp_verification, AgreementsView, CheckBlockchainView, LandListView,LandDetailView, LandMapDetailView, LandMapListView,  RegisteredUsersView,  TransactionsDetailView, TransactionsListView, UserProfileAPIView, forgot_password, login_user, logout_user, password_reset_confirm, reset_password, user_create
from api import views
from.views import RoomCreateView
from django.urls import path, re_path
from api.views import ChatMessageListCreateView, SendInvitationView, UserListView
from chatroom import consumers
from api.views import chat_room
from . import views



urlpatterns = [
    path('register/', user_create, name='user_create'),
    path('login/', login_user, name='login_user'),
    path('logout/', logout_user, name='logout_user'),
    path('password-reset-confirm/', password_reset_confirm, name='password_reset_confirm'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/', reset_password, name='reset_password'),
    path('user-profile/<int:user_id>/', UserProfileAPIView.as_view(), name='user_profile'),
    path('users/', RegisteredUsersView.as_view(), name='registered_users'),
    path('count/users/', RegisteredUsersView.as_view(), name='registered_users'),
    path('otp_verification/', views.otp_verification, name='otp_verification'),
    path('land-details/', LandListView.as_view(), name='land-detail-list'),
    path('count/land-details/', LandListView.as_view(), name='land-detail-list'),
    path('land-detail/', LandDetailView.as_view(), name='land-detail-detail'),
    path('map-url/<int:pk>/', LandMapDetailView.as_view(), name='land-map-url'),
    path('land-map/', LandMapListView.as_view({'get': 'list', 'post': 'create'}), name='land-map-view'), 
    path('agreements/', AgreementsView.as_view(), name='agreements_list'),
    path('count/agreements/', AgreementsView.as_view(), name='agreements_list'),
    path('agreements/<int:id>/', AgreementDetailView.as_view(), name='agreement_detail'),
    path("transactions/",TransactionsListView.as_view(), name="transactions_list_view"),
    path("count/transactions/",TransactionsListView.as_view(), name="transactions_list_view"),
    path('check-blockchain/', CheckBlockchainView.as_view(), name='check_blockchain'),
    path("transactions/<int:id>/", TransactionsDetailView.as_view(), name="transactions_detail_view"),
    path('login/', Login_View, name='login'),
    path('create-room/', RoomCreateView.as_view(), name='create_room'),
    path('room/<str:room_name>/', Message_View, name='messages'),
    path('messages/', ChatMessageListCreateView.as_view(), name='chat_message_list_create'),
    path('chats/message/', ChatMessageListCreateView.as_view(), name='chat_message_create'),
    path('send_invitation/', SendInvitationView.as_view(), name='send_invitation'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('chat/<str:room_name>/', chat_room, name='chat_room'),


  
]

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<user_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
 

