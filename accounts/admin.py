from django.contrib import admin
from .models import *


admin.site.register(UserBase)
admin.site.register(User)
admin.site.register(UserInfo)
admin.site.register(Company)
admin.site.register(CompanyInfo)
