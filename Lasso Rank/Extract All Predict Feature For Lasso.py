# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 19:56:14 2017 

@author: Administrator
"""

import numpy as np
import pandas as pd
import datetime
import os
os.chdir('D:/学生成绩预测李军利')

# 读入4个预测集
file_score = open("Lasso Rank/data/Score Predict.csv")
file_book = open("Lasso Rank/data/Book Predict.csv")
file_card = open("Lasso Rank/data/Card Predict.csv")
file_library = open("Lasso Rank/data/Library Predict.csv")
# id1 + id2 + 110个特征
file_feature_Predict = open("Lasso Rank/data/Predict_110NUM_Lasso.dat","w")


LABEL_SEM = 3
LIMIT_MAX_ID = 91
MaxId = 0
date_splite_num = 4
date_split = [15,30,60,120]
date_end = ["121","715","120"]

book_num = {}
card_day = {}
card_num = {}
card_day_am_time = {}
card_day_pm_time = {}
library_day = {}
learn_day = {}
score_num = {}


def DateToInt(d1,d2,sem):
    D1 = datetime.datetime(2005, int(int(d1) / 100), int(d1) % 100 )
    D2 = datetime.datetime(2006, int(int(d2) / 100), int(d2) % 100 )
    if sem == 2:
        D2 = datetime.datetime(2005, int(int(d2) / 100), int(d2) % 100 )
    if sem == 1 and (int(d1) / 100 < 9) :
        D1 = datetime.datetime(2006, int(int(d1) / 100), int(d1) % 100 )
    if sem == 3 and (int(d1) / 100 < 9) :
        D1 = datetime.datetime(2006, int(int(d1) / 100), int(d1) % 100 )
    return((D2-D1).days + 1)


def Extract_Book(file):
    class_dict = {}
    class_dict_num = {}
    max_num_class = ""
    max_num = 0
    book_class_file = open("Lasso Rank/data/book class.txt",encoding = "utf-8")
    first_line = 0
    for line in book_class_file:
        if first_line == 0:
            first_line = 1
            continue
        line_cur = line.replace("\n","").strip("").split("\t")
        #print line_cur
        class_dict.setdefault(line_cur[0],line_cur[1])
        class_dict_num.setdefault(line_cur[1],0)
        class_dict_num[line_cur[1]] += 1
        if class_dict_num[line_cur[1]] > max_num:
            max_num = class_dict_num[line_cur[1]]
            max_num_class = line_cur[1]
    print(max_num_class)
    book_class_file.close()
    first_line = 0
    for line in file:
        if first_line == 0:
            first_line = 1
            continue
        line_cur = line.replace("\n","").strip("").split(",")
        sem = int(line_cur[0])
        id = int(line_cur[1])
        bookname = line_cur[2]
        if bookname not in class_dict or class_dict[bookname] != max_num_class:
            continue
        date = line_cur[3]
        intdate = DateToInt(date,date_end[sem-1],sem)
        book_num.setdefault(id,{})
        book_num[id].setdefault(sem,{})
        for idx in date_split:
            if intdate < idx:
                book_num[id][sem].setdefault(idx,0.0)
                book_num[id][sem][idx] += 1.0
        global MaxId
        if id > MaxId:
            MaxId = id
    file.close()


def Extract_Library(file):
    first_line = 0
    for line in file:
        if first_line == 0:
            first_line = 1
            continue
        line_cur = line.replace("\n","").strip("").split(",")
        sem = int(line_cur[0])
        id = int(line_cur[1])
        date = line_cur[2]
        intdate = DateToInt(date,date_end[sem-1],sem)
        library_day.setdefault(id,{})
        library_day[id].setdefault(sem,{})
        learn_day.setdefault(id,{})
        learn_day[id].setdefault(sem,{})
        for idx in date_split:
            if intdate < idx:
                library_day[id][sem].setdefault(idx,{})
                library_day[id][sem][idx][date] = 0.0
                learn_day[id][sem].setdefault(idx,{})
                learn_day[id][sem][idx][date] = 0.0
                
        global MaxId
        if id > MaxId:
            MaxId = id
    file.close()


def Extract_Card(file):
    first_line = 0
    for line in file:
        if first_line == 0:
            first_line = 1
            continue
        line_cur = line.replace("\n","").strip("").split(",")
        sem = int(line_cur[0])
        id = int(line_cur[1])
        place = line_cur[2]
        #print place
        date = line_cur[3]
        day_time = int(line_cur[4]) / 10000
        if day_time < 5 :day_time += 24
        if len(date) >= 5:
            continue
        intdate = DateToInt(date,date_end[sem-1],sem)
        if place != u"教室":
            continue
        if day_time <= 10:
            card_day_am_time.setdefault(id,{})
            card_day_am_time[id].setdefault(sem,{})
            card_day_am_time[id][sem].setdefault(intdate,{})
            card_day_am_time[id][sem][intdate][day_time] = 0.0
        if day_time >= 21:
            card_day_pm_time.setdefault(id,{})
            card_day_pm_time[id].setdefault(sem,{})
            card_day_pm_time[id][sem].setdefault(intdate,{})
            card_day_pm_time[id][sem][intdate][day_time] = 0.0

        card_day.setdefault(id,{})
        card_day[id].setdefault(sem,{})
        learn_day.setdefault(id,{})
        learn_day[id].setdefault(sem,{})
        for idx in date_split:
            if intdate < idx:
                card_day[id][sem].setdefault(idx,{})
                card_day[id][sem][idx][date] = 0.0
                learn_day[id][sem].setdefault(idx,{})
                learn_day[id][sem][idx][date] = 0.0
        global MaxId
        if id > MaxId:
            MaxId = id
    file.close()


def Extract_Score(file):
    first_line = 0
    for line in file:
        if first_line == 0:
            first_line = 1
            continue
        line_cur = line.strip("\n").split(",")
        sem = int(line_cur[0])
        id = int(line_cur[1])
        rank = line_cur[2]
        score_num.setdefault(id,{})
        score_num[id].setdefault(sem,rank)
    file.close()


if __name__ == '__main__':
    Extract_Book(file_book)
    Extract_Library(file_library)
    Extract_Card(file_card)
    Extract_Score(file_score)
    print("max ID is " + str(LIMIT_MAX_ID))
    for id1 in range(1,92):
           for id2 in range(1,92):
                  if id1 != id2:
                         w_str = str(id1) + ',' + str(id2)
                         for sem in range(1,4):
                                for bsplit in date_split:
                                    if id1 in book_num and sem in book_num[id1]\
                                            and bsplit in book_num[id1][sem]:
                                        w_str += ',' + str(book_num[id1][sem][bsplit])
                                    else:
                                        w_str += ',0'
                                    if id2 in book_num and sem in book_num[id2]\
                                            and bsplit in book_num[id2][sem]:
                                        w_str += ',' + str(book_num[id2][sem][bsplit])
                                    else:
                                        w_str += ',0'
                         for sem in range(1,4):
                                for bsplit in date_split:
                                    if id1 in library_day and sem in library_day[id1]\
                                            and bsplit in library_day[id1][sem]:
                                        w_str += ',' + str(len(library_day[id1][sem][bsplit])) 
                                    else:
                                        w_str += ',0'
                                    if id2 in library_day and sem in library_day[id2]\
                                            and bsplit in library_day[id2][sem]:
                                        w_str += ',' + str(len(library_day[id2][sem][bsplit]))
                                    else:
                                        w_str += ',0'
                         for sem in range(1,4):
                                for bsplit in date_split:
                                    if id1 in card_day and sem in card_day[id1]\
                                            and bsplit in card_day[id1][sem]:
                                        w_str += ',' + str(len(card_day[id1][sem][bsplit])) 
                                    else:
                                        w_str += ',0'
                                    if id2 in card_day and sem in card_day[id2]\
                                            and bsplit in card_day[id2][sem]:
                                        w_str += ',' + str(len(card_day[id2][sem][bsplit]))
                                    else:
                                        w_str += ',0'
                         for sem in range(1,4):
                                card_day_min_time = []
                                if id1 not in card_day_am_time or sem not in card_day_am_time[id1]:
                                    w_str += ',0'
                                else:
                                    for one_day in card_day_am_time[id1][sem].items():#day:{}
                                        one_day_am_time = sorted(one_day[1].items(),key = lambda t:t[0])
                                        card_day_min_time.append(one_day_am_time[0][0])
                                    w_str += ',' + str(1.0*sum(card_day_min_time)/len(card_day_min_time)) 
                                card_day_min_time = []
                                if id2 not in card_day_am_time or sem not in card_day_am_time[id2]:
                                    w_str += ',0'
                                else:
                                    for one_day in card_day_am_time[id2][sem].items():
                                        one_day_am_time = sorted(one_day[1].items(),key = lambda t:t[0])
                                        card_day_min_time.append(one_day_am_time[0][0])
                                    w_str += ',' + str(1.0*sum(card_day_min_time)/len(card_day_min_time))
                                
                                card_day_max_time = []
                                if id1 not in card_day_pm_time or sem not in card_day_pm_time[id1]:
                                    w_str += ',0'
                                else:
                                    for one_day in card_day_pm_time[id1][sem].items():#day:{}
                                        one_day_pm_time = sorted(one_day[1].items(),key = lambda t:t[0],reverse=True)
                                        card_day_max_time.append(one_day_pm_time[0][0])
                                    w_str += ',' + str(1.0*sum(card_day_max_time)/len(card_day_max_time))
                                card_day_max_time = []
                                if id2 not in card_day_pm_time or sem not in card_day_pm_time[id2]:
                                    w_str += ',0'
                                else:
                                    for one_day in card_day_pm_time[id2][sem].items():#day:{}
                                        one_day_pm_time = sorted(one_day[1].items(),key = lambda t:t[0],reverse=True)
                                        card_day_max_time.append(one_day_pm_time[0][0])
                                    w_str += ',' + str(1.0*sum(card_day_max_time)/len(card_day_max_time))

                         for sem in range(1,4):
                                for bsplit in date_split:
                                    if id1 in learn_day and sem in learn_day[id1]\
                                            and bsplit in learn_day[id1][sem]:
                                        w_str += ',' + str(len(learn_day[id1][sem][bsplit]))
                                    else:
                                        w_str += ',0'
                                    if id2 in learn_day and sem in learn_day[id2]\
                                            and bsplit in learn_day[id2][sem]:
                                        w_str += ',' + str(len(learn_day[id2][sem][bsplit]))
                                    else:
                                        w_str += ',0'
                         for sem in range(1,3):
                             if int(score_num[id1][sem]) > int(score_num[id2][sem]):
                                 w_str += ",1"
                             else:
                                 w_str += ",0"
                         w_str += '\n'
                         file_feature_Predict.write(w_str)
    file_feature_Predict.close()

              
