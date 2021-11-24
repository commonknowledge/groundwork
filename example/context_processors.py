from django.conf import settings


def use_settings(request):
    return {"settings": settings}
