from django.shortcuts import render
from app.forms import *
from django.http import HttpResponse,HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from app.models import *
import random
# Create your views here.


def regestration(request):
    eufo=userForm()
    epfo=ProfileForm()
    d={'eufo':eufo,'epfo':epfo}
    if request.method=='POST' and request.FILES:
        nmufdo=userForm(request.POST)
        nmupdo=ProfileForm(request.POST,request.FILES)
        if nmufdo.is_valid() and nmupdo.is_valid():
            mufdo=nmufdo.save(commit=False)
            pw=nmufdo.cleaned_data['password']
            mufdo.set_password(pw)
            mufdo.save()
            mupdo=nmupdo.save(commit=False)
            mupdo.username=mufdo
            mupdo.save()
            send_mail('registration','thank you for registration ','reddydivya462@gmail.com',[mufdo.email],fail_silently=False)
            return HttpResponse('registration completed')
        else:
            return HttpResponse('invalid ')
        




    return render(request,'regestration.html',d)

def home(request):
    if request.session.get('username'):
        username=request.session.get('username')
        d={'username':username}
        return render(request,'home.html',d)
    
    return render(request,'home.html')

def user_login(request):
    if request.method=="POST":
        username=request.POST['un']
        password=request.POST['pw']
        AUO=authenticate(username=username,password=password)
        if AUO and AUO.is_active:
            login(request,AUO)
            request.session['username']=username
            return HttpResponseRedirect(reverse('home'))
        else:
            return HttpResponse('invalid credentails')


    return render(request,'user_login.html')

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

@login_required
def display_data(request):
    username=request.session['username']
    UO=User.objects.get(username=username)
    PO=profile.objects.get(username=UO)
    d={'UO':UO,'PO':PO}
    return render(request,'display_data.html',d)

@login_required
def changepassword(request):
    if request.method == 'POST':
        username = request.session['username']
        UO = User.objects.get(username=username)
        
        # Generate OTP
        otp = random.randint(100000, 999999)
        request.session['otp'] = otp
        request.session['username_for_otp'] = username
        request.session['action'] = 'change_password'
        
        # Send OTP to user's email
        send_mail(
            'Your OTP for Password Change',
            f'Your OTP for password change is {otp}.',
            'from@example.com',
            [UO.email],
            fail_silently=False,
        )
        
        # Redirect to OTP verification page
        return HttpResponseRedirect(reverse('verify_otp'))
    
    return render(request, 'changepassword.html')


def reset_password(request):
    if request.method == 'POST':
        username = request.POST['un']
        LUO = User.objects.filter(username=username)
        
        if LUO:
            UO = LUO[0]
            
            # Generate OTP
            otp = random.randint(100000, 999999)
            request.session['otp'] = otp
            request.session['username_for_otp'] = username
            request.session['action'] = 'reset_password'
            
            # Send OTP to user's email
            send_mail(
                'Your OTP for Password Reset',
                f'Your OTP for password reset is {otp}.',
                'from@example.com',
                [UO.email],
                fail_silently=False,
            )
            
            # Redirect to OTP verification page
            return HttpResponseRedirect(reverse('verify_otp'))
        else:
            return HttpResponse('User is not present')

    return render(request, 'reset_password.html')

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        username = request.session.get('username_for_otp')
        action = request.session.get('action')
        
        if str(entered_otp) == str(session_otp):
            # OTP is correct, proceed with the action
            new_password = request.POST.get('new_password')
            UO = User.objects.get(username=username)
            UO.set_password(new_password)
            UO.save()
            
            # Clear session data
            del request.session['otp']
            del request.session['username_for_otp']
            del request.session['action']
            
            if action == 'change_password':
                return HttpResponse('Password has been changed successfully.')
            elif action == 'reset_password':
                return HttpResponse('Password has been reset successfully.')
        else:
            # OTP is incorrect
            return render(request, 'verify_otp.html', {'error': 'Invalid OTP'})

    return render(request, 'verify_otp.html')
