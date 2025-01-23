from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Education(models.Model):
    certificate = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)
    year_start = models.IntegerField()
    year_end = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)


class Fellowship(models.Model):
    institution = models.CharField(max_length=100)
    date = models.DateField(null=True, blank=True)
 

class ProfessionalQualification(models.Model):
    institution = models.CharField(max_length=100)
    date = models.DateField(null=True, blank=True)


class Experience(models.Model):
    position = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    year_start = models.DateField()
    year_end = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

class AchievementAward(models.Model):
    TYPES = (
        ('achievement', 'Achievement'),
        ('award', 'Award'),
        ('recognition', 'Recognition'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    type = models.CharField(max_length=20, choices=TYPES)
    issuer = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title

class Service(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True,blank=True)



class Surgery(models.Model):
    type_of_surgery = models.CharField(max_length=100,null=True,blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='surgeries/', null=True, blank=True)
    date = models.DateField()



class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('blog_detail', args=[self.slug])


class Testimonial(models.Model):
    name = models.CharField(max_length=200)
    comment = models.TextField(unique=True)
    pub_date = models.DateTimeField(auto_now_add=True)


class Contact(models.Model):
    name = models.CharField(max_length=200)
    email=models.EmailField(null=True,blank=True)
    phone=models.PositiveIntegerField(null=True,blank=True)
    message = models.TextField(unique=True)
    pub_date = models.DateTimeField(auto_now_add=True)