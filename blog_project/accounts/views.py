from django.http import HttpResponse


def login_view(request):
    return HttpResponse('Accounts login placeholder')


def logout_view(request):
    return HttpResponse('Accounts logout placeholder')


def profile_view(request):
    return HttpResponse('Accounts profile placeholder')
