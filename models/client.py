from dataclasses import dataclass

@dataclass
class UserClient:
    id: int
    user_id: int
    api_id:int
    api_hash:str
    phone: str
    ai_settings:str
    mailing_text:str
    answers:int
    gs:str
    is_active:bool
    
    
@dataclass
class User:
    id:int
    user_id:int
    username:str
    full_name:str
    has_access:bool
    