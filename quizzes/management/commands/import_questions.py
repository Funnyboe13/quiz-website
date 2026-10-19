import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from quizzes.models import Subject, Topic, Question, Choice


class Command(BaseCommand):
    help = "Import quiz questions from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help="Path to the CSV file")
        parser.add_argument(
            '--update',
            action='store_true',
            help="Replace the choices, explanation and diagram of questions that already exist",
        )

    def handle(self, *args, **options):
        path = options['csv_file']
        update = options['update']
        diagram_dir = Path(settings.BASE_DIR) / 'quizzes' / 'static' / 'quizzes' / 'diagrams'
        try:
            f = open(path, newline='', encoding='utf-8-sig')
        except FileNotFoundError:
            raise CommandError(f"File not found: {path}")

        added = 0
        updated = 0
        skipped = 0
        errors = 0

        with f:
            reader = csv.DictReader(f)
            for line_no, row in enumerate(reader, start=2):
                subject_name = (row.get('subject') or '').strip()
                topic_name = (row.get('topic') or '').strip()
                text = (row.get('question') or '').strip()
                options_list = [
                    (row.get('option_a') or '').strip(),
                    (row.get('option_b') or '').strip(),
                    (row.get('option_c') or '').strip(),
                    (row.get('option_d') or '').strip(),
                ]
                correct = (row.get('correct') or '').strip().upper()
                explanation = (row.get('explanation') or '').strip()
                diagram = (row.get('diagram') or '').strip()

                if not (subject_name and topic_name and text and all(options_list)):
                    self.stdout.write(self.style.ERROR(
                        f"Line {line_no}: missing subject, topic, question or an option"))
                    errors += 1
                    continue

                if correct not in ('A', 'B', 'C', 'D'):
                    self.stdout.write(self.style.ERROR(f"Line {line_no}: 'correct' must be A, B, C or D"))
                    errors += 1
                    continue

                if diagram and not (diagram_dir / diagram).exists():
                    self.stdout.write(self.style.WARNING(
                        f"Line {line_no}: diagram file '{diagram}' was not found in {diagram_dir}"))

                with transaction.atomic():
                    subject = Subject.objects.filter(name__iexact=subject_name).first()
                    if subject is None:
                        subject = Subject.objects.create(name=subject_name)

                    topic = Topic.objects.filter(subject=subject, name__iexact=topic_name).first()
                    if topic is None:
                        topic = Topic.objects.create(subject=subject, name=topic_name)

                    question = Question.objects.filter(topic=topic, text=text).first()
                    if question is not None and not update:
                        skipped += 1
                        continue

                    if question is None:
                        question = Question.objects.create(
                            topic=topic, text=text, explanation=explanation, diagram=diagram)
                        added += 1
                    else:
                        question.explanation = explanation
                        question.diagram = diagram
                        question.save()
                        question.choices.all().delete()
                        updated += 1

                    correct_index = 'ABCD'.index(correct)
                    Choice.objects.bulk_create([
                        Choice(question=question, text=option_text, is_correct=(i == correct_index))
                        for i, option_text in enumerate(options_list)
                    ])

        self.stdout.write(self.style.SUCCESS(
            f"Added {added}, updated {updated}, skipped {skipped} duplicate(s), {errors} error(s)."))