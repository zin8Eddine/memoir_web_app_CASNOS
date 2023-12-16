from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from  .models import AssurerMalade


@login_required(login_url='login')
def Home(request):
    user_data = AssurerMalade.objects.filter(user=request.user).first()

    if user_data is not None:
        duree_consomations = user_data.dureeconsomations_set.all()
        last_duree = duree_consomations.last()
    else:
        duree_consomations = []
        last_duree = None

    selected_duration = request.GET.get('duration_id')
    selected_duree = None

    if selected_duration:
        selected_duree = duree_consomations.filter(id=selected_duration).first()
    context = {
        'title': 'Home',
        'user_data': user_data,
        'duree_consomations': duree_consomations,
        'selected_duree': selected_duree or last_duree,

    }
    return render(request, 'home.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('Home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Login successful.')
            return redirect('Home')
        else:
            messages.error(request, 'Login failed. Please check your credentials.')

    else:
        form = AuthenticationForm()

    context = {
        'title': 'Login',
        'form': form,
    }

    return render(request, 'login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

