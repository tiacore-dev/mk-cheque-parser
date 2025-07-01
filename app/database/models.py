from tortoise import fields
from tortoise.fields.relational import ReverseRelation
from tortoise.models import Model


class Cheque(Model):
    id = fields.CharField(max_length=255, pk=True)  # cheque_id
    name = fields.CharField(max_length=255)
    kkt_number = fields.CharField(max_length=255)
    date = fields.DatetimeField()
    total_price = fields.DecimalField(max_digits=10, decimal_places=2)

    created_at = fields.DatetimeField(auto_now_add=True)

    items: ReverseRelation["Item"]

    class Meta:
        table = "cheques"

    def __str__(self):
        return f"Cheque {self.id}"


class Item(Model):
    id = fields.CharField(max_length=255, pk=True)  # item_id
    cheque = fields.ForeignKeyField("models.Cheque", related_name="items")
    name = fields.CharField(max_length=255)
    quantity = fields.IntField()

    price_per_unit = fields.DecimalField(max_digits=10, decimal_places=2)
    total = fields.DecimalField(max_digits=10, decimal_places=2)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "items"

    def __str__(self):
        return f"Item {self.name} (x{self.quantity})"
