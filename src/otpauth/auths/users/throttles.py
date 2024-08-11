from rest_framework.throttling import SimpleRateThrottle

class PhoneRateThrottle(SimpleRateThrottle):
    scope = 'phone'

    def get_cache_key(self, request, view):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return None
        return f"throttle_{phone_number}"