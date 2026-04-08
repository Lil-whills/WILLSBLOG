from django.shortcuts import get_object_or_404, render
from .models import Blog

# Create your views here.

def index(request):
    return render(request, 'index.html')

def allblogs(request):
    blogs = Blog.objects.filter(status='published').order_by('-created_at')
    return render(request, 'allblogs.html', {'blogs': blogs})

def dashboard(request):
    return render(request, 'dashboard.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def payment(request):
    return render(request, 'payment.html')

def blogdetails(request, id):
      blog = get_object_or_404(Blog, id=id)
      return render(request, 'blogdetails.html', {'blog': blog})


