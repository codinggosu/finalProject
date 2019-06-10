from django.shortcuts import render, redirect, get_object_or_404, render_to_response
# Create your views here.
from .models import Item, Rate, Profile, Prediction, Candidates2
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
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def index(request):
    """View function for home page of site."""
    item = Item.objects.all().count()

    user = Profile.objects.all().count()
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


class ProfileDetailView(generic.DetailView):
    model = Profile


class ProfileListView(generic.ListView):
    model = Profile
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
        if Rate.objects.filter(user_id=int(request.user), item_id=int(request.POST.get('content[item_id]'))):
            print("이미 입력된 데이터입니다.")
            pass
        else:
            obj = Rate(user_id=int(request.user),
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
    # given_user_id = int(get_object_or_404(User, username=given_user_id).id)
    print(given_user_id, "recommend function printing given_user_id")
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
    # return [item_prediction[0] for item_prediction in top_10_items[given_user_id]]
    return top_10_items[given_user_id]


def prediction(request):
    return render(request, "prediction.html")

@login_required
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


def recommend_friends(request):
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
    for given_user_id in set(df['user_id']):
        print(given_user_id)
        given_user_id = int(given_user_id)
        _from = get_object_or_404(Profile, profile_id=given_user_id)
        inner_id = algo.trainset.to_inner_uid(given_user_id)
    #    to_inner_uid(), to_inner_iid(), to_raw_uid(), and to_raw_iid()
        neighbors = algo.get_neighbors(inner_id, k=5)
        results = [algo.trainset.to_raw_uid(inner_user_id) for inner_user_id in neighbors]
        print('The 5 nearest neighbors of Given User Id:')

        for raw_user_id in results:
            _to = get_object_or_404(Profile, user_id=int(raw_user_id))
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
    return render(request, "recommend_completed.html")


@login_required
def recommended_friends(request):
    profile_id = int(request.user.id)
    print(profile_id)
    user_from = get_object_or_404(Profile, profile_id=profile_id)
    print("y")
    users = user_from.user_from.all()
    print("x")
    datas = []
    for user in users[0].user_to.all():
        datas.append(user.user_id)
    friends = [get_object_or_404(Profile, profile_id=profile_id) for profile_id in datas]
    context = {
        "users": friends
    }
    return render(request, "recommended_friends.html", context=context)


def sign_up(request):
    if request.POST:
        if Profile.objects.filter(profile_id=int(request.POST.get('user_id'))):
            print("이미 입력된 데이터입니다.")
            return HttpResponse("이미 존재하는 유저 아이디 입니다. \n 다른 아이디를 입력해주세요 !<li><a href='sign_up_page'>다시 입력 하기</a></li>")
        else:
            obj = Profile(profile_id=int(request.POST.get('user_id')),
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
    items = Item.objects.all()
    paginator = Paginator(items, 11)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    combined = [(item.item_id, item.name, item.brand, item.image,) for item in items]
    context = {
    'items':combined,
    'products': products,
    }
    # print(context)
    return render(request, 'catalog/all_products.html', context)


def friend_review(request):
    profile_id = int(request.user.id)
    user_from = get_object_or_404(Profile, profile_id=profile_id)
    users = user_from.user_from.all()
    print(users)
    datas = []
    for user in users[0].user_to.all():
        datas.append(user.user_id)
    friends = [get_object_or_404(Profile, profile_id=profile_id) for profile_id in datas]
    context = {
        "users": friends
    }
    return render(request, "friendreview.html", context=context)



def recotest(request):

    # print(recommend(profile_id))
    lst = []
    if not request.user.is_authenticated:
        print("Not logged in")
        return redirect("/accounts/login/")
    else:
        print("else ")
        curr_user = request.user
        print(curr_user)
        print(curr_user.profile)
        if not Prediction.objects.filter(user_id=curr_user.profile.profile_id).exists():
            print("else if")
            print(curr_user.profile.profile_id)
            recommendations = recommend(curr_user.profile.profile_id)
            print("recommendations done")
            print(recommendations)
            products = [(Item.objects.get(item_id=i[0]),i[1]) for i in recommendations]
            # recommendations = Prediction.objects.filter(user_id=curr_user.profile.profile_id)
            # products = [(Item.objects(filter(item_id=i[0])),i[1]) for i in recommendations]
            print(products, "first if")
            if len(products)==0:
                messages.error(request, "You have to Rate something First to get recommendations!!")
                return all_items(request)
        else:
            print("else se")
            products = [(Item.objects.filter(item_id=i.item_id)[0],i.prediction) for i in Prediction.objects.filter(user_id=curr_user.profile.profile_id)]
            print(products, "products else")
        # lst = [ i.item_id for i in product_recommendations]
        # print(lst)
        context = {"products": products}
        return render(request, "catalog/recommended_products.html", context)








# homepage
def test(request):
    items = Item.objects.all()
    reviews = Rate.objects.all()[50:80]
    reviewers = [Profile.objects.get(user_id=i.user_id) for i in reviews]
    reviewers_with_pics = []
    for i in reviewers:
        if (i.image != None):
            reviewers_with_pics.append(i)
    sample = []
    # get 30 good raing items
    for i in items:
        if i.get_avgscore() > 4.3:
            sample.append(i)
        if len(sample) > 30:
            break


    return render(request, 'newindex.html', {'items': items, 'reviews': reviews, 'reviewers': reviewers_with_pics})


def my_page(request):
    curr_user = request.user
    if not curr_user.is_authenticated:
        messages.info(request, 'Your need to log in!')
        return render(request, '/accounts/login.html')
    else:
        context = Profile.objects.get(profile_id = curr_user.profile.profile_id)
        print(context)
        return render(request, 'catalog/mypage.html', {'context': context})


def social(request):
    return render(request, 'catalog/social.html')


def sample(request,pk):
    user = User.objects.filter(username='testing')[0]
    print(user)
    print(user.profile)
    print(user.id)
    print(user.profile.profile_id)
    return HttpResponse(user.profile)

def profile_detail(request, profile_id):
    profile = Profile.objects.filter(profile_id = profile_id)[0]
    return render(request, 'catalog/profile_detail.html', {'profile': profile})

def test_form(request,pk):
    item_instance= get_object_or_404(Item, item_id=pk)
    # if this is a POST request we need to process the form data
    items = Item.objects.all()
    paginator = Paginator(items, 11)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    # combined = [(item.item_id, item.name, item.brand, item.image,) for item in items]
    # context = {
    # 'items':combined,
    # 'products': products,
    # }
    if request.user.is_authenticated:
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
                print(newrate.user_id, "user id input of new review")
                newrate.save()
                return render(request, 'catalog/thanks.html')

        # if a GET (or any other method) we'll create a blank form
        else:
            form = ReviewForm()

        return render(request, 'catalog/item_detail.html', {'form': form, 'item': item_instance, 'products': products,})
    else:
        items = Item.objects.all()
        paginator = Paginator(items, 11)
        page = request.GET.get('page')
        products = paginator.get_page(page)
        return render(request, 'catalog/item-detail-out.html', {'item': item_instance})
