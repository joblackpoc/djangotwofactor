from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('post_list', views.PostListView.as_view(), name='post_list'),
    path('category/<slug:category_slug>/', views.CategoryPostListView.as_view(), name='category_posts'),
    path('search/', views.post_search, name='post_search'),
    # Post Detail/CRUD
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/new/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<slug:slug>/update/', views.PostUpdateView.as_view(), name='post_update'),
    path('post/<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
        
    # Post Actions
    path('post/<slug:slug>/like/', views.like_post, name='post_like'),
    path('post/<slug:slug>/share/', views.share_post, name='post_share'),
    
    # Comments
    path('posts/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    #path('post/<slug:slug>/add_reply/<int:comment_id>/', views.PostDetailView.as_view(), name='add_reply'),
    #path('post/<slug:post_slug>/comment/<int:comment_id>/reply/', views.add_reply, name='add_reply'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('posts/<slug:slug>/like/', views.like_post, name='like_post'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # User Posts
    path('user/<str:username>/posts/', views.UserPostListView.as_view(), name='user_posts'),
    path('my-posts/', views.UserPostListView.as_view(), name='my_posts'),
]