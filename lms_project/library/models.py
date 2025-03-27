from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.template.defaultfilters import escape
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from django.core.validators import MinValueValidator, MaxValueValidator

from userauths.models import User

import shortuuid
from taggit.managers import TaggableManager

ICON_TPYE = (
    ('Bootstap Icons', 'Bootstap Icons'),
    ('Fontawesome Icons', 'Fontawesome Icons'),
)



LIBRARY_STATUS = (
    ("Draft", "Draft"),
    ("Disabled", "Disabled"),
    ("Rejected", "Rejected"),
    ("In Review", "In Review"),
    ("Live", "Live"),
)

GENDER = (
    ("Male", "Male"),
    ("Female", "Female"),
)


DISCOUNT_TYPE = (
    ("Percentage", "Percentage"),
    ("Flat Rate", "Flat Rate"),
)

PAYMENT_STATUS = (
    ("paid", "Paid"),
    ("pending", "Pending"),
    ("processing", "Processing"),
    ("cancelled", "Cancelled"),
    ("initiated", 'Initiated'),
    ("failed", 'failed'),
    ("refunding", 'refunding'),
    ("refunded", 'refunded'),
    ("unpaid", 'unpaid'),
    ("expired", 'expired'),
)
SERVICES_TYPES = (
    ('Food', 'Food'),
    ('Cleaning', 'Cleaning'),
    ('Technical', 'Technical'),
)



NOTIFICATION_TYPE = (
    ("Barrowing Confirmed", "Barrowing Confirmed"),
    ("Barrowing Cancelled", "Barrowing Cancelled"),
)


RATING = (
    ( 1,  "★☆☆☆☆"),
    ( 2,  "★★☆☆☆"),
    ( 3,  "★★★☆☆"),
    ( 4,  "★★★★☆"),
    ( 5,  "★★★★★"),
)
class Library(models.Model):
    #user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    #name = models.CharField(max_length=100)
    #description = CKEditor5Field(config_name='extends', null=True, blank=True)
    #image = models.FileField(upload_to="library_gallery", null=True, blank=True)
    #address = models.CharField(max_length=200)
    #mobile = models.CharField(max_length=20)
    #email = models.CharField(max_length=20)
    title = models.CharField(max_length=100, null=True, blank=True)
    authors = models.CharField(max_length=100, null=True, blank=True)
    categories=models.CharField(max_length=100,null=True,)
    image = models.ImageField(upload_to='library_gallery',default='media/book.jpg')  # Varsayılan bir değer ekledik
    description = CKEditor5Field(config_name='extends', null=True, blank=True)
    published=models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(choices=LIBRARY_STATUS, max_length=10, default="published", null=True, blank=True)
    #tags = TaggableManager(blank=True)
    views = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=False)
    #hid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
    slug = models.SlugField(null=True, blank=True)
    #date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            uuid_key = shortuuid.uuid()
            uniqueid = uuid_key[:4]
            self.slug = slugify(self.title) + "-" + str(uniqueid.lower())
            
        super(Library, self).save(*args, **kwargs) 

    def thumbnail(self):
        if self.image and hasattr(self.image, 'url'):
            return mark_safe('<img src="%s" width="50" height="50" style="object-fit:cover; border-radius: 6px;" />' % (self.image.url))
        return "No Image"

    def library_gallery(self):
        return LibraryGallery.objects.filter(library=self)
    
    def library_features(self):
        return LibraryFeatures.objects.filter(library=self)

    def library_faqs(self):
        return LibraryFAQs.objects.filter(library=self)


    def average_rating(self):
        average_rating = Review.objects.filter(library=self, active=True).aggregate(avg_rating=models.Avg("rating"))
        return average_rating['avg_rating']
    
    def rating_count(self):
        rating_count = Review.objects.filter(library=self, active=True).count()
        return rating_count
    

class LibraryGallery(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    image = models.FileField(upload_to="library_gallery")
    hgid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")

    def __str__(self):
        return str(self.library)

    class Meta:
        verbose_name_plural = "Library Gallery"
    

class LibraryFeatures(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    icon_type = models.CharField(max_length=100, null=True, blank=True, choices=ICON_TPYE)
    icon = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100)
    hfid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")

    def __str__(self):
        return str(self.library)
    
    class Meta:
        verbose_name_plural = "Library Features"
    
class LibraryFAQs(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    question = models.CharField(max_length=1000)
    answer = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    hfid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")

    def __str__(self):
        return str(self.library)
    
    class Meta:
        verbose_name_plural = "Library FAQs"



class Barrowing(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    payment_status = models.CharField(max_length=100, choices=PAYMENT_STATUS, default="initiated")

    full_name = models.CharField(max_length=1000, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=1000, null=True, blank=True)
    
    library = models.ForeignKey(Library, on_delete=models.SET_NULL, null=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_days = models.PositiveIntegerField(default=0)
    checked_in = models.BooleanField(default=False)
    checked_out = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    checked_in_tracker = models.BooleanField(default=False, help_text="DO NOT CHECK THIS BOX")
    checked_out_tracker = models.BooleanField(default=False, help_text="DO NOT CHECK THIS BOX")
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    coupons = models.ManyToManyField("library.Coupon", blank=True)
    stripe_payment_intent = models.CharField(max_length=200,null=True, blank=True)
    success_id = ShortUUIDField(length=300, max_length=505, alphabet="abcdefghijklmnopqrstuvxyz1234567890")
    barrowing_id = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")


    def __str__(self):
        return f"{self.barrowing_id}"
    
    

    
class ActivityLog(models.Model):
    barrowing = models.ForeignKey(Barrowing, on_delete=models.CASCADE)
    guest_out = models.DateTimeField()
    guest_in = models.DateTimeField()
    description = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.barrowing)
    
class StaffOnDuty(models.Model):
    barrowing = models.ForeignKey(Barrowing, on_delete=models.CASCADE)
    staff_id = models.CharField(null=True, blank=True, max_length=100)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.staff_id)
    

class Coupon(models.Model):
    code = models.CharField(max_length=1000)
    type = models.CharField(max_length=100, choices=DISCOUNT_TYPE, default="Percentage")
    discount = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(100)])
    redemption = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    make_public = models.BooleanField(default=False)
    valid_from = models.DateField()
    valid_to = models.DateField()
    cid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz")

    
    def __str__(self):
        return self.code
    
    class Meta:
        ordering =['-id']


class CouponUsers(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    barrowing = models.ForeignKey(Barrowing, on_delete=models.CASCADE)
    
    full_name = models.CharField(max_length=1000)
    email = models.CharField(max_length=1000)
    mobile = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.coupon.code)
    
    class Meta:
        ordering =['-id']



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    barrowing = models.ForeignKey(Barrowing, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=100, default="new_order", choices=NOTIFICATION_TYPE)
    seen = models.BooleanField(default=False)
    nid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
    date= models.DateField(auto_now_add=True)
    
    def __str__(self):
        return str(self.user.username)
    
    class Meta:
        ordering = ['-date']


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    library = models.ForeignKey(Library, on_delete=models.CASCADE, null=True, blank=True)
    bid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
    date= models.DateField(auto_now_add=True)
    
    def __str__(self):
        return str(self.user.username)
    
    class Meta:
        ordering = ['-date']



class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    library = models.ForeignKey(Library, on_delete=models.SET_NULL, blank=True, null=True, related_name="reviews")
    review = models.TextField(null=True, blank=True)
    reply = models.CharField(null=True, blank=True, max_length=1000)
    rating = models.IntegerField(choices=RATING, default=None)
    active = models.BooleanField(default=True)
    helpful = models.ManyToManyField(User, blank=True, related_name="helpful")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Reviews & Rating"
        ordering = ["-date"]
        
    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.rating}"
        else:
            return f"Anonymous User - {self.rating}"
