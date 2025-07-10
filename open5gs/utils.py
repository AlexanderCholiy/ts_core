import secrets
from bson import ObjectId

from django.core.serializers.json import DjangoJSONEncoder


class MongoJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)


def generate_hex_key(length=32) -> str:
    """Генерирует случайный HEX-ключ заданной длины (в символах)"""
    byte_length = length // 2
    random_bytes = secrets.token_bytes(byte_length)
    hex_key = random_bytes.hex().upper()
    formatted_key = ' '.join(
        [hex_key[i:i+8] for i in range(0, len(hex_key), 8)]
    )
    return formatted_key
