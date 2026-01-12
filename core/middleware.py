from django.utils import translation
from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
from geoip2.errors import AddressNotFoundError

class SmartLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().lower()
        # Default language
        language_code = 'en'

        # 1. Check Top-Level Domain (TLD)
        if host.endswith('.ro') or 'localhost' in host:
            language_code = 'ro'
        elif host.endswith('.com') or host.endswith('.net') or host.endswith('.org'):
            # 2. Fallback to GeoIP for generic domains
            language_code = self.get_language_from_ip(request)

        # Activate the chosen language
        translation.activate(language_code)
        request.LANGUAGE_CODE = translation.get_language()
        
        response = self.get_response(request)
        
        # Deactivate to avoid bleeding into other requests
        translation.deactivate()
        return response

    def get_language_from_ip(self, request):
        ip = self.get_client_ip(request)
        if not ip:
            return 'en'
            
        try:
            g = GeoIP2()
            country_code = g.country_code(ip)
            
            # Map Country Codes to Language Codes
            country_map = {
                'RO': 'ro',
                'MD': 'ro',
            }
            return country_map.get(country_code, 'en')
        except (Exception, AddressNotFoundError):
            return 'en'

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        # Handle localhost/loopback
        if ip == '127.0.0.1':
            return None
        return ip
