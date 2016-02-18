from mptt.admin import MPTTModelAdmin

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.html import format_html

from .models import Choice, Poll, Vote, PollCategory


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class PollAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ['question', 'category', 'created_by',],
        }),
        ('Date information', {
            'fields': ['pub_date'],
            'classes': ['collapse'],
        }),
    ]
    inlines = [ChoiceInline]
    list_display = ('question', 'pub_date', 'category_link', 'num_voters', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question']
    date_hierarchy = 'pub_date'

    def category_link(self, obj):
        link = reverse("admin:%s_%s_change" % ('polls', 'pollcategory'), args=[obj.category.pk])
        return u'<a href="%s">%s</a>' % (link, obj.category.name)

    category_link.allow_tags = True


admin.site.register(Poll, PollAdmin)
admin.site.register(Choice)
admin.site.register(Vote)
admin.site.register(PollCategory, MPTTModelAdmin)
