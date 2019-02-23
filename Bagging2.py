# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 09:14:27 2018

@author: lijunli
"""


from operator import itemgetter
import os
os.chdir('D:/学生成绩预测李军利')

WRITE = 1
Weights = [0.5, 0.5]

file_score1 = open("Lasso Rank/result/Lasso Rank(0018).txt")
file_score2 = open("Basic Rule/result/35 and 65 of rank.txt")

file_score_write = open("bagging_(Lasso Rank)"+str(Weights[0])+"_Basic Rule"+str(Weights[1])+".txt", "w")

def Read_Score(file_score):
    first_line = 0
    score = {}
    for line in file_score:
        if first_line == 0:
            first_line = 1
            continue
        line_cur = line.strip().split(", ")
        score[line_cur[0]] = float(line_cur[1])
    return(score)

def Merge(s1, s2, x1, x2):
    new_score = {}
    for stu in s1:
        if stu in s2:
            new_score[stu] = x1 * s1[stu] + x2 * s2[stu]
        else:
            new_score[stu] = s1[stu]
    file_score1.close()
    file_score2.close()
    return(new_score)

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

if __name__ == "__main__":
    score1 = Read_Score(file_score1)
    score2 = Read_Score(file_score2)
    score = Merge(score1, score2, Weights[0], Weights[1])
    print(score1)
    print(score2)
    print(score)
    if WRITE == 1:
        I = []
        for i in score:
            I.append((i, score[i]))
        I = sorted(I, key = itemgetter(1))
        print(I)
        rank = {}
        for i in range(0, 91):
            rank[I[i][0]] = i + 1
        file_score_write.write("id, rank\n")
        print(len(rank))
        for stu in rank:
            file_score_write.write(str(stu)+", "+str(rank[stu])+'\n')
        print(rank)
    file_score_write.close()
        
        