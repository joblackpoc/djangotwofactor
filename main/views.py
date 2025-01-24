from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Count
from .models import Post, Category, Comment
from django.db.models import Q
from .forms import PostForm, CommentForm, PostSearchForm
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from django.contrib.sites.shortcuts import get_current_site
import json
from datetime import datetime, timedelta

#try:
#    from blogs.models import Post as BlogPost
#except ImportError:
#    BlogPost = None
def home(request):
    # Get featured posts
    featured_posts = Post.objects.filter(
        status='published',
        featured=True
    ).order_by('-created_date')[:3]

    # Get latest posts
    latest_posts = Post.objects.filter(
        status='published'
    ).order_by('-created_date')[:6]

    # Get popular posts (most viewed)
    popular_posts = Post.objects.filter(
        status='published'
    ).order_by('-views')[:4]

    # Get trending posts (most likes in last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    trending_posts = Post.objects.filter(
        status='published',
        created_date__gte=week_ago
    ).annotate(
        like_count=Count('likes')
    ).order_by('-like_count')[:4]

    # Get categories with post counts
    categories = Category.objects.annotate(
        post_count=Count('posts')
    ).order_by('-post_count')[:6]

    # Get recent categories
    recent_categories = Category.objects.order_by('-created_at')[:6]

    context = {
        'featured_posts': featured_posts,
        'latest_posts': latest_posts,
        'popular_posts': popular_posts,
        'trending_posts': trending_posts,
        'categories': categories,
        'recent_categories': recent_categories,
    }

    return render(request, 'main/home.html', context)
def index(request):
    posts = Post.objects.all().order_by('-created_at')

    context = {
        'posts' : posts,
    }
    return render(request, 'main/home.html', context)

def about(request):
    return render(request, 'main/about.html')

def contact(request):
    return render(request, 'main/contact.html')

# main/views.py
class CategoryPostListView(ListView):
    model = Post
    template_name = 'main/post_list.html'  # We can reuse the post_list template
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return Post.objects.filter(
            categories=self.category,
            status='published'
        ).order_by('-created_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['search_form'] = PostSearchForm()
        context['title'] = f'Posts in {self.category.name}'
        return context
    
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'main/post_form.html'
    success_url = reverse_lazy('main:post_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post created successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Post'
        context['submit_text'] = 'Create Post'
        return context
class PostListView(ListView):
    model = Post
    template_name = 'main/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_date']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_site'] = get_current_site(self.request)
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        """
        Add reply form to the context
        """
        context = super().get_context_data(**kwargs)
        
        # Create an empty reply form
        #context['reply_form'] = ReplyForm()
        
        # Fetch comments with their replies for this post
        #context['comments'] = self.object.comments.prefetch_related('replies')
        
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for adding replies
        """
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to add a reply.")
            return redirect('login')
        
        return self.add_reply(request, *args, **kwargs)

    # def add_reply(self, request, *args, **kwargs):
    #     """
    #     Add a reply to a specific comment
    #     """
    #     # Get the current post
    #     self.object = self.get_object()

    #     # Get the comment to reply to
    #     comment_id = kwargs.get('comment_id')
    #     comment = get_object_or_404(Comment, id=comment_id, post=self.object)

    #     # Create reply form with POST data
    #     reply_form = ReplyForm(request.POST)

    #     if reply_form.is_valid():
    #         # Save the reply
    #         reply = reply_form.save(commit=False)
    #         reply.comment = comment
    #         reply.user = request.user
    #         reply.save()

    #         messages.success(request, "Your reply has been added.")
    #     else:
    #         # If form is invalid, add form errors to messages
    #         for error in reply_form.errors.values():
    #             messages.error(request, error)

    #     # Redirect back to the post detail page
    #     return redirect(self.object.get_absolute_url())
# class PostDetailView(DetailView):
#     model = Post
#     template_name = 'main/post_detail.html'
#     context_object_name = 'post'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         post = self.get_object()
        
#         # Comments with pagination
#         comments_list = post.post_comments.filter(parent=None).order_by('-created_date')
#         paginator = Paginator(comments_list, 10)
#         page = self.request.GET.get('page')
#         comments = paginator.get_page(page)
        
#         # Social sharing URLs
#         current_site = get_current_site(self.request)
#         post_url = f"https://{current_site.domain}{post.get_absolute_url()}"
        
#         context.update({
#             'comments': comments,
#             'comment_form': CommentForm(),
#             'liked': post.likes.filter(id=self.request.user.id).exists() if self.request.user.is_authenticated else False,
#             'like_count': post.total_likes(),
#             'comment_count': post.total_comments(),
#             'share_url': {
#                 'facebook': f"https://www.facebook.com/sharer/sharer.php?u={post_url}",
#                 'twitter': f"https://twitter.com/intent/tweet?url={post_url}&text={post.title}",
#                 'linkedin': f"https://www.linkedin.com/shareArticle?mini=true&url={post_url}&title={post.title}",
#             }
#         })
#         return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'main/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.slug = self.generate_unique_slug(form.instance.title)
        response = super().form_valid(form)
        messages.success(self.request, 'Post created successfully!')
        return response

    def generate_unique_slug(self, title):
        slug = slugify(title)
        unique_slug = slug
        num = 1
        while Post.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{slug}-{num}"
            num += 1
        return unique_slug

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'main/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Post updated successfully!')
        return response

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to edit this post.")
        return redirect('post_detail', slug=self.get_object().slug)

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'main/post_confirm_delete.html'
    success_url = reverse_lazy('post_list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Post deleted successfully!')
        return super().delete(request, *args, **kwargs)

def post_search(request):
    """
    View to handle post search functionality
    """
    search_form = PostSearchForm(request.GET)
    query = request.GET.get('query', '')
    category = request.GET.get('category', '')
    posts = Post.objects.filter(status='published')

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query)
        )

    if category:
        posts = posts.filter(categories__id=category)

    # Ordering
    posts = posts.order_by('-created_date')

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(posts, 10)  # Show 10 posts per page

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts': posts,
        'query': query,
        'search_form': search_form,
        'total_results': paginator.count,
    }

    return render(request, 'main/search_results.html', context)
@login_required
@require_POST
def like_post(request):
    """
    Ajax view for handling post likes
    """
    data = json.loads(request.body)
    post_id = data.get('post_id')
    post = get_object_or_404(Post, id=post_id)
    
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
        
    return JsonResponse({
        'liked': liked,
        'like_count': post.total_likes(),
    })


@require_POST
@login_required
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'comment_id': comment.id,
                    'author': comment.author.username,
                    'content': comment.content,
                    'created_date': comment.created_date.strftime('%B %d, %Y %H:%M'),
                })
            
            messages.success(request, 'Your comment has been added successfully.')
            return redirect('main:post_detail', slug=slug)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'errors': form.errors
                }, status=400)
                
    return redirect('main:post_detail', slug=slug)

def share_post(request, slug):
    """
    View for tracking post shares
    """
    post = get_object_or_404(Post, slug=slug)
    platform = request.GET.get('platform', 'facebook')
    
    # Track share analytics if needed
    if platform == 'facebook':
        share_url = f"https://www.facebook.com/sharer/sharer.php?u={request.build_absolute_uri(post.get_absolute_url())}"
    elif platform == 'twitter':
        share_url = f"https://twitter.com/intent/tweet?url={request.build_absolute_uri(post.get_absolute_url())}&text={post.title}"
    elif platform == 'linkedin':
        share_url = f"https://www.linkedin.com/shareArticle?mini=true&url={request.build_absolute_uri(post.get_absolute_url())}&title={post.title}"
    else:
        share_url = request.build_absolute_uri(post.get_absolute_url())
    
    return JsonResponse({
        'share_url': share_url
    })

@login_required
def add_reply(request, slug, comment_id):
    """Handle adding replies to comments"""
    post = get_object_or_404(Post, slug=slug)
    parent_comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = post
            reply.author = request.user
            reply.parent = parent_comment
            reply.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'reply_id': reply.id,
                    'author': reply.author.username,
                    'content': reply.content,
                    'created_date': reply.created_date.strftime('%B %d, %Y %H:%M'),
                })
            
            messages.success(request, 'Your reply has been added.')
            return redirect('main:post_detail', slug=slug)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'errors': form.errors
                }, status=400)
    
    return redirect('main:post_detail', slug=slug)

@login_required
def delete_reply(request, reply_id):
    """
    View to handle deleting replies
    """
    reply = get_object_or_404(Comment, id=reply_id)
    
    # Check if user is the author of the reply
    if request.user != reply.author:
        messages.error(request, "You don't have permission to delete this reply.")
        return redirect('main:post_detail', slug=reply.post.slug)
    
    if request.method == 'POST':
        post_slug = reply.post.slug
        reply.delete()
        
        if request.is_ajax():
            return JsonResponse({'status': 'success'})
        
        messages.success(request, 'Your reply has been deleted.')
        return redirect('main:post_detail', slug=post_slug)
        
    return redirect('main:post_detail', slug=reply.post.slug)

# Also add this JavaScript to handle the reply functionality
@login_required
def get_reply_form(request, comment_id):
    """
    View to get the reply form HTML
    """
    try:
        comment = get_object_or_404(Comment, id=comment_id)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = ReplyForm()
            context = {
                'form': form,
                'comment': comment,
                'post': comment.post,
            }
            
            form_html = render_to_string(
                'main/includes/reply_form.html',
                context,
                request=request
            )
            
            return JsonResponse({
                'status': 'success',
                'form_html': form_html
            })
        
        # If not AJAX, redirect to post detail
        messages.warning(request, 'Invalid request method.')
        return redirect('main:post_detail', slug=comment.post.slug)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
@login_required
def like_comment(request, comment_id):
    """
    View to handle liking/unliking comments
    """
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        if comment.likes.filter(id=request.user.id).exists():
            # User has already liked this comment - unlike it
            comment.likes.remove(request.user)
            liked = False
        else:
            # User hasn't liked this comment yet - like it
            comment.likes.add(request.user)
            liked = True

        return JsonResponse({
            'status': 'success',
            'liked': liked,
            'likes_count': comment.likes.count(),
            'comment_id': comment_id
        })
        
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)

@login_required
def delete_comment(request, comment_id):
    """
    View to handle comment deletion
    """
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check if user has permission to delete this comment
    if request.user != comment.author:
        return JsonResponse({
            'status': 'error',
            'message': 'You do not have permission to delete this comment.'
        }, status=403)
    
    if request.method == 'POST':
        post_slug = comment.post.slug
        
        # Delete the comment
        comment.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Comment deleted successfully.',
                'comment_id': comment_id
            })
        
        messages.success(request, 'Your comment has been deleted.')
        return redirect('main:post_detail', slug=post_slug)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    }, status=400)

class UserPostListView(ListView):
    model = Post
    template_name = 'main/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(
            author=user,
            status='published'
        ).order_by('-created_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        context['profile_user'] = user
        context['is_owner'] = user == self.request.user
        return context
    
@login_required
def like_post(request, slug):
    if request.method == 'POST':
        post = get_object_or_404(Post, slug=slug)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True

        return JsonResponse({
            'status': 'success',
            'liked': liked,
            'like_count': post.total_likes()
        })

    return JsonResponse({'status': 'error'}, status=400)