from django.urls import path
from .views import AgreementsView,AgreementDetailView

urlpatterns =[
   path('agreements/', AgreementsView.as_view(), name='agreements_list'),
    path('agreements/<int:id>/', AgreementDetailView.as_view(), name='agreement_detail'),
    # path('api/agreements/edit/<int:pk>/', AgreementEditView.as_view(), name='agreement-edit'),
]