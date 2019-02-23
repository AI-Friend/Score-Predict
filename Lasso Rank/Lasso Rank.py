# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 21:06:20 2017 

@author: Administrator
"""

from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn import linear_model
from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
import  time
from operator import itemgetter
import numpy as np
import pandas as pd
import os
os.chdir('D:/学生成绩预测李军利')


train_filename   = "Lasso Rank/data/Train_110NUM_Lasso.dat"
predict_filename = "Lasso Rank/data/Predict_110NUM_Lasso.dat"
file_result = open("Lasso Rank/result/LassoRank(0018).txt","w")

n_feature = 0
predict_line_id = []
predict_line_to = []


def Read_Train_Data(file_name):
    file = open(file_name)
    x = []
    y = []
    positive = 0
    negative = 0
    for line in file:
        line_cur = line.strip().split(',')
        x.append([float(line_cur[i]) for i in range(2,len(line_cur)-1)])
        y.append(float(line_cur[len(line_cur)-1]))
        if int(line_cur[len(line_cur)-1]) == 1:
            positive += 1
        else:
            negative += 1
        if positive + negative >= 30000: # 根据需要选择训练样本个数
            break
    print("正样本:" + str(positive) + "负样本:" + str(negative))
    file.close()
    return(x,y)
    
    
def Read_Predict_Data(file_name):
    global predict_line_id
    global predict_line_to
    file = open(file_name)
    x = []
    first_line = 0 # 此次first_line是为了输出特征数，不是忽略第一行，所以下面没有用continue
    for line in file:
        line_cur = line.strip().split(',')
        if first_line == 0:
            global n_feature
            n_feature = len(line_cur)-2
            print("特征总数："+str(len(line_cur)-2))
            first_line = 1

        x.append([float(line_cur[i]) for i in range(2,len(line_cur))])
        predict_line_id.append(int(line_cur[0])) # id1
        predict_line_to.append(int(line_cur[1])) # id2
    file.close()
    return(x)


def Get_Rank(res):
    out_dict = {}
    for i in range(0,len(predict_line_id)):
        out_dict.setdefault(predict_line_id[i],0)
        out_dict[predict_line_id[i]] += res[i] # predict[i[与res[i]对应，指定id的学生与其余90个学生的排名对比
        # 后的值相加，比如值等于40说明有40个1，即该学生排名的数字大于40个学生，值越小越好。理论最大值应该是90(排名91)
    # print(out_dict)
    rank = {}
    cnt = 0
    for id in range(1,92):
        if id not in out_dict:
            rank[id] = 92.0
        else:
            cnt += 1
            rank[id] = 92.0 - out_dict[id] # 值越大，排名越靠前。理论最小值是2
    print(cnt) # cnt = 91 则无异常的学号

    I = []
    for i in rank:
        I.append((i,rank[i])) # dict变成tuple为元素的list:[()]，便于排序
    print("*******Before Ranked********")
    print(I)
    I = sorted(I, key = itemgetter(1)) # 按id对应值大小从小到大排序即——名次排序，还需要把值变成真正的名次
    print("*******Ranked********")
    print (I)
    rank = {}
    for i in range(0,91):
        rank[I[i][0]] = i + 1 # I已经按值从小到大排序了，所以循环里当i=0时,最后一名rank[80]= 1 ,最后92减1等于真正排名——91
    return(rank)


# 标准化
def PreProcess(x):
    min_max_scaler = preprocessing.MinMaxScaler() # 为了对付那些标准差相当小的的特征并且保留下稀疏矩阵中的0值，规模化特征到[0,1]范围内，
    minmax_x = min_max_scaler.fit_transform(x)
    return(minmax_x)


# 我们关心的是学生的大致排名，所以预测排名与实际排名仅仅差几个名次是允许的，所以此次排名问题最适合用
# Spearman相关性系数衡量实际排名和预测排名的相关性。
def Test(real_rank,predict_rank):
    error = 0.0
    first_line = 0
    predict_rank.seek(0)
    for line in predict_rank:
        if first_line == 0:
            first_line = 1
            continue
        line_cur = line.split(",")
        id = int(line_cur[0])
        rank = int(line_cur[1])
        error += pow(rank-res[id],2) * 6
    error = 1 - (error * 1.0) / ((91 * 91 - 1) * 91)
    return(error)



if __name__ == "__main__":
    print(time.localtime())
    x,y = Read_Train_Data(train_filename)
    print(len(x))
    # print(y)
    pre_x = Read_Predict_Data(predict_filename)
    x = PreProcess(x)
    pre_x = PreProcess(pre_x)
    print(len(pre_x))
    clf = linear_model.Lasso(alpha = 0.018)
    clf.fit(x,y)
    # print(clf.coef) #　与上一学期的排名的相关性最大
    # print(clf.intercept_) 截距
    res  = clf.predict(pre_x) # 模型预测
    #res = clf.predict_proba(pre_x)
    print(len(res))
    out_dict = Get_Rank(res)
    # print(out_dict)
    test_dict = {} # 92减去out_dict中的值就是真实排名
    file_result.write("id,rank\n")
    for idx in out_dict:
        test_dict[idx] = 92-int(out_dict[idx])
        file_result.write(str(idx)+","+str(test_dict[idx])+"\n")
    print(time.localtime())
    file_result.close()





