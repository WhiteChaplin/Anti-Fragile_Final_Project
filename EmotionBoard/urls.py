from django.urls import path, include
from .views import MainView, IndexView, post_diary, DiaryTempDone, DiaryDetailBeforeSave, DiarySave
from django.conf import settings
from django.conf.urls.static import static
app_name="EmotionBoard"
urlpatterns = [
    # path('account/view',UserView.as_view(), name = "account_view" ),
    path('', MainView.as_view(),name="board_main"),
    path('index/',IndexView.as_view(), name="index_view" ),
    path('post_diary/', post_diary, name="post_diary"),
    path('diary_temp/', DiaryTempDone.as_view(), name="diary_temp"),
    path('diary_detail_before_save/',DiaryDetailBeforeSave.as_view(), name="diary_detail_before_save" ),
    path('diary_save/', DiarySave.as_view())
    
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

