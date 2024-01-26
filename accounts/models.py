from datetime import datetime
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _
from django.utils.text import slugify

from .managers import CustomUserManager
from locations.models import City


class UserBase(AbstractUser):
    class UserTypes(models.TextChoices):
        USER = 'USER', 'User'
        COMPANY = 'COMPANY', 'Company'

    base_type = UserTypes.USER

    type = models.CharField(_('Type'), max_length=7, choices=UserTypes.choices, default=base_type)    
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', )

    objects = CustomUserManager()

    @property
    def is_user(self):
        return self.type == UserBase.UserTypes.USER

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = self.base_type
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.get_full_name()} - {self.type}'


# USER
class UserInfo(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    middle_name = models.CharField(_("middle name"), max_length=150, blank=True, null=True)
    birthday = models.DateField(null=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT)

    _GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )
    gender = models.CharField(max_length=2, choices=_GENDER_CHOICES)

    @property
    def age(self):
        td = datetime.now() - self.birthday
        return td.days
    
    @property
    def location(self):
        return f'{self.city}, {self.city.state}, {self.city.state.country}'

    def __str__(self):
        return f'{self.user.get_full_name()}'


class UserManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=UserBase.UserTypes.USER)

class User(UserBase):
    base_type = UserBase.UserTypes.USER
    objects = UserManager()

    @property
    def data(self):
        return self.userinfo

    class Meta:
        proxy = True

# COMPANY
class Industry(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, allow_unicode=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super(Industry, self).save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.name

class CompanyInfo(models.Model):
    company = models.OneToOneField('Company', on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, allow_unicode=True, editable=False)
    description = models.TextField(max_length=1000, blank=True, null=True)
    foundation_year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1000), MaxValueValidator(datetime.now().year + 1)])
    logo = models.ImageField(upload_to='company-logo', default='company-logo/default.png')
    cover = models.ImageField(upload_to='company-cover', blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    
    size = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    
    industry = models.ForeignKey(Industry, on_delete=models.PROTECT, related_name='companies')


    @property
    def location(self):
        return f'{self.city}, {self.city.state}, {self.city.state.country}'

    @property
    def size_category(self):
        if self.size < 11:
            return '1-10'
        if self.size < 51:
            return '11-50'    
        if self.size < 101:
            return '51-100'    
        if self.size < 501:
            return '101-500'    
        if self.size < 1001:
            return '501-1000'    
        return 'more than 1000'    

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.name, allow_unicode=True)
            if CompanyInfo.objects.filter(slug=slug).exists():
                slug = slugify(f'{self.name} {self.city.name}', allow_unicode=True)
                while CompanyInfo.objects.filter(slug=slug).exists():
                    random_num = str(datetime.now().timestamp()).split('.')[-1][-3:]
                    slug = slugify(f'{self.name} {self.city.name} {random_num}', allow_unicode=True)
            self.slug = slug
        super(CompanyInfo, self).save(*args, **kwargs)


class CompanyManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=UserBase.UserTypes.COMPANY)

class Company(UserBase):
    base_type = UserBase.UserTypes.COMPANY
    objects = CompanyManager()

    @property
    def data(self):
        return self.companyinfo

    class Meta:
        proxy = True
