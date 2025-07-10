from bson import ObjectId

from django.core.serializers.json import DjangoJSONEncoder


class MongoJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)
