from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class CameraDetails(models.Model):
    camera_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    url = models.URLField()

    def save(self, *args, **kwargs):
        # Check if the number of existing records exceeds 4
        if CameraDetails.objects.count() >= 4 and not self.pk:
            raise ValidationError("Only 4 items are allowed in the database.")
        
        super().save(*args, **kwargs)