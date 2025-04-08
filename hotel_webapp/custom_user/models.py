from django.db import models

# Create your models here.

class CustomUser(models.Model):
    f_name = models.CharField(max_length=50,null=True,blank=True)
    l_name = models.CharField(max_length=50,null=True,blank=True)
    email = models.EmailField()
    phone_no = models.CharField(max_length=12,null=True,blank=True)
    created_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'GUEST'

    def __str__(self):
        return f"{self.f_name} {self.l_name}"