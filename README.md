# Student Quiz

A Django web app where students practice science subjects with multiple-choice quizzes. Pick a subject, pick a topic, answer the questions, and get a score with a review of every answer.

![Subjects page](screenshot-subjects.png)
![Results page](screenshot-results.png)

## Features

- Subjects (Physics, Chemistry, Biology), each with its own topics
- Multiple-choice questions with one correct answer
- Instant score and percentage after submitting
- Review page showing your answer, the correct answer, and an explanation
- Admin panel to add subjects, topics, questions, and choices (all four options on one page)

## Built with

- Python
- Django
- HTML and CSS

## How to run it

1. Clone the repository

```bash
   git clone https://github.com/Funnyboe13/quiz-website.git
   cd quiz-website
```

2. Create and activate a virtual environment

```bash
   python -m venv venv
   venv\Scripts\activate
```

3. Install the requirements

```bash
   pip install -r requirements.txt
```

4. Set up the database

```bash
   python manage.py migrate
   python manage.py createsuperuser
```

5. Start the server

```bash
   python manage.py runserver
```

6. Open http://127.0.0.1:8000/admin, add subjects, topics, and questions, then visit http://127.0.0.1:8000 to take a quiz

## Future improvements

- Student accounts with saved score history
- Random question order
- Timed quizzes

## Author

Made by Funnyboe13