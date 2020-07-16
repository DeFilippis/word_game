from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random
from collections import Counter
from django.db import models as djmodels
from django.db.models import Sum

import yaml


author = 'Evan DeFilippis'

doc = """
Word game involving interdependence and cooperation
"""

class Constants(BaseConstants):
    # Set the number of players in this game
    players_per_group = 2

    # Load yaml file containing scrabble values
    with open(r'./data/scrabble.yaml') as file:
        scrabble_data = yaml.load(file, Loader=yaml.FullLoader)

    # Define the points scored per letter (Scrabble values)
    letter_values = {k: v['value'] for k, v in scrabble_data.items()}
    scrabble_bag = [k for k, v in scrabble_data.items() for _ in range(v['quantity'])]

    # Import word list to validate words
    dictionary = open("data/wordlist.txt").read().splitlines()

    # URL name
    name_in_url = 'word-game-2'
    tile_size = 6

    # Number of rounds
    num_rounds = 1
    NON_EXISTENCE_VALUE = -1


class Subsession(BaseSubsession):
    def creating_session(self):
        # Generates tiles for the group on the first round
        for g in self.get_groups():
            g.regenerate_tiles()

class TileOwnerMixin:

    def get_available_tiles(self):
        return self.tiles.filter(used=False)

    def get_list_of_available_tiles(self):
        return list(self.get_available_tiles().values_list('letter', flat=True))


class Group(TileOwnerMixin, BaseGroup):
    final_score = models.IntegerField(initial = 0)

    def total_words(self):
        group_score = self.words.aggregate(totwords=Sum('value'))['totwords']
        if group_score is None:
            return 0
        else:
            return group_score

    @property
    def words(self):
        return Word.objects.filter(owner__group=self).order_by('-id')

    def regenerate_tiles(self):
        """Theoretically can be a transactional conflict here...."""
        self.get_available_tiles().update(used=True)
        tiles_to_add = []
        for p in self.get_players():
            tile_items = random.sample(Constants.scrabble_bag, k=Constants.tile_size)
            tiles = [Tile(owner=p, letter=i, group=self) for i in tile_items]
            tiles_to_add.extend(tiles)
        Tile.objects.bulk_create(tiles_to_add)

    def live_word(self, id_in_group, data):
        w = data['word'].upper()
        p = self.get_player_by_id(id_in_group) # get player who submitted the word
        word = p.words.create() #create new instance of "word model" in the database
        word.body = w
        total_score = self.total_words()

        response = dict(id_in_group=id_in_group,
                        word=word.body,
                        word_value=word.value,
                        message=word.status,
                        total_score= total_score
                        )
        #if word.status == 'Success':
        TileSet.objects.create(word=word, tset=''.join(self.get_list_of_available_tiles()))
        self.regenerate_tiles()
        response['group_tiles'] = self.get_list_of_available_tiles()
        #else:
        #    self.regenerate_tiles()
        #    TileSet.objects.create(word=word, tset=''.join(self.get_list_of_available_tiles()))

        resp_dict = {}
        for i in self.get_players():
            resp_dict[i.id_in_group] = {**response, 'own_tiles': "".join(i.get_list_of_available_tiles())}
        return resp_dict

class Player(TileOwnerMixin, BasePlayer):
    pass

class Word(djmodels.Model):
    owner = djmodels.ForeignKey(to=Player, related_name='words', on_delete=djmodels.CASCADE)
    _body = models.StringField()
    exists = models.BooleanField()
    attainable = models.BooleanField()
    value = models.IntegerField()

    def set_value(self, body):
        if self.exists and self.attainable:
            return sum([Constants.letter_values[l] for l in body])
        else:
            return Constants.NON_EXISTENCE_VALUE

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        self._body = value
        self.exists = value in Constants.dictionary
        self.attainable = set(self.body).issubset(set(self.owner.group.get_list_of_available_tiles()))
        self.value = self.set_value(value)
        self.save()

    @property
    def status(self):
        if self.exists and self.attainable:
            return 'Success'
        if self.exists and not self.attainable:
            return "You do not have the right tiles for this word"
        return "This word is not in the dictionary"


class Tile(djmodels.Model):
    owner = djmodels.ForeignKey(to=Player, related_name='tiles', on_delete=djmodels.CASCADE)
    group = djmodels.ForeignKey(to=Group, related_name='tiles', on_delete=djmodels.CASCADE)
    letter = djmodels.CharField(max_length=1)
    used = models.BooleanField(initial=False)

class TileSet(djmodels.Model):
    tset = models.StringField()
    word = djmodels.OneToOneField(to=Word, on_delete=djmodels.CASCADE)
    when = djmodels.DateTimeField(auto_now=True)

def custom_export(players):
    # header row
    yield ['session', 'participant_code', 'word', 'tiles', 'when', 'value']
    for t in TileSet.objects.all():
        yield [t.word.owner.session.code, t.word.owner.participant.code, t.word.body, t.tset, str(t.when), t.word.value]