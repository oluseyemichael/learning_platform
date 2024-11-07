from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model  # Import get_user_model
from .services.youtube_service import get_youtube_videos
from .services.blog_service import get_blog_posts
from django.core.validators import EmailValidator
from django.utils import timezone
from django.db.models import Q


# User model
class User(AbstractUser):
    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        error_messages={
            'unique': "A user with that email already exists.",
        }
    )
    is_admin = models.BooleanField(default=False)
    
    # Use username as the primary identifier
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'full_name']


User = get_user_model()  # Assigning User model via get_user_model()

# Course model
class Course(models.Model):
    course_name = models.CharField(max_length=255)
    description = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.course_name

# LearningPath model
class LearningPath(models.Model):
    path_name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, related_name='learning_paths', on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.path_name

# Module model with auto-fetching for YouTube video and blog content
class Module(models.Model):
    module_name = models.CharField(max_length=255)
    learning_path = models.ForeignKey(LearningPath, related_name='modules', on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    video_link = models.CharField(max_length=500, blank=True)
    blog_link = models.CharField(max_length=500, blank=True)

    def save(self, *args, **kwargs):
        # Fetch the highest-rated, latest 15-minute YouTube video based on the topic
        youtube_videos = get_youtube_videos(self.topic)
        if youtube_videos:
            print(f"Video fetched: {youtube_videos[0]['url']}")
            self.video_link = youtube_videos[0]['url']  # Use the best match

        # Fetch blog content
        blog_post = get_blog_posts(self.topic)
        if blog_post:
            print(f"Blog fetched: {blog_post['url']}")
            self.blog_link = blog_post['url']

        super(Module, self).save(*args, **kwargs)

    def __str__(self):
        return self.module_name

# Quiz model
class Quiz(models.Model):
    quiz_name = models.CharField(max_length=255)
    module = models.ForeignKey(Module, related_name='quizzes', on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.quiz_name

# Question model
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField()

    def __str__(self):
        return self.question_text

# Answer model
class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.answer_text

# Progress Tracking Models
class ModuleProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="module_progress")
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    video_watched = models.BooleanField(default=False)  # Track if video content is completed
    quiz_completed = models.BooleanField(default=False)  # Track if module quiz is completed

    def calculate_progress(self):
        # Calculate if module progress is complete
        self.completed = self.video_watched and self.quiz_completed
        if self.completed:
            self.completion_date = timezone.now()
        else:
            self.completion_date = None
        self.save()

        # Update CourseProgress whenever a module's progress changes
        course_progress = CourseProgress.objects.filter(user=self.user, course=self.module.learning_path.course).first()
        if course_progress:
            course_progress.calculate_progress()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.calculate_progress()

    def __str__(self):
        return f"{self.user.username} - {self.module.module_name} - {'Completed' if self.completed else 'In Progress'}"

class QuizProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz_progress")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)

    def calculate_progress(self):
        self.completed = self.score >= 70.0  # passing score of 70%
        if self.completed:
            self.completion_date = timezone.now()
        else:
            self.completion_date = None
        self.save()

        # Trigger course progress update
        course_progress = CourseProgress.objects.filter(user=self.user, course=self.quiz.module.learning_path.course).first()
        if course_progress:
            course_progress.calculate_progress()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.calculate_progress()

    def __str__(self):
        return f"{self.user.username} - {self.quiz.quiz_name} - {'Completed' if self.completed else 'In Progress'}"

class CourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="course_progress")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.FloatField(default=0.0)  # Track overall progress as a percentage

    def calculate_progress(self):
        total_modules = self.course.learning_paths.aggregate(
            total_modules=models.Count('modules')
        )['total_modules'] or 0
        completed_modules = ModuleProgress.objects.filter(
            user=self.user, module__learning_path__course=self.course, completed=True
        ).count()

        if total_modules > 0:
            self.progress_percentage = (completed_modules / total_modules) * 100
            self.completed = self.progress_percentage == 100
            if self.completed:
                self.completion_date = timezone.now()
            self.save()

    def __str__(self):
        return f"{self.user.username} - {self.course.course_name} - {self.progress_percentage}% complete"