#!/usr/bin/python
# -*- coding: utf-8 -*-
#匯入資源
import os
import requests
import time
import json
import glob
from bs4 import BeautifulSoup
from bs4 import NavigableString

#設定
title_dic = {'標題':'title', '作者':'author', '時間':'time'}
#先找出目前最大的頁面
pre = 'https://www.ptt.cc'
url = 'https://www.ptt.cc/bbs/NTUcourse/index.html'
result = requests.get(url)
soup = BeautifulSoup(result.text, "lxml")
btn = soup.find(class_='btn-group-paging')
end = int(btn.find_all('a')[1]['href'].split('index')[1].split('.')[0]) + 1
url = pre + '/bbs/NTUcourse/index%d.html'%end
pages = end
y = 0
t = 0
suc = True
e1 = ''
e2 = ''
e3 = ''
e4 = ''
e5 = ''
#開始抓取資料
#資料格式：{'time':XX, 'title':'', 'author':'', 'content':xx, 'comments':XX, 'site':XX, 'ip':xx}
#comments的資料結構是：{'tag':xx, 'user':XX, 'content':xx, 'time':XX}
#一篇用一個dictionary裝起來

#先是文章列表，先把所有網址儲存起來
def cycleresults(url, t, e1):
    suc = True
    rdata = ''
    if t < 10:
        time.sleep(t)
    try:
        rdata = requests.get(url)
    except:
        t += 1
        e1 = 'error 1'
        print(e1)
        suc = False
        print(t)
        if suc == False:
            if t < 10:
                rdata, t, e1 = cycleresults(url, t, e1)
            elif t >= 10:
                t = 0
                rdata = ''
                pass
    return rdata, t, e1

def linkscrwaling(pages, y, e1, e2, e3, e4, e5, t):
    post_list = []
    links = []
    url = 'https://www.ptt.cc/bbs/NTUcourse/index%d.html'%(int(pages))
    y += 1
    if os.path.exists(str(pages)+'.json') == False or os.path.exists(str(pages)+e1[:1]+e1[-1:]+e2[:1]+e2[-1:]+e3[:1]+e3[-1:]+e4[:1]+e4[-1:]+e5[:1]+e5[-1:]+'.json') == False:
        e1 = ''
        e2 = ''
        e3 = ''
        e4 = ''
        e5 = ''
        results, t, e1 = cycleresults(url, t, e1)
        try:
            soup = BeautifulSoup(results.text, "lxml")
            posts = soup.find_all(class_='r-ent')
            for link in posts:#此為列表的每個主題
                #若文章被刪除或水桶，網址會消失，會出錯
                if 'NTUCourse板板規'.decode('utf-8') not in link.find(class_='title').text.strip() and '本文已被刪除'.decode('utf-8') not in link.find(class_='title').text.strip():
                    links.append(pre + link.find(class_='title').a['href'])
        except:
            e1 = 'error 1'
            print(e1)
            if rdata == '':
                _post = {}
                for i in list(title_dic.keys()):
                    _post[title_dic[i]] = ''
                _post['ip'] = ''
                _post['site'] = ''
                _post['content'] = '404-No Found.'
                _post['comments'] = []
                _post['comments'].append({'tag':'', 'user':'', 'pushcontent':'', 'time':''})
                post_list.append(_post)
            pass
        #開始存資料
        if results != '':
            for link in links:
                try:
                    results = requests.get(link)
                except:
                    e2 = 'error 2'
                    print(e2)
                    try:
                        time.sleep(1)
                        results = requests.get(link)
                    except:
                        suc = False
                        e2 = 'error 2'
                        print(e2)
                        pass
                soup = BeautifulSoup(results.text, "lxml")
                try:
                    meta1 = soup.find(id='main-content').find_all(class_='article-meta-value')
                    meta2 = soup.find(id='main-content').find_all(class_='f2')
                except:
                    suc = False
                    e3 = 'error 3'
                    print(e3)
                    print link
                    if soup.find(id='main-content') == None:
                        pass
                _post = {}
                try:
                    # print 'a'
                    #開始加入資料
                    _post['ip'] = meta2[0].text.split(' ')[-1:][0].rstrip('\n')#ip位置
                    _post['site'] = link#這個meta2[1].text.split(' ')[-1:][0].rstrip('\n')會有點錯誤#文章網址
                    for i in list(title_dic.keys()):#標題、時間、作者
                        for x in range(len(soup.find(id='main-content').find_all(class_='article-meta-tag'))):
                            if soup.find(id='main-content').find_all(class_='article-meta-tag')[x].text == i.decode('utf-8'):
                                _post[title_dic[i]] = meta1[x].text
                        if meta1 == None:
                            _post[title_dic[i]] = 'I do not know TAT'
                except:
                    # print 'b'
                    for link2 in posts:
                        if pre + link2.find(class_='title').a['href'] == link:
                            _post['author'] = link2.find(class_='author').text
                            _post['title'] = link2.find(class_='title').text
                            _post['time'] = link2.find(class_='date').text
                try:
                    for text in soup.find(id='main-content'):#內文
                        if isinstance(text, NavigableString):
                            _post['content'] = text.strip()
                except:
                    #https://www.ptt.cc/bbs/NTUcourse/M.1329877051.A.FA5.html的情況
                    suc = False
                    e4 = 'error 4'
                    print(e4)
                    _post['content'] = []#下面的comments，每一則留言分成一個dictionary集合
                _post['comments'] = []
                try:
                    for comment in soup.find_all(class_='push'):
                        _post['comments'].append({'tag':comment.find(class_='push-tag').text,
                         'user':comment.find(class_='push-userid').text, 
                         'pushcontent':comment.find(class_='push-content').text.lstrip(':'),
                          'time':comment.find(class_='push-ipdatetime').text.strip()})
                except:
                    suc = False
                    e5 = 'error 5'
                    print(e5)
                    print(link)
                    _post['comments'] = []
                post_list.append(_post)
        with open(str(pages)+e1[:1]+e1[-1:]+e2[:1]+e2[-1:]+e3[:1]+e3[-1:]+e4[:1]+e4[-1:]+e5[:1]+e5[-1:]+'.json', 'w') as fout:
            json.dump(post_list, fout)
    print url
    print str(y)+'次', str(pages) + '.json saved'
    if pages > 1:
        pages -= 1
    #繼續跑回圈
    if pages >= 1 and os.path.exists(str(pages)+'.json') == False:#int(url.rstrip('.html').lstrip('https://www.ptt.cc/bbs/NTUcourse/index'))-1001:
        pages, y, e1, e2, e3, e4, e5, t = linkscrwaling(pages, y, e1, e2, e3, e4, e5, t)
    elif pages >= 1 and os.path.exists(str(pages)+'.json') == True:
        time.sleep(0.1)
        pages, y, e1, e2, e3, e4, e5, t = linkscrwaling(pages, y, e1, e2, e3, e4, e5, t)
    return pages, y, e1, e2, e3, e4, e5, t
pages, y, e1, e2, e3, e4, e5, t = linkscrwaling(pages, y, e1, e2, e3, e4, e5, t)
#http://stackoverflow.com/questions/25105541/python-quicksort-runtime-error-maximum-recursion-depth-exceeded-in-cmp
#list資料太多會有runtime-error-maximum-recursion-depth-exceeded-in-cmp的問題，所以變成每跑一個index頁面就存一次
# =.(='main-content').(='article-meta-value')     52=.(='main-content').(='f2')     53={}AttributeError

#合併檔案#http://stackoverflow.com/questions/23520542/issue-with-merging-multiple-json-files-in-python
read_files = glob.glob("*.json")
output_list = []
for f in read_files:
    with open(f, "r") as infile:
        output_list += json.load(infile)
with open("merged_ptt.json", "w") as outfile:
    json.dump(output_list, outfile)