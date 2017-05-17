# -*- coding: utf-8 -*-
SPIT_LV = True
SPIT_NAME = False
SPIT_MID = True
SPIT_MSG = True
# -*- coding: utf-8 -*-
"""
Created on Mon May 26 23:59:09 2014
@author: Vespa
"""
import urllib2
import urllib
import re
import json
import zlib
import gzip
import xml.dom.minidom
import hashlib
import time
import sys
import os
import codecs
import workerpool
class User():
    def __init__(self,m_mid=None,m_name=None):
        if m_mid:
            self.mid = m_mid
        if m_name:
            if isinstance(m_name,unicode):
                m_name = m_name.encode('utf8')
            self.name = m_name
#   获取空间地址
    def GetSpace(self):
        return 'http://space.bilibili.tv/'+str(self.mid)
    mid = None
    name = None
    isApprove = None#是否是认证账号
    spaceName = None
    sex = None
    rank = None
    avatar = None
    follow = None#关注好友数目
    fans = None#粉丝数目
    article = None#投稿数
    place = None#所在地
    description = None#认证用户为认证信息 普通用户为交友宣言
    followlist = None#关注的好友列表
    friend = None
    DisplayRank = None
class Comment():
    def __init__(self):
        self.post_user = User()
    lv = None#楼层
    fbid = None#评论id
    msg = None
    ad_check = None#状态 (0: 正常 1: UP主隐藏 2: 管理员删除 3: 因举报删除)
    post_user = None
class CommentList():
    def __init__(self):
        pass
    comments = None
    commentLen = None
    page = None
class JsonInfo():
	def __init__(self,url):
		self.info = json.loads(getURLContent(url))
		while self.info.has_key('code') and self.info['code'] != 0:
			time.sleep(0.01)
			self.info = json.loads(getURLContent(url))
			print('Entered!')
			if self.info.has_key('message'):
				print("【Error】code=%d, msg=%s, url=%s"%(self.info['code'],self.Getvalue('message'),url))
			elif self.info.has_key('error'):
				print("【Error】code=%d, msg=%s, url=%s"%(self.info['code'],self.Getvalue('error'),url))
			error = True
		error = False
	def Getvalue(self,*keys):
		if len(keys) == 0:
			return None
		if self.info.has_key(keys[0]):
			temp = self.info[keys[0]]
		else:
			return None
		if len(keys) > 1:
			for key in keys[1:]:
				if temp.has_key(key):
					temp = temp[key]
				else:
					return None
		if isinstance(temp,unicode):
			temp = temp.encode('utf8')
		return temp
	info = None
	error = False
	
def getURLContent(url):
	while True:
		flag = 1
		try:
			headers = {'User-Agent':'Mozilla/5.0 (Windows U Windows NT 6.1 en-US rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
			req = urllib2.Request(url = url,headers = headers)
			content = urllib2.urlopen(req).read()
		except:
			flag = 0
		if flag == 1:
			break
	return content
	
def GetString(t):
	if type(t) == int:
		return str(t)
	return t
def GetComment(aid, page = None, pagesize = None, order = None):
	"""
输入：
	aid：AV号
	page：页码
	pagesize：单页返回的记录条数，最大不超过300，默认为10。
	order：排序方式 默认按发布时间倒序 可选：good 按点赞人数排序 hot 按热门回复排序
返回：
	评论列表
	"""
	url = 'http://api.bilibili.cn/feedback?aid='+GetString(aid)
	if page:
		url += '&page='+GetString(page)
	if pagesize:
		url += '&pagesize='+GetString(pagesize)
	if order:
		url += '&order='+GetString(order)
	jsoninfo = JsonInfo(url)
	commentList = CommentList()
	commentList.comments = [Comment()] * pagesize
	commentList.commentLen = jsoninfo.Getvalue('totalResult')
	commentList.page = jsoninfo.Getvalue('pages')
	idx = 0
	while jsoninfo.Getvalue(str(idx)):
		liuyan = Comment()
		liuyan.lv = jsoninfo.Getvalue(str(idx),'lv')
		liuyan.fbid = jsoninfo.Getvalue(str(idx),'fbid')
		liuyan.msg = jsoninfo.Getvalue(str(idx),'msg')
		liuyan.ad_check = jsoninfo.Getvalue(str(idx),'ad_check')
		#liuyan.post_user = GetUserInfoBymid(jsoninfo.Getvalue(str(idx),'mid'))
		liuyan.post_user.mid = jsoninfo.Getvalue(str(idx),'mid')
		'''
		liuyan.post_user.avatar = jsoninfo.Getvalue(str(idx),'face')
		liuyan.post_user.rank = jsoninfo.Getvalue(str(idx),'rank')
		liuyan.post_user.name = jsoninfo.Getvalue(str(idx),'nick')'''
		commentList.comments[idx] = liuyan
		idx += 1
	return commentList
def GetAllComment(aid, order = None):
	"""
获取一个视频全部评论，有可能需要多次爬取，所以会有较大耗时
输入：
	aid：AV号
	order：排序方式 默认按发布时间倒序 可选：good 按点赞人数排序 hot 按热门回复排序
返回：
	评论列表
	"""
	MaxPageSize = 300
	commentLists = [GetComment(aid = aid, page = 1, pagesize = MaxPageSize, order = order)]
	totalPage = commentLists[0].page
	directory = 'av' + str(aid) + 'Comments'
	if not os.path.exists(directory):
		os.makedirs(directory)
	if totalPage > 1:
		#urls = ['http://api.bilibili.cn/feedback?aid=' + str(aid) + '&page=' + str(p) + '&pagesize=' + str(MaxPageSize) for p in range(2, commentList.page + 1)]
		# Make a pool
		#pool = workerpool.WorkerPool(size = 10)
		pool = workerpool.WorkerPool(size = totalPage - 1)
		# Build our `map` parameters
		#saveto = [directory + '/' + str(x) for x in range(2, commentList.page + 1)]
		# Perform the mapping
		#pool.map(urllib.urlretrieve, urls, saveto)
		commentLists2 = pool.map(GetComment, [aid] * (totalPage - 1), range(2, totalPage + 1), [MaxPageSize] *  (totalPage - 1))
		# Send shutdown jobs to all threads, and wait until all the jobs have been completed
		pool.shutdown()
		pool.wait()
		for cl in commentLists2:
			commentLists.append(cl)
		'''
		commentList.comments += [Comment()] * (commentList.page - 1)
		for p in range(2, commentList.page + 1):
			commentPath = directory + '/' + str(p)
			commentList.comments[(p - 1) * MaxPageSize :] = GetCommentLocal(commentPath, MaxPageSize).comments
			os.remove(commentPath)
		os.rmdir(directory)
	#经测试发现，如果视频评论涨幅过快(av2816940)
	#那么JSON第一层的totalResult和pages可能不准
	#即使每抓一页都重新读取totalResult也无济于事
	while commentList.comments[len(commentList.comments) - 1].lv == None:
		commentList.comments.pop()
	commentList.commentLen = len(commentList.comments)'''
	for cl in commentLists:
		while cl.comments[len(cl.comments) - 1].lv == None:
			cl.comments.pop()
	commentLists = sorted(commentLists, key = GetCommentListKey, reverse = True)
	return commentLists
def GetCommentListKey(commentList):
	return commentList.comments[0].lv
if __name__ == "__main__":
	print(u'请输入要拽取评论视频的av号')
	videoaid = input()
	commentTxt = codecs.open('av' + str(videoaid) + 'comments.txt',  encoding = 'utf-8', mode = 'w')
	allComment = GetAllComment(videoaid)
	x = 0
	#commentTxtList = [u''] * len(allComment.comments)
	tempStrListSize = SPIT_LV + SPIT_NAME + SPIT_MID
	for cl in allComment:
		for aComment in cl.comments:
	#while x < len(allComment.comments):
		#aComment = allComment.comments[x]
			tempStrList = [u''] * tempStrListSize
			tempStr = u''
			i = 0
			if SPIT_LV:
				tempStrList[i] = unicode(str(aComment.lv)) + u'楼'
				i += 1
			if SPIT_NAME:
				tempStrList[i] = u'昵称: ' + unicode(str(aComment.post_user.name))
				i += 1
			if SPIT_MID:
				tempStrList[i] = u'UID: ' + unicode(str(aComment.post_user.mid))
				i += 1
			y = 0
			if tempStrListSize == 1:
				tempStr += tempStrList[0] + u'\n'
			if tempStrListSize > 1:
				while y < tempStrListSize - 1:
					tempStr += tempStrList[y] + u'\t'
					y += 1
				tempStr += tempStrList[y] + u'\n'
			if SPIT_MSG:
				tempStr += aComment.msg.decode('utf8')
				tempStr += u'\n'
			commentTxt.write(tempStr)
	commentTxt.close()
    
