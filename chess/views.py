# -*- coding: utf-8 -*-

import random

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from models import *


AI_NAME = 'Crazy AI'
PASSWORD = 'pipechess'
VS = ['豁达', '潇洒', '雍容', '轩昂', '爽朗', '悠然', '从容', '坦荡', '大方', '宽容', '厚道', '风度', '高雅', '情调', '淡泊', '迷人', '安然', '宁静', '随和', '随性', '傲骨', '大气', '柔韧', '洋气', '海涵', '儒雅', '淡定', '漂亮', '可爱', '美丽', '黑暗', '强壮', '丑陋', '小巧', '精致']
NS = ['孩子', '眼睛', '地方', '过去', '事情', '晚上', '知识', '故事', '冬天', '样子', '后来', '以前', '童年', '日子', '活动', '公园', '房间', '空气', '笑容', '明天', '风景', '音乐', '岁月', '文化', '机会', '身影', '天气', '空中', '书包', '汽车', '早晨', '道路', '星星', '礼物', '夜晚', '意义', '耳朵', '厨房', '风雨', '电话', '种子', '广场', '清晨', '故乡', '笑脸', '水面', '思想', '伙伴', '美景', '照片', '水果', '彩虹', '先生', '鲜花', '灯光', '亲人', '语言', '爱心', '角落', '青蛙', '电影', '阳台', '动力', '花园', '诗人', '树林', '雨伞', '乡村', '对手', '上午', '分别', '作用', '活力', '古代', '公主', '力气', '从前', '作品', '空间', '黑夜', '说明', '青年', '面包', '往事', '中心', '嘴角', '书本', '雪人', '笑话', '云朵', '早饭', '行人', '乐园', '花草', '人才', '课文', '年代', '灰尘', '沙子', '明星', '本子', '水珠', '彩色', '路灯', '房屋', '心愿', '市场', '雨点', '细雨', '书房', '毛巾', '画家', '绿豆', '起点', '青菜', '土豆']



def make_random_name():
    v = random.choice(VS)
    n = random.choice(NS)
    name = v + '的' + n
    return name


def index(request):
    game_name = request.session.get('game_name')
    if not game_name:
        return HttpResponseRedirect('/new/?ai=1')
    return HttpResponseRedirect('/game/%s/' % game_name)


def new(request):
    ai = request.GET.get('ai', False)
    game_name = None
    for i in range(1000):
        game_name = str(random.randint(100000, 999999))
        if ai:
            game_name = 'ai' + game_name
        if not Game.objects.filter(name=game_name).exists():
            return HttpResponseRedirect('/game/%s/' % game_name)
    # clear games
    t = timezone.now() - timezone.timedelta(hours=1)
    Game.objects.filter(last_pipe=[], create_time__lt=t)
    return HttpResponseRedirect('/game/1/')


def match(request):
    user = request.user
    t = timezone.now() - timezone.timedelta(minutes=5)
    game = Game.objects.filter(player2__isnull=True, create_time__gt=t).exclude(player1=user).order_by('-create_time').first()
    if game:
        return HttpResponseRedirect('/game/%s/' % game.name)
    return HttpResponseRedirect('/new/')


def game(request, name):

    request.session['game_name'] = name
    request.session.save()

    user = request.user

    if not user.is_authenticated():
        username = make_random_name()
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(PASSWORD)
            user.save()
            # user = auth.authenticate(username=username, password=PASSWORD)
        auth.login(request, user)

    game, created = Game.objects.get_or_create(name=name)

    if game.is_ai and not game.player1 and not game.player2:
        ai, created = User.objects.get_or_create(username=AI_NAME)
        if random.random() > 0.5:
            game.player1 = ai
        else:
            game.player2 = ai
        game.save()

    if not game.player1:
        game.player1 = user
        game.save()
    elif not game.player2 and game.player1 != user:
        game.player2 = user
        game.save()

    return render_to_response('game.html', locals())


def game_status(request, name):

    game = Game.objects.get(name=name)

    if game.is_ai:
        game.ai_try_to_draw()

    result = {
        'game': game.status
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

    if not game.player2:
        return JsonResponse({'success': False, 'detail': u'请等待玩家就绪'})

    if game.winner:
        return JsonResponse({'success': False, 'detail': u'游戏已结束'})

    game.check_winner()

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

    if result['success'] and game.board[pipe_i][pipe_j]:
        result['success'] = False
        result['detail'] = u'此两点间已有连线'

    if result['success']:
        game.draw_pipe(pipe_i, pipe_j, user)
        result['game'] = game.status

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

