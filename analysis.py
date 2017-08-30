# -*- coding: utf-8 -*-
"""
Created on Thu May  4 19:57:27 2017

@author: liu23
"""

import re
from operator import itemgetter
import os
import jieba
import codecs

#build a dictionary, add new words
jieba.load_userdict("dictionaryForProcessing/danmudictuni.txt")


        
#generate comments
def generateDanmu(filename):
    jieba.load_userdict("dictionaryForProcessing/danmudictuni.txt")

    #read files
    stopList=[]
    stopFile = open('dictionaryForProcessing/stop_words.txt','r',encoding='ANSI')
    for stopWord in stopFile:
        stopWord=stopWord.rstrip()
        if stopWord != '':
            stopList.append(stopWord)
            
    danmulist=[]
    f=open("datasetForSentiment/" + filename + ".txt","r",encoding="utf8")
    for line in f:
        line=line.rstrip()
        danmu=re.findall(r'(\S+)',line)[0]
        danmulist.append(danmu)


    #using jieba package and split the words 
    worddict=dict()
    for danmuline in danmulist:
        wordlist=jieba.lcut(danmuline)
        for word in wordlist:
            if word in stopList:
                # print "stopword: %s" % word
                continue
            else:
                worddict[word]=worddict.get(word,0) + 1
    
    #sorting the word frequency            
    b=sorted(worddict.items(), key=itemgetter(1),reverse=True)
    return b
             
def generateComment(filename):
     #using the dictionary
    jieba.load_userdict("dictionaryForProcessing/danmudictuni.txt")

    #load file
    stopList=[]
    stopFile = open('dictionaryForProcessing/stop_words.txt','r',encoding='ANSI')
    for stopWord in stopFile:
        stopWord=stopWord.rstrip()
        if stopWord != '':
            stopList.append(stopWord)
    
    commentlist=[]
    f=open("datasetForSentiment/" + filename + ".txt","r",encoding="ANSI")
    commentDict=re.findall(r'content=(.+)\$\t\d{4}-\d{2}-\d{2} \d{2}:\d{2}\treplyNum=(\d+)\$',f.read())
    for commentTuple in commentDict:
        comment=commentTuple[0]
        commentlist.append(comment)
        

    worddict=dict()
    for commentline in commentlist:
        wordlist=jieba.lcut(commentline)
        for word in wordlist:
            if word in stopList:
                # print "stopword: %s" % word
                continue
            else:
                worddict[word]=worddict.get(word,0) + 1
    
    #ssorting the word frequency             
    b=sorted(worddict.items(), key=itemgetter(1),reverse=True)
    return b


b=generateComment("gameMessage")
#b=generateDanmu("gameDanmu")
print(b)


