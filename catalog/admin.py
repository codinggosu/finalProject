from django.contrib import admin
from catalog.models import Item, Rate, Profile, Prediction

# Register your models here.

admin.site.register(Item)
admin.site.register(Rate)
admin.site.register(Profile)
admin.site.register(Prediction)
