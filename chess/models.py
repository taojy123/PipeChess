# -*- coding: utf-8 -*-
import random
import copy

import time
from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField


FULL_BOARD_DATA = [
    ['.', '-', '.', '-', '.', '-', '.'],
    ['|', '1', '|', '1', '|', '1', '|'],
    ['.', '-', '.', '-', '.', '-', '.'],
    ['|', '2', '|', '2', '|', '2', '|'],
    ['.', '-', '.', '-', '.', '-', '.'],
    ['|', '1', '|', '1', '|', '1', '|'],
    ['.', '-', '.', '-', '.', '-', '.'],
    ['|', '2', '|', '2', '|', '2', '|'],
    ['.', '-', '.', '-', '.', '-', '.'],
    ['|', '1', '|', '1', '|', '1', '|'],
    ['.', '-', '.', '-', '.', '-', '.'],
]

INIT_BOARD_DATA = [
    ['.', '', '.', '', '.', '', '.'],
    ['', '0', '', '0', '', '0', ''],
    ['.', '', '.', '', '.', '', '.'],
    ['', '0', '', '0', '', '0', ''],
    ['.', '', '.', '', '.', '', '.'],
    ['', '0', '', '0', '', '0', ''],
    ['.', '', '.', '', '.', '', '.'],
    ['', '0', '', '0', '', '0', ''],
    ['.', '', '.', '', '.', '', '.'],
    ['', '0', '', '0', '', '0', ''],
    ['.', '', '.', '', '.', '', '.'],
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
            self.board[i][j] = '-'
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

        t1 = time.time()
        i, j = self.get_best_draw()
        t2 = time.time()
        print 'ai_try_to_draw, cost:', t2 - t1

        self.draw_pipe(i, j, ai)

    # 获取当前棋局的影子棋局 即单纯复制 board
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

    # 获取当前棋局上 直接吃的 / 不吃不送的 / 要送子的 下棋位置
    def get_gain_normal_lost_pipes(self):
        game = self.get_shadow()
        gain_pipes = []
        normal_pipes = []
        lost_pipes = []
        for i in range(11):
            for j in range(7):
                if game.board[i][j]:
                    continue
                game.board[i][j] = '+'
                if game.get_surrounded_count():
                    gain_pipes.append((i, j))
                elif game.get_surrounded_count(n=3):
                    lost_pipes.append((i, j))
                else:
                    normal_pipes.append((i, j))
                game.board[i][j] = ''

        return gain_pipes, normal_pipes, lost_pipes

    def get_best_draw(self):

        gain_pipes, normal_pipes, lost_pipes = self.get_gain_normal_lost_pipes()

        print '================================================'
        print 'gain_pipes:', gain_pipes
        print 'normal_pipes:', normal_pipes
        print 'lost_pipes:', lost_pipes

        if not gain_pipes and not normal_pipes and not lost_pipes:
            return 0, 0

        if gain_pipes:
            print '=========== ai draw gain =============='
            game = self.get_shadow()
            try_count = game.try_to_gain_all()
            gs, ns, ls = game.get_gain_normal_lost_pipes()
            if not gs and not ns and ls:
                # 面临吃完必须得到送的情况
                print '面临吃完必须得到送的情况'
                lost_stat = game.get_lost_stat(ls)
                if sorted(lost_stat)[0] >= 3:
                    # 如果剩下还有龙（连着3个以上可吃的）
                    print '如果剩下还有龙'
                    if try_count == 2:
                        # 如果这是最后的2个吃，就让给对方，换的下一条龙
                        print '如果这是最后的2个吃'
                        game2 = self.get_shadow()
                        game2.try_to_gain_one()
                        i, j = game2.try_to_gain_one()
                        return i, j

                    # 否则还剩下2个以上的吃，就按顺序吃
                    return gain_pipes[0]

            return random.choice(gain_pipes)

        if normal_pipes:
            print '=========== ai draw normal ============'
            return random.choice(normal_pipes)

        print '========= ai draw lost ============='
        lost_stat = self.get_lost_stat(lost_pipes)

        max_losts = sorted(lost_stat)[0]
        print 'max_losts:', max_losts

        # 当必须送2个的时候 在2个格子中间划线（避免主动权交由对方）
        if max_losts == 2:
            for i, j in lost_stat[2]:
                game = self.get_shadow()
                game.board[i][j] = '+'
                if game.get_surrounded_count(n=3) == 2:
                    return i, j

        return random.choice(lost_stat[max_losts])

    # 获取下这些步时对应要送出多少个子 返回 dict
    def get_lost_stat(self, pipes):
        lost_stat = {}
        for i, j in pipes:
            max_losts = self.max_losts(i, j)
            lost_stat[max_losts] = lost_stat.get(max_losts, [])
            lost_stat[max_losts].append((i, j))
        return lost_stat

    # 获取当前棋盘上被包围 n 面的旗子的数量
    def get_surrounded_count(self, n=4, set_flag=None):
        count = 0
        board = self.board
        for i in range(11):
            for j in range(7):
                if board[i][j] != '0':
                    continue
                assert (0 < i < 10) and (0 < j < 6), (i, j)
                if not self.is_surrounded(i, j, n):
                    continue
                count += 1
                if set_flag:
                    board[i][j] = set_flag
        return count

    # 获取尝试吃掉尽量多子后的棋局 (只有影子棋局可用）
    def try_to_gain_all(self):
        assert not self.player1
        count = 0
        while True:
            if not self.try_to_gain_one():
                break
            count += 1
        return count

    # 尝试吃掉一个旗子 吃到返回 True 否则 False
    def try_to_gain_one(self):
        for i in range(11):
            for j in range(7):
                if self.board[i][j]:
                    continue
                self.board[i][j] = '+'
                if self.get_surrounded_count(set_flag='X'):
                    return i, j
                self.board[i][j] = ''
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







