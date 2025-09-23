from tortoise import fields, models

class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=20, unique=True)
    password = fields.CharField(max_length=128) # Hashed password
    email = fields.CharField(max_length=255, unique=True, null=True)
    full_name = fields.CharField(max_length=255, null=True)
    disabled = fields.BooleanField(default=False)

    class Meta:
        table = "users"

    def __str__(self):
        return self.username

class Book(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    author = fields.CharField(max_length=255)
    published_year = fields.IntField()

    class Meta:
        table = "books"

    def __str__(self):
        return f"{self.title} by {self.author}"