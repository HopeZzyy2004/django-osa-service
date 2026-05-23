from django.http import HttpResponse


def blog_home(request):
    return HttpResponse('Blog API root')


def blog_detail(request, post_id):
    return HttpResponse(f'Blog post {post_id}')
