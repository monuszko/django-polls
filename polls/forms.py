from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from .models import Poll, Choice


class PollForm(ModelForm):
    class Meta:
        model = Poll
        fields = ('question', 'category')


ChoiceFormSet = inlineformset_factory(Poll, Choice, fields=('choice_text',), extra=5)
