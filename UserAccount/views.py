from django.shortcuts import render,redirect
from UserAccount.form import *
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
import smtplib
from django.db import models
from django import template
from django.template.loader import get_template
from UserAccount.form import SignUpForm
from UserAccount.models import Profile,Book
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.conf import settings
from django.shortcuts import redirect

from django.http import JsonResponse
from django.core import serializers
from django.core.mail import send_mail, BadHeaderError
import pprint
import datetime
import json
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth import update_session_auth_hash



def index(request):
    return render(request, 'index.html')

def home(request):
    return render(request, 'UserAccount/home.html')

def writetous(request):
    return render(request, 'UserAccount/contactus.html')

def search_view(request):
    return render(request, 'UserAccount/search.html')

def login_user(request):
    if request.method == "POST":
        mail = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=mail, password=password)
        if user is not None:
            if user.is_active:
                login(request,user)
                request.session['id'] = user.id

                return render(request, 'UserAccount/home.html')
            else:
                return HttpResponse("Inactive User")
        else:
            return render(request, 'UserAccount/login.html',{'error_message':"Invalid user Credentials"})
    return render(request, 'UserAccount/login.html')

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST or None)
        if form.is_valid():
            username = request.POST.get('username')
            email =request.POST.get('email')
            password = request.POST.get('password1')
            firstname=request.POST.get('first_name')
            lastname=request.POST.get('last_name')
            phone_number=request.POST.get('phone_number')
            year=request.POST.get('year')
            branch=request.POST.get('branch')
            course=request.POST.get('course')


            p1=User(username=username,email=email,password=password,first_name=firstname,last_name=lastname)
            p1.set_password(password)
            p1.save()
            newUser=Profile(user=p1,phone_number=phone_number,year=year,branch=branch,course=course)
            newUser.save()
            subject = 'Registration Successful- Share And Care'

            message = 'Greetings! You have been successfully registered on Share And Care - An Online Student Help Platform. Now you can easily find second hand books online without going anywhere by just visiting our website. '
            from_email = 'shareadcare@gmail.com'
            email_msg="Subject: {} \n\n{}".format(subject,message)
            smtp = smtplib.SMTP('smtp.gmail.com',587)
            smtp.starttls()
            smtp.login('shareadcare@gmail.com','mirsajsob2017')
            smtp.sendmail('shareadcare@gmail.com',email,email_msg)
            smtp.quit()
            
            return render(request, 'UserAccount/login.html')
        else:
            form = SignUpForm()
            context={
            'form':form,
            'error_message':"Invalid User details"
            }
            return render(request, 'UserAccount/register.html',context)

    form = SignUpForm()
    return render(request, 'UserAccount/register.html',{'form': form})

def search_book(request):
    if not request.user.is_authenticated:
        return render(request, 'UserAccount/login.html')
    if request.method == "POST":
        q = request.POST['query']
        option = request.POST['option']

        if( q is None or q==""):
            return render(request, 'UserAccount/notfound.html')
        if(option=='Name'):
            try:
                queryset = Book.objects.filter(book_title__icontains=q,).filter(b_type='Sell')
            except Book.DoesNotExist:
                return HttpResponse("No results found")
            context = {
            'queryset':queryset,
            'q':q,
            }
            return render(request, 'UserAccount/search_results.html', context)
        elif(option=='Subject'):
            try:
                queryset=Book.objects.filter(subject__icontains=q).filter(b_type='Sell')
            except Book.DoesNotExist:
                return HttpResponse("No results found")
            context = {
            'queryset':queryset,
            'q':q,
            }
            return render(request, 'UserAccount/search_results.html', context)
            

def new_book_post(request):
    if not request.user.is_authenticated:
        return render(request, 'UserAccount/login.html')
    if request.method=='POST':
        form=BookPostForm(request.POST,request.FILES)
        if form.is_valid():
            book = Book()

            user = User.objects.get(id=request.session['id'])
            profile = Profile.objects.get(user=user)
            book.user_book=profile
            book.book_pic = form.cleaned_data['image']
            book.book_title = request.POST["book_title"]
            book.subject = request.POST["subject"]
            book.author = request.POST["author"]
            book.pub_year = request.POST["pub_year"]
            book.pub_name = request.POST["pub_name"]
            book.book_cond = request.POST["book_cond"]
            book.negotiable = request.POST["negotiable"]
            book.price = request.POST["price"]
            book.b_type = 'Sell'

            book.save()
            return HttpResponse('New book post has been added')
        else:
            return HttpResponse(form.errors)
    

    BookForm =BookPostForm(None)
    return render(request, 'UserAccount/bookform.html', {'form' :BookForm})
	
def donate_book_post(request):
    if not request.user.is_authenticated:
        return render(request, 'UserAccount/login.html')
    if request.method=='POST':
        form=BookDonateForm(request.POST,request.FILES)
        if form.is_valid():
            book = Book()

            user = User.objects.get(id=request.session['id'])
            profile = Profile.objects.get(user=user)
            book.user_book=profile
            book.book_pic = form.cleaned_data['image']
            book.book_title = request.POST["book_title"]
            book.subject = request.POST["subject"]
            book.author = request.POST["author"]
            book.pub_year = request.POST["pub_year"]
            book.pub_name = request.POST["pub_name"]
            book.book_cond = request.POST["book_cond"]
            book.b_type = 'Donate'
            book.negotiable = 'No'
            book.price = 0.0
            book.save()
            return HttpResponse('New book for donation has been added')
        else:
            return HttpResponse(form.errors)
    

    donateBookForm =BookDonateForm(None)
    return render(request, 'UserAccount/donatebookform.html', {'form' :donateBookForm})


	
def counselling_post(request):
    if request.method=='POST':
        form=CounsellingForm(request.POST,request.FILES)
        if form.is_valid():
            counselling = Counselling()
            #user = User.objects.get(id=request.session['id'])
            counselling.name1 = request.POST["name1"]
            counselling.email = request.POST["email"]
            counselling.college = request.POST["college"]
            counselling.phone_number = request.POST["phone_number"]
            counselling.branch = request.POST["branch"]
            counselling.c_choices = request.POST["c_choices"]
            counselling.description = request.POST["description"]
            counselling.status_c = request.POST["status_c"]
   
            counselling.save()
            return HttpResponse('New counselling request has been saved')
        else:
            return HttpResponse(form.errors)
    

    counsellingForm =CounsellingForm(None)
    return render(request, 'UserAccount/counsellingform.html', {'form' :counsellingForm}) #to chancge

def change_password(request):
    message = " "
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if not request.user.is_authenticated:
            return redirect('login_user')
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('view_profile')
        else:
            message = "Either Old Password Incorrect or New Passwords do not match"
            context={
            'form':form,
            'error_message':message
            }
            return render(request,'UserAccount/change_password.html',context)
    form = PasswordChangeForm(request.user, request.POST)
    return render(request, 'UserAccount/change_password.html',{'form': form})


def view_profile(request):
    if request.user.is_authenticated:
        user = User.objects.get(id=request.session['id'])
        userprofile = Profile.objects.get(user=user)
        context = {
        'userprofile':userprofile,
                }
        return render(request, 'UserAccount/view_profile.html', context)
    else:
        return render(request, 'UserAccount/login.html')



def recent(request):
    results=Book.objects.all().order_by('-created_time')[:5]
    #results=Book.objects.all()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(results)
    #print results
    posts_serialized = serializers.serialize('json', results)
    #pp.pprint(posts_serialized)
    return JsonResponse(posts_serialized, safe=False) 

def allposts(request):
    #results=Book.objects.all().order_by('-created_time')[:5]
    results=Book.objects.all()
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(results)
    posts_serialized = serializers.serialize('json', results)
    #pp.pprint(posts_serialized)
    return JsonResponse(posts_serialized, safe=False) 


def bookdetail(request):

    if request.method == "POST":
        #name = request.GET.get('name', '')
        pk=request.POST.get('pk', '')
        obj = Book.objects.get(id=pk)
        #user = User.objects.get(id=)
        #userprofile = Profile.objects.get(id=obj.user_book)
        #print json.dumps(userprofile)
        book= serializers.serialize('json', [obj])
        struct = json.loads(book)
        data = json.dumps(struct[0])
        #print data
        return JsonResponse(data, safe=False)
       

