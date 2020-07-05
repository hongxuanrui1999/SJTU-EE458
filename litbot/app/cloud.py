from wordcloud import WordCloud
import matplotlib.pyplot as plt
##########################
# input: (int: user id for saving figure, list<string>: a list of keywrods)
# ouput: (status: bool, msg: string) msg is the error message, it's empty if status=1 
##########################
def get_wordcloud(id, keys):
    if(len(keys)<1):
        return (0,"请检查函数输入")
    try:
        font = '/home/ubuntu/litbot/app/simhei.ttf' 
        
        #if(len(keys)<10):
            #keys += keys
        keys = " ".join(keys)
        cloud = WordCloud(scale=4, font_path=font, background_color="white", width=1000, height=860, margin=2).generate(keys)
        #cloud = WordCloud(scale=4,  background_color="white", width=1000, height=860, margin=2).generate(keys)
        fig = plt.figure(num=1, #figsize=(15, 8),
                         dpi=80) 
        plt.imshow(cloud, interpolation='bilinear')
        plt.axis("off")
        
        fig.savefig('/home/ubuntu/litbot/app/static/cloud/'+str(id)+'.eps',dpi=80,format='eps')
        fig.savefig('/home/ubuntu/litbot/app/static/cloud/'+str(id)+'.jpg',dpi=600)
    except Exception as e:
        print("make fault:", e)
        return (0,"词云制作失败")
    return (1,"")

'''
##########################
# input: (list<string>: a list of keywrods)
# ouput: (list<string>: enlarged keywords, len()>=10)
##########################
def enlarge(keys):
    pass
   return keys 
'''
    
