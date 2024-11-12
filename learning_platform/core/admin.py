from django.contrib import admin
from .models import User, Course, LearningPath, Module, Quiz, Question, Answer, ModuleProgress, QuizProgress, CourseProgress

# User Admin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_admin')
    search_fields = ('username', 'email')

# Course Admin
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'description', 'date_created')
    search_fields = ('course_name',)

# LearningPath Admin
@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ('path_name', 'course', 'date_created')
    search_fields = ('path_name',)

# Module Admin
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('module_name', 'learning_path', 'topic', 'video_link', 'blog_link')
    search_fields = ('module_name', 'topic')
    save_on_top = True
    save_as = True
    
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({
            'save_label': _('Save Module'),
            'save_and_continue_label': _('Save & Continue Editing'),
            'save_and_add_another_label': _('Save & Add Another Module')
        })
        return super().changeform_view(request, object_id, form_url, extra_context)

# Quiz Admin
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('quiz_name', 'module', 'date_created')
    search_fields = ('quiz_name',)

# Question Admin
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'quiz')
    search_fields = ('question_text',)

# Answer Admin
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('answer_text', 'question', 'is_correct')
    search_fields = ('answer_text',)

@admin.register(ModuleProgress)
class ModuleProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'completed', 'completion_date', 'video_watched', 'quiz_completed')
    search_fields = ('user__username', 'module__module_name')
    list_filter = ('completed', 'video_watched', 'quiz_completed')


@admin.register(QuizProgress)
class QuizProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'completed', 'completion_date')
    search_fields = ('user__username', 'quiz__quiz_name')
    list_filter = ('completed',)


@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'completed', 'completion_date', 'progress_percentage')
    search_fields = ('user__username', 'course__course_name')
    list_filter = ('completed',)