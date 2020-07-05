from django.contrib import admin
from app.models import user,keyword,note,keep,recommend

admin.site.register(user)
admin.site.register(keyword)
admin.site.register(note)
admin.site.register(keep)
admin.site.register(recommend)