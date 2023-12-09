from typing import Optional, List

from pydantic import BaseModel


class BaseValidator(BaseModel):
    class ConfigDict:
        extra = 'forbid'


class CreateBotValidator(BaseValidator):
    handle: str
    prompt: str
    base_model: str
    display_name: Optional[str] = None
    description: Optional[str] = ""
    intro_message: Optional[str] = ""
    api_key: Optional[str] = None
    custom_message_limit: Optional[int] = None
    is_api_bot: Optional[bool] = False
    api_url: Optional[str] = None
    is_prompt_public: Optional[bool] = True
    profile_picture_url: Optional[str] = None
    has_markdown_rendering: Optional[bool] = True
    has_suggested_replies: Optional[bool] = False
    is_private: Optional[bool] = True
    temperature: Optional[float] = None
    
    
class EditBotValidator(BaseValidator):
    bot_id: int
    handle: Optional[str] = None
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    base_model: Optional[str] = None
    custom_message_limit: Optional[int] = None
    description: Optional[str] = None
    display_name: Optional[str] = None
    has_markdown_rendering: Optional[bool] = None
    has_suggested_replies: Optional[bool] = None
    intro_message: Optional[str] = None
    is_private: Optional[bool] = None
    is_prompt_public: Optional[bool] = None
    profile_picture_url: Optional[str] = None
    prompt: Optional[str] = None
    temperature: Optional[float] = None


class DeleteMessagesValidator(BaseValidator):
    message_ids: List[int]


class SendMessageValidator(BaseValidator):
    message: str
