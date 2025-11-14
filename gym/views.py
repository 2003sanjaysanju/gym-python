from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from datetime import date, timedelta
from .models import Member, Payment
from .forms import MemberForm, PaymentForm


def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username == 'admin' and password == 'power25':
            # Create or get a user for admin
            from django.contrib.auth.models import User
            user, created = User.objects.get_or_create(
                username='admin',
                defaults={'is_staff': True, 'is_superuser': True}
            )
            if created:
                user.set_password('power25')
                user.save()
            
            user = authenticate(request, username='admin', password='power25')
            if user:
                login(request, user)
                return redirect('dashboard')
        
        messages.error(request, 'Invalid username or password.')
    
    return render(request, 'gym/login.html')


@login_required
def custom_logout(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    members = Member.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        members = members.filter(
            Q(name__icontains=search_query) | Q(phone__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', 'all')
    today = date.today()
    due_soon_date = today + timedelta(days=3)
    
    if status_filter == 'overdue':
        members = members.filter(next_due_date__lt=today)
    elif status_filter == 'due-soon':
        members = members.filter(next_due_date__gte=today, next_due_date__lte=due_soon_date)
    
    # Statistics
    total_members = Member.objects.count()
    overdue_count = Member.objects.filter(next_due_date__lt=today).count()
    due_soon_count = Member.objects.filter(
        next_due_date__gte=today,
        next_due_date__lte=due_soon_date
    ).count()
    
    context = {
        'members': members,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_members': total_members,
        'overdue_count': overdue_count,
        'due_soon_count': due_soon_count,
    }
    
    return render(request, 'gym/dashboard.html', context)


@login_required
def add_member(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            try:
                member = form.save()
                messages.success(request, f'Member {member.name} added successfully!')
                return redirect('dashboard')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = MemberForm()
    
    return render(request, 'gym/add_member.html', {'form': form})


@login_required
def record_payment(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, member=member)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.member = member
            payment.save()
            messages.success(request, f'Payment recorded for {member.name}. Next due date: {member.next_due_date}')
            return redirect('dashboard')
    else:
        form = PaymentForm(member=member)
    
    return render(request, 'gym/record_payment.html', {'form': form, 'member': member})


@login_required
def delete_member(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    
    if request.method == 'POST':
        member_name = member.name
        member.delete()
        messages.success(request, f'Member {member_name} deleted successfully.')
        return redirect('dashboard')
    
    return render(request, 'gym/delete_member.html', {'member': member})

