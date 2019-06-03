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
    path('sign_up_page', views.sign_up_page, name='sign_up_page'),
    path('test', views.test, name='test'),
    path('mypage', views.my_page, name='my_page'),
    path('social', views.social, name='social'),
    path('friend_review', views.friend_review, name='friend_review'),
    path('rate-detail/<int:pk>', views.RateDetailView.as_view(), name='rate-detail'),
    path('allitems', views.all_items, name='allitems'),

]
