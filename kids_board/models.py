from django.db import models
from django.conf import settings


# ファミリーテーブル
# 標準Userを使う為、classは書かない


# こどもテーブル
class Child(models.Model):
    family = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="children"
    )

    child_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "children"
        constraints = [
            models.UniqueConstraint(
                fields=["family", "child_name"], name="unique_family_child_name"
            )
        ]

    def __str__(self):
        return self.child_name


# お支度カテゴリーテーブル
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


# 表示ルールテーブル
class PrepRule(models.Model):
    prep_item = models.ForeignKey("PrepItem", on_delete=models.CASCADE, related_name="rules")

    rule_type = models.CharField(max_length=20)
    weekday = models.BooleanField(default=False)
    day_of_week = models.PositiveSmallIntegerField(null=True, blank=True)
    specific_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "prep_rules"

    def __str__(self):
        return f"{self.prep_item.item_name} - {self.rule_type}"


# 特定日テーブル
class SpecificDate(models.Model):
    start_at = models.DateField()
    end_at = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "specific_dates"

    def __str__(self):
        return f"{self.start_at} ~ {self.end_at}"


# 一日の項目テーブル
class DailyPrepItem(models.Model):
    prep_item = models.ForeignKey(
        "PrepItem",
        on_delete=models.CASCADE,
        related_name="daily_items",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        db_table = "daily_prep_items"

    def __str__(self):
        status = "完了" if self.is_completed else "未完了"
        return f"{self.prep_item.item_name} - {status}"


# スケジュールテーブル
class Schedule(models.Model):
    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name="schedules",
    )

    title = models.CharField(max_length=255)
    schedule_type = models.CharField(max_length=20)
    color = models.IntegerField()

    day_of_week = models.PositiveSmallIntegerField(null=True, blank=True)
    specific_date = models.DateField(null=True, blank=True)

    start_time = models.TimeField()
    end_time = models.TimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "schedules"

    def __str__(self):
        return f"{self.title} - {self.child.child_name}"


# こどもアイコンテーブル
class ChildrenIcon(models.Model):
    icon_name = models.CharField(max_length=255)
    icon_image = models.CharField(max_length=255)

    class Meta:
        db_table = "children_icons"

    def __str__(self):
        return self.icon_name


# 項目アイコンテーブル
class PrepIcon(models.Model):
    icon_name = models.CharField(max_length=255)
    icon_image = models.CharField(max_length=255)

    class Meta:
        db_table = "prep_icons"

    def __str__(self):
        return self.icon_name
