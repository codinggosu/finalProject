from django.urls import path
from catalog import views


urlpatterns = [
    path('', views.index, name='index'),
    path('items', views.ItemListView.as_view(), name='items'),
    path('users', views.UserListView.as_view(), name='users'),
    path('rates', views.RateListView.as_view(), name='rates'),
    path('predictions', views.PredictionListView.as_view(), name='predictions'),
    path('save_rate', views.save_rate, name='save_rate'),
    path('prediction', views.prediction, name='prediction'),
    path('prediction_result', views.prediction_result, name='prediction_result'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('sign_up_page', views.sign_up_page, name='sign_up_page')
]