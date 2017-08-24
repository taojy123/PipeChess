# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField


# '—' is not '-' !

FULL_BOARD_DATA = [
    ['·', '—', '·', '—', '·', '—', '·'],
    ['|', '1', '|', '1', '|', '1', '|'],
    ['·', '—', '·', '—', '·', '—', '·'],
    ['|', '2', '|', '2', '|', '2', '|'],
    ['·', '—', '·', '—', '·', '—', '·'],
    ['|', '1', '|', '1', '|', '1', '|'],
    ['·', '—', '·', '—', '·', '—', '·'],
    ['|', '2', '|', '2', '|', '2', '|'],
    ['·', '—', '·', '—', '·', '—', '·'],
    ['|', '1', '|', '1', '|', '1', '|'],
    ['·', '—', '·', '—', '·', '—', '·'],
]

INIT_BOARD_DATA = [
    ['·', ' ', '·', ' ', '·', ' ', '·'],
    [' ', '0', ' ', '0', ' ', '0', ' '],
    ['·', ' ', '·', ' ', '·', ' ', '·'],
    [' ', '0', ' ', '0', ' ', '0', ' '],
    ['·', ' ', '·', ' ', '·', ' ', '·'],
    [' ', '0', ' ', '0', ' ', '0', ' '],
    ['·', ' ', '·', ' ', '·', ' ', '·'],
    [' ', '0', ' ', '0', ' ', '0', ' '],
    ['·', ' ', '·', ' ', '·', ' ', '·'],
    [' ', '0', ' ', '0', ' ', '0', ' '],
    ['·', ' ', '·', ' ', '·', ' ', '·'],
]


class Game(models.Model):

    name = models.CharField(max_length=255)
    board = JSONField(default=INIT_BOARD_DATA)
    player1 = models.ForeignKey(User, related_name='as_player1_games', null=True, blank=True)
    player2 = models.ForeignKey(User, related_name='as_player2_games', null=True, blank=True)
    winner = models.IntegerField(default=0)     # 0,1,2
    turn = models.IntegerField(default=1)       # 1,2
    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

    def draw_pipe(self, i, j):
        assert self.board[i][j] == ' '
        if i % 2 == 0:
            self.board[i][j] = '—'
        else:
            self.board[i][j] = '|'
        self.check_flag()
        self.switch_turn()

    def check_flag(self):
        board = self.board
        for i in range(11):
            for j in range(7):
                if board[i][j] != '0':
                    continue
                assert (0 < i < 10) and (0 < j < 6), (i, j)
                if not self.is_surrounded(i, j):
                    continue
                self.board[i][j] = str(self.turn)

    def is_surrounded(self, i, j):
        board = self.board
        if board[i+1][j] == ' ':
            return False
        if board[i-1][j] == ' ':
            return False
        if board[i][j+1] == ' ':
            return False
        if board[i][j-1] == ' ':
            return False
        return True

    def switch_turn(self):
        if self.turn == 1:
            self.turn = 2
        elif self.turn == 2:
            self.turn = 1
        else:
            raise AssertionError('turn must be 1 or 2')
        self.save()

    def check_winner(self):
        items = self.items
        if '0' in items:
            assert self.winner == 0
            return 0
        if items['1'] > items['2']:
            self.winner = 1
        else:
            self.winner = 2
        self.save()
        return self.winner

    @property
    def items(self):
        rs = {}
        for line in self.board:
            for item in line:
                rs[item] = rs.get(item, 0) + 1
        return rs

    @property
    def count1(self):
        return self.items.get('1')

    @property
    def count2(self):
        return self.items.get('2')

    @property
    def board_display(self):
        display = ''
        for line in self.board:
            display += ' '.join(line) + '\n'
        return display

    @property
    def board_display_html(self):
        display = self.board_display.strip().replace('\n', '<br>').replace(' ', '&nbsp;')
        display = '<code>%s<code>' % display
        return display







