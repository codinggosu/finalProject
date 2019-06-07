from django.db import models
from django.urls import reverse
from django.db.models import Sum
from django.shortcuts import render
# Create your models here.


class Item(models.Model):
    item_id = models.IntegerField(primary_key = True)
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=50, null=True)
    image = models.TextField(null=True)
    texts = models.TextField(null=True)

    def get_absolute_url(self):
        """Returns the url to access a detail record for this Item."""
        return reverse('rate-detail', args=[str(self.id)])

    def get_avgscore(self):
        total = Rate.objects.filter(item_id=self.item_id).aggregate(Sum('rate'))
        numberOfRates = Rate.objects.filter(item_id=self.item_id).count()
        return round(total['rate__sum']/numberOfRates,3)

    def get_reviews(self):
        return Rate.objects.filter(item_id=self.item_id)


    def enter_review(self):
        return "have to implement"
    # def get_review_site(self):
    #     reviews = Rate.objects.filter(item_id=self.item_id)
    #     return render(request, 'product-review.html', {'reviews': reviews})

    def __str__(self):
        return self.name


class Rate(models.Model):
    content = models.TextField(default="just testing content for rate model, confliction with views.save_rate")
    review = models.TextField(blank=False, null=True)
    rate = models.IntegerField(blank=False, null=False)
    item_id = models.IntegerField(blank=False, null=False)
    user_id = models.IntegerField(blank=False, null=False)
    created_at = models.DateField(auto_now=True)
    # new_id = models.AutoField(primary_key=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.review[:20] + " ... "

    def get_absolute_url(self):

        """Returns the url to access a detail record for this Rate."""
        return reverse('rate-detail', args=[str(self.id)])
    def get_user(self):
        return User.objects.get(user_id=self.user_id)
    def get_item(self):
        return Item.objects.get(item_id=self.item_id)
    def get_item_pic(self):
        return Item.objects.get(item_id=self.item_id).image


class User(models.Model):
    """Model representing User."""
    user_id = models.IntegerField(primary_key=True)
    gender = models.CharField(max_length=10, default='F')
    skin_type = models.CharField(max_length=10)
    age = models.FloatField(null=True)
    nickname = models.CharField(max_length=20, default='anonymous')
    profile = models.TextField(null=True)
    candidates = models.ManyToManyField("self", symmetrical=False, blank=True)


    def get_written_reviews(self):
        return Rate.objects.filter(user_id = self.user_id)


    def __str__(self):
        """String for representing the Model object."""
        return self.nickname


class Candidates2(models.Model):
    user_from = models.ManyToManyField(User, related_name="user_from")
    user_to = models.ManyToManyField(User, related_name="user_to")


class Prediction(models.Model):
    """Model repesenting prediction."""
    prediction = models.FloatField(null=True)
    user_id = models.IntegerField(null=True)
    item_id = models.IntegerField(null=True)


#functionality:
#fast prediction
#recommend friend
#user model에 friends 필드 추가
#ㄴ friend recent review display


#pages:
#product detail page
#review detail page

#friend profile page
#social page
#friend reviews
#recommend similar friend
#my page
#ㄴ recommendation
#ㄴ my reviews
