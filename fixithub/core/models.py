from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, full_name, phone, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, full_name, phone, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('handyman', 'Handyman'),
        ('admin', 'Admin'),
    )

    user_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    password_hash = models.TextField()  # Handled by set_password
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    location = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone']

    def __str__(self):
        return self.email

class HandymanProfile(models.Model):
    CATEGORY_CHOICES = (
        ('electrician', 'Electrician'),
        ('plumber', 'Plumber'),
        ('carpenter', 'Carpenter'),
        ('other', 'Other'),
    )

    handyman = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='profile')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    experience_years = models.IntegerField(default=0)
    bio = models.TextField(blank=True, null=True)
    rating = models.FloatField(default=0)
    jobs_completed = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    subscription_plan = models.CharField(max_length=20, choices=(('free', 'Free'), ('premium', 'Premium')), default='free')

    def __str__(self):
        return f"{self.handyman.email}'s Profile"

class JobRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    job_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_requests')
    handyman = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_jobs')
    category = models.CharField(max_length=50)
    job_description = models.TextField()
    job_location = models.CharField(max_length=100)
    preferred_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Job {self.job_id} by {self.client.email}"

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    job = models.ForeignKey(JobRequest, on_delete=models.CASCADE, related_name='reviews')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    handyman = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review {self.review_id} for Job {self.job.job_id}"

class Payment(models.Model):
    PURPOSE_CHOICES = (
        ('job_commission', 'Job Commission'),
        ('subscription', 'Subscription'),
        ('ad_payment', 'Ad Payment'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    )

    payment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES)
    reference_code = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.payment_id} by {self.user.email}"

class JobAd(models.Model):
    ad_id = models.AutoField(primary_key=True)
    handyman = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_ads')
    title = models.CharField(max_length=100)
    ad_description = models.TextField()
    image_url = models.URLField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Ad {self.ad_id} by {self.handyman.email}"

class SMSLog(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    )

    sms_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sms_logs')
    message = models.TextField()
    phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SMS {self.sms_id} to {self.phone}"

class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.TextField()  # Manual hashing needed
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username