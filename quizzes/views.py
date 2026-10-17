from django.shortcuts import render, get_object_or_404
from .models import Subject, Topic


def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'quizzes/subject_list.html', {'subjects': subjects})


def topic_list(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    topics = subject.topics.all()
    return render(request, 'quizzes/topic_list.html', {'subject': subject, 'topics': topics})


def take_quiz(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    questions = list(topic.questions.prefetch_related('choices'))

    if request.method == 'POST':
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
        return render(request, 'quizzes/result.html', {
            'topic': topic,
            'results': results,
            'score': score,
            'total': total,
            'percent': percent,
        })

    return render(request, 'quizzes/quiz.html', {'topic': topic, 'questions': questions})

# Create your views here.
