from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from MainApp.models import Snippet
from django.core.exceptions import ObjectDoesNotExist
from MainApp.forms import CommentForm,SnippetForm, UserRegistrationForm
from django.contrib import auth
from django.contrib.auth.decorators import login_required


def index_page(request):
    context = {'pagename': 'PythonBin'}
    return render(request, 'pages/index.html', context)


@login_required
def my_snippets(request):
    snippets = Snippet.objects.filter(user=request.user)
    context = {
        'pagename': 'Мои сниппеты',
        'snippets': snippets,
        }
    return render(request, 'pages/view_snippets.html', context)

@login_required(login_url="home")
def add_snippet_page(request):
    # Создаем пустую форму при запросе GET
    if request.method == "GET":
        form = SnippetForm()
        context = {
            'pagename': 'Добавление нового сниппета',
            'form': form,
            }
        return render(request, 'pages/add_snippet.html', context)

    # Получаем данные из формы и на их основе создаем новый сниппет в БД
    if request.method == "POST":
        form = SnippetForm(request.POST)
        if form.is_valid():
            snippet = form.save(commit=False)
            if request.user.is_authenticated:
                snippet.user = request.user
                snippet.save()
            # GET /snippets/list
            return redirect("snippets-list") # URL для списка сниппетов
        return render(request,'pages/add_snippet.html', {'form': form})
    

def snippets_page(request):
    snippets = Snippet.objects.filter(public=True)
    context = {
        'pagename': 'Просмотр сниппетов',
        'snippets': snippets,
        }
    return render(request, 'pages/view_snippets.html', context)


def snippet_detail(request, snippet_id):
    context = {'pagename': 'Просмотр сниппета'}
    try:
        snippet = Snippet.objects.get(id=snippet_id)
    except ObjectDoesNotExist:
        return render(request, "pages/errors.html", context | {"error": f"Snippet with id={snippet_id} not found"})
    else:
        comments_form = CommentForm()
        context["snippet"] = snippet
        context["type"] = "view"
        context["comments_form"] = comments_form
        return render(request, 'pages/snippet_detail.html', context)

@login_required
def snippet_edit(request, snippet_id):
    # pass
    context = {'pagename': 'Редактирование сниппета'}
    snippet = get_object_or_404(Snippet.objects.filter(user=request.user))
    # 1 вариант - использование SnippetForm
    if request.method == "GET":
        form = SnippetForm(instance=snippet)
        return render(request, "pages/add_snippet.html", context | {"form": form})
    
    # 2 вариант
    # Получаем страница с данными сниппета
    # if request.method == "GET":
    #     context.update({
    #         "snippet": snippet,
    #         "type": "edit",
    #         })
    #     return render(request, 'pages/snippet_detail.html', context)
    
    # Получаем данные из формы и на их основе обновляем данный сниппет в БД
    if request.method == "POST":
        data_form = request.POST
        snippet.name = data_form["name"]
        snippet.code = data_form["code"]
        snippet.public = data_form.get("public", False)
        snippet.save()
        return redirect("snippets-list") # GET /snippets/list


def snippet_delete(request, snippet_id):
    if request.method == "GET" or request.method == "POST":
        snippet = get_object_or_404(Snippet.objects.filter(user=request.user))
        snippet.delete()
    return redirect("snippets-list")

def login(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        # print("username =", username)
        # print("password =", password)
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
        else:
            # Return error message
            context = {
                "pagename": "PythonBin",
                "errors": ["wrong username or password"],
            }
            return render(request, "pages/index.html", context)
    return redirect('home')
def logout(request):
    auth.logout(request)
    return redirect('home')

def create_user(request):
    context = {"pagename": "Регистрация нового пользователя"}
    # Создаем новую форму при запросе GET
    if request.method == "GET":
        form = UserRegistrationForm()
    
    # Получаем данные из формы и на их основе создаем нового пользователя и сохраняем его в БД
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
        
    context['form'] = form
    return render(request, "pages/registration.html", context)

def comments_add(request):
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            snippet_id = request.POST.get("snippet_id")
            snippet = Snippet.objects.get(id=snippet_id)
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.snippet = snippet
            comment.save()
            return redirect('snippet-detail', snippet_id=snippet.id)