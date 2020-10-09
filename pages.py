from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage


class Play_Game_R1(Page):
    #minimum of 45 seconds
    #maximum of 4 minutes 45 seconds
    timeout_seconds = 2 * 60

    live_method = 'live_word'

    #form_model = 'group'
    #form_fields = ['final_score']

    def is_displayed(self):
        # rounds 1 - 5 should be the "easy" game
        return self.round_number >= 1 & self.round_number < 6

 #   def before_next_page(self):
 #        cumulative_score = 


    def vars_for_template(self):
        own_tiles= self.player.get_list_of_available_tiles()
        own_tiles_value= [str(v) for v in self.player.get_tile_values(own_tiles)]

        return dict(
            tile_value_tuple=[(own_tiles[i], own_tiles_value[i]) for i in range(0, len(own_tiles_value))],
            own_tiles="".join(own_tiles),
            own_tiles_value="".join(own_tiles_value),
            group_tiles=''.join(self.group.get_list_of_available_tiles()),
            cumulative_score=sum([i.total_words() for i in self.group.in_all_rounds()])
        )


class Play_Game_R2(Page):
    timeout_seconds = 1
    
    live_method = 'live_word'

    #form_model = 'group'
    #form_fields = ['final_score']
    
    def is_displayed(self):
        # rounds 6 - 21 should be the "medium" difficulty game (16 rounds)
        return self.round_number >= 6 & self.round_number < 22

    def vars_for_template(self):
        own_tiles= self.player.get_list_of_available_tiles()
        own_tiles_value= [str(v) for v in self.player.get_tile_values(own_tiles)]

        return dict(
            tile_value_tuple= [(own_tiles[i], own_tiles_value[i]) for i in range(0, len(own_tiles_value))],
            own_tiles= "".join(own_tiles),
            own_tiles_value= "".join(own_tiles_value),
            group_tiles=''.join(self.group.get_list_of_available_tiles()),
        )



class Play_Game_R3(Page):
    timeout_seconds = 60*30
    
    live_method = 'live_word'

    #form_model = 'group'
    #form_fields = ['final_score']
    
    def is_displayed(self):
        # rounds 22 - 37 should be the "medium" difficulty game (16 rounds)
        return self.round_number >= 22

    def vars_for_template(self):
        own_tiles= self.player.get_list_of_available_tiles()
        own_tiles_value= [str(v) for v in self.player.get_tile_values(own_tiles)]
        own_tiles_colors = self.player.get_tile_colors()
        letter_color_tuple = [(letter, color) for letter, color in zip(own_tiles, own_tiles_colors)]

        return dict(
            tile_value_tuple= [(own_tiles[i], own_tiles_value[i]) for i in range(0, len(own_tiles_value))],
            own_tiles= "".join(own_tiles),
            own_tiles_value= "".join(own_tiles_value),
            group_tiles=''.join(self.group.get_list_of_available_tiles()),
            own_tiles_colors = "".join(own_tiles_colors),
            letter_color_tuple = letter_color_tuple
        )

class MyWaitPage(WaitPage):
    group_by_arrival_time = True

page_sequence = [
    MyWaitPage,
    Play_Game_R1,
    Play_Game_R2,
    Play_Game_R3,
]
