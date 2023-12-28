from django.contrib import admin
from .models import Investment, UserValueHistory, CurrentValue, UserStats, itemPrice, Portfolio


# Register your models here.

admin.site.register(Investment)
admin.site.register(UserValueHistory)
admin.site.register(CurrentValue)
admin.site.register(UserStats)
admin.site.register(itemPrice)
admin.site.register(Portfolio)