from django.db import models
from django.conf import settings

class ContactMessage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="contact_messages"
    )
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.user.email} at {self.created}"