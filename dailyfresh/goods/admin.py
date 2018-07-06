from django.contrib import admin
from goods.models import *
from django.core.cache import cache



def delete_model(modeladmin, request, queryset):
    print('delete_model...')
    for obj in queryset:
        # obj.is_delete = True
        obj.delete()
    cache.delete('cache_index_page_data')


class BaseAdmin(admin.ModelAdmin):
    actions = [delete_model]
    def save_model(self, request, obj, form, change):
        print('save_model...')
        '''新增或更新表中的数据时调用'''

        # 重新调用父类方法完成save
        super().save_model(request, obj, form, change)
        # 清除首页的缓存数据
        cache.delete('cache_index_page_data')




class GoodsAdmin(BaseAdmin):
    pass

class GoodsSKUAdmin(BaseAdmin):
    pass

class GoodsTypeSKUAdmin(BaseAdmin):
    pass



admin.site.register(Goods, GoodsAdmin)
admin.site.register(GoodsSKU,GoodsSKUAdmin)
admin.site.register(GoodsType,GoodsTypeSKUAdmin)
admin.site.register(IndexGoodsBanner)
admin.site.register(IndexTypeGoodsBanner)
admin.site.register(IndexPromotionBanner)
admin.site.register(GoodsImage)
