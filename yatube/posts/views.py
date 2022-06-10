from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PostForm
from .models import Post, Group, User
from .utils import paginate_page


def index(request):
    """Отображает все посты, включая те, у которых есть группа."""
    posts = Post.objects.select_related('author', 'group')
    page_obj = paginate_page(request, posts)
    return render(
        request,
        'posts/index.html',
        {'page_obj': page_obj, }
    )


def group_posts(request, slug):
    """Отображает все посты из группы, определенной по slug."""
    group = get_object_or_404(Group, slug=slug)
    page_obj = paginate_page(request, group.posts.all())
    return render(
        request,
        'posts/group_list.html',
        {
            'group': group,
            'page_obj': page_obj,
        }
    )


def profile(request, username):
    """Отображает посты пользователя, определенного по username."""
    author = get_object_or_404(User, username=username)
    page_obj = paginate_page(request, author.posts.all())
    return render(
        request,
        'posts/profile.html',
        {
            'author': author,
            'page_obj': page_obj,
        }
    )


def post_detail(request, post_id):
    """Отображает единичный пост, выбранный по post_id."""
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    if post.author != request.user:
        is_edit = False
    return render(
        request,
        'posts/post_detail.html',
        {'post': post, 'is_edit': is_edit, }
    )


@login_required
def post_create(request):
    """
    Выводит форму для создания поста с полями 'Текст' и 'Группа'.
    Декотратор отправляет неавторизованного пользователя залогиниться.
    """
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if not request.method == 'POST':
        return render(
            request,
            'posts/create_post.html',
            {'form': form, }
        )
    if not form.is_valid():
        return render(
            request,
            'posts/create_post.html',
            {'form': form, }
        )
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author)


@login_required
def post_edit(request, post_id):
    """
    Выводит форму для редактирования поста с проверкой,
    что пост принадлежит пользователю.
    Декотратор отправляет неавторизованного пользователя залогиниться.
    """
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not request.method == 'POST':
        return render(
            request,
            'posts/create_post.html',
            {
                'form': form,
                'post': post,
            }
        )
    if not form.is_valid():
        return render(
            request,
            'posts/create_post.html',
            {
                'form': form,
                'post': post,
            }
        )
    form.save(commit=True)
    return redirect('posts:post_detail', post_id)
