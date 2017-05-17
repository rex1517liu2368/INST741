# -*- coding: utf-8 -*-
"""
Created on Fri May  5 22:48:10 2017

@author: liu23
"""

import urllib
import json
import urllib.request

def get_comment(aidN):
    aid=aidN
    
    url = 'http://api.bilibili.cn/feedback?aid='+str(aid)
    data1 = urllib.request.urlopen(url).read()
    
    js1 = json.loads(data1.decode("utf-8"))
    
    pages=js1["pages"]
    
    page=1
    
    fw = open("msg"+aid+'.txt', 'w+')
    
    #for hot list
    
    url= 'http://api.bilibili.cn/feedback?aid='+str(aid) + '&page='+ str(page) 
    data = urllib.request.urlopen(url).read()
    js=json.loads(data.decode("utf-8"))
        
    for hotcomment in js["hotList"]:
        content=='content='+ hotcomment["msg"]+"$"
        time=hotcomment["create_at"]
        hotreplyNum='replyNum='+str(hotcomment["reply_count"])+'$'
        content=content.encode("GBK",'ignore').decode("GBK")
        fw.write(content + '\t' + time + '\t' + str(hotreplyNum) + '\n')
       
    #for general list     
    while (page<=pages):
        url= 'http://api.bilibili.cn/feedback?aid='+str(aid) + '&page='+ str(page) 
        data = urllib.request.urlopen(url).read()
        js=json.loads(data.decode("utf-8"))
        
        for comment in js["list"]:
            content='content='+comment["msg"]+"$"
            time=comment["create_at"]
            if comment["reply"] is None:
                replyNum=0
            else:
                replyNum=len(comment["reply"])
            replyNum='replyNum='+str(replyNum)+'$'
            content=content.encode("GBK",'ignore').decode("GBK")
            fw.write(content + '\t' + time + '\t' + str(replyNum) + '\n')
        
        page=page+1
        
    fw.close()
    print(str(aid)+"video已写入完成")
    
f=open("collectionList.txt","r")
for line in f:
    line=line.rstrip()
    videoNum=line
    try:
        get_comment(videoNum)
    except Exception as e:
        print("something serious happened for 视频" + str(videoNum))
        continue
            
