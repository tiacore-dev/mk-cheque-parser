from tortoise import fields
from tortoise.models import Model


class Cheque(Model):
    id = fields.CharField(max_length=255, pk=True)
    name = fields.CharField(max_length=255)
    kkt_number = fields.CharField(max_length=255, null=True)
    date = fields.DatetimeField()

    class Meta:
        table = "cheques"


class Items(Model):
    id = fields.CharField(max_length=255, pk=True)
    cheque = fields.ForeignKeyField("models.Cheque", related_name="items")
    name = fields.CharField(max_length=255)
    quantity = fields.IntField()
    price_per_unit = fields.DecimalField()
    total = fields.DecimalField()

    class Meta:
        table = "items"
