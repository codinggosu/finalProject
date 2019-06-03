import pandas as pd
import sqlite3
import surprise
import os
# Python이 실행될 때 DJANGO_SETTINGS_MODULE이라는 환경 변수에 현재 프로젝트의 settings.py파일 경로를 등록합니다.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recoduct.settings")
# 이제 장고를 가져와 장고 프로젝트를 사용할 수 있도록 환경을 만듭니다.
import django
django.setup()

from catalog.models import User
from catalog.models import Item
from catalog.models import Rate


def load_item():
    con = sqlite3.connect("C:\dev\glowpickDB.db")
    item_df = pd.read_sql("SELECT product_id, name, product_image FROM merged_data", con)
    return item_df


def load_user():
    con = sqlite3.connect("C:\dev\glowpickDB.db")
    user_df = pd.read_sql("SELECT user_id, age, gender, skin_type, nickname, profile_image FROM merged_data", con)
    return user_df


def load_rate():
    con = sqlite3.connect("C:\dev\glowpickDB.db")
    rate_df = pd.read_sql("SELECT user_id, product_id, rating, contents, created_at FROM merged_data", con)
    return rate_df


if __name__=='__main__':
#    item_df = load_item()
#    for idx in range(len(item_df)):
#        Item(item_id=item_df.iloc[idx, 0], name=item_df.iloc[idx, 1], image=item_df.iloc[idx, 2], brand='이니스프리').save()
    print("완료")
#    user_df = load_user()
#    for idx in range(len(user_df)):
#        User(user_id=user_df.iloc[idx, 0], age=user_df.iloc[idx, 1], gender=user_df.iloc[idx, 2], skin_type=user_df.iloc[idx, 3], nickname=user_df.iloc[idx, 4], profile=user_df.iloc[idx, 5]).save()
    print("완료")
    rate_df = load_rate()
    for idx in range(len(rate_df)):
        Rate(user_id=rate_df.iloc[idx, 0], item_id=rate_df.iloc[idx, 1], rate=rate_df.iloc[idx, 2], review=rate_df.iloc[idx, 3], created_at=rate_df.iloc[idx, 4]).save()
    print("완료")

#prediction_df = load_prediction()
#for idx in range(len(prediction_df)):
#Prediction(user_id=prediction_df.iloc[idx, 0], item_id=prediction_df.iloc[idx, 1], prediction=prediction_df.iloc[idx, 2]).save()

#userId=pd.to_numeric(df['user_id'])
#productId=pd.to_numeric(df['product_id'])
#rating=pd.to_numeric(df['rating'])

#temp={"user":userId,'item':productId,'rating':rating}

#df2=pd.DataFrame(temp,columns = ['user', 'item','rating'])