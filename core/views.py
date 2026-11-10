from django.shortcuts import render

# ==========================================================
# CUSTOM ERROR PAGES
# ==========================================================

def custom_404(request, exception):
    return render(request, '404.html', status=404)


def custom_500(request):
    return render(request, '500.html', status=500)