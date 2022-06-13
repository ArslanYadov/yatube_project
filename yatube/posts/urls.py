from django.urls import path
from . import views


app_name = 'posts'

urlpatterns = [
    # Url к постам, главная страница
    path('', views.index, name='index'),
    # Url к всем постам определенной группы
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    # Url к профилю username
    path('profile/<str:username>/', views.profile, name='profile'),
    # Url к деталям по посту из post_id
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    # Url к созданию поста
    path('create/', views.post_create, name='post_create'),
    # Url к редактированию поста по post_id
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    # Url к добавлению комментария к посту по post_id
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),
]
