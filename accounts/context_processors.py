from .models import Engineer

def global_data(request):
    if request.user. is_authenticated:

        current_user = Engineer.objects.get(id=request.user.id)
        favorites = current_user.favorites.all()
    else:
        favorites = []
        
    return {'favorites': favorites}