from django.db import models
from django.conf import settings


# ファミリーテーブル 
# 標準Userを使う為、classは書かない


#こどもテーブル   
class Child(models.Model):
    family = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="children"
    )

    child_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "children"
        constraints = [
            models.UniqueConstraint(
                fields=["family", "child_name"],
                name="unique_family_child_name"
            )
        ]
    
    def __str__(self):
        return self.child_name
    
    
#お支度カテゴリーテーブル
class PrepCategory(models.Model):
    category_type = models.CharField(max_length=50, unique=True)
    display_order = models.PositiveBigIntegerField(default=0)

    class Meta:
        db_table = "prep_categories"
        ordering = ["display_order"]
    
    def __str__(self):
        return self.category_type

    
# お支度項目テーブル
class PrepItem(models.Model):
    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name="prep_items",
    )
    category = models.ForeignKey(
        PrepCategory,
        on_delete=models.PROTECT,
        related_name="prep_items",
    )

    item_name = models.CharField(max_length=255)
    is_custom = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "prep_items"
        constraints = [
            models.UniqueConstraint(
                fields=["child", "category", "item_name"],
                name="unique_child_category_item_name",
            )
        ]

    def __str__(self):
        return self.item_name



