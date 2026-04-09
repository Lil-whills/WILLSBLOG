from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from .models import Blog
from .forms import BlogForm

# Create your views here.

def index(request):
    blogs = Blog.objects.filter(status='published').order_by('-created_at')[:3]

    technology_blogs = Blog.objects.filter(category='technology', status='published').order_by('-created_at')[:3]

    health_blogs = Blog.objects.filter(category='health', status='published').order_by('-created_at')[:3]

    economics_blogs = Blog.objects.filter(category='economics', status='published').order_by('-created_at')[:3]

    lifestyle_blogs = Blog.objects.filter(category='lifestyle', status='published').order_by('-created_at')[:3]

    return render(request, 'index.html', {'blogs': blogs, 'technology_blogs': technology_blogs, 'health_blogs': health_blogs, 'economics_blogs': economics_blogs, 'lifestyle_blogs': lifestyle_blogs})

def allblogs(request):
    blogs = Blog.objects.filter(status='published')
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    is_premium = request.GET.get('is_premium', '').strip().lower()
    sort = request.GET.get('sort', 'newest').strip().lower()

    if query:
        blogs = blogs.filter(
            Q(title__icontains=query)
            | Q(excerpt__icontains=query)
            | Q(author__icontains=query)
        )

    if category:
        blogs = blogs.filter(category=category)

    if is_premium == 'true':
        blogs = blogs.filter(is_premium=True)
    elif is_premium == 'false':
        blogs = blogs.filter(is_premium=False)

    if sort == 'oldest':
        blogs = blogs.order_by('created_at')
    elif sort == 'price_low_high':
        blogs = blogs.order_by('price', '-created_at')
    elif sort == 'price_high_low':
        blogs = blogs.order_by('-price', '-created_at')
    else:
        blogs = blogs.order_by('-created_at')


    context = {
        'blogs': blogs,
        'query': query,
        'category': category,
        'is_premium': is_premium,
        'sort': sort,
    }

    return render(request, 'allblogs.html', context)

def dashboard(request):
    totalblogs = Blog.objects.count()
    publishedcount = Blog.objects.filter(status='published').count()
    draftcount = Blog.objects.filter(status='draft').count()
    premiumcount = Blog.objects.filter(is_premium=True).count()

    blogs = Blog.objects.all()

    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    is_premium = request.GET.get('is_premium', '').strip().lower()
    status = request.GET.get('status', '').strip().lower()
    sort = request.GET.get('sort', 'newest').strip().lower()

    if query:
        blogs = blogs.filter(
            Q(title__icontains=query)
            | Q(excerpt__icontains=query)
            | Q(author__icontains=query)
        )

    if category:
        blogs = blogs.filter(category=category)

    if is_premium == 'true':
        blogs = blogs.filter(is_premium=True)
    elif is_premium == 'false':
        blogs = blogs.filter(is_premium=False)

    if status in ['published', 'draft']:
        blogs = blogs.filter(status=status)

    if sort == 'oldest':
        blogs = blogs.order_by('created_at')
    elif sort == 'price_low_high':
        blogs = blogs.order_by('price', '-created_at')
    elif sort == 'price_high_low':
        blogs = blogs.order_by('-price', '-created_at')
    else:
        blogs = blogs.order_by('-created_at')

    context = {
        'totalblogs': totalblogs,
        'publishedcount': publishedcount,
        'draftcount': draftcount,
        'premiumcount': premiumcount,
        'blogs': blogs,
        'query': query,
        'category': category,
        'is_premium': is_premium,
        'status': status,
        'sort': sort,
    }

    return render(request, 'dashboard.html', context)

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def payment(request):
    return render(request, 'payment.html')

def blogdetails(request, id):
      blog = get_object_or_404(Blog, id=id)
      return render(request, 'blogdetails.html', {'blog': blog})

def postblog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = BlogForm()
    return render(request, 'postblog.html', {'form': form, 'blog': None})

def editblog(request, id):
    blog = get_object_or_404(Blog, id=id)
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = BlogForm(instance=blog)
    return render(request, 'postblog.html', {'form': form, 'blog': blog})

def deleteblog(request, id):
    blog = get_object_or_404(Blog, id=id)
    if request.method == 'POST':
        blog.delete()
        return redirect('dashboard')
    return render(request, 'deleteblog.html', {'blog': blog})

