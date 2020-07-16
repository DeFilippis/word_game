from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage


class Play_Game(Page):
    timeout_seconds = 60 * 30
    
    live_method = 'live_word'

    form_model = 'group'
    form_fields = ['final_score']

    def vars_for_template(self):
        return dict(
            own_tiles=''.join(self.player.get_list_of_available_tiles()),
            group_tiles=''.join(self.group.get_list_of_available_tiles()),
        )


page_sequence = [
    Play_Game
]
