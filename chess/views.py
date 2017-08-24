# -*- coding: utf-8 -*-

import StringIO
import HTMLParser
import random
import string

import BeautifulSoup
import xlwt

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from models import *


PASSWORD = 'pipechess'


def index(request):
    game_name = request.session.get('game_name')
    if not game_name:
        game_name = str(random.randint(1000, 9999))
        request.session['game_name'] = game_name
        request.session.save()

    return HttpResponseRedirect('/game/%s/' % game_name)


def game(request, name):

    user = request.user

    if not user.is_authenticated():
        username = salt = ''.join(random.sample(string.ascii_letters + string.digits, 6))
        user = User.objects.create(username=username)
        user.set_password(PASSWORD)
        user.save()
        user = auth.authenticate(username=username, password=PASSWORD)
        auth.login(request, user)

    game, created = Game.objects.get_or_create(name=name)

    if not game.player1:
        game.player1 = user
        game.save()
    elif not game.player2 and game.player1 != user:
        game.player2 = user
        game.save()

    return render_to_response('game.html', locals())


def game_status(request, name):

    game = Game.objects.get(name=name)

    result = {
        'game': {
            'board': game.board,
            'winner': game.winner,
            'turn': game.turn,
        }
    }

    return JsonResponse(result)


def try_to_draw(request):

    game_id = request.POST.get('game_id')
    from_id = request.POST.get('from_id')
    to_id = request.POST.get('to_id')
    result = {
        'success': True,
        'detail': ''
    }

    game = Game.objects.get(id=game_id)

    user = request.user

    if not user:
        return JsonResponse({'success': False, 'detail': u'未登录'})

    if getattr(game, 'player%d' % game.turn) != user:
        return JsonResponse({'success': False, 'detail': u'现在不是您的回合'})

    from_i = int(from_id[2]) * 2
    from_j = int(from_id[1]) * 2
    to_i = int(to_id[2]) * 2
    to_j = int(to_id[1]) * 2

    print from_i, from_j, to_i, to_j

    pipe_i = pipe_j = 0
    if from_i == to_i:
        if from_j - to_j == 2:
            pipe_i = from_i
            pipe_j = from_j - 1
        elif to_j - from_j == 2:
            pipe_i = from_i
            pipe_j = to_j - 1
        else:
            result['success'] = False
    elif from_j == to_j:
        if from_i - to_i == 2:
            pipe_j = from_j
            pipe_i = from_i - 1
        elif to_i - from_i == 2:
            pipe_j = from_j
            pipe_i = to_i - 1
        else:
            result['success'] = False
    else:
        result['success'] = False

    if not result['success']:
        result['detail'] = u'此两点间无法连线，只能连接相邻一格距离的两点'

    if result['success'] and game.board[pipe_i][pipe_j] != ' ':
        print game.board[pipe_i][pipe_j]
        result['success'] = False
        result['detail'] = u'此两点间已有连线'

    if result['success']:
        game.draw_pipe(pipe_i, pipe_j)
        result['game'] = {
            'board': game.board,
            'winner': game.winner,
            'turn': game.turn,
        }

    return JsonResponse(result)


def login(request):
    msg = ''
    next_url = request.GET.get('next', '/')
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        next_url = request.POST.get('next', '/')
        user = auth.authenticate(username=username, password=password)
        print(username, password)
        if user is not None and user.is_active:
            auth.login(request, user)
            return HttpResponseRedirect(next_url)
        else:
            msg = u'username or password error'
    return render_to_response('login.html', locals())


def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return HttpResponseRedirect("/")


@login_required
def password(request):
    msg = ''
    if request.method == 'POST':
        password = request.POST.get('password', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        user = request.user

        if not user.check_password(password):
            msg = u'old password error'

        if password1 != password2:
            msg = u'two passwords not the same'

        if not msg:
            user.set_password(password1)
            user.save()
            return HttpResponseRedirect('/login/')

    return render_to_response('password.html', locals())


def output(request):
    data = request.POST.get('data')
    begin_index = int(request.POST.get('begin_index', 0))
    end_index = int(request.POST.get('end_index', 999))

    html_parser = HTMLParser.HTMLParser()

    wb = xlwt.Workbook()
    ws = wb.add_sheet('output')

    soup = BeautifulSoup.BeautifulSoup(data)

    thead_soup = soup.find('thead')
    th_soups = thead_soup.findAll(['th', 'td'])
    th_soups = th_soups[begin_index:end_index]

    j = 0
    for th_soup in th_soups:
        th = th_soup.getText()
        th = html_parser.unescape(th).strip()
        ws.write(0, j, th)
        j += 1

    tbody_soup = soup.find('tbody')
    tr_soups = tbody_soup.findAll('tr')

    i = 1
    for tr_soup in tr_soups:
        td_soups = tr_soup.findAll(['td', 'th'])
        td_soups = td_soups[begin_index:end_index]

        j = 0
        for td_soup in td_soups:
            td = td_soup.getText()
            td = html_parser.unescape(td).strip()
            ws.write(i, j, td)
            j += 1

        i += 1

    s = StringIO.StringIO()
    wb.save(s)
    s.seek(0)
    data = s.read()
    response = HttpResponse(data)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="output.xls"'

    return response
