from pydantic_mongo import PydanticMongoModel as PmModel


class BaseAppModel(PmModel):
    def update(self, **kwargs):
        [setattr(self, field, value) for field, value in kwargs.items()]

        return self.save()
