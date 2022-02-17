from random import choices
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

MEALS = (
    ('B', 'Breakfast'),
    ('L', 'Lunch'),
    ('D', 'Dinner')
    )

class Toy(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=50)

    def get_absolute_url(self):
        return reverse('toys_detail', kwargs={'pk': self.id})


# Create your models here.
class Cat(models.Model):
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    age = models.IntegerField()
    # Add the Many:Many relationship
    toys = models.ManyToManyField(Toy)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #changes to instance methods do not require re-generation / running migrations
    def __str__(self):
        return self.name


    def get_absolute_url(self):
        return reverse('detail', kwargs={'cat_id': self.id})

class Feeding(models.Model):
    date = models.DateField()
    meal = models.CharField(
        max_length=1,
        # add the 'choices' filed option
        choices=MEALS,
        # set the default value for meal to be 'B'
        default=MEALS[0][0]
    )
    #Create a cat_id FK
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE)

    def __str__(self):
        # Nice method for obtaining the friendly value of a Field
        return f"{self.get_meal_display()} on {self.date}"

    class Meta:
        ordering = ['-date']

class Photo(models.Model):
    url = models.CharField(max_length=200)
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE)

    def __str__(self):
        return f"Photo for cat_id: {self.cat_id} @{self.url}"