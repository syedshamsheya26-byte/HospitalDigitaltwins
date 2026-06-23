from django.shortcuts import redirect
from django.urls import reverse


class RefreshToLoginMiddleware:
    """Redirect every page to login on refresh, except right after a fresh login."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        login_url = reverse('accounts:login')
        path = request.path

        if path == login_url or path.startswith('/static/') or path.startswith('/admin/'):
            return self.get_response(request)

        if request.method == 'GET' and not request.session.pop('_fresh_login', False):
            if request.user.is_authenticated or 'patient_name' in request.session:
                return redirect(login_url)

        return self.get_response(request)
