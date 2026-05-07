# Create your views here.
from django.views.generic import TemplateView


# todo:LoginRequiredMixinを追加
class HomeView(TemplateView):
    template_name = "/home.html"


# todo:LoginRequiredMixinを追加
class KidsBoardView(TemplateView):
    template_name = "kids_board/kids_board.html"

    # kids_board.htmlに渡すデータ（context)を作るメソッドを定義（花丸表示用）。
    def get_context_data(self, **kwargs):
        # 親クラス(TemplateView)が用意する基本のcontextを取得し、context変数に格納.
        context = super().get_context_data(**kwargs)
        # 花丸を表示する場合はTrueにする。
        # 子供のタスク達成状況などに応じてTrue/Falseを切り替える想定。
        context["show_badge"] = False
        return context


# todo:LoginRequiredMixinを追加
class PrepItemsMornView(TemplateView):
    template_name = "kids_board/prep_items_morn.html"


# todo:LoginRequiredMixinを追加
class PrepItemsView(TemplateView):
    template_name = "kids_board/prep_items.html"


# todo:LoginRequiredMixinを追加
class ScheduleView(TemplateView):
    template_name = "kids_board/schedule.html"
