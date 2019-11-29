from django.test import TestCase
import datetime
from django.utils import timezone
from .models import Question
from django.urls import reverse

def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date = time)

class QuestionIndexViewText(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Question with a pub_date in the past are displayed on the index page
        """
        create_question(question_text="Past Question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past Question.>'])

    def test_future_question(self):
        """
        Question with a pub_date in the future aren't displayed on the index page
        """
        create_question(question_text = "Future Question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        even if both past and future questions exist, only past questions are displayed
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question.>'])

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [
        '<Question: Past question 2.>','<Question: Past question 1.>'
        ])

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        404 error should be return
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_past_question(self):
        """
        202 if question is in the past
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class QuestionModelTest(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns false for questions whose pub_date
        is in the future
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)
    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns false for questions whose pub_date
        is older than 1 day
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds= 1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)
    def test_was_published_recently_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)
