from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


# Create your views here.




def login_account(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)

            if user.groups.filter(name ='instructor').exists():
                return redirect('instructor_home')
            elif user.groups.filter(name ='registrar').exists():
                return redirect('admin_dashboard')
            elif user.groups.filter(name ='guardian').exists():
                return redirect('guardian_home')
        
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'authentication/login.html')

        
def accounts_login(request):
    return render(request, 'authentication/login.html')
    
def register_page(request):
    return render(request, 'authentication/register.html')

def logout_account(request):
    logout(request)
    messages.success(request, 'Successfully logged out')
    return redirect('login-account')