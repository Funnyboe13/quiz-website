import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from quizzes.models import Subject, Topic, Question, Choice


class Command(BaseCommand):
    help = "Import quiz questions from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help="Path to the CSV file")

    def handle(self, *args, **options):
        path = options['csv_file']
        try:
            f = open(path, newline='', encoding='utf-8-sig')
        except FileNotFoundError:
            raise CommandError(f"File not found: {path}")

        added = 0
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

                if not (subject_name and topic_name and text and all(options_list)):
                    self.stdout.write(self.style.ERROR(f"Line {line_no}: missing subject, topic, question or an option"))
                    errors += 1
                    continue

                if correct not in ('A', 'B', 'C', 'D'):
                    self.stdout.write(self.style.ERROR(f"Line {line_no}: 'correct' must be A, B, C or D"))
                    errors += 1
                    continue

                with transaction.atomic():
                    subject = Subject.objects.filter(name__iexact=subject_name).first()
                    if subject is None:
                        subject = Subject.objects.create(name=subject_name)

                    topic = Topic.objects.filter(subject=subject, name__iexact=topic_name).first()
                    if topic is None:
                        topic = Topic.objects.create(subject=subject, name=topic_name)

                    if Question.objects.filter(topic=topic, text=text).exists():
                        skipped += 1
                        continue

                    question = Question.objects.create(topic=topic, text=text, explanation=explanation)
                    correct_index = 'ABCD'.index(correct)
                    Choice.objects.bulk_create([
                        Choice(question=question, text=option_text, is_correct=(i == correct_index))
                        for i, option_text in enumerate(options_list)
                    ])
                    added += 1

        self.stdout.write(self.style.SUCCESS(f"Added {added} question(s), skipped {skipped} duplicate(s), {errors} error(s)."))