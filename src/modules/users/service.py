from .models import User
from ...core.services.base import BaseService


class UserService(BaseService[User]):
    def __init__(self):
        super().__init__(User)

    async def find_by_email(self, email: str):
        return await User.find_one(User.email == email)

    async def get_by_email(self, email: str):
        return await User.find_one(User.email == email)


user_service = UserService()
