# -*- coding: utf-8 -*-
import random
import copy

from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField


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
# '—' is different from '-'

INIT_BOARD_DATA = [
    ['·', '', '·', '', '·', '', '·'],
    ['', '0', '', '0', '', '0', ''],
    ['·', '', '·', '', '·', '', '·'],
    ['', '0', '', '0', '', '0', ''],
    ['·', '', '·', '', '·', '', '·'],
    ['', '0', '', '0', '', '0', ''],
    ['·', '', '·', '', '·', '', '·'],
    ['', '0', '', '0', '', '0', ''],
    ['·', '', '·', '', '·', '', '·'],
    ['', '0', '', '0', '', '0', ''],
    ['·', '', '·', '', '·', '', '·'],
]


class Game(models.Model):

    name = models.CharField(max_length=255)
    board = JSONField(default=INIT_BOARD_DATA)
    player1 = models.ForeignKey(User, related_name='as_player1_games', null=True, blank=True)
    player2 = models.ForeignKey(User, related_name='as_player2_games', null=True, blank=True)
    winner = models.IntegerField(default=0)     # 0,1,2
    turn = models.IntegerField(default=1)       # 1,2
    last_pipe = JSONField(default=list)
    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

    def draw_pipe(self, i, j, player=None):
        if player and self.current_player != player:
            return False
        if self.board[i][j]:
            return False
        if i % 2 == 0:
            self.board[i][j] = '—'
        else:
            self.board[i][j] = '|'
        if not self.check_flag():
            self.switch_turn()
        self.last_pipe = [i, j]
        self.save()
        return True

    def check_flag(self):
        flag = False
        board = self.board
        for i in range(11):
            for j in range(7):
                if board[i][j] != '0':
                    continue
                assert (0 < i < 10) and (0 < j < 6), (i, j)
                if not self.is_surrounded(i, j):
                    continue
                self.board[i][j] = str(self.turn)
                flag = True
        self.check_winner()
        return flag

    def is_surrounded(self, i, j, n=4):
        board = self.board
        count = 0
        if board[i+1][j]:
            count += 1
        if board[i-1][j]:
            count += 1
        if board[i][j+1]:
            count += 1
        if board[i][j-1]:
            count += 1
        return count == n

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
        if items.get('1', 0) > items.get('2', 0):
            self.winner = 1
        else:
            self.winner = 2
        self.save()
        return self.winner

    def ai_try_to_draw(self):
        if self.winner:
            return
        ai, created = User.objects.get_or_create(username='AI')
        if self.current_player != ai:
            return
        i, j = self.get_best_draw()
        self.draw_pipe(i, j, ai)

    def get_shadow(self):
        board = [line[:] for line in self.board[:]]
        game = Game(board=board)
        return game

    def get_gain_pipe(self):
        board = self.board
        ii, jj = 0, 0
        for i in range(11):
            for j in range(7):
                if board[i][j] != '0':
                    continue
                count = 0
                if not board[i + 1][j]:
                    count += 1
                    ii, jj = i+1, j
                if not board[i - 1][j]:
                    count += 1
                    ii, jj = i-1, j
                if not board[i][j + 1]:
                    count += 1
                    ii, jj = i, j+1
                if not board[i][j - 1]:
                    count += 1
                    ii, jj = i, j-1
                if count == 1:
                    return ii, jj
        return 0, 0

    def max_gains(self):
        game = self.get_shadow()
        while True:
            i, j = game.get_gain_pipe()
            if i or j:
                game.board[i][j] = '+'
            else:
                break

        count = 0
        for i in range(11):
            for j in range(7):
                if game.board[i][j] != '0':
                    continue
                assert (0 < i < 10) and (0 < j < 6), (i, j)
                if game.is_surrounded(i, j):
                    count += 1

        return count

    def max_losts(self, i, j):
        game = self.get_shadow()
        game.board[i][j] = '+'
        return game.max_gains()

    def get_best_draw(self):
        game = self.get_shadow()
        gain_pipes = []
        normal_pipes = []
        lost_pipes = []
        for i in range(11):
            for j in range(7):
                if game.board[i][j]:
                    continue
                game.board[i][j] = '+'
                if game.check_surrounded():
                    gain_pipes.append((i, j))
                elif game.check_surrounded(n=3):
                    lost_pipes.append((i, j))
                else:
                    normal_pipes.append((i, j))
                game.board[i][j] = ''

        print gain_pipes
        print normal_pipes
        print lost_pipes

        if gain_pipes:
            print 'ai draw gain'
            return random.choice(gain_pipes)

        if normal_pipes:
            print 'ai draw normal'
            return random.choice(normal_pipes)

        print 'ai draw lost'
        rs = {}
        for i, j in lost_pipes:
            max_losts = self.max_losts(i, j)
            rs[max_losts] = rs.get(max_losts, [])
            rs[max_losts].append((i, j))

        max_losts = sorted(rs)[0]

        return random.choice(rs[max_losts])


    def check_surrounded(self, n=4):
        board = self.board
        for i in range(11):
            for j in range(7):
                if board[i][j] != '0':
                    continue
                assert (0 < i < 10) and (0 < j < 6), (i, j)
                if not self.is_surrounded(i, j, n):
                    continue
                return True
        return False

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
            line = [item if item else ' ' for item in line]
            display += ' '.join(line) + '\n'
        return display

    @property
    def board_display_html(self):
        display = self.board_display.strip().replace('\n', '<br>').replace(' ', '&nbsp;')
        display = '<code>%s<code>' % display
        return display

    @property
    def is_ai(self):
        return self.name.startswith('ai')

    @property
    def current_player(self):
        return getattr(self, 'player%d' % self.turn)

    @property
    def status(self):
        return {
            'board': self.board,
            'winner': self.winner,
            'turn': self.turn,
            'player1': self.player1.username if self.player1 else '',
            'player2': self.player2.username if self.player2 else '',
            'last_pipe': self.last_pipe,
        }







