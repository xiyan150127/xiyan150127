# -*- coding: utf-8 -*-
"""
Created on Sat May 29 20:16:57 2021

@author: DELL
"""

#因为感觉词云图好看，所以我也制作了一份
from wordcloud import WordCloud
import jieba
from tkinter import _flatten
#from matplotlib.pyplot import imread
import matplotlib.pyplot as plt
import pandas as pd
with open('C:\\Users\\DELL\\Desktop\\停用词.txt', 'r', encoding='utf-8') as f:
    stopWords = f.read()
def my_word_cloud(data=None, stopWords=None, img=None):
    dataCut = data.apply(jieba.lcut)  # 分词
    dataAfter = dataCut.apply(lambda x: [i for i in x if i not in stopWords])  # 去除停用词
    wordFre = pd.Series(_flatten(list(dataAfter))).value_counts()  # 统计词频
    print(dict(wordFre))
  
    mask = plt.imread(img)
    plt.figure(figsize=(20,20))
    wc  = WordCloud(scale=10,font_path='C:/Windows/Fonts/simfang.ttf',mask=mask,background_color="white")
    wc.fit_words(wordFre)
    plt.imshow(wc)
    plt.axis('off')
    wc.to_file('C:\\Users\\DELL\\Desktop\\冬梦飞扬.jpg')
    
data = pd.read_csv(r"D:\\冬梦飞扬.csv",encoding='gbk')
my_word_cloud(data=data['用户评论'],stopWords=stopWords,img='C:\\Users\\DELL\\Desktop\\demo.jpg')
#这个demo图片自己去网上随便照一张就行，用处就是限制词语大致在哪个轮廓中）