from django.contrib import admin
from .models import *

class EducationAdmin(admin.ModelAdmin):
    list_display = ('certificate', 'institution', 'year_start', 'year_end')
    list_filter = ('institution',)
    search_fields = ('certificate', 'institution')


class FellowshipAdmin(admin.ModelAdmin):
    list_display = ('institution', 'date')
    list_filter = ('institution',)
 

class ProqualAdmin(admin.ModelAdmin):
    list_display = ('institution', 'date')
    list_filter = ('institution',)


class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'comment','pub_date')
    list_filter = ('name','pub_date')

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone','email','message','pub_date')
    list_filter = ('name','pub_date')
 

class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('position', 'company', 'year_start', 'year_end')
    list_filter = ('company',)
    search_fields = ('position', 'company')

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title', 'description')

class SurgeryAdmin(admin.ModelAdmin):
    list_display = ('type_of_surgery','title', 'date')
    list_filter = ('date',)
    search_fields = ('type_of_surgery','title', 'description')
    date_hierarchy = 'date'

class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date')
    list_filter = ('pub_date',)
    search_fields = ('title', 'content')
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = 'pub_date'

class AchievementAwardAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'date', 'issuer')
    list_filter = ('type', 'date')
    search_fields = ('title', 'description', 'issuer')
    date_hierarchy = 'date'

admin.site.register(Education, EducationAdmin)
admin.site.register(Fellowship, FellowshipAdmin)
admin.site.register(Testimonial, TestimonialAdmin)
admin.site.register(Contact, ContactMessageAdmin)
admin.site.register(ProfessionalQualification, ProqualAdmin)
admin.site.register(Experience, ExperienceAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Surgery, SurgeryAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(AchievementAward, AchievementAwardAdmin)