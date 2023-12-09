from api.controllers.base import BC
from api.models.settings import Settings
from api.utils.errorhandlers import handle_errors


class SettingsController(BC[Settings]):
    model = Settings

    @property
    def settings(self) -> Settings:
        return self.model.get()

    def get_limits(self):
        return self.response200([limit.model_dump(by_alias=True) for limit in self.settings.get_limits()])
