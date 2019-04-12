import numpy as np
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import pickle

con = sqlite3.connect("C:\dev\cosmo-hackers\glowpickDB.db")
df = pd.read_sql_query("SELECT * FROM innisfree", con)
df2 = pd.read_sql("SELECT product_id, rating, user_id, age,skin_type, review_count, name, gender FROM innisfree", con)

df2['user_id']=pd.to_numeric(df2['user_id'])
df2['product_id']=pd.to_numeric(df2['product_id'])
df2['rating']=pd.to_numeric(df2['rating'])

users = list(df2['user_id'].value_counts()[lambda x:x>15].index)
products = list(df2['product_id'].value_counts()[lambda x:x>20].index)
new_df = df2[(df2['user_id'].isin(users)) & df2['product_id'].isin(products)]

new_df_group=new_df.groupby(by=['product_id','skin_type']).mean() #각 피부타입별 평균 구한 df

new_df_group.reset_index(level=['product_id','skin_type'], inplace=True) # product id, skin type이 index로 되는거 다시 column 변수로

rate_avg=pd.DataFrame(new_df.groupby(by=['product_id']).mean()['rating']) # 각 아이템별(피부타입 상관 X) 평균을 구함

rate_avg.reset_index(level=['product_id'], inplace=True) #index되어버린 product id 다시 컬럼으로 가져옴

result = pd.merge(new_df_group, rate_avg, on='product_id') # 각 아이템별 평균 컬럼을 merge

result['dominus']=((result['rating_x']-result['rating_y'])<=-1) #rating_x(각 스킨타입별 평균)-rating_y(아이템별 평균) 이 -1보다 작으면 dominus 열에 TRUE

f_df=result[result['dominus']].drop(['user_id'],1)

dry=pd.DataFrame(f_df[f_df['skin_type'] == '건성'])
med=pd.DataFrame(f_df[f_df['skin_type'] == '중성'])
oil=pd.DataFrame(f_df[f_df['skin_type'] == '지성'])
sens=pd.DataFrame(f_df[f_df['skin_type'] == '민감성'])
combine=pd.DataFrame(f_df[f_df['skin_type'] == '복합성'])

type_dict = {}
type_dict['건성'] = list(dry['product_id'])
type_dict['중성'] = list(med['product_id'])
type_dict['지성'] = list(oil['product_id'])
type_dict['민감성'] = list(sens['product_id'])
type_dict['복합성'] = list(combine['product_id'])

with open('type_dict.pickle', 'wb') as f:
    pickle.dump(type_dict, f)