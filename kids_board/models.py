from django.db import models
from django.conf import settings


# ファミリーテーブル
# 標準Userを使う為、classは書かない

# しほ：Djangoが用意してくれているUserテーブルを使用する
# UserテーブルをFamilyテーブルとして使用


# 🔽こどもテーブル
class Child(models.Model):
    # 親id FK
    parent = models.ForeignKey(
        # childが削除されたら、このモデルのデータも消える(CASCADE)
        # related_name="children　→ Userテーブル(family)から、このユーザーの子供一覧を取れる
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="children",
    )
    # 画像のパスのデータを持っているカラム
    child_icon = models.CharField(max_length=255, blank=True, null=True)

    # 子どもの名前のデータを持っているカラム
    child_name = models.CharField(max_length=50)

    # 作成日時のデータを持っているカラム
    created_at = models.DateTimeField(auto_now_add=True)

    # 更新日時のデータを持っているカラム
    updated_at = models.DateTimeField(auto_now=True)

    # 子どもを論理削除するためのカラム
    deleted_at = models.DateTimeField(null=True, blank=True)

    # 子どもに紐づくお支度項目を管理する中間テーブル
    prep_items = models.ManyToManyField(
        "PrepItem",
        related_name="children",
        verbose_name="お支度項目",
        # お支度項目が未選択でも子どもを保存できる
        blank=True,
    )

    class Meta:
        db_table = "children"
        constraints = [
            # parentとchild_nameをユニーク制約にする事で、
            # 同じユーザーに同名の子どもを登録できないようにしている
            models.UniqueConstraint(
                fields=["parent", "child_name"], name="unique_parent_child_name"
            )
        ]

    # __str__は文字として表示する時に呼ばれる
    # selfはそのオブジェクト自身(childインスタンス)
    def __str__(self):
        return self.child_name


# 🔽お支度項目テーブル
class PrepItem(models.Model):
    # 朝・帰宅後・夜のお支度カテゴリを管理する選択肢
    class CategoryType(models.TextChoices):
        MORNING = "morning", "朝"
        AFTERNOON = "afternoon", "帰宅後"
        NIGHT = "night", "夜"

    # 親id FK
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        # 逆参照
        related_name="prep_items",
    )
    # 朝/帰宅後/夜のカテゴリを管理するカラム
    category_type = models.CharField(
        max_length=20,
        # CategoryTypeで定義したカテゴリのみ選択できるように制限
        choices=CategoryType.choices,
    )

    # お支度項目の名前を持っているデータのカラム
    item_name = models.CharField(max_length=255)

    # ユーザーが独自で作成した項目か判断するフラグ
    is_custom = models.BooleanField(default=False)

    # このお支度項目を一覧に表示するかどうかを管理するフラグ
    # Falseの場合は項目一覧に表示しない
    is_active = models.BooleanField(default=True)

    # カテゴリ内でのお支度項目の表示順を管理するカラム
    display_order = models.PositiveIntegerField(default=0)

    # 作成日時
    created_at = models.DateTimeField(auto_now_add=True)

    # 更新日時
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "prep_items"

        # お支度項目をdisplay_order順に並び替える
        ordering = ["display_order"]

        constraints = [
            # 同じユーザー内で同一カテゴリ・同名のお支度項目を重複登録できないようにする
            models.UniqueConstraint(
                fields=["parent", "category_type", "item_name"],
                name="unique_parent_category_type_item_name",
            )
        ]

    def __str__(self):
        return self.item_name


# 🔽表示ルールテーブル
class PrepRule(models.Model):
    # TextChoices → 選択肢を定義するためのクラス
    class RuleType(models.TextChoices):
        # 左側の値　→ DBに保存される値
        # 右側の値 → 画面に表示される名前

        # 各ルールの判定処理はviews.py側で行う

        # 毎週平日(月〜金)に表示するルール
        WEEKDAY = "weekday", "平日"

        # 祝日に表示するルール
        # ※祝日判定には別途pythonライブラリ(jpholiday)が必要
        HOLIDAY = "holiday", "祝日"

        # 毎週特定の曜日に表示するルール
        DAY_OF_WEEK = "day_of_week", "曜日指定"

        # その日だけのルール（例)予定：遠足/項目：お弁当・水筒・レジャーシート
        SPECIFIC = "specific", "特定日"

    # お支度項目Fk
    prep_item = models.ForeignKey(
        "PrepItem",
        on_delete=models.CASCADE,
        related_name="rules",
    )

    # ルールの種類を管理するカラム
    rule_type = models.CharField(
        max_length=20,
        # RuleType　で定義した選択肢のみ保存できるように制限
        choices=RuleType.choices,
    )

    # 「何曜日か」を数字で保存するためのカラム(曜日指定ルール)
    # 0=月曜, 6=日曜
    # PositiveSmallIntegerField:0以上の小さい整数を保存する
    day_of_week = models.PositiveSmallIntegerField(
        # 曜日指定ルールの時のみ使用するため、
        # NULLと空入力を許可
        null=True,
        blank=True,
    )

    # 特定日ルールで使用する日付カラム
    specific_date = models.DateField(
        null=True,
        blank=True,
    )
    # 作成日時
    created_at = models.DateTimeField(auto_now_add=True)
    # 更新日時
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "prep_rules"

    def __str__(self):
        # get_フィールド名_display（）で表示用の文字列を取得する
        # "weekday"　→ "平日"
        return self.get_rule_type_display()


# 🔽一日の項目履歴テーブル
class PrepItemLog(models.Model):
    # お支度項目FK
    prep_item = models.ForeignKey(
        "PrepItem",
        on_delete=models.CASCADE,
        related_name="logs",
    )
    # 子どもFK
    child = models.ForeignKey(
        "Child",
        on_delete=models.CASCADE,
        related_name="logs",
    )
    # お支度項目がいつの日付のデータなのかを持っているカラム
    target_date = models.DateField()

    # 完了/未完了フラグ
    is_completed = models.BooleanField(default=False)

    class Meta:
        db_table = "prep_items_logs"

        # このテーブルの制約一覧を定義
        constraints = [
            # 同じ子ども・同じお支度項目・同じ日付の
            # 履歴データが重複しないように制限
            models.UniqueConstraint(
                fields=["child", "prep_item", "target_date"], name="unique_child_prep_item_date"
            )
        ]

    def __str__(self):
        # prep_itemはオブジェクトのため、そのままでは文字列にならないのでstr()で変換する
        return str(self.prep_item)


# 🔽スケジュールテーブル
class Schedule(models.Model):
    # スケジュールタグの表示色を管理する選択肢
    class ColorType(models.IntegerChoices):
        RED = 1, "赤"
        YELLOW = 2, "黄色"
        GREEN = 3, "緑"
        EMERALD_GREEN = 4, "エメラルドグリーン"
        SKY_BLUE = 5, "水色"
        BLUE = 6, "青"
        PURPLE = 7, "紫"
        PINK = 8, "ピンク"
        ORANGE = 9, "オレンジ"
        WHITE = 10, "白"

    # 子どもFK
    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    # スケジュールの日付のデータのカラム
    # (例)5/10:学校
    schedule_date = models.DateField()

    # 具体的な予定名のデータのカラム
    title = models.CharField(max_length=255)

    # タグ色・表示色の色番号を管理するカラム
    color = models.IntegerField(
        # ColorTypeで定義した色のみ選択できるように制限
        choices=ColorType.choices
    )

    # 開始時間
    start_time = models.TimeField(null=True, blank=True)  # 時間未定を許可

    # 終了時間
    end_time = models.TimeField(null=True, blank=True)  # 時間未定を許可

    # 作成日時
    created_at = models.DateTimeField(auto_now_add=True)

    # 更新日時
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "schedules"

    def __str__(self):
        return self.title
