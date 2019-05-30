from django.db import models

# Create your models here.


class Item(models.Model):
    item_id = models.IntegerField(primary_key = True)
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=50, null=True)
    image = models.TextField(null=True)
    content = models.TextField(null=True)

    def __str__(self):
        return self.name


class Rate(models.Model):
    content = models.TextField(blank=False, null=True)
    rate = models.IntegerField(blank=False, null=False)
    item_id = models.IntegerField(blank=False, null=False)
    user_id = models.IntegerField(blank=False, null=False)
    created_at = models.DateField(auto_now=True)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.item_id.name}:{self.user_id.user_id}'


class User(models.Model):
    """Model representing User."""
    user_id = models.IntegerField(primary_key=True)
    gender = models.CharField(max_length=10, default='F')
    skin_type = models.CharField(max_length=10)
    age = models.FloatField(null=True)
    nickname = models.CharField(max_length=20, default='anonymous')
    profile = models.TextField(null=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.nickname


# class Brand(models.Model):
#     """Model representing name."""
#     name = models.CharField(max_length=100)
#
#     def __str__(self):
#         return self.name


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


