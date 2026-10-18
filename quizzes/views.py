import random

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache

from .models import Subject, Topic, Attempt

DEFAULT_SIZE = 20


class CustomLoginView(LoginView):
    template_name = 'quizzes/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Welcome back, {form.get_user().username}!")
        return response


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect('subject_list')
    else:
        form = UserCreationForm()
    return render(request, 'quizzes/signup.html', {'form': form})


def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'quizzes/subject_list.html', {'subjects': subjects})


def topic_list(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    topics = subject.topics.all()
    return render(request, 'quizzes/topic_list.html', {'subject': subject, 'topics': topics})


def clean_size(value):
    """Return '10', '20' or 'all'. Anything else becomes the default."""
    value = (value or '').strip().lower()
    if value in ('10', '20', 'all'):
        return value
    return str(DEFAULT_SIZE)


@never_cache
@login_required
def take_quiz(request, pk):
    topic = get_object_or_404(Topic, pk=pk)

    if request.method == 'POST':
        n_param = clean_size(request.POST.get('n'))
        ids = [int(i) for i in request.POST.get('question_ids', '').split(',') if i.isdigit()]
        found = {q.pk: q for q in topic.questions.prefetch_related('choices').filter(pk__in=ids)}
        questions = [found[i] for i in ids if i in found]

        results = []
        score = 0
        for q in questions:
            selected = None
            selected_id = request.POST.get(f'question_{q.pk}')
            if selected_id:
                selected = q.choices.filter(pk=selected_id).first()
            correct = q.choices.filter(is_correct=True).first()
            is_right = selected is not None and selected.is_correct
            if is_right:
                score += 1
            results.append({
                'question': q,
                'selected': selected,
                'correct': correct,
                'is_right': is_right,
            })
        total = len(results)
        percent = round(score / total * 100) if total else 0

        if total:
            Attempt.objects.create(user=request.user, topic=topic, score=score, total=total)

        return render(request, 'quizzes/result.html', {
            'topic': topic,
            'results': results,
            'score': score,
            'total': total,
            'percent': percent,
            'n_param': n_param,
        })

    n_param = clean_size(request.GET.get('n'))
    all_questions = list(topic.questions.prefetch_related('choices'))
    total_available = len(all_questions)
    size = total_available if n_param == 'all' else min(int(n_param), total_available)
    questions = random.sample(all_questions, size)

    return render(request, 'quizzes/quiz.html', {
        'topic': topic,
        'questions': questions,
        'question_ids': ','.join(str(q.pk) for q in questions),
        'total_available': total_available,
        'n_param': n_param,
    })


@never_cache
@login_required
def my_results(request):
    attempts = Attempt.objects.filter(user=request.user).select_related('topic__subject')
    return render(request, 'quizzes/my_results.html', {'attempts': attempts})