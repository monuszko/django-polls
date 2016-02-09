import datetime

from django.http import Http404
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.test import TestCase
from django.contrib.auth.models import User

from .models import Poll
from .forms import PollForm, ChoiceFormSet
from .views import vote, ResultsView

class BaseTestCase(TestCase):

    def setUp(self):
        self.u1 = User.objects.create(
            password='0d7ef89790c560955c04b11fa01a2af76c34add5',
            is_superuser=False, username='borsuk',
            first_name='Borsuk', last_name='Euroazjatycki',
            email='borsuk@example.com', is_staff=False, is_active=True,
            date_joined=datetime.datetime(2008, 5, 30, 13, 20, 10)
            )

    def create_poll(self, question, days, creator):
        """
        Creates a poll with the given `question` published the given number of
        `days` offset to now (negative for polls published in the past,
        positive for polls that have yet to be published).
        """
        return Poll.objects.create(
            question=question,
            pub_date=timezone.now() + datetime.timedelta(days=days),
            created_by=creator,
        )


class FormTests(TestCase):

    def test_pollform_with_question(self):
        """
        A pollform should be accepted if it's question is filled in.
        """
        form_data = {'question': "Jak jest po staroegipsku 'krokodyl' ?"}
        form = PollForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_pollform_without_question(self):
        """
        A pollform should be rejected if it's question is blank.
        """
        form_data = {'question': ""}
        form = PollForm(data=form_data)

        self.assertFalse(form.is_valid())


class PollMethodTests(BaseTestCase):

    def test_was_published_recently_with_future_poll(self):
        """
        was_published_recently() should return False for polls whose
        pub_date is in the future
        """
        future_poll = Poll(pub_date=timezone.now() + datetime.timedelta(days=30))

        self.assertEqual(future_poll.was_published_recently(), False)

    def test_was_published_recently_with_old_poll(self):
        """
        was_published_recently() should return False for polls whose pub_date
        is older than 1 day
        """
        old_poll = Poll(pub_date=timezone.now() - datetime.timedelta(days=30))

        self.assertEqual(old_poll.was_published_recently(), False)

    def test_was_published_recently_with_recent_poll(self):
        """
        was_published_recently() should return True for polls whose pub_date
        is within the last day
        """
        recent_poll = Poll(pub_date=timezone.now() - datetime.timedelta(hours=1))

        self.assertEqual(recent_poll.was_published_recently(), True)


class PollIndexViewTests(BaseTestCase):

    def test_index_view_with_no_polls(self):
        """
        If no polls exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('polls:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_a_past_poll(self):
        """
        Polls with a pub_date in the past should be displayed on the index page.
        """
        self.create_poll(question="Past poll.", days=-30, creator=self.u1)
        response = self.client.get(reverse('polls:index'))

        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
            ['<Poll: Past poll.>']
        )

    def test_index_view_with_a_future_poll(self):
        """
        Polls with a pub_date in the future should not be displayed on the
        index page.
        """
        self.create_poll(question="Future poll.", days=30, creator=self.u1)
        response = self.client.get(reverse('polls:index'))

        self.assertContains(response, "No polls are available.", status_code=200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_future_poll_and_past_poll(self):
        """
        Even if both past and future polls exist, only past polls should be
        displayed.
        """
        self.create_poll(question="Past poll.", days=-30, creator=self.u1)
        self.create_poll(question="Future poll.", days=30, creator=self.u1)
        response = self.client.get(reverse('polls:index'))

        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
            ['<Poll: Past poll.>']
        )

    def test_index_view_with_two_past_polls(self):
        """
        The polls index page may display multiple polls.
        """
        self.create_poll(question="Past poll 1.", days=-30, creator=self.u1)
        self.create_poll(question="Past poll 2.", days=-5, creator=self.u1)
        response = self.client.get(reverse('polls:index'))

        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
            ['<Poll: Past poll 2.>', '<Poll: Past poll 1.>']
        )


class VotingFormViewTests(BaseTestCase):
    #TODO: test POST
    
    def test_voting_form_view_with_a_future_poll(self):
        """
        The voting_form view of a poll with a pub_date in the future should
        return a 404 not found.
        """
        self.client.force_login(self.u1)
        future_poll = self.create_poll(question='Future poll.', days=5, creator=self.u1)
        response = self.client.get(reverse('polls:voting_form', args=(future_poll.id,)))

        self.assertEqual(response.status_code, 404)

    def test_voting_form_view_with_a_past_poll(self):
        """
        The voting_form view of a poll with a pub_date in the past should display
        the poll's question.
        """
        self.client.force_login(self.u1)
        past_poll = self.create_poll(question='Past Poll.', days=-5, creator=self.u1)
        response = self.client.get(reverse('polls:voting_form', args=(past_poll.id,)))

        self.assertContains(response, past_poll.question, status_code=200)

    def test_voting_form_view_without_login(self):
        """
        The voting_form view without login should return a 302 redirect.
        """
        poll = self.create_poll(question='Future poll.', days=0, creator=self.u1)
        response = self.client.get(reverse('polls:voting_form', args=(poll.id,)))

        self.assertEqual(response.status_code, 302)


class ResultsViewTest(BaseTestCase):
    
    def test_results_view_with_a_future_poll(self):
        """
        The results view of a poll with a pub_date in the future should
        return a 404 not found.
        """
        self.client.force_login(self.u1)
        future_poll = self.create_poll(question='Future poll.', days=5, creator=self.u1)
        response = self.client.get(reverse('polls:results', args=(future_poll.id,)))

        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_past_poll(self):
        """
        The results view of a poll with a pub_date in the past should display
        the poll's question.
        """
        self.client.force_login(self.u1)
        past_poll = self.create_poll(question='Past Poll.', days=-5, creator=self.u1)
        response = self.client.get(reverse('polls:results', args=(past_poll.pk,)))

        self.assertContains(response, past_poll.question, status_code=200)
        self.assertContains(response, 'Update ?')
        self.assertContains(response, 'Delete ?')

    def test_results_view_without_login(self):
        """
        The results view of a poll with a pub_date in the past should display
        the poll's question.
        """
        poll = self.create_poll(question='A poll.', days=-5, creator=self.u1)
        response = self.client.get(reverse('polls:results', args=[poll.pk]))

        self.assertContains(response, poll.question, status_code=200)
        self.assertNotContains(response, 'You voted:')
        self.assertNotContains(response, 'Update ?')
        self.assertNotContains(response, 'Delete ?')


class PollCreateViewTests(BaseTestCase):

    def test_create_poll_view_get_without_login(self):
        """
        The create view without login should return a 302 redirect.
        """
        response = self.client.get(reverse('polls:create'))

        self.assertEqual(response.status_code, 302)

    def test_create_poll_view_get_with_login(self):
        """
        The create view without login should return a 302 redirect.
        """
        self.client.force_login(self.u1)
        response = self.client.get(reverse('polls:create'))

        self.assertEqual(response.status_code, 200)
