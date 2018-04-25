from django.conf.urls import url
from core import views
from django.urls import include

v1_patterns = [
    url(r'^accounts$', views.AccountsList.as_view()),
    url(r'^payments$', views.PaymentsList.as_view()),
]

urlpatterns = [
    url(r'^v1/', include(v1_patterns)),
]
