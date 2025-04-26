from mongoengine import Document, StringField, DateTimeField, BooleanField
from datetime import datetime


class PasswordResetCode(Document):
    user_id = StringField(required=True)
    code = StringField(required=True, max_length=6)
    created_at = DateTimeField(default=datetime.now)
    expires_at = DateTimeField(required=True)
    is_used = BooleanField(default=False)

    meta = {
        'collection': 'password_reset_codes',
        'indexes': [
            {'fields': ['user_id', 'created_at']}
        ]
    }

    def is_valid(self):
        return not self.is_used and datetime.now() < self.expires_at
