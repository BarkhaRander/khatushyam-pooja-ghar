from django.db import models
from accounts.models import Account

class ContactUs(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    s = models.CharField(max_length=250,blank=True)

    def __str__(self):
        return self.s
    class Meta:
        verbose_name = 'contactus'
        verbose_name_plural = 'contact us'