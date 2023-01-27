from django.shortcuts import render, redirect
from django.urls import path
from django.views.generic import TemplateView,CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Movie_Drama_Recommend, Genre_Category, Diary, DiaryTemp, Recommend_Youtube, Emotion_Category
from EmotionBoard.forms import DiaryForm
from scripts.process import predictSenti
# Create your views here.

emotion_dict = {
    "angry":['코미디','드라마','애니메이션','음악'],
    "terror":['모험','판타지','SF', '로맨스'],
    "sadness":['코미디','애니메이션','음악'],
    "loathing":['액션','모험','코미디','가족'],
    "shock":['코미디','드라마','애니메이션','음악'],
    "expect":['코미디','로맨스','SF'],
    "pleasure":['모험','드라마','판타지','SF'],
    "평온":['코미디','가족','음악','애니메이션']
}

genre_list = ['모험','판타지','애니메이션','드라마','액션','코미디','SF','음악','로맨스','가족','TV 영화']

class MainView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'EmotionBoard/mainPage.html'
    
    def test_func(self):
        print(self.request.user)
        return self.request.user.is_superuser or self.request.user.is_staff or self.request.user.is_authenticated
    
    # #해당 장르 영화 가져오는 코드
    # def get_context_data(self, **kwargs):
    #     context = super(MainView,self).get_context_data()
    #     context['categories'] = Movie_Drama_Recommend.objects.filter(genre__name__startswith="로맨스")
    #     print(context['categories'])
    #     return context
    
class IndexView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'EmotionBoard/mainPage_1.html'
    def test_func(self):
        print(self.request.user)
        return self.request.user.is_superuser or self.request.user.is_staff or self.request.user.is_authenticated
    
class DiaryTempDone(TemplateView):
    template_name = "EmotionBoard/diary_temp_save_complete.html"    
    

class DiaryDetailBeforeSave(TemplateView):
    template_name = "EmotionBoard/diary_before_save_detail.html"        
    
def post_diary(request):
    print(f"request : {request.POST}")
    if not request.user.is_authenticated:
        return redirect("/board/")
    else:
        if request.POST:
            if request.method == "POST" and 'diary_temp' in request.POST:
                print(len(DiaryTemp.objects.filter(author = request.user)))
                if len(DiaryTemp.objects.filter(author = request.user)) > 0 :
                    delete_DB = DiaryTemp.objects.filter(author = request.user)
                    delete_DB.delete()
                response = DiaryTemp()
                response.diary_title = request.POST['title']
                # response.diary_img = request.FILES['image']
                print(request.FILES.get('image'))
                response.diary_img = request.FILES.get('image')
                response.diary_content = str(request.POST['content']).strip()
                response.author = request.user
                response.save()
                print("temp")
                return redirect("/board/post_diary")
            elif request.method == "POST" and 'diary_submit' in request.POST:
                response = Diary()
                response.diary_title = request.POST['title']
                print(request.FILES.get('image'))
                if request.FILES.get('image') is None:
                    response.diary_img = DiaryTemp.objects.get(author = request.user).diary_img
                else:
                    response.diary_img = request.FILES.get('image')
                # response.diary_img = request.FILES['image']
                # print(request.FILES['image'])
                diary_content = str(request.POST['content']).strip()
                senti, percentlist = predictSenti(diary_content)
                main = senti[0]
                sub = senti[1]
                response.diary_content = str(request.POST['content']).strip()
                response.author = request.user
                response.main_emotion = Emotion_Category.objects.get(name = "angry")
                response.angry_percent = 43.0
                response.terror_percent = 31.0
                response.sadness_percent = 16.0
                response.loathing_percent = 2.0
                response.shock_percent = 2.0
                response.expect_percent = 2.0
                response.pleasure_percent = 2.0
                response.calmness_percent = 2.0
                response.save()
                print("submit")
                angry_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].angry_percent
                terror_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].terror_percent
                sadness_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].sadness_percent
                loathing_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].loathing_percent
                shock_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].shock_percent
                expect_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].expect_percent
                pleasure_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].pleasure_percent
                calmness_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].calmness_percent
                main_emotion = Diary.objects.filter(author=request.user).order_by("-write_date")[0].main_emotion.name
                
                emotion_list = [angry_score, terror_score, sadness_score, 
                loathing_score, shock_score, expect_score,
                pleasure_score, calmness_score
                ]
                print(emotion_list)
                
                context = {
                    "diary_title":request.POST['title'],
                    "diary_img":Diary.objects.filter(author = request.user).order_by("-write_date")[0].diary_img,
                    "diary_content":str(request.POST['content']).strip(),
                    "movie_genre_list": emotion_dict[main_emotion],
                    "genre_list": genre_list,
                    "youtube_list" : Recommend_Youtube.objects.filter(emotion_id = Emotion_Category.objects.get(name = "sadness")).order_by("?")[:10],
                    "emotion_score": emotion_list,
                    "main_emotion" : main_emotion,
                    "data" : Emotion_Category.objects.all(),
                    'main' : main,
                    'sub' : sub,
                    'percent' :percentlist,
                }
                return render(request, "EmotionBoard/diary_emotion.html", context = context)
            elif request.method == "POST" and 'load_diary' in request.POST:
                get_DB = DiaryTemp.objects.get(author = request.user)
                print(get_DB.diary_title)
                print(get_DB.diary_img)
                print(get_DB.diary_content)
                context = {
                    "diary_title" : get_DB.diary_title,
                    "diary_img" : get_DB.diary_img,
                    "diary_content" : get_DB.diary_content,
                    "form" : DiaryForm()
                }
                return render(request, "EmotionBoard/post_diary_temp.html", context=context)
            elif request.method == "POST" and 'final_save' in request.POST:
                main_emotion = Diary.objects.filter(author=request.user).order_by("-write_date")[0].main_emotion.name
                print("diary_final")
                print(request.POST['title'])
                print(str(request.POST['content']).strip())
                print(main_emotion)
                context = {
                    "main_emotion":main_emotion,
                    "genre_list": genre_list,
                    "youtube_list" : Recommend_Youtube.objects.filter(emotion_id = Emotion_Category.objects.get(name = "sadness")).order_by("?")[:10],
                    "main_emotion" : Diary.objects.filter(author=request.user).order_by("-write_date")[0].main_emotion,
                    "movie_genre_list": emotion_dict.get(main_emotion),
                }
                return render(request, "EmotionBoard/diary_result.html",context=context)
            elif request.method == "POST" and 'movie_drama_recommend' in request.POST:
                print("체크박스")
                genre_select_list = request.POST.getlist('selected')
                
                print(request.POST.getlist('selected'))
                movie_drama_recommend_list = []
                for i in genre_select_list:
                    movie_drama_recommend_list.append(Movie_Drama_Recommend.objects.filter(genre__name__startswith=i).order_by("?")[:5].values())
                print(movie_drama_recommend_list)
                
                angry_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].angry_percent
                terror_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].terror_percent
                sadness_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].sadness_percent
                loathing_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].loathing_percent
                shock_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].shock_percent
                expect_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].expect_percent
                pleasure_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].pleasure_percent
                calmness_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].calmness_percent
                main_emotion = Diary.objects.filter(author=request.user).order_by("-write_date")[0].main_emotion.name
                
                emotion_list = [angry_score, terror_score, sadness_score, 
                loathing_score, shock_score, expect_score,
                pleasure_score, calmness_score
                ]
                
                context = {
                    "main_emotion":main_emotion,
                    "genre_list": genre_list,
                    "youtube_list" : Recommend_Youtube.objects.filter(emotion_id = Emotion_Category.objects.get(name = "sadness")).order_by("?")[:10],
                    "movie_genre_list": emotion_dict.get(main_emotion),
                    "recomment_list" : movie_drama_recommend_list,
                    "selected_list" : genre_select_list,
                    "emotion_score": emotion_list,
                    "main_emotion" : main_emotion,
                    "data" : Emotion_Category.objects.all()
                }
                return render(request, "EmotionBoard/diary_result.html", context = context)
    form = DiaryForm()
    return render(request, "EmotionBoard/post_diary.html", {"form":form})

class DiarySave(TemplateView):
    template_name = "EmotionBoard/diary_final_save.html"        

    
# class PostDiary(LoginRequiredMixin, UserPassesTestMixin,TemplateView):
#     template_name = 'EmotionBoard/post_diary.html'
#     model = Diary
#     def test_func(self):
#         print(self.request.user)
#         return self.request.user.is_superuser or self.request.user.is_staff or self.request.user.is_authenticated
    
#     def form_valid(request):
#         print(f"request : {request}")
#         if request.method == "POST" and 'diary_temp' in request.POST:
#             print("temp")
#         elif request.method == "POST" and 'diary_submit' in request.POST:
#             print("submit")


