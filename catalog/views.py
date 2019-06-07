from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from .models import Item, Rate, User, Prediction, Candidates2
from django.views import generic
from catalog.forms import RateForm
from django.http import HttpResponse
import pandas as pd
from sklearn.model_selection import train_test_split
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import cross_validate
from surprise import SVD
from surprise import BaselineOnly, KNNBaseline
from surprise.model_selection import cross_validate, KFold
from surprise.model_selection import GridSearchCV
from surprise import accuracy
from collections import defaultdict
from django.db import connections
import pickle
import os
from django.core import serializers
from django.http import HttpResponseRedirect
from .forms import ReviewForm
from django.core.paginator import Paginator
def index(request):
    """View function for home page of site."""
    item = Item.objects.all().count()
    user = User.objects.all().count()
    rate = Rate.objects.all().count()
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    context = {
        'item': item,
        'user': user,
        'rate': rate,
        'num_visits': num_visits,
    }
    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class ItemListView(generic.ListView):
    model = Item
    paginate_by = 10


class ItemDetailView(generic.DetailView):
    model = Item

class UserDetailView(generic.DetailView):
    model = User

class UserListView(generic.ListView):
    model = User
    paginate_by = 10


class RateListView(generic.ListView):
    model = Rate
    paginate_by = 10

class RateDetailView(generic.DetailView):
    model = Rate


class PredictionListView(generic.ListView):
    model = Prediction
    paginate_by = 20


def save_rate(request):
    if request.POST:
        print("okay")
        print(request.POST)
        if Rate.objects.filter(user_id=int(request.POST.get('content[user_id]')), item_id=int(request.POST.get('content[item_id]'))):
            print("이미 입력된 데이터입니다.")
            pass
        else:
            obj = Rate(user_id=int(request.POST.get('content[user_id]')),
                       item_id=int(request.POST.get('content[item_id]')),
                       rate=int(request.POST.get('content[rate]')))
            obj.save()
        print(request.POST.get('content[item_id]'))
        return render(request, "catalog/item_list.html")
    return HttpResponse(status=405)


def get_top_n(predictions, n, given_user_id):

    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        if uid == given_user_id:
            top_n[uid].append((iid, est))

    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n


def recommend(given_user_id):
    given_user_id = int(given_user_id)
    print(given_user_id)
    queryset = Rate.objects.all()
    query, params = queryset.query.as_sql(compiler='django.db.backends.sqlite3.compiler.SQLCompiler', connection=connections['default'])
    df = pd.read_sql_query(query, con=connections['default'], params=params)
    print("load df")
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[['user_id', 'item_id', 'rate']], reader)
    trainset = data.build_full_trainset()
    testset = trainset.build_anti_testset()
    algo = SVD()
    algo.fit(trainset)
    print("fit 완료")
    predictions = algo.test(testset)
    print("예측 완료")
    top_10_items = get_top_n(predictions, 10, given_user_id)
    print("top 10 선별 완료, 길이 : %s" % len(list(top_10_items.keys())))
    print(top_10_items[given_user_id])
    for item_prediction in top_10_items[given_user_id]:
        if Prediction.objects.filter(item_id=item_prediction[0], user_id=given_user_id):
            pass
        else:
            obj = Prediction(user_id=given_user_id, item_id=item_prediction[0], prediction=round(item_prediction[1], 1))
            obj.save()
    print("해당 유저 %s 에 대한 데이터 저장완료" % given_user_id)
    return [item_prediction[0] for item_prediction in top_10_items[given_user_id]]


def prediction(request):
    return render(request, "prediction.html")


def prediction_result(request):
    user_id = request.POST.get('uid')
    print(user_id)
    item_id_list = recommend(user_id)
    print(item_id_list)
    predictions = Prediction.objects.filter(user_id=user_id).order_by('-prediction')
    items = Item.objects.filter(item_id__in=item_id_list)
    context = {
        'predictions': predictions,
        'items': items
    }
    return render(request, "prediction_result.html", context=context)


def recommend_friend(given_user_id):
    queryset = Rate.objects.all()
    query, params = queryset.query.as_sql(compiler='django.db.backends.sqlite3.compiler.SQLCompiler', connection=connections['default'])
    df = pd.read_sql_query(query, con=connections['default'], params=params)
    print("load data")
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[['user_id', 'item_id', 'rate']], reader)
    trainset = data.build_full_trainset()
    sim_options = {'name': 'pearson_baseline'}
    algo = KNNBaseline(sim_options=sim_options)
    algo.fit(trainset)
    print(given_user_id)
    given_user_id = int(given_user_id)
    _from = get_object_or_404(User, user_id=given_user_id)
    inner_id = algo.trainset.to_inner_uid(given_user_id)
#    to_inner_uid(), to_inner_iid(), to_raw_uid(), and to_raw_iid()
    neighbors = algo.get_neighbors(inner_id, k=5)
    results = [algo.trainset.to_raw_uid(inner_user_id) for inner_user_id in neighbors]
    print('The 5 nearest neighbors of Given User Id:')

    for raw_user_id in results:
        _to = get_object_or_404(User, user_id=int(raw_user_id))
        # print(raw_user_id,Candidates2.objects.filter(user_from=user_from,user_to=user_to))
        if Candidates2.objects.filter(user_from=_from):
            if Candidates2.objects.filter(user_from=_from, user_to=_to):
                print("user from , to 다 일치")
                pass
            else:
                cand = Candidates2.objects.get(user_from=_from)
                cand.user_to.add(_to)
                print("user from만 일치, to 추가")
        else:
            cand=Candidates2.objects.create()
            cand.user_from.add(_from)
            cand.user_to.add(_to)
        print("해당 유저 %s 에 대한 데이터 저장완료" % given_user_id)
    return results


def friend(request):
    return render(request, "friend.html")


def recommended_friends(request):
    user_id = request.POST.get('uid')
    print(user_id)
    recommend_friend(user_id)
    user_from = get_object_or_404(User, user_id=user_id)
    users = user_from.user_from.all()
    datas = []
    for user in users[0].user_to.all():
        datas.append(user.user_id)
    friends = [get_object_or_404(User, user_id=user_id) for user_id in datas]
    context = {
        "users": friends
    }

    return render(request, "recommended_friends.html", context=context)


def sign_up(request):
    if request.POST:
        if User.objects.filter(user_id=int(request.POST.get('user_id'))):
            print("이미 입력된 데이터입니다.")
            return HttpResponse("이미 존재하는 유저 아이디 입니다. \n 다른 아이디를 입력해주세요 !<li><a href='sign_up_page'>다시 입력 하기</a></li>")
        else:
            obj = User(user_id=int(request.POST.get('user_id')),
                       skin_type=request.POST.get('skin_type'),
                       age=int(request.POST.get('age')),
                       gender=request.POST.get('gender'))
            obj.save()
            request.session['user_id'] = request.POST.get('user_id')
        return render(request, "catalog/sign_up.html")
    return HttpResponse(status=405)


def sign_up_page(request):
    return render(request, "catalog/sign_up.html")




def all_items(request):
    # data = serializers.serialize( "python", Item.objects.all())
    items = Item.objects.all()
    paginator = Paginator(items, 11)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    # print(test)
    # ids = [item.item_id for item in items]
    # names = [item.name for item in items]
    # brands= [item.brand for item in items]
    # images = [item.image for item in items]

    # names = [i['fields']['name'] for i in data]
    # brands = [i['fields']['brand'] for i in data]
    # images = [i['fields']['image'] for i in data]
    # texts = [i['fields']['texts'] for i in data]
    # lst = [(i['fields']['name'], i['fields']['brand'], i['fields']['image'],i['fields']['texts'],) for i in data]
    combined = [(item.item_id, item.name, item.brand, item.image,) for item in items]
    context = {
    'items':combined,
    'products': products,
    }
    # print(context)
    return render(request, 'catalog/all_products.html', context)


def test(request):
    return render(request, 'newindex.html')


def my_page(request):
  return render(request, 'catalog/mypage.html')


def social(request):
    return render(request, 'catalog/social.html')

def friend_review(request):
    rate = Rate.objects.all().count()
    return render(request, 'catalog/friendreview.html')

#
# def test_form(request, pk):
#     # if this is a POST request we need to process the form data
#     context = Item.objects.filter(item_id=pk)
#     # print("before methods")
#     if request.methods == 'POST':
#         print("inside test form")
#     #     # form = ReviewForm(request.POST)
#     #     # print("form itself")
#     #     # print(form)
#     #     # print("pringing indexed")
#     #     # print(type(form["your_review"]))
#     #     # print("method is post")
#         # print(request.POST['your_review'])
#         # if form.is_valid():
#         # return HttpResponseRedirect('thanks')
#     # else:
#     #     # form = ReviewForm()
#     #     print("else!!!")
#     #     # return HttpResponseRedirect('404')
#     return render(request, 'name.html', {'item': context[0]})


def test_form(request,pk):
    item_instance= get_object_or_404(Item, item_id=pk)
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ReviewForm(request.POST)
        current_user = request.user
        print("current_user id" , current_user.id)
        # check whether it's valid:
        if form.is_valid():
            newrate = Rate()
            newrate.review = form.cleaned_data['your_review']
            newrate.rate = form.cleaned_data['your_rate']
            # newrate.user_id = form.cleaned_data['user']
            # incremented_id = Rate.objects.count()+1
            # print(incremented_id, " incremented_id")
            newrate.item_id = pk
            if current_user.id == None:
                user_id = 1234
                newrate.user_id = user_id
            else:
                newrate.user_id = current_user.id
            newrate.save()
            return HttpResponse('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ReviewForm()

    return render(request, 'name.html', {'form': form, 'item': item_instance})

def thanks(request):
    return HttpResponse("THANKS!!!!!!!!")
