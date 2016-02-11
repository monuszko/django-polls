# -*- coding: utf-8 -*-
import datetime

from django.http import Http404
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.test import TestCase
from django.contrib.auth.models import User

from .models import Poll, Choice, Vote
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
        self.u2 = User.objects.create(
            password='2ece25e98d3379376093834e713717e23c825ca1',
            is_superuser=False, username='jazavac',
            first_name='Jazavac', last_name='Euroazijski',
            email='jazavac@example.com', is_staff=False, is_active=True,
            date_joined=datetime.datetime(2009, 6, 21, 13, 20, 10)
            )
        self.u3 = User.objects.create(
            password='d5eba09c4191d6a1a9739b5e18c22e995e50455e',
            is_superuser=False, username='mochyn',
            first_name='Mochyn', last_name='daear',
            email='mochyn@example.com', is_staff=False, is_active=True,
            date_joined=datetime.datetime(2009, 6, 22, 13, 20, 10)
            )
        self.u4 = User.objects.create(
            password='8bb75fe7b0693f8dda98213f61d1513b6b0a95ec',
            is_superuser=False, username='dachs',
            first_name='Europäischer', last_name='Dachs',
            email='dachs@example.com', is_staff=False, is_active=True,
            date_joined=datetime.datetime(2003, 6, 22, 13, 21, 10)
            )
        self.u5 = User.objects.create(
            password='baf11129ce63c4eef654f39a360b31cfc7d1ac67',
            is_superuser=False, username='azkonar',
            first_name='Azkonar', last_name='Arrunt',
            email='azkonar@example.com', is_staff=False, is_active=True,
            date_joined=datetime.datetime(2004, 7, 22, 13, 21, 10)
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
        future_poll = self.create_poll(question="Future poll.", days=30, creator=self.u1)

        self.assertEqual(future_poll.was_published_recently(), False)

    def test_was_published_recently_with_old_poll(self):
        """
        was_published_recently() should return False for polls whose pub_date
        is older than 1 day
        """
        old_poll = self.create_poll(question="Old poll.", days=-30, creator=self.u1)

        self.assertEqual(old_poll.was_published_recently(), False)

    def test_was_published_recently_with_recent_poll(self):
        """
        was_published_recently() should return True for polls whose pub_date
        is within the last day
        """
        #TODO: hour support for create_poll
        recent_poll = Poll(pub_date=timezone.now() - datetime.timedelta(hours=1))

        self.assertEqual(recent_poll.was_published_recently(), True)

    def test_num_voters_with_no_votes(self):
        """
        num_voters() should return 0 for polls no one voted on.
        """
        another_poll = self.create_poll(question="Past poll.", days=-3, creator=self.u1)
        choice1 = Choice.objects.create(poll=another_poll, choice_text='Another answer 1')
        choice2 = Choice.objects.create(poll=another_poll, choice_text='Another answer 2')
        choice3 = Choice.objects.create(poll=another_poll, choice_text='Another answer 3')
        choice4 = Choice.objects.create(poll=another_poll, choice_text='Another answer 4')
        choice5 = Choice.objects.create(poll=another_poll, choice_text='Another answer 5')

        self.assertEqual(another_poll.num_voters(), 0)

    def test_num_voters_with_votes(self):
        """
        num_voters() should return the number of users who voted on this poll.
        """
        another_poll = self.create_poll(question="Past poll.", days=-3, creator=self.u1)
        choice1 = Choice.objects.create(poll=another_poll, choice_text='Another answer 1')
        choice2 = Choice.objects.create(poll=another_poll, choice_text='Another answer 2')
        choice3 = Choice.objects.create(poll=another_poll, choice_text='Another answer 3')
        choice4 = Choice.objects.create(poll=another_poll, choice_text='Another answer 4')
        choice5 = Choice.objects.create(poll=another_poll, choice_text='Another answer 5')
        Vote.objects.create(user=self.u2, choice=choice1)
        Vote.objects.create(user=self.u3, choice=choice2)
        Vote.objects.create(user=self.u4, choice=choice3)
        Vote.objects.create(user=self.u5, choice=choice4)

        self.assertEqual(another_poll.num_voters(), 4)

    def test_num_voters_with_votes(self):
        """
        Votes on one poll shouldn't affect the number of voters on another poll.
        """
        first_poll = self.create_poll(question="First poll.", days=-3, creator=self.u1)
        second_poll = self.create_poll(question="Second poll.", days=-2, creator=self.u2)

        choice1_f = Choice.objects.create(poll=first_poll, choice_text='First answer 1')
        choice2_f = Choice.objects.create(poll=first_poll, choice_text='First answer 2')
        choice3_f = Choice.objects.create(poll=first_poll, choice_text='First answer 3')
        choice4_f = Choice.objects.create(poll=first_poll, choice_text='First answer 4')

        choice1_s = Choice.objects.create(poll=second_poll, choice_text='Second answer 1')
        choice2_s = Choice.objects.create(poll=second_poll, choice_text='Second answer 2')
        choice3_s = Choice.objects.create(poll=second_poll, choice_text='Second answer 3')
        choice4_s = Choice.objects.create(poll=second_poll, choice_text='Second answer 4')

        Vote.objects.create(user=self.u2, choice=choice1_f)

        Vote.objects.create(user=self.u3, choice=choice2_s)
        Vote.objects.create(user=self.u4, choice=choice3_s)
        Vote.objects.create(user=self.u5, choice=choice4_s)

        self.assertEqual(first_poll.num_voters(), 1)
        self.assertEqual(second_poll.num_voters(), 3)

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


class VoteViewTests(BaseTestCase):
    #TODO: test POST
    
    def test_vote_GET_with_a_future_poll(self):
        """
        The voting_form view of a poll with a pub_date in the future should
        return a 404 not found.
        """
        self.client.force_login(self.u1)
        future_poll = self.create_poll(question='Future poll.', days=5, creator=self.u1)
        response = self.client.get(reverse('polls:voting_form', args=(future_poll.id,)))

        self.assertEqual(response.status_code, 404)

    def test_vote_GET_with_a_past_poll(self):
        """
        The voting_form view of a poll with a pub_date in the past should display
        the poll's question.
        """
        self.client.force_login(self.u1)
        past_poll = self.create_poll(question='Past Poll.', days=-5, creator=self.u1)
        response = self.client.get(reverse('polls:voting_form', args=(past_poll.id,)))

        self.assertContains(response, past_poll.question, status_code=200)

    def test_vote_GET_without_login(self):
        """
        The voting_form view without login should return a 302 redirect.
        """
        poll = self.create_poll(question='Future poll.', days=0, creator=self.u1)
        response = self.client.get(reverse('polls:voting_form', args=(poll.id,)))

        self.assertEqual(response.status_code, 302)

    def test_vote_POST_with_a_future_poll(self):
        '''
        Voting on a future poll doesn't work even if it exists
        '''
        self.client.force_login(self.u2)
        future_poll = self.create_poll(question='Future poll.', days=5, creator=self.u1)
        choice1 = Choice.objects.create(poll=future_poll, choice_text='Future answer 1')
        choice2 = Choice.objects.create(poll=future_poll, choice_text='Future answer 2')
        choice3 = Choice.objects.create(poll=future_poll, choice_text='Future answer 3')
        choice4 = Choice.objects.create(poll=future_poll, choice_text='Future answer 4')
        choice5 = Choice.objects.create(poll=future_poll, choice_text='Future answer 5')
        selected_choice = future_poll.choice_set.all()[2]
        post_data = {'choice': 2}

        response = self.client.post(
                reverse('polls:voting_form', args=(future_poll.id,)),
                post_data)
        self.assertEqual(Vote.objects.all().count(), 0)
        self.assertEqual(response.status_code, 404)

    def test_vote_POST_with_a_past_poll(self):
        self.client.force_login(self.u2)
        past_poll = self.create_poll(question='Past poll.', days=-5, creator=self.u1)
        choice1 = Choice.objects.create(poll=past_poll, choice_text='Past answer 1')
        choice2 = Choice.objects.create(poll=past_poll, choice_text='Past answer 2')
        choice3 = Choice.objects.create(poll=past_poll, choice_text='Past answer 3')
        choice4 = Choice.objects.create(poll=past_poll, choice_text='Past answer 4')
        choice5 = Choice.objects.create(poll=past_poll, choice_text='Past answer 5')
        selected_choice = past_poll.choice_set.all()[2]
        post_data = {u'choice': selected_choice.pk}

        response = self.client.post(
                reverse('polls:voting_form', args=(past_poll.id,)),
                post_data)
        self.assertEqual(Vote.objects.all().count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_vote_POST_without_login(self):
        """
        The voting_form view without login should return a 302 redirect, even
        if sent correct POST
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

    def test_create_poll_GET_without_login(self):
        """
        The create view without login should return a 302 redirect.
        """
        response = self.client.get(reverse('polls:create'))

        self.assertEqual(response.status_code, 302)

    def test_create_poll_GET_with_login(self):
        """
        The create view with login should display the form.
        """
        self.client.force_login(self.u1)
        response = self.client.get(reverse('polls:create'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Question:')
        self.assertContains(response, 'Answers:')

    def test_create_poll_POST_with_login(self):
        """
        The create view should create objects when sent correct POST
        """
        self.client.force_login(self.u1)
        post_data = {
        u'choice_set-1-choice_text': [u'5'],
        u'choice_set-4-choice_text': [u''],
        u'choice_set-3-choice_text': [u'1'],
        u'question': [u'Ile widzisz palców ?'],
        u'choice_set-INITIAL_FORMS': [u'0'],
        u'choice_set-2-choice_text': [u'7'],
        u'choice_set-0-choice_text': [u'2'],
        u'choice_set-MAX_NUM_FORMS': [u'1000'],
        u'choice_set-MIN_NUM_FORMS': [u'0'],
        u'choice_set-TOTAL_FORMS': [u'5']
        }
        response = self.client.post(reverse('polls:create'), post_data)
        poll = Poll.objects.all()[0]
        choices = poll.choice_set.all().values_list('choice_text', flat=True)
        choices = set(choices)

        #TODO: take it further with response (view, status code)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Poll.objects.all().count(), 1)
        self.assertEqual(poll.question, u'Ile widzisz palców ?')
        self.assertEqual(poll.created_by, self.u1)
        self.assertEqual(len(choices), 4)
        self.assertEqual(choices, {u'1', u'2', u'5', u'7'})

    def test_create_poll_POST_without_login(self):
        """
        The create view should NOT create objects when sent correct POST
        without being logged in
        """
        post_data = {
        u'choice_set-1-choice_text': [u'5'],
        u'choice_set-4-choice_text': [u''],
        u'choice_set-3-choice_text': [u'1'],
        u'question': [u'Ile widzisz palców ?'],
        u'choice_set-INITIAL_FORMS': [u'0'],
        u'choice_set-2-choice_text': [u'7'],
        u'choice_set-0-choice_text': [u'2'],
        u'choice_set-MAX_NUM_FORMS': [u'1000'],
        u'choice_set-MIN_NUM_FORMS': [u'0'],
        u'choice_set-TOTAL_FORMS': [u'5']
        }
        response = self.client.post(reverse('polls:create'), post_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Poll.objects.all().count(), 0)
        self.assertEqual(Choice.objects.all().count(), 0)

