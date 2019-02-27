from django.contrib import admin
from django.utils.functional import curry


from .models import Poll, Choice, Vote


class ChoiceInLine(admin.TabularInline):
    model = Choice
    extra = 1


class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_by', 'pub_date', 'choices_count')
    list_filter = ('created_by', 'pub_date')
    search_fields = ('question',)
    inlines = [
        ChoiceInLine
    ]

    def choices_count(self, obj):
        return obj.choices.count()

admin.site.register(Poll, PollAdmin)

class VoteInLine(admin.TabularInline):
    model = Vote
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        initial = []
        if request.method == "GET":
            initial.append({
                'poll': obj.poll,
            })
        formset = super(VoteInLine, self).get_formset(request, obj, **kwargs)
        formset.__init__ = curry(formset.__init__, initial=initial)
        return formset


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_text', 'poll', 'votes_count')
    readonly_fields = ('poll',)
    list_filter = ('poll',)
    search_fields = ('choice_text','poll__question')
    inlines = [
        VoteInLine
    ]

    def votes_count(self, obj):
        return obj.votes.count()

admin.site.register(Choice, ChoiceAdmin)
