#!/usr/bin/python
# -*- coding: utf-8 -*-

#有參考一些https://github.com/wy36101299/PTTcrawler的想法，解決一些error的問題
#匯入資源
import os
import requests
import time
import json
import glob
import random
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
        time.sleep(random.uniform(0, 1)/5)
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
                        time.sleep(random.uniform(0, 1)/5)
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
                    try:
                        _post['ip'] = meta2[0].text.split(' ')[-1:][0].rstrip('\n').encode('utf-8')#ip位置
                    except:
                        _post['ip'] = 'ip is not find'.encode('utf-8')
                    _post['site'] = link#這個meta2[1].text.split(' ')[-1:][0].rstrip('\n')會有點錯誤#文章網址
                    for i in list(title_dic.keys()):#標題、時間、作者
                        for x in range(len(soup.find(id='main-content').find_all(class_='article-meta-tag'))):
                            if soup.find(id='main-content').find_all(class_='article-meta-tag')[x].text == i.decode('utf-8'):
                                _post[title_dic[i]] = meta1[x].text.encode('utf-8')
                        if meta1 == None:
                            _post[title_dic[i]] = 'I do not know TAT'.encode('utf-8')
                except:
                    # print 'b'
                    try:
                        _post['ip'] = meta2[0].text.split(' ')[-1:][0].rstrip('\n')#ip位置
                    except:
                        _post['ip'] = 'ip is not find'.encode('utf-8')
                    _post['site'] = link#這個meta2[1].text.split(' ')[-1:][0].rstrip('\n')會有點錯誤#文章網址
                    for link2 in posts:
                        if pre + link2.find(class_='title').a['href'] == link:
                            _post['author'] = link2.find(class_='author').text.encode('utf-8')
                            _post['title'] = link2.find(class_='title').text.encode('utf-8')
                            _post['time'] = link2.find(class_='date').text.encode('utf-8')
                try:
                    date = soup.select('.article-meta-value')[3].text
                    content = soup.find(id="main-content").text
                    target_content=u'※ 發信站: 批踢踢實業坊(ptt.cc),'
                    content = content.split(target_content)
                    content = content[0].split(date)
                    main_content = content[1].replace('\n', '  ').replace('\t', '  ')
                    _post['content'] = main_content.encode('utf-8')
                except:
                    try:
                        for text in soup.find(id='main-content'):#內文
                            if isinstance(text, NavigableString):
                                _post['content'] = text.strip().encode('utf-8')
                    except:
                        #https://www.ptt.cc/bbs/NTUcourse/M.1329877051.A.FA5.html的情況
                        suc = False
                        e4 = 'error 4'
                        print(e4)
                        _post['content'] = []#下面的comments，每一則留言分成一個dictionary集合
                _post['comments'] = []
                try:
                    num , g , b , n ,message = 0,0,0,0,{}
                    for tag in soup.select('div.push'):
                        num += 1
                        push_tag = tag.find("span", {'class': 'push-tag'}).text
                        push_userid = tag.find("span", {'class': 'push-userid'}).text       
                        push_content = tag.find("span", {'class': 'push-content'}).text   
                        push_content = push_content[1:]
                        push_ipdatetime = tag.find("span", {'class': 'push-ipdatetime'}).text   
                        push_ipdatetime = remove(push_ipdatetime, '\n')
                        message[num]={"狀態":push_tag.encode('utf-8'),"留言者":push_userid.encode('utf-8'),"留言內容":push_content.encode('utf-8'),"留言時間":push_ipdatetime.encode('utf-8')}
                        if push_tag == u'推 ':
                            g += 1
                        elif push_tag == u'噓 ':
                            b += 1
                        else:
                            n += 1
                    messageNum = {"g":g,"b":b,"n":n,"all":num}
                except:
                    try:
                        num , g , b , n ,message = 0,0,0,0,{}
                        for comment in soup.find_all(class_='push'):
                            num += 1
                            _post['comments'].append({'tag':comment.find(class_='push-tag').text.encode('utf-8'),
                         'user':comment.find(class_='push-userid').text.encode('utf-8'), 
                         'pushcontent':comment.find(class_='push-content').text.lstrip(':').encode('utf-8'),
                          'time':comment.find(class_='push-ipdatetime').text.strip().encode('utf-8')})
                            if comment.find(class_='push-tag').text == u'推 ':
                                g += 1
                            elif comment.find(class_='push-tag').text == u'噓 ':
                                b += 1
                            else:
                                n += 1
                        messageNum = {"g":g,"b":b,"n":n,"all":num}
                    except:
                        suc = False
                        e5 = 'error 5'
                        print(e5)
                        print(link)
                        _post['comments'] = []
                post_list.append(_post)
        with open(str(pages)+e1[:1]+e1[-1:]+e2[:1]+e2[-1:]+e3[:1]+e3[-1:]+e4[:1]+e4[-1:]+e5[:1]+e5[-1:]+'.json', 'w') as fout:
            json.dump(post_list, fout,ensure_ascii=False,indent=4,sort_keys=True)
    print url
    print str(y)+'次', str(pages) + '.json saved'
    if pages > 1:
        pages -= 1
    #繼續跑回圈
    if pages >= 1 and os.path.exists(str(pages)+'.json') == False:#int(url.rstrip('.html').lstrip('https://www.ptt.cc/bbs/NTUcourse/index'))-1001:
        time.sleep(random.uniform(0, 1)/5)
        pages, y, e1, e2, e3, e4, e5, t = linkscrwaling(pages, y, e1, e2, e3, e4, e5, t)
    elif pages >= 1 and os.path.exists(str(pages)+'.json') == True:
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