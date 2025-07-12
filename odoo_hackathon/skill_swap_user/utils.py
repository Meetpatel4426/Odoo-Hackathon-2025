# skill_swap_user/utils.py
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

class CustomTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return text_type(user.pk) + text_type(timestamp) + text_type(user.password)

password_reset_token = CustomTokenGenerator()
