from django.http import HttpResponse


def index(request):
    return HttpResponse('Hello there!')


def group_posts(request, string):
    return HttpResponse(f'Let\'s see our post: {string}')