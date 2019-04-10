from django.contrib import admin
from catalog.models import Item, Rate, User, Prediction

# Register your models here.

admin.site.register(Item)
admin.site.register(Rate)
admin.site.register(User)
admin.site.register(Prediction)
