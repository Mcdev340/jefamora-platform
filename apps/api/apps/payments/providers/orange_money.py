from apps.core.exceptions import APIError


class OrangeMoneyProvider:
    def collect(self, amount):
        raise APIError("module_inactive", "Orange Money sera activé après financement.", status_code=403)
