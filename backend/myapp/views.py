from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import BlogForm
from .models import Blog


BLOG_APP_LABEL = Blog._meta.app_label
VIEW_BLOG_PERMISSION = f"{BLOG_APP_LABEL}.view_blog"
ADD_BLOG_PERMISSION = f"{BLOG_APP_LABEL}.add_blog"
CHANGE_BLOG_PERMISSION = f"{BLOG_APP_LABEL}.change_blog"
DELETE_BLOG_PERMISSION = f"{BLOG_APP_LABEL}.delete_blog"


def can_access_dashboard(user):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return (
        user.has_perm(VIEW_BLOG_PERMISSION)
        or user.has_perm(ADD_BLOG_PERMISSION)
        or user.has_perm(CHANGE_BLOG_PERMISSION)
        or user.has_perm(DELETE_BLOG_PERMISSION)
    )


def apply_blog_filters(queryset, request, include_status=False):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    is_premium = request.GET.get("is_premium", "").strip().lower()
    status = request.GET.get("status", "").strip().lower()
    sort = request.GET.get("sort", "newest").strip().lower()

    if query:
        queryset = queryset.filter(
            Q(title__icontains=query)
            | Q(excerpt__icontains=query)
            | Q(author__icontains=query)
        )

    if category:
        queryset = queryset.filter(category=category)

    if is_premium == "true":
        queryset = queryset.filter(is_premium=True)
    elif is_premium == "false":
        queryset = queryset.filter(is_premium=False)

    if include_status and status in ["published", "draft"]:
        queryset = queryset.filter(status=status)

    if sort == "oldest":
        queryset = queryset.order_by("created_at")
    elif sort == "price_low_high":
        queryset = queryset.order_by("price", "-created_at")
    elif sort == "price_high_low":
        queryset = queryset.order_by("-price", "-created_at")
    else:
        queryset = queryset.order_by("-created_at")

    filters = {
        "query": query,
        "category": category,
        "is_premium": is_premium,
        "sort": sort,
    }

    if include_status:
        filters["status"] = status

    return queryset, filters


def index(request):
    blogs = Blog.objects.filter(status="published").order_by("-created_at")[:3]
    technology_blogs = Blog.objects.filter(
        category="technology", status="published"
    ).order_by("-created_at")[:3]
    health_blogs = Blog.objects.filter(
        category="health", status="published"
    ).order_by("-created_at")[:3]
    economics_blogs = Blog.objects.filter(
        category="economics", status="published"
    ).order_by("-created_at")[:3]
    lifestyle_blogs = Blog.objects.filter(
        category="lifestyle", status="published"
    ).order_by("-created_at")[:3]

    context = {
        "blogs": blogs,
        "technology_blogs": technology_blogs,
        "health_blogs": health_blogs,
        "economics_blogs": economics_blogs,
        "lifestyle_blogs": lifestyle_blogs,
    }
    return render(request, "index.html", context)


def allblogs(request):
    blogs = Blog.objects.filter(status="published")
    blogs, filters = apply_blog_filters(blogs, request)

    context = {
        "blogs": blogs,
        **filters,
    }
    return render(request, "allblogs.html", context)


@login_required
def dashboard(request):
    if not can_access_dashboard(request.user):
        raise PermissionDenied

    blogs = Blog.objects.all()
    blogs, filters = apply_blog_filters(blogs, request, include_status=True)

    context = {
        "totalblogs": Blog.objects.count(),
        "publishedcount": Blog.objects.filter(status="published").count(),
        "draftcount": Blog.objects.filter(status="draft").count(),
        "premiumcount": Blog.objects.filter(is_premium=True).count(),
        "blogs": blogs,
        "can_add_blog": request.user.is_superuser or request.user.has_perm(ADD_BLOG_PERMISSION),
        "can_change_blog": request.user.is_superuser or request.user.has_perm(CHANGE_BLOG_PERMISSION),
        "can_delete_blog": request.user.is_superuser or request.user.has_perm(DELETE_BLOG_PERMISSION),
        **filters,
    }
    return render(request, "dashboard.html", context)


def login(request):
    raw_next_url = request.GET.get("next") or request.POST.get("next") or ""
    next_url = ""
    if raw_next_url and url_has_allowed_host_and_scheme(
        raw_next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = raw_next_url

    if request.user.is_authenticated:
        if can_access_dashboard(request.user):
            return redirect("dashboard")
        return redirect("index")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)

            if next_url:
                return redirect(next_url)

            if can_access_dashboard(user):
                return redirect("dashboard")

            return redirect("index")

        messages.error(request, "Invalid username or password.")

    return render(request, "login.html", {"next": next_url})


def register(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not all([username, first_name, last_name, email, password, confirm_password]):
            messages.error(request, "All fields are required.")
            return render(request, "register.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "register.html")

        User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )

        messages.success(request, "Account created successfully. Please log in.")
        return redirect("login")

    return render(request, "register.html")


@login_required
def logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("index")


@login_required
def payment(request):
    return render(request, "payment.html")


def blogdetails(request, id):
    blog = get_object_or_404(Blog, id=id)

    if blog.status != "published" and not can_access_dashboard(request.user):
        raise Http404("Blog not found.")

    return render(request, "blogdetails.html", {"blog": blog})


@login_required
@permission_required(ADD_BLOG_PERMISSION, raise_exception=True)
def postblog(request):
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog posted successfully.")
            return redirect("dashboard")
    else:
        form = BlogForm()

    return render(request, "postblog.html", {"form": form, "blog": None})


@login_required
@permission_required(CHANGE_BLOG_PERMISSION, raise_exception=True)
def editblog(request, id):
    blog = get_object_or_404(Blog, id=id)

    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog updated successfully.")
            return redirect("dashboard")
    else:
        form = BlogForm(instance=blog)

    return render(request, "postblog.html", {"form": form, "blog": blog})


@login_required
@permission_required(DELETE_BLOG_PERMISSION, raise_exception=True)
def deleteblog(request, id):
    blog = get_object_or_404(Blog, id=id)

    if request.method == "POST":
        blog.delete()
        messages.success(request, "Blog deleted successfully.")
        return redirect("dashboard")

    return render(request, "deleteblog.html", {"blog": blog})