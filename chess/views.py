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
VS = ['different', 'used', 'important', 'every', 'large', 'available', 'popular', 'able', 'basic', 'known', 'various', 'difficult', 'several', 'united', 'historical', 'hot', 'useful', 'mental', 'scared', 'additional', 'emotional', 'old', 'political', 'similar', 'healthy', 'financial', 'medical', 'traditional', 'federal', 'entire', 'strong', 'actual', 'significant', 'successful', 'electrical', 'expensive', 'pregnant', 'intelligent', 'interesting', 'poor', 'happy', 'responsible', 'cute', 'helpful', 'recent', 'willing', 'nice', 'wonderful', 'impossible', 'serious', 'huge', 'rare', 'technical', 'typical', 'competitive', 'critical', 'electronic', 'immediate', 'aware', 'educational', 'environmental', 'global', 'legal', 'relevant', 'accurate', 'capable', 'dangerous', 'dramatic', 'efficient', 'powerful', 'foreign', 'hungry', 'practical', 'psychological', 'severe', 'suitable', 'numerous', 'sufficient', 'unusual', 'consistent', 'cultural', 'existing', 'famous', 'pure', 'afraid', 'obvious', 'careful', 'latter', 'unhappy', 'acceptable', 'aggressive', 'boring', 'distinct', 'eastern', 'logical', 'reasonable', 'strict', 'administrative', 'automatic', 'civil', 'former', 'massive', 'southern', 'unfair', 'visible', 'alive', 'angry', 'desperate', 'exciting', 'friendly', 'lucky', 'realistic', 'sorry', 'ugly', 'unlikely', 'anxious', 'comprehensive', 'curious', 'impressive', 'informal', 'inner', 'pleasant', 'sexual', 'sudden', 'terrible', 'unable', 'weak', 'wooden', 'asleep', 'confident', 'conscious', 'decent', 'embarrassed', 'guilty', 'lonely', 'mad', 'nervous', 'odd', 'remarkable', 'substantial', 'suspicious', 'tall', 'tiny', 'more', 'some', 'one', 'all', 'many', 'most', 'other', 'such', 'even', 'new', 'just', 'good', 'any', 'each', 'much', 'own', 'great', 'another', 'same', 'few', 'free', 'right', 'still', 'best', 'public', 'human', 'both', 'local', 'sure', 'better', 'general', 'specific', 'enough', 'long', 'small', 'less', 'high', 'certain', 'little', 'common', 'next', 'simple', 'hard', 'past', 'big', 'possible', 'particular', 'real', 'major', 'personal', 'current', 'left', 'national', 'least', 'natural', 'physical', 'short', 'last', 'single', 'individual', 'main', 'potential', 'professional', 'international', 'lower', 'open', 'according', 'alternative', 'special', 'working', 'true', 'whole', 'clear', 'dry', 'easy', 'cold', 'commercial', 'full', 'low', 'primary', 'worth', 'necessary', 'positive', 'present', 'close', 'creative', 'green', 'late', 'fit', 'glad', 'proper', 'complex', 'content', 'due', 'effective', 'middle', 'regular', 'fast', 'independent', 'original', 'wide', 'beautiful', 'complete', 'active', 'negative', 'safe', 'visual', 'wrong', 'ago', 'quick', 'ready', 'straight', 'white', 'direct', 'excellent', 'extra', 'junior', 'pretty', 'unique', 'classic', 'final', 'overall', 'private', 'separate', 'western', 'alone', 'familiar', 'official', 'perfect', 'bright', 'broad', 'comfortable', 'flat', 'rich', 'warm', 'young', 'heavy', 'valuable', 'correct', 'leading', 'slow', 'clean', 'fresh', 'normal', 'secret', 'tough', 'brown', 'cheap', 'deep', 'objective', 'secure', 'thin', 'chemical', 'cool', 'extreme', 'exact', 'fair']
NS = ['people', 'history', 'way', 'art', 'world', 'information', 'map', 'two', 'family', 'government', 'health', 'system', 'computer', 'meat', 'year', 'thanks', 'music', 'person', 'reading', 'method', 'data', 'food', 'understanding', 'theory', 'law', 'bird', 'literature', 'problem', 'software', 'control', 'knowledge', 'power', 'ability', 'economics', 'love', 'internet', 'television', 'science', 'library', 'nature', 'fact', 'product', 'idea', 'temperature', 'investment', 'area', 'society', 'activity', 'story', 'industry', 'media', 'thing', 'oven', 'community', 'definition', 'safety', 'quality', 'development', 'language', 'management', 'player', 'variety', 'video', 'week', 'security', 'country', 'exam', 'movie', 'organization', 'equipment', 'physics', 'analysis', 'policy', 'series', 'thought', 'basis', 'boyfriend', 'direction', 'strategy', 'technology', 'army', 'camera', 'freedom', 'paper', 'environment', 'child', 'instance', 'month', 'truth', 'marketing', 'university', 'writing', 'article', 'department', 'difference', 'goal', 'news', 'audience', 'fishing', 'growth', 'income', 'marriage', 'user', 'combination', 'failure', 'meaning', 'medicine', 'philosophy', 'teacher', 'communication', 'night', 'chemistry', 'disease', 'disk', 'energy', 'nation', 'road', 'role', 'soup', 'advertising', 'location', 'success', 'addition', 'apartment', 'education', 'math', 'moment', 'painting', 'politics', 'attention', 'decision', 'event', 'property', 'shopping', 'student', 'wood', 'competition', 'distribution', 'entertainment', 'office', 'population', 'president', 'unit', 'category', 'cigarette', 'context', 'introduction', 'opportunity', 'performance', 'driver', 'flight', 'length', 'magazine', 'newspaper', 'relationship', 'teaching', 'cell', 'dealer', 'finding', 'lake', 'member', 'message', 'phone', 'scene', 'appearance', 'association', 'concept', 'customer', 'death', 'discussion', 'housing', 'inflation', 'insurance', 'mood', 'woman', 'advice', 'blood', 'effort', 'expression', 'importance', 'opinion', 'payment', 'reality', 'responsibility', 'situation', 'skill', 'statement', 'wealth', 'application', 'city', 'county', 'depth', 'estate', 'foundation', 'grandmother', 'heart', 'perspective', 'photo', 'recipe', 'studio', 'topic', 'collection', 'depression', 'imagination', 'passion', 'percentage', 'resource', 'setting', 'ad', 'agency', 'college', 'connection', 'criticism', 'debt', 'description', 'memory', 'patience', 'secretary', 'solution', 'administration', 'aspect', 'attitude', 'director', 'personality', 'psychology', 'recommendation', 'response', 'selection', 'storage', 'version', 'alcohol', 'argument', 'complaint', 'contract', 'emphasis', 'highway', 'loss', 'membership', 'possession', 'preparation', 'steak', 'union', 'agreement', 'cancer', 'currency', 'employment', 'engineering', 'entry', 'interaction', 'mixture', 'preference', 'region', 'republic', 'tradition', 'virus', 'actor', 'classroom', 'delivery', 'device', 'difficulty', 'drama', 'election', 'engine', 'football', 'guidance', 'hotel', 'owner', 'priority', 'protection', 'suggestion', 'tension', 'variation', 'anxiety', 'atmosphere', 'awareness', 'bath', 'bread', 'candidate', 'climate', 'comparison', 'confusion', 'construction', 'elevator', 'emotion', 'employee', 'employer', 'guest', 'height', 'leadership', 'mall', 'manager', 'operation', 'recording', 'sample', 'transportation', 'charity', 'cousin', 'disaster', 'editor', 'efficiency', 'excitement', 'extent', 'feedback', 'guitar', 'homework', 'leader', 'mom', 'outcome', 'permission', 'presentation', 'promotion', 'reflection', 'refrigerator', 'resolution', 'revenue', 'session', 'singer', 'tennis', 'basket', 'bonus', 'cabinet', 'childhood', 'church', 'clothes', 'coffee', 'dinner', 'drawing', 'hair', 'hearing', 'initiative', 'judgment', 'lab', 'measurement', 'mode', 'mud', 'orange', 'poetry', 'police', 'possibility', 'procedure', 'queen', 'ratio', 'relation', 'restaurant', 'satisfaction', 'sector', 'signature', 'significance', 'song', 'tooth', 'town', 'vehicle', 'volume', 'wife', 'accident', 'airport', 'appointment', 'arrival', 'assumption', 'baseball', 'chapter', 'committee', 'conversation', 'database', 'enthusiasm', 'error', 'explanation', 'farmer', 'gate', 'girl', 'hall', 'historian', 'hospital', 'injury', 'instruction', 'maintenance', 'manufacturer', 'meal', 'perception', 'pie', 'poem', 'presence', 'proposal', 'reception', 'replacement', 'revolution', 'river', 'son', 'speech', 'tea', 'village', 'warning', 'winner', 'worker', 'writer', 'assistance', 'breath', 'buyer', 'chest', 'chocolate']


def make_random_name():
    v = random.choice(VS)
    n = random.choice(NS)
    name = v + n
    return name


def index(request):
    game_name = request.session.get('game_name')
    if not game_name:
        game_name = str(random.randint(1000, 9999))

    return HttpResponseRedirect('/game/%s/' % game_name)


def game(request, name):

    request.session['game_name'] = name
    request.session.save()

    user = request.user

    if not user.is_authenticated():
        username = make_random_name()
        user = User.objects.create(username=username)
        user.set_password(PASSWORD)
        user.save()
        user = auth.authenticate(username=username, password=PASSWORD)
        auth.login(request, user)

    game, created = Game.objects.get_or_create(name=name)

    if game.is_ai:
        ai, created = User.objects.get_or_create(username=settings.AI_NAME)
        if game.player1 != ai and game.player2 != ai:
            if game.name.startswith('ai1'):
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
