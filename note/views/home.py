from django.shortcuts import render


def home_view(request):
    """
    GET: Render the home page
    We are not passing anything to the home page from the backend.
    We are using vanilla JavaScript to fetch the data from the API.
    """
    return render(request, 'pages/home.html')


def login_view(request):
    """
    GET: Render the login page
    We are not passing anything to the login page from the backend.
    We are using vanilla JavaScript to fetch the data from the API.
    """
    return render(request, "pages/login.html")