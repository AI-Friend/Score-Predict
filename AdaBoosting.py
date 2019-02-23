# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 20:31:04 2018

@author: lijunli
"""

from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing
from sklearn.ensemble import GradientBoostingClassifier
import time
import math
from operator import itemgetter
import os
os.chdir('D:/学生成绩预测李军利')
                         
                         
train_filename = "Lasso Rank/data/Train_110NUM_Lasso.dat"
predict_filename = "Lasso Rank/data/Predict_110NUM_Lasso.dat"
file_result_name = "AdaBoosting.txt"

SUBMIT = 1
n_feature = 0
n_sample = 0
model_weight = []
sample_weight = []
model_list = []
predict_line_id = []
predict_line_to = []


def Read_Train_Data(file_name):
    file = open(file_name)
    x = []
    y = []
    positive = 0
    nagative = 0
    for line in file:
        line_cur = line.strip().split(', ')
        x.append([float(line_cur[i]) for i in range(2, len(line_cur)-1)])
        y.append(float(line_cur[len(line_cur)-1]))
        if int(line_cur[len(line_cur)-1]) == 1:
            positive += 1
        else:
            nagative += 1
        if positive + nagative >= 30000:
            break
    global n_sample
    n_sample = positive + nagative
    print("正样本:" + str(positive) + "负样本:" + str(nagative))
    file.close()
    return(x, y)


def Read_Predict_Data(file_name):
    global predict_line_id
    global predict_line_to
    file = open(file_name)
    x = []
    first_line = 0
    for line in file:
        line_cur = line.strip().split(', ')
        if first_line == 0:
            global n_feature
            n_feature = len(line_cur)-2
            print("特征总数："+str(len(line_cur)-2))
            first_line = 1

        x.append([float(line_cur[i]) for i in range(2, len(line_cur))])
        predict_line_id.append(int(line_cur[0]))
        predict_line_to.append(int(line_cur[1]))
    file.close()
    return(x)


def Get_Rank(res):
    out_dict = {}
    for i in range(0, len(predict_line_id)):
        out_dict.setdefault(predict_line_id[i], 0)
        out_dict[predict_line_id[i]] += res[i]
    # print(out_dict)
    rank = {}
    cnt = 0
    for id in range(1, 92):
        if id not in out_dict:
            rank[id] = 92.0
        else:
            cnt += 1
            rank[id] = 92.0 - out_dict[id]
    print(cnt)
    
    I = []
    for i in rank:
        I.append((i, rank[i]))
    print("*******Before Ranked********")
    print(I)
    I = sorted(I, key = itemgetter(1))
    print("*******Ranked********")
    print(I)
    rank = {}
    for i in range(0, 91):
        rank[I[i][0]] = i + 1
    return(rank)


def PreProcess(x):
    min_max_scaler = preprocessing.MinMaxScaler()
    minmax_x = min_max_scaler.fit_transform(x)
    return(minmax_x)


def Test(real_rank, predict_rank):
    error = 0.0
    first_line = 0
    predict_rank.seek(0)
    for line in predict_rank:
        if first_line == 0:
            first_line = 1
            continue
        line_cur = line.split(", ")
        id = int(line_cur[0])
        rank = int(line_cur[1])
        error += pow(rank-real_rank[id], 2) * 6
    error = 1 - (error * 1.0) / ((91 * 91 - 1) * 91)
    return(error)
    
    
def Train_Model(x, y, t):
    if t == 0:
        clf = LogisticRegression(C=0.0093, penalty='l1', tol=0.0005)
        clf.fit(x, y)
        model_list.append(clf)
        res = clf.predict(x) # 主程序的错误率 error = 0.069
        return(res)
    elif t == 1:
        clf = LogisticRegression(C=0.0055, penalty='l1', tol=0.0005)
        clf.fit(x, y)
        model_list.append(clf) 
        res = clf.predict(x) # error =0.490, C的效果不好
        return(res)
    elif t == 2:
        clf = LogisticRegression(C=0.013, penalty='l1', tol=0.0005)
        clf.fit(x, y)
        model_list.append(clf)
        res = clf.predict(x) # error = 0.493, C的效果不好
        return(res)
    elif t == 3:
        clf = svm.SVC()
        clf.fit(x, y)
        model_list.append(clf)
        res = clf.predict(x) # error = 0.491 SVM的效果不好，
                             # SVM的核函数取sigmoid时效果也不好，所以就不试神经网络了
        return(res)
    elif t == 4:
        clf = GradientBoostingClassifier(n_estimators=3000, max_depth=6)
        clf.fit(x, y)
        model_list.append(clf)
        res = clf.predict(x) # error = 0.00051，效果很好，但是迭代次数较多，速度慢
        return(res)
    elif t == 5:
        clf = GradientBoostingClassifier(n_estimators=40, max_depth=6)
        clf.fit(x, y)
        model_list.append(clf)
        res = clf.predict(x) # error = 0.481，迭代次数太少，效果不好，下面不一一列举，
                             # 最后给这些模型赋予合适的权重即可 
        return(res)
    elif t == 6:
        clf = GradientBoostingClassifier(n_estimators=35, max_depth=6)
        clf.fit(x, y)
        model_list.append(clf)
        res = clf.predict(x)
        return(res)
    elif t == 7:
        clf = GradientBoostingClassifier(n_estimators=1037, max_depth=6)
        clf.fit(x, y)
        model_list.append(clf)
        res = clf.predict(x)
        return(res)
    elif t == 8:
        clf = LogisticRegression(C=0.0073, penalty='l1', tol=0.0005)
        clf.fit(x, y)
        model_list.append(clf)
        res = clf.predict(x)
        return(res)
    elif t == 9:
        clf = LogisticRegression(C=0.0068, penalty='l1', tol=0.0006)
        clf.fit(x, y)
        model_list.append(clf)
        res = clf.predict(x)
        return(res)

if __name__ == "__main__":
    print(time.localtime())
    x, y = Read_Train_Data(train_filename)
    print(len(x))
    # print(y)
    pre_x = Read_Predict_Data(predict_filename)
    x = PreProcess(x)
    pre_x = PreProcess(pre_x)
    sample_weight = [1.0/n_sample] * n_sample # 样本权重，没有影响大的样本，所有的样本权重取相同值
    for t in range(0, 10): # 10个模型
        print("this t = " + str(t))
        train_y = Train_Model(x, y, t)
        # print(train_y)
        error = 0.0
        for i in range(0, len(y)): # 计算分类错误率
            error += 0.5 * sample_weight[i] * abs(train_y[i] - y[i])
        print(error)
        if error == 0:
            model_weight.append(100)
        else:
            model_weight.append(math.log((1-error)/error)) 
            # 利用log函数给各模型赋予恰当的系数，log((1-0.5)/0.5)=0, 若错误率大于0.5，模型权重为负
        sum = 0.0
        for i in range(0, n_sample):
            if train_y[i] != y[i]:
#                if error == 0:
#                    sample_weight[i] *= (1 - error) / error
 #               else:
                    sample_weight[i] *= 10000 # 加大错分样本的权重
            sum += sample_weight[i]
        for i in range(0, n_sample):
            sample_weight[i] = sample_weight[i] / sum # 保证所有样本的权重和等于1

    adares = []
    print(model_weight)
    for t in range(0, 10):
        res  = model_list[t].predict(pre_x)
        # print("current res:",)
        # print(res)
        for i in range(0, len(pre_x)):
            if res[i] < 0.5:
                res[i] = -1
            if t == 0:
                adares.append(res[i]*model_weight[t])
            else:
                adares[i] += res[i]*model_weight[t]
        # print("after process res:",)
        # print(res)
    #res = clf.predict_proba(pre_x)
    for i in range(0, len(pre_x)):
        if adares[i] <= 0:
            adares[i] = 0
        else:
            adares[i] = 1
    print(len(adares))
    out_dict = Get_Rank(adares)
    # (print out_dict)
    if SUBMIT == 1:
        file_result = open(file_result_name, "w")
        test_dict = {}
        file_result.write("id, rank\n")
        for idx in out_dict:
            test_dict[idx] = 92-int(out_dict[idx])
            file_result.write(str(idx)+", "+str(test_dict[idx])+"\n")
    file_result.close()
    print(time.localtime())
    
    
