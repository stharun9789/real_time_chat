from django.urls import path
from django.shortcuts import render

# View function to serve index.html
def home(request):
    return render(request, "chat/index.html")

urlpatterns = [
    path("", home, name="home"),  # Serves the single index.html file
]
