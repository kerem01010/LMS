from django.contrib import admin
from library.models import Library, Barrowing, LibraryGallery, LibraryFeatures, LibraryFAQs, ActivityLog, StaffOnDuty, Coupon, CouponUsers, Notification, Bookmark, Review
from import_export.admin import ImportExportModelAdmin

class libraryGallery_Tab(admin.TabularInline):
    model = LibraryGallery

class libraryFeatures_Tab(admin.TabularInline):
    model = LibraryFeatures

class libraryFAQs_Tab(admin.TabularInline):
    model = LibraryFAQs


class ActivityLog_Tab(admin.TabularInline):
    model = ActivityLog

class StaffOnDuty_Tab(admin.TabularInline):
    model = StaffOnDuty

class CouponUsers_Tab(admin.TabularInline):
    model = CouponUsers

class LibraryAdmin(ImportExportModelAdmin):
    search_fields = ['user__username', 'title']
    list_filter = ['featured', 'status']
    list_editable = ['status']
    #list_display = ['thumbnail' ,'user',  'name', 'status', 'featured' ,'views']
    list_display = ['thumbnail' ,  'title', 'authors', 'categories' ,'status','views','featured']

    list_per_page = 100
    prepopulated_fields = {"slug": ("title", )}




class BarrowingAdmin(ImportExportModelAdmin):
    inlines = [ActivityLog_Tab, StaffOnDuty_Tab]
    list_filter = [ 'library',  'check_in_date', 'check_out_date', 'is_active' , 'checked_in' ,'checked_out']
    list_display = ['barrowing_id', 'user', 'library',  'total_days', 'check_in_date', 'check_out_date', 'is_active' , 'checked_in' ,'checked_out']
    search_fields = ['barrowing_id', 'user__username', 'user__email']
    list_per_page = 100




class CouponAdmin(ImportExportModelAdmin):
    inlines = [CouponUsers_Tab]
    list_editable = ['valid_from', 'valid_to', 'active', 'type']
    list_display = ['code', 'discount', 'type', 'redemption', 'valid_from', 'valid_to' , 'active', 'date']
        
class NotificationAdmin(ImportExportModelAdmin):
    list_editable = ['seen', 'type']
    list_display = ['user', 'barrowing', 'type', 'seen', 'date']

class BookmarkAdmin(ImportExportModelAdmin):
    list_display = ['user', 'library']

class ReviewAdmin(admin.ModelAdmin):
    list_editable = ['active']
    list_display = ['user', 'library', 'review', 'reply' ,'rating', 'active']


admin.site.register(Library, LibraryAdmin)
admin.site.register(Barrowing, BarrowingAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(Review, ReviewAdmin)

