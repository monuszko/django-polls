from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views import generic

from .models import Choice, Poll, Vote
from .forms import PollForm, ChoiceFormSet


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_poll_list'

    def get_queryset(self):
        """
        Return the last five published polls (not including those set to be
        published in the future).
        """
        return Poll.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


#TODO: Don't even display it for people who voted
class DetailView(generic.DetailView):
    model = Poll
    template_name = 'polls/detail.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DetailView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        """
        Excludes any polls that aren't published yet.
        """
        return Poll.objects.filter(pub_date__lte=timezone.now())



class ResultsView(generic.DetailView):
    model = Poll
    template_name = 'polls/results.html'


@login_required
def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)

    error_message = None
    if Vote.objects.filter(user=request.user, choice__poll=p).exists():
        error_message = "Voting twice is not allowed."
    elif p.created_by == request.user:
        error_message = "You can't vote in your own poll!"
    if error_message:
        return render(request, 'polls/detail.html', {
        'poll': p,
        'error_message': error_message,
        })

    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the poll voting form.
        return render(request, 'polls/detail.html', {
            'poll': p,
            'error_message': "You didn't select a choice.",
        })
    else:
        v = Vote(user=request.user, choice=selected_choice)
        v.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))


class PollCreate(generic.edit.CreateView):

    model = Poll
    form_class = PollForm
    template_name = 'polls/poll_form.html'
    object = None

    def form_valid(self, poll_form, choice_formset):
        poll = poll_form.save(commit=False)
        poll.created_by = self.request.user
        poll.save()
        choice_formset.instance = poll
        choice_formset.save()
        return super(PollCreate, self).form_valid(poll_form)

    def form_invalid(self, poll_form, choice_formset):
        return self.render_to_response(self.get_context_data(form=poll_form,
                                                       formset=choice_formset))

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        poll_form = self.get_form(form_class)
        choice_formset = ChoiceFormSet(self.request.POST)

        if poll_form.is_valid() and choice_formset.is_valid():
            return self.form_valid(poll_form, choice_formset)
        return self.form_invalid(poll_form, choice_formset)

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        poll_form = self.get_form(form_class)
        choice_formset = ChoiceFormSet()
        return self.render_to_response(self.get_context_data(form=poll_form,
                                                       formset=choice_formset))
    def get_success_url(self):
        return self.object.get_absolute_url()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PollCreate, self).dispatch(*args, **kwargs)
