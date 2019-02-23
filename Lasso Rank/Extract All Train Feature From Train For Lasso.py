# -*- coding: utf-8 -*-
"""
Created on Sat Nov 25 08:16:31 2017 

@author: Administrator
"""

import numpy as np
import pandas as pd
import datetime
import os
os.chdir('D:/学生成绩预测李军利')

# 读入4个训练集
file_score = open("Lasso Rank/data/Score Train.csv")
file_book = open("Lasso Rank/data/Book Train.csv")
file_card = open("Lasso Rank/data/Card Train.csv")
file_library = open("Lasso Rank/data/Library Train.csv")
# id1,id2 + 提取的110个特征 + '1'/'0' 写入下面的文件
file_feature_train = open("Lasso Rank/data/Train_110NUM_Lasso.dat","w")


LABEL_SEM = 3
MaxId = 0
date_split_num = 4  # 离最后一天的天数有4个间隔点
date_split = [15,30,60,120] # 具体间隔, 因为离考试时间越近的学习对成绩提升越大，所以测试后分了4段
date_end = ["121","715","120"]   # 3个学期有记录的最后一天
# 学期1: [903,121]，  学期2: [224,715] 2月只有28天， 学期3：[901,120]
book_num = {} # 按照{id:{sem:{idx:}}}形式   
card_day = {}
card_num = {}
card_day_am_time = {}
card_day_pm_time = {}
library_day = {}
learn_day = {}
score_num = {}


'''
计算当前日期离最后一天的天数，随机选取一个年份2005，即使年份不同最多也只相差1天。
学期1: [903,121]和学期3：[901,120]，9月到12月的日期年份取2005年,1月之后的年份取2006年。
学期3：[901,120]，计算时都取2005年即可。
'''

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
    max_num_class = "" # 已知'学习类'书籍被借次数最多
    max_num = 0
    book_class_file = open("Lasso Rank/data/book class.txt",encoding = "utf-8") 
    first_line = 0
    for line in book_class_file:
        if first_line == 0:
            first_line = 1
            continue
        line_cur = line.replace("\n","").strip("").split("\t")
        # print(line_cur)   ex:['1005159', 'H']
        class_dict.setdefault(line_cur[0],line_cur[1]) # ex: {'1005159': 'H'}
        class_dict_num.setdefault(line_cur[1],0)  # ex: {'H': 0}
        class_dict_num[line_cur[1]] += 1 # 可以查看哪些书受欢迎，给东财图书馆提供参考，东财图书馆的改进：
        if class_dict_num[line_cur[1]] > max_num:
            max_num = class_dict_num[line_cur[1]]
            max_num_class = line_cur[1]
    print(max_num_class) # TP
    book_class_file.close()
    class_dict_num_write = open("Lasso Rank/中间文件/class_dict_num.txt","w")
    class_dict_num_write.write(str(class_dict_num))
    class_dict_num_write.close()
      
    first_line = 0
    for line in file:
        if first_line == 0:
            first_line = 1
            continue
        line_cur = line.replace("\n","").strip("").split(",")
        # print(line_cur) ex: ['2', '513', '2960805', '715']
        sem = int(line_cur[0])
        id = int(line_cur[1])
        bookname = line_cur[2]
        if bookname not in class_dict or class_dict[bookname] != max_num_class:
            continue  # 必须是max_num_class(TP) '学习类/教科书'
        date = line_cur[3]
        intdate = DateToInt(date,date_end[sem-1],sem)#离最后一天的天数
        # print(date + "\t" + str(intdate)) ex: 302  136
        book_num.setdefault(id,{})
        book_num[id].setdefault(sem,{})
        for idx in date_split: # 借书时间超过120不计入，所以会出现 3：{}这样的。
            if intdate < idx:
                book_num[id][sem].setdefault(idx,0.0)
                book_num[id][sem][idx] += 1.0
        global MaxId
        if id > MaxId:
            MaxId = id # 537
    file.close()
    book_num_write = open("Lasso Rank/中间文件/book_num.txt","w")
    book_num_write.write(str(book_num))
    book_num_write.close()

    
def Extract_Library(file):
    first_line = 0
    for line in file:
        if first_line == 0:
            first_line = 1
            continue
        line_cur = line.strip("").split(",")
        sem = int(line_cur[0])
        id = int(line_cur[1])
        date = line_cur[2]
        intdate = DateToInt(date,date_end[sem-1],sem)#离最后一天的天数
        #print date + "\t" + str(intdate)
        library_day.setdefault(id,{})
        library_day[id].setdefault(sem,{})
        learn_day.setdefault(id,{})
        learn_day[id].setdefault(sem,{})
        for idx in date_split:
            if intdate < idx:
                library_day[id][sem].setdefault(idx,{})
                library_day[id][sem][idx][date] = 0.0  # 都赋值为0，以后求天数只需求len()即可
                # 比如日期'109'即使出现多次，也是'109': 0.0,计天数与计次数都可以
                learn_day[id][sem].setdefault(idx,{})
                learn_day[id][sem][idx][date] = 0.0
        global MaxId
        if id > MaxId:
            MaxId = id # 538
    file.close()
    library_day_write = open("Lasso Rank/中间文件/library_day.txt","w")
    library_day_write.write(str(library_day))
    library_day_write.close()
    learn_day_write = open("Lasso Rank/中间文件/learn_library_day.txt","w")
    learn_day_write.write(str(learn_day))
    learn_day_write.close()
    

def Extract_Card(file):
    first_line = 0
    for line in file:  # line ex: '1,538,超市,1013,225601,5\n'
        if first_line == 0:
            first_line = 1
            continue
        line_cur = line.replace("\n","").strip("").split(",") # ex: ['1', '538', '超市', '1013', '225601', '5']
        sem = int(line_cur[0])
        id = int(line_cur[1])
        place = line_cur[2]
        #print(place)
        date = line_cur[3]  # ex:'1013'
        day_time = int(line_cur[4]) / 10000 # ex: 22.5601
        if day_time < 5 :day_time += 24 # 0点到5点之间的时间，早出时间要排除这些时间
        if len(date) >= 5:
            continue # 若有错误的异常日期，结束此次循环
        intdate = DateToInt(date,date_end[sem-1],sem)#离最后一天的天数
        #print(date + "\t" + str(intdate))
        if place != "教室": 
            continue   # 如果place不是教室，停止这一次循环，为了选择出place=='教室'
        if day_time <= 10:  # 早出时间
            card_day_am_time.setdefault(id,{})
            card_day_am_time[id].setdefault(sem,{})
            card_day_am_time[id][sem].setdefault(intdate,{})
            card_day_am_time[id][sem][intdate][day_time] = 0.0
        if day_time >= 21:  # 晚归时间
            card_day_pm_time.setdefault(id,{})
            card_day_pm_time[id].setdefault(sem,{})
            card_day_pm_time[id][sem].setdefault(intdate,{})
            card_day_pm_time[id][sem][intdate][day_time] = 0.0

        card_day.setdefault(id,{})
        card_day[id].setdefault(sem,{})
        learn_day.setdefault(id,{})
        learn_day[id].setdefault(sem,{})
        for idx in date_split:
            #print(line,intdate,idx)
            if intdate < idx:
                card_day[id][sem].setdefault(idx,{})
                card_day[id][sem][idx][date] = 0.0  # 最后选择在教室自习的天数，不能选择次数，因为一天中刷卡次数(尤其打水)会很多
                learn_day[id][sem].setdefault(idx,{})
                learn_day[id][sem][idx][date] = 0.0

        global MaxId
        if id > MaxId:
            MaxId = id # 538
            
    file.close()
    card_day_am_time_write = open("Lasso Rank/中间文件/card_day_am_time.txt","w")
    card_day_am_time_write.write(str(card_day_am_time))
    card_day_am_time_write.close()
    card_day_pm_time_write = open("Lasso Rank/中间文件/card_day_pm_time.txt","w")
    card_day_pm_time_write.write(str(card_day_pm_time))
    card_day_pm_time_write.close()
    card_day_write = open("Lasso Rank/中间文件/card_day.txt","w")
    card_day_write.write(str(card_day))
    card_day_write.close()
    learn_day_write = open("Lasso Rank/中间文件/learn_sum_day.txt","w")
    learn_day_write.write(str(learn_day))
    learn_day_write.close()
    

def Extract_Score(file):
    first_line = 0
    for line in file:
        if first_line == 0:
            first_line = 1
            continue
        line_cur = line.strip("\n").split(",") # ex: ['2', '538', '498']
        sem = int(line_cur[0])
        id = int(line_cur[1])
        rank = line_cur[2]
        score_num.setdefault(id,{})
        score_num[id].setdefault(sem,rank)
    file.close()
    score_num_write = open("Lasso Rank/中间文件/score_num.txt","w")
    score_num_write.write(str(score_num))
    score_num_write.close()

 

if __name__ == '__main__':
    Extract_Book(file_book)
    Extract_Library(file_library)
    Extract_Card(file_card)
    Extract_Score(file_score)
    for id1 in range(1,539):
           for id2 in range(1,539):
                  if id1 != id2:
                         w_str = str(id1) + ',' + str(id2)
                         for sem in range(1,4):
                                for bsplit in date_split:
                                    if id1 in book_num and sem in book_num[id1]\
                                            and bsplit in book_num[id1][sem]:
                                        w_str += ',' + str(book_num[id1][sem][bsplit]) # 离考试时间在bsplit内借书次数
                                    else:
                                        w_str += ',0' # 以0补缺失值
                                    if id2 in book_num and sem in book_num[id2]\
                                            and bsplit in book_num[id2][sem]:
                                        w_str += ',' + str(book_num[id2][sem][bsplit])
                                    else:
                                        w_str += ',0'
                         for sem in range(1,4):
                                for bsplit in date_split:
                                    if id1 in library_day and sem in library_day[id1]\
                                            and bsplit in library_day[id1][sem]:
                                        w_str += ',' + str(len(library_day[id1][sem][bsplit])) # 离考试时间在bsplit内去图书馆的天数
                                    else:
                                        w_str += ',0'
                                    if id2 in library_day and sem in library_day[id2]\
                                            and bsplit in library_day[id2][sem]:
                                        w_str += ',' + str(len(library_day[id2][sem][bsplit])) # 去图书馆的天数
                                    else:
                                        w_str += ',0'
                         for sem in range(1,4):
                                for bsplit in date_split:
                                    if id1 in card_day and sem in card_day[id1]\
                                            and bsplit in card_day[id1][sem]:
                                        w_str += ',' + str(len(card_day[id1][sem][bsplit])) # 去教室的天数
                                    else:
                                        w_str += ',0'
                                    if id2 in card_day and sem in card_day[id2]\
                                            and bsplit in card_day[id2][sem]:
                                        w_str += ',' + str(len(card_day[id2][sem][bsplit]))
                                    else:
                                        w_str += ',0'
                         for sem in range(1,4):
                                # print("***********")
                                # 每一天在教室最早的消费时间
                                card_day_min_time = []
                                if id1 not in card_day_am_time or sem not in card_day_am_time[id1]:
                                    w_str += ',0' # 缺失值(不去教室)补0
                                else:
                                    for one_day in card_day_am_time[id1][sem].items(): 
                                        one_day_am_time = sorted(one_day[1].items(),key = lambda t:t[0]) # 注意one_day是tuple不是dict
                                        card_day_min_time.append(one_day_am_time[0][0]) # 只需每天上午最早的消费时间
                                    w_str += ',' + str(1.0*sum(card_day_min_time)/len(card_day_min_time)) # id1早上平均去教室的时间
                                card_day_min_time = []
                                if id2 not in card_day_am_time or sem not in card_day_am_time[id2]:
                                    w_str += ',0'
                                else:
                                    for one_day in card_day_am_time[id2][sem].items():#day:{}
                                        one_day_am_time = sorted(one_day[1].items(),key = lambda t:t[0])
                                        card_day_min_time.append(one_day_am_time[0][0])
                                    w_str += ',' + str(1.0*sum(card_day_min_time)/len(card_day_min_time)) # id2早上平均去教室的时间
                                # 每一天在教室最晚的消费时间
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
                                    #print card_day_max_time
                                    #print "max"+str(1.0*sum(card_day_max_time)/len(card_day_max_time))

                         for sem in range(1,4):
                                for bsplit in date_split:
                                    if id1 in learn_day and sem in learn_day[id1]\
                                            and bsplit in learn_day[id1][sem]:
                                        w_str += ',' + str(len(learn_day[id1][sem][bsplit])) # 在图书馆和教室的天数之和
                                    else:
                                        w_str += ',0'
                                    if id2 in learn_day and sem in learn_day[id2]\
                                            and bsplit in learn_day[id2][sem]:
                                        w_str += ',' + str(len(learn_day[id2][sem][bsplit]))
                                    else:
                                        w_str += ',0'
                         for sem in range(1,3):
                             if int(score_num[id1][sem]) > int(score_num[id2][sem]):
                                 w_str += ",1"  # 如果id1的排名数字大于id2(数字大，则排名低)，写入'1'
                             else:
                                 w_str += ",0"
                         if int(score_num[id1][LABEL_SEM]) > int(score_num[id2][LABEL_SEM]):
                             w_str += ',1'
                         else:
                             w_str += ',0'
                         w_str += '\n'
                         file_feature_train.write(w_str)
    file_feature_train.close()
