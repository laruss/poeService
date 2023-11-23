from api.controllers.base import BC
from api.models.settings import Settings
from api.utils.errorhandlers import handle_errors


class SettingsController(BC):
    model = Settings

    @property
    def settings(self) -> Settings:
        return self.model.get()

    def get_settings(self):
        return self.response200(self.settings.model_dump(exclude={'id'}))

    @handle_errors
    def set_settings(self, data: dict):
        self.settings.update(**data)
        return self.response204()
