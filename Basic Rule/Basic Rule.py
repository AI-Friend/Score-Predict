# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 20:45:25 2017 

@author: lijunli
"""

import os 
os.chdir('D:/学生成绩预测李军利')

def Weight_score():
    file_score = open("data/Score Predict.csv") # 将原来的txt文件按学号从大到小排序后保存为csv文件
    file_result = open("Basic Rule/result/35 and 65 of rank.txt", "w")
    factor = [0.35, 0.65]
    stu = {}
    first_line = 0
    for line in file_score:
        if first_line == 0:
              first_line = 1
              continue # 第一行是 学期 学号 排名，要先排除第一行
        sem, id, rank = line.strip("").split(",")
        stu.setdefault(id, 0)
        # 第一学期：rank * 0.35, 第二学期：rank * 0.65
        stu[id] += int(rank) * factor[int(sem)-1]
    Ranked = sorted(zip(stu.values(), stu.keys()))  # 按得到的名次排序，id在后
    file_result.write("id,rank\n")
    i = 1
    for line in Ranked:
        file_result.write(line[1] + "," + str(i) + "\n")
        i = i + 1
    file_score.close()
    file_result.close()

if __name__ == '__main__':
    Weight_score() # 第一二学期排名乘以权重
