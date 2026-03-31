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
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_data = users.get(username)
        if user_data and user_data.get('password') == password:
            request.session['user'] = username
            messages.success(request, "Login successful")
            return redirect('home')
        error = "Invalid username or password"

    return render(request, 'core/login.html', {'error': error})

def register(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        home_address = request.POST.get('home_address')
        cell_number = request.POST.get('cell_number')

        if not all([username, password, email, home_address, cell_number]):
            error = "Please fill all required fields."
        elif username in users:
            error = "Username already exists"
        else:
            users[username] = {
                'password': password,
                'email': email,
                'home_address': home_address,
                'cell_number': cell_number,
            }
            request.session['user'] = username
            messages.success(request, "Registration successful")
            return redirect('home')

    return render(request, 'core/register.html', {'error': error})

# REPORT ISSUE
def report_issue(request):
    user = request.session.get('user', 'Guest')
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

    return render(request, 'core/report.html', {'ref': ref, 'username': user})

# TRACK
def track_request(request):
    user = request.session.get('user', 'Guest')
    status = None
    if request.method == 'POST':
        ref = request.POST.get('ref')
        status = requests_db.get(ref, "Reference not found")
    return render(request, 'core/track.html', {'status': status, 'username': user})

# ABOUT
def about(request):
    user = request.session.get('user', 'Guest')
    return render(request, 'core/about.html', {'username': user})

# ACCOUNT
def account(request):
    user = request.session.get('user')
    if user is None:
        return redirect('login')

    balance = balances.get(user, 100)
    profile = users.get(user, {})

    return render(request, 'core/account.html', {
        'balance': balance,
        'username': user,
        'email': profile.get('email', 'Not set'),
        'home_address': profile.get('home_address', 'Not set'),
        'cell_number': profile.get('cell_number', 'Not set'),
    })

# PAYMENT
def payment(request):
    user = request.session.get('user')
    if user is None:
        return redirect('login')

    balance = balances.get(user, 100)
    confirmed = False

    if request.method == 'POST':
        confirm = request.POST.get('confirm_balance') == 'on'
        amount_raw = request.POST.get('amount')

        if not confirm:
            messages.error(request, "Please confirm your balance before paying.")
        elif not amount_raw or int(amount_raw) <= 0:
            messages.error(request, "Enter a valid amount.")
        else:
            amount = int(amount_raw)
            if amount <= balance:
                balance -= amount
                balances[user] = balance
                messages.success(request, f"Payment of R{amount} successful")
                confirmed = True
            else:
                messages.error(request, "Insufficient balance")

    return render(request, 'core/payment.html', {
        'balance': balance,
        'username': user,
        'email': users.get(user, {}).get('email', ''),
        'home_address': users.get(user, {}).get('home_address', ''),
        'cell_number': users.get(user, {}).get('cell_number', ''),
    })

def about(request):
    return render(request, 'core/about.html')