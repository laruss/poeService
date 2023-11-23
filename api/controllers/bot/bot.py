from api.controllers.base import BC
from api.models.bot import Bot
from api.poe_agent import agent
from api.utils.errorhandlers import handle_errors


class BotController(BC):
    model = Bot

    @handle_errors
    def init_bot(self, bot_name: str):
        bot = agent.init_bot(bot_name)
        return self.response200(bot.model_dump(True))

    @handle_errors
    def init_many_bots(self, bot_names: list):
        bots = [agent.init_bot(bot_name) for bot_name in bot_names]
        return self.response200([bot.model_dump(True) for bot in bots])

    @handle_errors
    def update_bot_from_api(self, bot_name: str):
        bot = agent.update_bot_from_api(bot_name)
        return self.response200(bot.model_dump(True))

    @handle_errors
    def get_bot(self, bot_name: str):
        bot = Bot.get_by_filter({"handle": bot_name})
        if not bot:
            return self.response404(data={"error": f"Bot {bot_name} not found in DB"})

        return self.response200(bot.model_dump(True))

    @handle_errors
    def unregister_bot(self, bot_name: str):
        bot = Bot.get_by_filter({"handle": bot_name})
        if not bot:
            return self.response404(data={"error": f"Bot {bot_name} not found in DB"})

        bot.delete()

        return self.response204()

    @handle_errors
    def unregister_all_bots(self):
        bots = Bot.objects()
        for bot in bots:
            bot.delete()

        return self.response204()

    @handle_errors
    def get_all_bots(self):
        bots = Bot.objects()

        return self.response200([bot.model_dump(True) for bot in bots])

    @handle_errors
    def set_prompt(self, bot_name: str, prompt: str):
        bot = Bot.get_by_filter({"handle": bot_name})
        if not bot:
            return self.response404(data={"error": f"Bot {bot_name} not found in DB"})

        agent.set_bot_prompt(bot_name, prompt)
        return self.response204()
