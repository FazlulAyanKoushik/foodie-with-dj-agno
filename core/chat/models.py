from django.db import models

from commons.models import BaseModel


# Create your models here.
class Thread(BaseModel):
    restaurant = models.ForeignKey("restaurants.Restaurant", on_delete=models.CASCADE)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, blank=True, null=True)
    summary = models.TextField()

    def __str__(self):
        return f"{self.restaurant} - {self.user}"


class Message(BaseModel):
    thread = models.ForeignKey('chat.Thread', on_delete=models.CASCADE)
    user_message = models.TextField()
    ai_response = models.TextField()

    def __str__(self):
        return f"{self.thread}"

