from django.shortcuts import render, render_to_response, RequestContext
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.core.context_processors import csrf
from forms import MyRegistrationForm

# Create your views here.

def home(request):
    return render_to_response("base.html",locals(), context_instance=RequestContext(request))

def signup(request):
    if request.method == 'POST':
        form = MyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/signup_success/")
     
    args = {}
    args.update(csrf(request))
    
    args['form'] = MyRegistrationForm()
    
    return render_to_response("signup.html", args)

def signup_success(request):
    return render_to_response("signup_success.html")
    

def signin(request):
    c = {}
    c.update(csrf(request))
    return render_to_response("signin.html", c)

def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    
    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect("/dashboard/")
    else:
        return HttpResponseRedirect("/invalid/")

def invalid_signin(request):
    return render_to_response("invalid_signin.html")

