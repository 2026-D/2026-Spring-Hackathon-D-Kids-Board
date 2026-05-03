from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


# ファミリーテーブル
# 標準Userを使う為、classは書かない

# しほ：Djangoが用意してくれているUserテーブルを使用する
# UserテーブルをFamilyテーブルとして使用


# こどもテーブル
class Child(models.Model):
    family = models.ForeignKey(
        # childが削除されたら、このモデルのデータも消える(CASCADE)
        # related_name="children　→ Userテーブル(family)から、このユーザーの子供一覧を取れる
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="children",
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

    # __str__は文字として表示する時に呼ばれる
    # selfはそのオブジェクト自身(childインスタンス)
    def __str__(self):
        return self.child_name


# お支度カテゴリーテーブル
class PrepCategory(models.Model):
    category_type = models.CharField(max_length=50, unique=True)
    display_order = models.PositiveBigIntegerField(default=0)

    class Meta:
        db_table = "prep_categories"
        # 朝/帰宅後/夜の並び順を固定している
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
        # PROTECT→ PrepItem(子)が存在する限り、PrepCategory(親)は削除できない
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
    # TextChoices → 選択肢を定義するためのクラス
    # rule_typeに入る値をweekdayとspecificの２つに限定し、バグを防ぐ
    class RuleType(models.TextChoices):
        # "weekday" → DBに保存される値
        # "平日" → 画面に表示される名前
        WEEKDAY = "weekday", "平日"
        SPECIFIC = "specific", "特定日"

    prep_item = models.ForeignKey(
        "PrepItem",
        on_delete=models.CASCADE,
        related_name="rules",
    )

    rule_type = models.CharField(
        max_length=20,
        # RuleType.choicesを使用して、rule_typeに入る値を制限している
        choices=RuleType.choices,
        # 🔽ミノルさんコード
        # rule_type = models.CharField(max_length=20)
    )

    weekday = models.BooleanField(default=False)
    day_of_week = models.PositiveSmallIntegerField(null=True, blank=True)

    # しほ：特定日を共通データとして使い回しつつ、無いケースも許容し、参照整合性を壊さないための設定
    specific_date = models.ForeignKey(
        # 特定日テーブル(SpecificDate)を参照
        "SpecificDate",
        # PrepRule が存在する限り SpecificDate は削除されない
        on_delete=models.PROTECT,
        # NULLを許可(曜日ルール(weekday)では特定は必要ない)
        null=True,
        # 入力的に空を許可(フォーム入力しなくてもエラーにしないため)
        blank=True,
        # 逆参照の名前(逆から見た時にわかりやすくするため)
        related_name="prep_rules",
    )

    # 🔽ミノルさんコード
    # DateFieldだと特定日を使い回せず、ER図の設計とズレるため使用しない
    # specific_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "prep_rules"

    def __str__(self):
        # get_フィールド名_display（）で表示用の文字列を取得する
        # "weekday"　→ "平日"
        return self.get_rule_type_display()

        # 🔽ミノルさんコード
        # 関連モデルへの依存を避けるため、シンプルにrule_typeのみを返すため使用しない
        # return f"{self.prep_item.item_name} - {self.rule_type}"


# 特定日テーブル
class SpecificDate(models.Model):
    start_at = models.DateField()
    end_at = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "specific_dates"

    # しほ：バリデーションエラー
    # clean()はこのデータが正しいかチェックする関数
    def clean(self):
        # 開始日が終了日より後にならないようにする
        if self.start_at > self.end_at:
            # raise → エラーを発生させる
            raise ValidationError("開始日は終了日より前にしてください")

    def __str__(self):
        # 期間が分かるように開始日と終了日を表示
        # 例：{{ specific_date }}→　2026-05-01 ~ 2026-05-07
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
        # prep_itemはオブジェクトのため、そのままでは文字列にならないのでstr()で変換する
        return str(self.prep_item)

        # 🔽ミノルさんコード
        # status = "完了" if self.is_completed else "未完了"　← UIの表示はHTML側でやるので使用しない
        # return f"{self.prep_item.item_name} - {status}"


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
        return self.title

        # 🔽ミノルさんコード
        # 関連モデルの依存を避けるために、シンプルにtitleを返すため使用しない
        # return f"{self.title} - {self.child.child_name}"


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
