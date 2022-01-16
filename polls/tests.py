import datetime, pprint
from django.test import TestCase
from django.utils import timezone
from polls.models import Question, Choice
from django.test import Client
from django.urls import reverse


def create_polls(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


def create_choice(choice_text, question):
    return Choice.objects.create(choice_text=choice_text, question=question)


class QuestionModelTests(TestCase):

    def test_question_name(self):
        name = Question.objects.create(question_text="question", pub_date=timezone.now())
        self.assertEqual(name.__str__(), 'question')
        self.assertEqual(str(name), 'question')

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


class ChoiceModelTest(TestCase):

    def test_choice_name(self):
        question = create_polls(question_text='question', days=1)
        choice = Choice.objects.create(choice_text='choice', question=question)
        self.assertEqual(choice.__str__(), "choice")



class ApiTests(TestCase):

    def setUp(self) -> None:
        self.client = Client()

    def test_question(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 404)

    def test_api_polls(self):
        response = self.client.get('/polls/')
        self.assertIs(response.status_code, 200)


class QuestionIndexTest(TestCase):

    def test_no_question(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        question = create_polls(question_text="Past question", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question])

    def test_future_question(self):
        create_polls(question_text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_and_past_question(self):
        question = create_polls(question_text="Past question", days=-30)
        create_polls(question_text="Future Question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question])

    def test_two_past_question(self):
        question1 = create_polls(question_text="1 Past question", days=-30)
        question2 = create_polls(question_text="2 Past question", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question2, question1])


class QuestionNewIndexViewsTest(TestCase):

    def test_past_question_without_choice(self):
        create_polls(question_text="choice", days=-5)
        response = self.client.get(reverse('polls:newindex'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question_with_choice(self):
        question = create_polls(question_text='question', days=-5)
        create_choice(choice_text='choice', question=question)
        response = self.client.get(reverse('polls:newindex'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question])

    def test_future_question_without_choice(self):
        create_polls(question_text="choice", days=5)
        response = self.client.get(reverse('polls:newindex'))
        self.assertContains(response, "No polls are available.")


class QuestionDetailViewsTest(TestCase):

    def test_future_question(self):
        future_question = create_polls(question_text="Future question", days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_polls(question_text="Past question", days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class QuestionResultViewsTest(TestCase):

    def test_future_question(self):
        future_question = create_polls(question_text="Future question", days=5)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_polls(question_text="Past question", days=-5)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
