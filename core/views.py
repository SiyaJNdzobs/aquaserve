from django.shortcuts import render, redirect
from django.contrib import messages
import random

# SESSION STORAGE
users = {}
requests_db = {}

balances = {
    "user1": 500,
    "user2": 200,
    "user3": 300,
    "user4": 800,
    "user5": 1500,
}

def home(request):
    return render(request, 'core/home.html')

# AUTH
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        request.session['user'] = username
        messages.success(request, "Login successful")
        return redirect('home')
    return render(request, 'core/login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        users[username] = True
        request.session['user'] = username
        return redirect('home')
    return render(request, 'core/register.html')

# REPORT ISSUE
def report_issue(request):
    ref = None
    if request.method == 'POST':
        issue = request.POST.get('issue')
        location = request.POST.get('location')

        if not issue or not location:
            messages.error(request, "All fields required")
        else:
            ref = "REF" + str(random.randint(1000, 9999))
            requests_db[ref] = "Request Received"
            messages.success(request, f"Issue submitted! Reference: {ref}")

    return render(request, 'core/report.html', {'ref': ref})

# TRACK
def track_request(request):
    status = None
    if request.method == 'POST':
        ref = request.POST.get('ref')
        status = requests_db.get(ref, "Reference not found")
    return render(request, 'core/track.html', {'status': status})

# ACCOUNT
def account(request):
    user = request.session.get('user', 'user1')
    balance = balances.get(user, 100)
    return render(request, 'core/account.html', {'balance': balance})

# PAYMENT
def payment(request):
    user = request.session.get('user', 'user1')
    balance = balances.get(user, 100)

    if request.method == 'POST':
        amount = int(request.POST.get('amount'))

        if amount <= balance:
            balance -= amount
            balances[user] = balance
            messages.success(request, "Payment successful")
        else:
            messages.error(request, "Insufficient balance")

    return render(request, 'core/payment.html', {'balance': balance})

def about(request):
    return render(request, 'core/about.html')