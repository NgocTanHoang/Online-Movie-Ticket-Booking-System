from .models import Theater

def theater_processor(request):
    theaters = Theater.objects.all()
    selected_theater = None
    if 'selected_theater' in request.session:
        try:
            selected_theater = Theater.objects.get(id=request.session['selected_theater'])
        except Theater.DoesNotExist:
            del request.session['selected_theater']
    
    return {
        'theaters': theaters,
        'selected_theater': selected_theater
    } 