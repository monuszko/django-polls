from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views import generic
from django.http import Http404

from .models import Choice, Poll, Vote, PollCategory
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
                pub_date__lte=timezone.now()).order_by('-pub_date')[:5]


class ResultsView(generic.DetailView):
    model = Poll
    template_name = 'polls/results.html'
    
    def get_object(self):
        return get_object_or_404(self.model.objects.public(), 
                pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(ResultsView, self).get_context_data(**kwargs)
        your_vote = ''
        if self.request.user.is_authenticated():
            # Would break with AnonymousUser 
            try:
                your_vote = Vote.objects.get(
                        user=self.request.user,
                        choice__poll__pk=self.object.pk
                        )
                your_vote = your_vote.choice.choice_text
            except (KeyError, Vote.DoesNotExist):
                pass

        context['your_vote'] = your_vote
        return context


@login_required
def vote(request, pk):
    p = get_object_or_404(Poll.objects.public(), pk=pk)

    error_message = None
    if Vote.objects.filter(user=request.user, choice__poll=p).exists():
        error_message = "Voting twice is not allowed."
    elif p.created_by == request.user:
        error_message = "You can't vote in your own poll!"

    if request.method=='POST' and not error_message:
        try:
            selected_choice = p.choice_set.get(pk=request.POST['choice'])
        except (KeyError, Choice.DoesNotExist):
            error_message = "You didn't select a choice."
        if not error_message:
            v = Vote(user=request.user, choice=selected_choice)
            v.save()
            return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))
 
    return render(request, 'polls/voting_form.html', {
    'poll': p,
    'error_message': error_message,
    })


@login_required
def create_poll(request, template='polls/poll_form.html'):

    if request.method=='POST':
        form = PollForm(request.POST)
        p = Poll()
        formset = ChoiceFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            p = form.save(commit=False)
            p.created_by = request.user
            p.save()

            formset.instance = p
            formset.save()

            return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))
    else:
        form = PollForm()
        p = Poll()
        formset = ChoiceFormSet()

    return render(request, template, {'form': form, 'formset': formset})


class PollDelete(generic.DeleteView):
    model = Poll
    success_url = reverse_lazy('polls:index')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        poll = self.get_object()
        if poll.created_by != self.request.user:
            raise Http404

        return super(PollDelete, self).dispatch(*args, **kwargs)


@login_required
def update_poll(request, pk):
    poll = get_object_or_404(Poll, pk=pk)
    if poll.created_by != request.user:
        raise Http404
    if request.method == 'POST':
        poll_form = PollForm(request.POST, instance=poll)
        choice_formset = ChoiceFormSet(request.POST, instance=poll)
        if poll_form.is_valid() and choice_formset.is_valid():
            poll_form.save()
            choice_formset.save()
            return HttpResponseRedirect(reverse('polls:results', args=[pk]))
    else:
        poll_form = PollForm(instance=poll)
        choice_formset = ChoiceFormSet(instance=poll)
    return render(request, 'polls/update.html', {
                                                 'form': poll_form,
                                                 'formset': choice_formset
                                                 })



def category(request, pk):
    cat = get_object_or_404(PollCategory, pk=pk)
    all_cats = cat.get_root().get_descendants(include_self=True)
    child_cats = all_cats if cat.is_root_node() else cat.get_descendants(include_self=True)
    polls = Poll.objects.public().filter(category__in=child_cats)
    return render(request, 'polls/category.html', {
        'category': cat,
        'all_categories': all_cats,
        'polls': polls,
        })


