from django.db import models
import django.utils.timezone as timezone

class user(models.Model):
    user_name=models.CharField(primary_key=True,max_length=20)
    password=models.CharField('password',max_length=50)
    profile=models.CharField('profile_path',max_length=50)  #肖像图片路径
    def __unicode__(self):
        return self.user_name

class note(models.Model):
    note_id=models.AutoField(primary_key = True)
    note_name=models.CharField(max_length=20)
    author=models.ForeignKey(user,on_delete=models.CASCADE,to_field="user_name")
    raw_path=models.CharField(max_length=50)
    mark_path=models.CharField(max_length=50)
    is_public=models.BooleanField(default=False) #false指不公开
    submit_time=models.DateTimeField(default = timezone.now)
    def __unicode__(self):
        return self.note_id

class keyword(models.Model):
    keyword_id=models.AutoField(primary_key = True)
    keyword_content=models.CharField(max_length=20)
    user=models.ForeignKey(user,on_delete=models.CASCADE,to_field="user_name")
    note=models.ForeignKey(note,on_delete=models.CASCADE,to_field="note_id")
    def __unicode__(self):
        return self.keyword_content

class keep(models.Model):
    keep_id=models.AutoField(primary_key = True)
    user=models.ForeignKey(user,on_delete=models.CASCADE,to_field="user_name")
    note = models.ForeignKey(note, on_delete=models.CASCADE, to_field="note_id")
    keep_time=models.DateTimeField(default = timezone.now)
    def __unicode__(self):
        return self.keep_id

class recommend(models.Model):
    recommend_id=models.AutoField(primary_key = True)
    user=models.ForeignKey(user,on_delete=models.CASCADE,to_field="user_name")
    note = models.ForeignKey(note, on_delete=models.CASCADE, to_field="note_id")
    status=models.BooleanField(default=False) #false指未推荐
    recommend_time=models.DateTimeField(default = timezone.now)
    def __unicode__(self):
        return self.recommend_id





