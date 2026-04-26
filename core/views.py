from django.shortcuts import render, redirect
from django.contrib import messages
import random

# SESSION STORAGE
users = {}
requests_db = {}
disputes_db = {}

balances = {
    "user1": 500,
    "user2": 200,
    "user3": 300,
    "user4": 800,
    "user5": 1500,
}

def home(request):
    user = request.session.get('user')
    active_requests = []
    
    if user:
        # Get user's active requests (not resolved/closed)
        for ref, data in requests_db.items():
            if isinstance(data, dict) and data.get('user') == user:
                status = data.get('status', '').lower()
                if status not in ['resolved', 'closed']:
                    active_requests.append({
                        'ref': ref,
                        'issue': data.get('issue', 'Unknown'),
                        'status': data.get('status', 'Unknown'),
                    })
        
        # Get active disputes
        for ref, data in disputes_db.items():
            if data.get('user') == user:
                status = data.get('status', '').lower()
                if status not in ['resolved', 'closed']:
                    active_requests.append({
                        'ref': ref,
                        'issue': f"Balance Dispute - {data.get('invoice_ref', '')}",
                        'status': data.get('status', 'Unknown'),
                    })
    
    return render(request, 'core/home.html', {
        'active_requests': active_requests,
        'username': user
    })

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
    user = request.session.get('user')
    if user is None:
        return redirect('login')

    ref = None
    dispute_ref = None
    profile = users.get(user, {})
    balance = balances.get(user, 100)

    if request.method == 'POST':
        # Check if this is a dispute balance submission
        if 'invoice_ref' in request.POST:
            invoice_ref = request.POST.get('invoice_ref', '').strip()
            invoice_balance = request.POST.get('invoice_balance', '').strip()

            if not invoice_ref or not invoice_balance:
                messages.error(request, "All dispute fields are required")
            else:
                try:
                    invoice_balance = float(invoice_balance)
                    dispute_ref = "DSP" + str(random.randint(10000, 99999))
                    disputes_db[dispute_ref] = {
                        'user': user,
                        'invoice_ref': invoice_ref,
                        'invoice_balance': invoice_balance,
                        'status': 'Dispute Received'
                    }
                    messages.success(request, f"Balance dispute submitted! Reference: {dispute_ref}")
                except ValueError:
                    messages.error(request, "Please enter a valid balance amount")
        else:
            # Regular issue report
            issue = request.POST.get('issue')
            location = request.POST.get('location')
            description = request.POST.get('description', '')

            if not issue or not location:
                messages.error(request, "All fields required")
            else:
                ref = "REF" + str(random.randint(1000, 9999))
                requests_db[ref] = {
                    'user': user,
                    'issue': issue,
                    'location': location,
                    'description': description,
                    'status': 'Request Received'
                }
                # Redirect to success page instead of showing message
                return redirect('submission_success', ref=ref)

    return render(request, 'core/report.html', {
        'ref': ref,
        'dispute_ref': dispute_ref,
        'username': user,
        'email': profile.get('email', 'Not set'),
        'home_address': profile.get('home_address', 'Not set'),
        'cell_number': profile.get('cell_number', 'Not set'),
        'balance': balance,
    })

# SUBMISSION SUCCESS
def submission_success(request, ref):
    user = request.session.get('user')
    if user is None:
        return redirect('login')
    
    request_data = requests_db.get(ref)
    if not request_data or request_data.get('user') != user:
        return redirect('home')
    
    return render(request, 'core/submission_success.html', {
        'ref': ref,
        'request_data': request_data,
        'username': user
    })

# TRACK / DASHBOARD / DASHBOARD
def track_request(request):
    user = request.session.get('user')
    if user is None:
        return redirect('login')
    
    # Get user's requests
    user_requests = []
    for ref, data in requests_db.items():
        if isinstance(data, dict) and data.get('user') == user:
            user_requests.append({
                'ref': ref,
                'issue': data.get('issue', 'Unknown'),
                'location': data.get('location', 'Unknown'),
                'status': data.get('status', 'Unknown'),
                'description': data.get('description', ''),
            })
    
    # Get user's disputes
    user_disputes = []
    for ref, data in disputes_db.items():
        if data.get('user') == user:
            user_disputes.append({
                'ref': ref,
                'invoice_ref': data.get('invoice_ref', ''),
                'invoice_balance': data.get('invoice_balance', 0),
                'status': data.get('status', 'Unknown'),
            })
    
    return render(request, 'core/track.html', {
        'user_requests': user_requests,
        'user_disputes': user_disputes,
        'username': user
    })

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