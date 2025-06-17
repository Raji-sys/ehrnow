from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user attribute exists and is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                # Check if session has expired due to inactivity
                time_since_activity = timezone.now().timestamp() - last_activity
                if time_since_activity > 1800:  # 30 minutes
                    logout(request)
                    return redirect('login')
            
            # Update last activity timestamp
            request.session['last_activity'] = timezone.now().timestamp()
        
        response = self.get_response(request)
        return response
