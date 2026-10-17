from django.contrib import admin
from .models import Subject, Topic, Question, Choice


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('text', 'topic')
    list_filter = ('topic__subject', 'topic')


class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject')
    list_filter = ('subject',)


admin.site.register(Subject)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Question, QuestionAdmin)