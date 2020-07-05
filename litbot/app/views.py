# -*- coding: utf-8 -*-
from django.shortcuts import render
from app.models import user,keyword,note,keep,recommend
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.template import loader,Context
from .forms import NoteForm
from .models import note, keyword
import hashlib
import json
import datetime
from app import automark, cloud


class DateEncoder(json.JSONEncoder):

    def default(self, obj):

        if isinstance(obj, datetime.datetime):

            return obj.strftime("%Y-%m-%d %H:%M:%S.%f %Z")

        else:

            return json.JSONEncoder.default(self, obj)


def login(request):
    t=loader.get_template('newLogin.html')
    message=''
    c={}
    if 'login' in request.POST:
        name=request.POST['username']
        password=request.POST['password']
        a=hashlib.md5()
        a.update(password.encode('utf-8'))
        hashpwd=a.hexdigest()
        try :
            real_hashpwd = user.objects.get(user_name=name).password
            if hashpwd == real_hashpwd:
                print('登录成功')
                request.session['user_name']= name
                return HttpResponseRedirect('/index/')
            else:
                message = '密码错误'
                print('密码错误')
               # print(hashpwd)
               # print(real_hashpwd)
                c = {'message': message}
                return HttpResponse(t.render(c))
        except:
            message='用户不存在'
            print('用户不存在')
    c={'message':message}
    return HttpResponse(t.render(c))



def index(request):
    try:
        userName = request.session['user_name']
    except:
        return login(request)
    t=loader.get_template('newIndex.html')
    c={'userName':request.session['user_name']}
    return HttpResponse(t.render(c))

#上传笔记，将笔记存在note类中，note类中id（自动），name，author，raw_path，mark_path，is_public，submit_time
def upload(request):
#    print(request.POST['editordata'])
    noteName = request.POST['noteName'] #笔记名称
    noteContent = request.POST['editordata'] #笔记内容，是一串字符串，需要写入raw文件夹中的文件<note_id>.html

    note.objects.create(note_name=noteName, author=user.objects.get(user_name=request.session['user_name']))   #创建数据库中note对象

    noteIdList=note.objects.filter(note_name=noteName).order_by('-submit_time')[:1].values('note_id')
    noteId = noteIdList[0]['note_id']

    keep.objects.create(note=note.objects.get(note_id=noteId), user=user.objects.get(user_name=request.session['user_name']))
    #print(noteIdList[0]['note_id'])

    #当用户选中isPublic时，"shared:on"，当用户未选中时，什么都没有，所以用try except

    shared = True #用于recommend
    try:
        isPublic = request.POST['shared']
    except:
        #当用户未选中时
        note.objects.filter(note_id=noteId).update(is_public=False)
        shared = False
    else:
        note.objects.filter(note_id=noteId).update(is_public=True)

    #将note_id写入session
    request.session['note_id']=noteId
    # 将笔记内容写入文件
    GEN_HTML = "/home/ubuntu/litbot/app/raw/" + str(noteId) + ".html"
    f = open(GEN_HTML, 'w', encoding='utf-8')
    f.write(noteContent)
    f.close()

    #调用automark.py
    (keys, status, msg) = automark.mark(noteId)
    #将keys存入数据库，并返回给前端
    backList=[]
    backList.append(('resultCode', '200'))
    if(status==1):
        if(len(keys)>0):
            for word in keys:
                 keyword.objects.create(keyword_content=word, user=user.objects.get(user_name=request.session['user_name']),
                                        note=note.objects.get(note_id=noteId))
            backList.append(('keys', keys))



    #将raw_path和mark_path存入数据库
    note.objects.filter(note_id=noteId).update(raw_path="/home/ubuntu/litbot/app/raw/" + str(noteId) + ".html")
    note.objects.filter(note_id=noteId).update(mark_path="/home/ubuntu/litbot/app/raw/a" + str(noteId) + ".html")

    '''
    下方的函数将上传的笔记与recommend关联
    如果上传笔记允许共享，将该篇笔记的关键词与数据库中每个用户的关键词相匹配
    如果有交集，则存入recommend类中
    status为false(还未推荐)
    time默认是存入的当前时间，在推荐函数中修改到推荐的当前时间
    '''
    if(shared):#当前上传的笔记允许共享
        #keys是当前上传笔记的关键词列表
        #需要查出用户的关键词列表，将queryset转换为list
        if(len(keys)>0):
            allUser = user.objects.all()
            for u in allUser:
                if(u.user_name != request.session['user_name']):
                    keyList = []
                    keysQuerySet = u.keyword_set.values('keyword_content')
                    # print(keysQuerySet)
                    if (len(keysQuerySet) > 0):
                        for k in keysQuerySet:
                            keyList.append(k['keyword_content'])
                        if (len([i for i in keys if i in keyList]) > 0):  # 笔记关键词和用户关键词有交集
                            recommend.objects.create(user=u, note=note.objects.get(note_id=noteId))  # 创建推荐对象


    return JsonResponse(json.dumps(dict(backList)), safe = False)

def queryForUser(request):
    #该函数的用处是查询用户的笔记列表和个性化肖像的路径，以json形式返回给前端
    '''
    a = 5
    b = []
    b.append(('num', a))
    c = [{'name': 'a', 'age': 18}, {'name': 'b', 'age': 19}]
    b.append(('note', c))
    print(dict(b))
    print(json.dumps(dict(b)))
    '''


    noteNum = user.objects.get(user_name=request.session['user_name']).keep_set.all().count()
    queryList=[]
    queryList.append(('num', noteNum))

    noteDic = []
    keepSet = user.objects.get(user_name=request.session['user_name']).keep_set.order_by('-keep_time').values()
    #print(keepSet)

    for k in keepSet:
        noteDic.append(list(note.objects.filter(note_id=k['note_id']).values()))

    queryList.append(('note', noteDic))

#    print(queryList)
    return JsonResponse(json.dumps(dict(queryList), cls=DateEncoder),safe=False)

def readNote(request):
    request.session['readNote_id']= request.POST['note_id']
    return HttpResponseRedirect('/read/')


def read(request, noteId):
    #到数据库中查询raw_path和mark_path

    #判断这篇笔记是否公开
    if(note.objects.get(note_id=noteId).is_public == False):
        try:
            tmpUserName = request.session['user_name']
            if(tmpUserName!=note.objects.get(note_id=noteId).author.user_name):
                return HttpResponse("怎么乱访问别人的私密笔记！！！")
        except:
            return HttpResponse("怎么乱访问别人的私密笔记！！！")

    noteRawPath = note.objects.get(note_id=noteId).raw_path
    noteMarkPath = note.objects.get(note_id=noteId).mark_path
    author = note.objects.get(note_id=noteId).author.user_name
    upload_time = note.objects.get(note_id=noteId).submit_time
    note_name = note.objects.get(note_id=noteId).note_name

    with open(noteRawPath, 'r', encoding='utf-8') as f:
        rawContent = f.read()
    with open(noteMarkPath, 'r', encoding='utf-8') as f1:
        markContent = f1.read()

    t = loader.get_template('newReader.html')
    c = {'test_content': markContent, 'read_content': rawContent,
         'author': author, 'upload_time' : upload_time, 'note_name' : note_name}
    return HttpResponse(t.render(c))

#预览函数
def preview(request, noteId):
    #到数据库中查询raw_path和mark_path

    #判断这篇笔记是否公开
    if(note.objects.get(note_id=noteId).is_public == False):
        try:
            tmpUserName = request.session['user_name']
            if(tmpUserName!=note.objects.get(note_id=noteId).author.user_name):
                return HttpResponse("怎么乱访问别人的私密笔记！！！")
        except:
            return HttpResponse("怎么乱访问别人的私密笔记！！！")

    noteRawPath = note.objects.get(note_id=noteId).raw_path

    with open(noteRawPath, 'r', encoding='utf-8') as f:
        rawContent = f.read()

    return HttpResponse(rawContent)


#给用户推荐一篇文章
def rec(request):
    reco = (user.objects.get(user_name=request.session['user_name'])).recommend_set.filter().all()
    if(len(reco)==0):
        finalList = []
        return JsonResponse(json.dumps(dict(finalList), cls=DateEncoder), safe=False)
    else:
        if(len(reco)<4):
            #print("我进到reco<4里了！！！")
            finalList = []
            for r in reco:
                noteRec = r.note
                #noteRec.status = True
                noteRec.save()
                noteRecList = list(note.objects.filter(note_id=noteRec.note_id).values())
                #finalList.append(('rec', noteRecList))
                finalList.append(noteRecList)
        else:
            print("我进到reco>4了！！")
            finalList = []
            for r in reco[:4]:
                noteRec = r.note
                #noteRec.status = True
                noteRec.save()
                noteRecList = list(note.objects.filter(note_id=noteRec.note_id).values())
                #finalList.append(('rec', noteRecList))
                finalList.append(noteRecList)

        #return JsonResponse(json.dumps(dict(finalList), cls=DateEncoder), safe=False)
        dictFinal = {'rec': finalList}
        return JsonResponse(json.dumps(dictFinal, cls=DateEncoder), safe=False)


def save_keyword(request):
    if request.POST:
        user1 = user.objects.get(user_name=request.session['user_name'])
        note1 = note.objects.get(note_id=request.session['note_id'])
        old_keyword= keyword.objects.filter(user=user1,note=note1)
        old_keyword.delete()
        try:
            #keyword1 = json.loads(request.POST['keyword'])
            keyword1 = request.POST
            keyword1=keyword1.getlist('keyword')
            #print(keyword1)
            for i in keyword1:
                to_save_keyword=keyword(keyword_content=i,user=user1,note=note1)
                to_save_keyword.save()

            #更新肖像
            keywordlist=[ t[0] for t in keyword.objects.filter(user=user1).values_list('keyword_content')]
            (status,result)=cloud.get_wordcloud(request.session['user_name'], keywordlist)
            return HttpResponse("200")
        except Exception as e:
            print(e)
            status='fail'
            result='load error'
            return HttpResponse("700")

def keep_book(request, noteId):
    note_id=noteId
    user1 = user.objects.get(user_name=request.session['user_name'])
    note1 = note.objects.get(note_id=note_id)
    keep1=keep(user=user1,note=note1)
    keep2=keep.objects.filter(note=note1,user=user1)
    if keep2:
        return HttpResponse(700)
    keep1.save()
    keywordlist = keyword.objects.filter(note=note1).values_list('keyword_content')
    (status,result)=cloud.get_wordcloud(request.session['user_name'], keywordlist)
    return HttpResponse (200)












