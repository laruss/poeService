import json
import queue
import re
import ssl
import threading
from time import sleep, time
from typing import Optional

from loguru import logger
from poe_api_wrapper import PoeApi
from poe_api_wrapper.api import BOT_CREATION_MODELS, bot_map, generate_nonce, generate_file
from poe_api_wrapper.queries import generate_payload
from requests_toolbelt import MultipartEncoder


class AppPoeApi(PoeApi):
    def ws_run_thread(self):
        if not self.ws.sock:
            kwargs = {"sslopt": {"cert_reqs": ssl.CERT_NONE}}
            self.ws.run_forever(**kwargs)

    @staticmethod
    def _validate_handle(handle):
        pattern = re.compile(r"^[A-Za-z0-9_-]{4,20}$")
        if not bool(pattern.match(handle)):
            raise ValueError("Invalid handle, must be 4-20 characters, alphanumeric, underscores and dashes only")

    def create_bot(self,
                   handle: str,
                   prompt: str,
                   display_name=None,
                   base_model: str = "beaver",
                   description: str = "",
                   intro_message: str = "",
                   api_key: str = None,
                   api_bot: bool = False,
                   api_url: str = None,
                   prompt_public: bool = True,
                   pfp_url: str = None,
                   linkification: bool = False,
                   markdown_rendering: bool = True,
                   suggested_replies: bool = False,
                   private: bool = False,
                   temperature: float = None,
                   ):
        self._validate_handle(handle)

        if base_model not in BOT_CREATION_MODELS:
            raise ValueError(f"Invalid base model {base_model}. Please choose from {BOT_CREATION_MODELS}")
        # Auto complete profile
        try:
            self.send_request('gql_POST', 'MarkMultiplayerNuxCompleted', {})
        except:
            self.complete_profile()
        variables = {
            "model": base_model,
            "displayName": display_name,
            "handle": handle,
            "prompt": prompt,
            "isPromptPublic": prompt_public,
            "introduction": intro_message,
            "description": description,
            "profilePictureUrl": pfp_url,
            "apiUrl": api_url,
            "apiKey": api_key,
            "isApiBot": api_bot,
            "hasLinkification": linkification,
            "hasMarkdownRendering": markdown_rendering,
            "hasSuggestedReplies": suggested_replies,
            "isPrivateBot": private,
            "temperature": temperature
        }
        full_result = self.send_request('gql_POST', 'PoeBotCreate', variables)

        result = full_result['data']['poeBotCreate']
        if result["status"] != "success":
            logger.error(f"Poe returned an error while trying to create a bot: {result['status']}")
        else:
            logger.success(f"Bot created successfully | {handle}")

        return result

    def edit_bot(self,
                 handle,
                 prompt: str = None,
                 bot_id: int = None,
                 display_name: str = None,
                 base_model: str = "beaver",
                 description: str = "",
                 intro_message: str = "",
                 api_key: str = None,
                 api_url: str = None,
                 private: bool = False,
                 prompt_public: bool = False,
                 profile_picture_url: str = None,
                 linkification: bool = False,
                 markdown_rendering: bool = True,
                 suggested_replies: bool = False,
                 temperature: float = None,
                 ):
        if not bot_id:
            raise ValueError("Bot id must be provided")
        if base_model not in BOT_CREATION_MODELS:
            raise ValueError(f"Invalid base model {base_model}. Please choose from {BOT_CREATION_MODELS}")
        variables = {
            "baseBot": base_model,
            "botId": bot_id,
            "handle": handle,
            "displayName": display_name,
            "prompt": prompt,
            "isPromptPublic": prompt_public,
            "introduction": intro_message,
            "description": description,
            "profilePictureUrl": profile_picture_url,
            "apiUrl": api_url,
            "apiKey": api_key,
            "hasLinkification": linkification,
            "hasMarkdownRendering": markdown_rendering,
            "hasSuggestedReplies": suggested_replies,
            "isPrivateBot": private,
            "temperature": temperature
        }
        result = self.send_request('gql_POST', 'PoeBotEdit', variables)["data"]["poeBotEdit"]
        if result["status"] != "success":
            logger.error(f"Poe returned an error while trying to edit a bot: {result['status']}")
        else:
            logger.info(f"Bot edited successfully | {handle}")

        return result

    def get_bot_data(self, chat_code: str = None, bot_name: str = None, bot_id: int = None) -> dict:
        if sum(bool(x) for x in [chat_code, bot_name, bot_id]) != 1:
            raise ValueError("Only one of chat_code, bot_name, bot_id must be used")

        variables = dict(
            botId=bot_id or 0,
            botName=bot_name or "",
            chatCode=chat_code or "",
            postId=0,
            shareCode="",
            useBotId=bool(bot_id),
            useBotName=bool(bot_name),
            useChat=bool(chat_code),
            usePostId=False,
            useShareCode=False,
        )
        result = self.send_request("gql_POST", "LayoutRightSidebarQuery", variables)

        return result["data"]

    @staticmethod
    def _generate_payload_for_message(variables) -> str:
        payload = {
            "queryName": "sendMessageMutation",
            "variables": variables,
            "extensions": {
                "hash": "53a8dcf49abbcd0cb4ffa8d85de8ed2a3bcf41018492eec2b4f78623c0e1dda6"
            }
        }
        return json.dumps(payload, separators=(",", ":"))

    def send_request(self, path: str, query_name: str = "", variables: dict = None, file_form: list = None):
        variables = variables or {}
        file_form = file_form or []
        payload = generate_payload(query_name, variables) if query_name else self._generate_payload_for_message(variables)
        if not file_form:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        else:
            fields = {'queryInfo': payload}
            for i in range(len(file_form)):
                fields[f'file{i}'] = file_form[i]
            payload = MultipartEncoder(
                fields=fields
                )
            headers = {'Content-Type': payload.content_type}
            payload = payload.to_string()
        response = self.client.post(f'{self.BASE_URL}/poe_api/{path}', data=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise RuntimeError(f"An unknown error occurred. Raw response data: {response.text}")

    def _wait_for_active_messages(self, timeout: int = 10):
        timer = 0
        while None in self.active_messages.values():
            sleep(0.01)
            timer += 0.01
            if timer > timeout:
                raise RuntimeError("Timed out waiting for other messages to send.")

            self.active_messages["pending"] = None

    @staticmethod
    def _get_message_variables(bot: str, chatId: int, message: str, attachments: list):
        return dict(
            bot=bot, chatId=chatId, query=message, shouldFetchChat=True, source=dict(
                sourceType="chat_input",
                chatInputMetadata=dict(useVoiceRecord=False),
            ), clientNonce=generate_nonce(), sdid="", attachments=attachments
        )

    def _send_message(self, bot: str, message: str, attachments: list,
                      file_form: list, apiPath: str, chatCode: Optional[str], chatId: Optional[int]):
        variables = self._get_message_variables(bot, chatId, message, attachments)
        try:
            message_data = self.send_request(apiPath, '', variables, file_form)
        except Exception as e:
            del self.active_messages["pending"]
            raise e

        if errors := message_data.get('errors'):
            raise RuntimeError(f"Poe returned an error while trying to send a message: {errors[0]['message']}")

        data = message_data['data']
        status = data['messageEdgeCreate']['status']

        status_mapper = dict(
            reached_limit=f"Daily limit reached for {bot}.",
            too_many_tokens=f"{data['messageEdgeCreate']['statusMessage']}",
            unsupported_file_type="This file type is not supported. Please try again with a different file.",
        )

        if status in status_mapper.keys():
            raise RuntimeError(status_mapper[status])

        if not chatCode and not chatId:
            logger.info(f"New Thread created | {data['messageEdgeCreate']['chat']['chatCode']}")

        message_data = message_data['data']['messageEdgeCreate']['chat']
        title = message_data['title']

        self.current_thread[bot] = [dict(chatId=message_data['chatId'], chatCode=message_data['chatCode'],
                                         id=message_data['id'], title=title)]

        if self.active_messages.get("pending"):
            del self.active_messages["pending"]

        try:
            human_message_id = message_data['messagesConnection']['edges'][0]['node']['messageId']
        except TypeError:
            raise RuntimeError(f"An unknown error occurred. Raw response data: {message_data}")

        return human_message_id, title

    def send_message(self, bot: str, message: str, chatId: int = None, chatCode: str = None, file_path: list = None,
                     suggest_replies: bool = False, timeout: int = 10) -> dict:
        bot = bot_map(bot)
        self.retry_attempts = 3

        self._wait_for_active_messages(timeout=timeout)

        while self.ws_error:
            sleep(0.01)
        self.connect_ws()

        attachments = []
        file_form = []
        apiPath = 'gql_upload_POST' if file_path else 'gql_POST'

        if file_path:
            file_form, file_size = generate_file(file_path, self.proxy)
            if file_size > 100000000:
                raise RuntimeError("File size too large. Please try again with a smaller file.")
            [attachments.append(f'file{i}') for i, _ in enumerate(file_form)]

        human_message_id, title = self._send_message(bot, message, attachments, file_form, apiPath, chatCode,
                                                     chatId)

        self.message_generating = True
        self.active_messages[human_message_id] = None
        self.message_queues[human_message_id] = queue.Queue()

        last_text, message_id = "", None

        stateChange = False

        while True:
            try:
                response = self.message_queues[human_message_id].get(timeout=timeout)
            except queue.Empty:
                try:
                    if self.retry_attempts > 0:
                        self.retry_attempts -= 1
                        logger.warning(f"Retrying request {3 - self.retry_attempts}/3 times...")
                    else:
                        self.retry_attempts = 3
                        del self.active_messages[human_message_id]
                        del self.message_queues[human_message_id]
                        raise RuntimeError("Timed out waiting for response.")
                    self.connect_ws()
                    continue
                except Exception as e:
                    raise e

            response.update(dict(chatCode=chatCode, chatId=chatId, title=title))

            if response["state"] == "error_user_message_too_long":
                response["response"] = 'Message too long. Please try again!'
                yield response
                break

            if response['author'] == 'pacarana' and response['text'].strip() == last_text.strip():
                response["response"] = ''
            elif response['author'] == 'pacarana' and (last_text == '' or bot != 'web-search'):
                response["response"] = f'{response["text"]}\n'
            else:
                if stateChange:
                    response["response"] = response["text"][len(last_text):]
                else:
                    response["response"] = response["text"]
                    stateChange = True

            yield response

            if response["state"] == "complete" or not self.message_generating:
                if last_text and response["messageId"] == message_id:
                    break
                else:
                    continue

            last_text = response["text"]
            message_id = response["messageId"]

        def recv_post_thread():
            bot_message_id = self.active_messages[human_message_id]
            sleep(2.5)
            self.send_request("receive_POST", "recv", {
                "bot_name": bot,
                "time_to_first_typing_indicator": 300,  # randomly select
                "time_to_first_subscription_response": 600,
                "time_to_full_bot_response": 1100,
                "full_response_length": len(last_text) + 1,
                "full_response_word_count": len(last_text.split(" ")) + 1,
                "human_message_id": human_message_id,
                "bot_message_id": bot_message_id,
                "chat_id": chatId,
                "bot_response_status": "success",
            })
            sleep(0.5)

        def get_suggestions(queue, chatCode: str = None, timeout: int = 5):
            variables = {'chatCode': chatCode}
            state = 'incomplete'
            suggestions = []
            start_time = time()
            while True:
                elapsed_time = time() - start_time
                if elapsed_time >= timeout:
                    break
                sleep(0.5)
                response_json = self.send_request('gql_POST', 'ChatPageQuery', variables)
                hasSuggestedReplies = response_json['data']['chatOfCode']['defaultBotObject']['hasSuggestedReplies']
                edges = response_json['data']['chatOfCode']['messagesConnection']['edges']
                if hasSuggestedReplies and edges:
                    latest_message = edges[-1]['node']
                    suggestions = latest_message['suggestedReplies']
                    state = latest_message['state']
                    if state == 'complete' and suggestions:
                        break
                    if state == 'error_user_message_too_long':
                        break
                else:
                    break
            queue.put({'text': response["text"], 'response': '', 'suggestedReplies': suggestions, 'state': state,
                       'chatCode': chatCode, 'chatId': chatId, 'title': title})

        if response["state"] != "error_user_message_too_long":
            t1 = threading.Thread(target=recv_post_thread, daemon=True)
            t1.start()

            if suggest_replies:
                self.suggestions_queue = queue.Queue()
                t2 = threading.Thread(target=get_suggestions, args=(self.suggestions_queue, chatCode, 5), daemon=True)
                t2.start()
                try:
                    suggestions = self.suggestions_queue.get(timeout=5)
                    yield suggestions
                except queue.Empty:
                    yield {'text': response["text"], 'response': '', 'suggestedReplies': [], 'state': None,
                           'chatCode': chatCode, 'chatId': chatId, 'title': title}
                del self.suggestions_queue

        del self.active_messages[human_message_id]
        del self.message_queues[human_message_id]
        self.retry_attempts = 3
