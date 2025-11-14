from django.contrib import admin
from .models import CustomUser, Bounty, Submission

admin.site.register(CustomUser)
admin.site.register(Bounty)
admin.site.register(Submission)
