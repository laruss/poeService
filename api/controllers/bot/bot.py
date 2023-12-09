from api.controllers.base import BC
from api.validators import CreateBotValidator, EditBotValidator
from api.models.bot import Bot
from api.utils.errorhandlers import handle_errors


class BotController(BC[Bot]):
    model = Bot

    @handle_errors
    def get_base_models(self):
        return self.response200(self.model.get_base_models())

    @handle_errors
    def create_bot(self, data: dict):
        model = CreateBotValidator(**data)
        return self.response200(self.model.create(model).model_dump(by_alias=True))

    @handle_errors
    def edit_bot(self, bot_name: str, data: dict):
        bot = self.model.get_by_bot_name(bot_name)
        model = EditBotValidator(bot_id=bot.botId, **data)
        return self.response200(self.model.edit_in_api(model).model_dump(by_alias=True))

    @handle_errors
    def update_bot_from_api(self, bot_name: str):
        return self.response200(self.model.get_from_api(bot_name=bot_name).model_dump(by_alias=True))

    @handle_errors
    def get_bot(self, bot_name: str):
        return self.response200(self.model.get_by_bot_name(bot_name).model_dump(by_alias=True))

    @handle_errors
    def delete_bot(self, bot_name: str):
        self.model.delete_in_api(bot_name)
        return self.response204()

    @handle_errors
    def get_all_bots(self):
        return [obj.model_dump(by_alias=True) for obj in self.model.objects()]
