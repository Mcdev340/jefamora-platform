from apps.core.exceptions import APIError


class WaveProvider:
    def collect(self, amount):
        raise APIError("module_inactive", "Wave sera activé après financement.", status_code=403)
