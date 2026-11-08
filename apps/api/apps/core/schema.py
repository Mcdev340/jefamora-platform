from drf_spectacular.openapi import AutoSchema


class AppTagAutoSchema(AutoSchema):
    """Groupe chaque opération Swagger sous le nom du module Django."""

    def get_tags(self):
        parts = self.view.__class__.__module__.split(".")
        if parts and parts[0] == "apps" and len(parts) > 1:
            return [parts[1]]
        return super().get_tags()
