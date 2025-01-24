from django.contrib import admin
from django.utils.html import format_html
from .models import YearCategory, Category, SubCategory, Post

@admin.register(YearCategory)
class YearCategoryAdmin(admin.ModelAdmin):
    list_display = ('year', 'get_posts_count')
    search_fields = ('year',)
    ordering = ('-year',)

    def get_posts_count(self, obj):
        count = Post.objects.filter(subcategory__category__year_category=obj).count()
        return format_html('<b>{}</b> posts', count)
    get_posts_count.short_description = 'Total Posts'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'year_category', 'get_subcategories_count', 'get_posts_count')
    list_filter = ('year_category',)
    search_fields = ('name', 'year_category__year')
    ordering = ('name',)

    def get_subcategories_count(self, obj):
        return obj.subcategory_set.count()
    get_subcategories_count.short_description = 'Subcategories'

    def get_posts_count(self, obj):
        count = Post.objects.filter(subcategory__category=obj).count()
        return format_html('<b>{}</b> posts', count)
    get_posts_count.short_description = 'Total Posts'

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'get_year', 'get_posts_count')
    list_filter = ('category__year_category', 'category')
    search_fields = ('name', 'category__name', 'category__year_category__year')
    ordering = ('name',)

    def get_year(self, obj):
        return obj.category.year_category.year
    get_year.short_description = 'Year'
    get_year.admin_order_field = 'category__year_category__year'

    def get_posts_count(self, obj):
        count = obj.post_set.count()
        return format_html('<b>{}</b> posts', count)
    get_posts_count.short_description = 'Posts'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_year', 'get_category', 'subcategory', 
                   'created_at', 'updated_at', 'pdf_file_link')
    list_filter = ('subcategory__category__year_category', 
                  'subcategory__category', 'subcategory', 'created_at')
    search_fields = ('title', 'description', 
                    'subcategory__name',
                    'subcategory__category__name',
                    'subcategory__category__year_category__year')
    readonly_fields = ('created_at', 'updated_at', 'pdf_file_preview')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Document Information', {
            'fields': ('title', 'description')
        }),
        ('Category Information', {
            'fields': ('subcategory',)
        }),
        ('PDF File', {
            'fields': ('pdf_file', 'pdf_file_preview'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_year(self, obj):
        return obj.subcategory.category.year_category.year
    get_year.short_description = 'Year'
    get_year.admin_order_field = 'subcategory__category__year_category__year'

    def get_category(self, obj):
        return obj.subcategory.category.name
    get_category.short_description = 'Category'
    get_category.admin_order_field = 'subcategory__category__name'

    def pdf_file_link(self, obj):
        if obj.pdf_file:
            return format_html('<a href="{}" target="_blank">View PDF</a>', obj.pdf_file.url)
        return "No file"
    pdf_file_link.short_description = 'PDF File'

    def pdf_file_preview(self, obj):
        if obj.pdf_file:
            return format_html(
                '<div style="margin-top: 10px;">'
                '<p><a href="{}" target="_blank" class="button">View PDF</a></p>'
                '<p>File name: {}</p>'
                '</div>',
                obj.pdf_file.url,
                obj.pdf_file.name
            )
        return "No file uploaded"
    pdf_file_preview.short_description = 'PDF Preview'

    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }
        js = ('js/admin_enhancements.js',)

# Customize admin site header and title
admin.site.site_header = 'PDF Management System Administration'
admin.site.site_title = 'PDF Management Admin'
admin.site.index_title = 'Welcome to PDF Management System'