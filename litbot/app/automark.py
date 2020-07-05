import jieba.posseg as pseg
import jieba.analyse as analyse
import re, jieba
from bs4 import BeautifulSoup

class CausalityExractor():
    def __init__(self):
        pass

    '''1由果溯因配套式'''
    def ruler1(self, sentence):
        datas = list()
        word_pairs =[['之所以', '是因为'], ['之?所以', '由于'], ['之?所以', '缘于']]
        for word in word_pairs:
            pattern = re.compile(r'\s?(%s)/[p|c]+\s(.*)(%s)/[p|c]+\s(.*)' % (word[0], word[1]))
            result = pattern.findall(sentence)

            data = dict()
            if result:
                data['tag'] = result[0][0] + '-' + result[0][2]
                data['cause'] = result[0][3]
                data['effect'] = result[0][1]
                datas.append(data)
        if datas:
            return 1,datas[0]
        else:
            return 0,{}
    '''2由因到果配套式'''
    def ruler2(self, sentence):
        '''
        conm1:〈因为,从而〉、〈因为,为此〉、〈既[然],所以〉、〈因为,为此〉、〈由于,为此〉、〈只有|除非,才〉、〈由于,以至[于]>、〈既[然],却>、
        〈如果,那么|则〉、<由于,从而〉、<既[然],就〉、〈既[然],因此〉、〈如果,就〉、〈只要,就〉〈因为,所以〉、 <由于,于是〉、〈因为,因此〉、
         <由于,故〉、 〈因为,以致[于]〉、〈因为,因而〉、〈由于,因此〉、<因为,于是〉、〈由于,致使〉、〈因为,致使〉、〈由于,以致[于] >
         〈因为,故〉、〈因[为],以至[于]>,〈由于,所以〉、〈因为,故而〉、〈由于,因而〉
        conm1_model:<Conj>{Cause}, <Conj>{Effect}
        '''
        datas = list()
        word_pairs =[['因为', '从而'], ['既然?', '所以'],
                    ['由于', '以至于?'],
                     ['由于', '从而'],
                    ['既然?', '因此'],
                    ['因为', '所以'], ['由于', '于是'],
                    ['因为', '因此'], ['由于', '故'],
                    ['因为', '因而'], ['由于', '因此'],
                    ['因为', '于是'],
                    ['由于', '所以'], ['由于', '因而'],
        #extra
                    ['因为?','故']
                    ]

        for word in word_pairs:
            pattern = re.compile(r'\s?(%s)/[p|c]+\s(.*)(%s)/[p|c|n]+\s(.*)' % (word[0], word[1]))
            result = pattern.findall(sentence)
            data = dict()
            if result:
                data['tag'] = result[0][0] + '-' + result[0][2]
                data['cause'] = result[0][1]
                data['effect'] = result[0][3]
                datas.append(data)
        if datas:
            return 1,datas[0]
        else:
            return 0,{}
    '''3由因到果居中式明确'''
    def ruler3(self, sentence): #-->r'(.*)[,，]+.*()/[p|c]+\s(.*)'
        pattern = re.compile(r'(.*)[,，]+.*(于是|所以|致使|以致于?|因此|以至于?|从而|因而)/[p|c|v]+\s(.*)')
        result = pattern.findall(sentence)
        data = dict()
        if result:
            data['tag'] = result[0][1]
            data['cause'] = result[0][0]
            data['effect'] = result[0][2]
            return 1, data
        return 0, data
    '''4由因到果居中式精确'''
    def ruler4(self, sentence):
        pattern = re.compile(r'(.*)\s+(已致|导致|指引|使|促成|造成|造就|促使|酿成|引发|促进|引起|引来|促发|引致|诱发|推动|招致|致使|滋生|作用|使得|决定|令人|带来|触发|归因于)/[d|v]+\s(.*)')
        result = pattern.findall(sentence)
        data = dict()
        if result:
            data['tag'] = result[0][1]
            data['cause'] = result[0][0]
            data['effect'] = result[0][2]
            return 1, data
        return 0, data
    '''5由因到果前端式模糊'''
    def ruler5(self, sentence):
        pattern = re.compile(r'\s?(因为|因|凭借|由于)/[p|c]+\s(.*)[,，]+(.*)')
        result = pattern.findall(sentence)
        data = dict()
        if result:
            data['tag'] = result[0][0]
            data['cause'] = result[0][1]
            data['effect'] = result[0][2]
            return 1, data
        return 0, data

    '''6由因到果居中式模糊'''
    def ruler6(self, sentence):
        pattern = re.compile(r'\s(.*)(以免|以便)/[c|d]+\s(.*)')
        result = pattern.findall(sentence)

        data = dict()
        if result:
            data['tag'] = result[0][1]
            data['cause'] = result[0][0]
            data['effect'] = result[0][2]
            return 1, data
        return 0, data

    '''7由因到果前端式精确'''
    def ruler7(self, sentence):
        pattern = re.compile(r'\s?(只要)/[p|c]+\s(.*)[,，]+(.*)')
        result = pattern.findall(sentence)
        data = dict()
        if result:
            data['tag'] = result[0][0]
            data['cause'] = result[0][1]
            data['effect'] = result[0][2]
            return 1, data
        return 0, data

    '''8由果溯因居中式模糊'''
    def ruler8(self, sentence):
        pattern = re.compile(r'(.*)(取决于|缘于|在于|出自|来自|发自|源于)[p|c|v]+\s(.*)')
        result = pattern.findall(sentence)
        data = dict()
        if result:
            data['tag'] = result[0][1]
            data['cause'] = result[0][2]
            data['effect'] = result[0][0]
            return 1, data
        return 0, data

    '''9 名词性匹配'''
    def ruler9(self,sentence):
        '''的原因是，'''
        pattern = re.compile(r'(.*)的/uj 原因/n 是/v+\s(.*)')
        result = pattern.findall(sentence)
        data = dict()
        if result:
            data['tag'] = "的原因是"
            data['cause'] = result[0][1]
            data['effect'] = result[0][0]
            return 1,data
        return 0,data

    '''10 名词性匹配'''
    def ruler10(self,sentence):
        '''的结果是'''
        pattern = re.compile(r'(.*)的/uj 结果n 是/v+\s(.*)')
        result = pattern.findall(sentence)
        data = dict()
        if result:
            data['tag'] = "的结果是"
            data['cause'] = result[0][0]
            data['effect'] = result[0][1]
            return 1, data
        return 0, data

    '''抽取主函数'''
    def extract_triples(self, sentence):

        result = dict()
        match, result = self.ruler1(sentence)
        if match==1:
            return result

        match, result = self.ruler9(sentence)
        if match==1:
            return result

        match, result = self.ruler10(sentence)
        if match==1:
            return result

        match, result = self.ruler2(sentence)
        if match==1:
            return result

        match, result = self.ruler3(sentence)
        if match==1:
            return result

        match, result = self.ruler4(sentence)
        if match==1:
            return result

        match, result = self.ruler5(sentence)
        if match==1:
            return result

        match, result = self.ruler6(sentence)
        if match==1:
            return result

        match, result = self.ruler7(sentence)
        if match==1:
            return result

        match, result = self.ruler8(sentence)
        if match==1:
            return result

        return result

    '''抽取主控函数'''
    def extract_main(self, sent):
        #分词+词性标注
        sent = ' '.join([word.word + '/' + word.flag for word in pseg.cut(sent)])
        result = self.extract_triples(sent)
        return result

def get_key(sent,k):
    #print("extacting ",k, "words\n")
    keywords = analyse.extract_tags(sent, topK=k, withWeight=False, allowPOS=('n','a','ad','v'))
    #keywords = analyse.textrank(sent, topK=k, withWeight=True, allowPOS=('n', 'a', 'ad', 'v'))
    return keywords

def get_score(sent):
    #print(sent)
    keywords = analyse.extract_tags(sent, topK=1, withWeight=True, allowPOS=('n','a','ad','v'))
    if(len(keywords)>0):
         return keywords[0][1]
    else:
        return "empty sent"

def get_mark(tag,doc_keys):
    try:
        extractor = CausalityExractor()
        text = str(tag.string)
        #print("Get marking:")
        #print(text)
        #cut into words
        words = [word.word for word in pseg.cut(text)]
        
        #get keys
        density = 0.02
        num = int(len(text)*density)
        keys = [item for item in get_key(text,num)]
        #print("Key Extracted...")
        #generate marked text by keys
        mark = ''
        for w in words:
            if w in keys and not w in doc_keys:
                mark += '__'*len(w)
            else:
                mark += w

        #find causilty relation
        #cut into sentences
        paras = re.split(r'[;；。.?!？！\s]\s*', mark)
        for para in paras:
            #print("Find causality in a para:")
            #print(para)
            result = extractor.extract_main(para)
            #find some causily relation
            if result:
                cause = ''.join([word.split('/')[0] for word in result['cause'].split(' ') if word.split('/')[0]])
                effect = ''.join([word.split('/')[0] for word in result['effect'].split(' ') if word.split('/')[0]])
                #print("Cause:",cause)
                #print("Effect:", effect)
                c_s = -1
                e_s = -1

                if(2<=len(cause)<=30):
                    c_s = get_score(cause)
                if(2<=len(effect)<=30):
                    e_s = get_score(effect)
                #print("Scores:",c_s, e_s)
                if(c_s!="empty sent" and e_s!="empty sent"): 
                    
                    if(c_s>=e_s>-1):
                        mark.replace(cause,'_'*2*len(cause),10)
                    elif(e_s>c_s>-1):
                        mark.replace(effect,'_'*2*len(effect),10)
                
        tag.string = mark
        #print("Causality Extracted...")
    except:
        return 0
    return 1



##############################
#input: (int: noteid) 
#output: (list<string>: keywords of the documents 0=<len<=3), 
#          bool: status-whether the automark file generated, 
#          string: msg-error message, empty if status=1)  
##############################
def mark(noteid):
    source = open('/home/ubuntu/litbot/app/raw/'+str(noteid)+'.html','r',encoding='utf-8')
    #source = open('raw/'+str(noteid)+'.html','r',encoding='utf-8')
    #读入html
    orig = ""
    k = 0
    while(True):
        tmp = source.readline()
        if(tmp==''):
            break
        orig += tmp
        k += 1
    source.close()
    
    # 生成html结构
    soup = BeautifulSoup(orig,'lxml') 
    
    # 获取全部文字，输出关键词
    doc = soup.get_text()
    n_doc_keys = 5
    tmp = int(len(doc)/500)
    if(tmp>n_doc_keys):
        tmp = n_doc_keys
    elif (tmp==0):
        tmp = 1
    doc_keys = get_key(doc,tmp)

    # 找到所有标签
    #print(soup.prettify())
    tag_s1 = soup.find_all()
    for i in range(len(tag_s1)):
        if(tag_s1[i].string!=None):
                #print(tag_s1[i].name, tag_s1[i].string)
                if(not get_mark(tag_s1[i],doc_keys)):
                    return doc_keys, 0, "自动抽取错误" 
    #print(soup.prettify())
    f = open('/home/ubuntu/litbot/app/raw/a'+str(noteid)+'.html','w',encoding='utf-8')
    #f = open('automark/a'+str(noteid)+'.html','w',encoding='utf-8')
    f.write(soup.prettify())
    f.close()

    return doc_keys, 1, ''

""" s = [1,26,27,30,40,101,126,177,178,179,180,181,182]
for id in s:
    print(mark(id)) """