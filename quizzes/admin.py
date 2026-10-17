from django.contrib import admin
from .models import Subject, Topic, Question, Choice, Attempt


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


class AttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'score', 'total', 'taken_at')
    list_filter = ('topic__subject', 'user')


admin.site.register(Subject)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Attempt, AttemptAdmin)