from rest_framework import serializers
from django.contrib.auth.models import User
from .models import User, Course, LearningPath, Module, Quiz, Question, ModuleProgress, QuizProgress, CourseProgress

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'full_name')
        extra_kwargs = {
            'password': {'write_only': True},  # Password should not be readable
            'email': {'required': True, 'allow_blank': False},  # Ensure email is required and not blank
            'full_name': {'required': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            full_name=validated_data['full_name']
        )
        return user

class CourseSerializer(serializers.ModelSerializer):
    learning_paths = serializers.StringRelatedField(many=True)

    class Meta:
        model = Course
        fields = ['course_name', 'description', 'learning_paths']

class LearningPathSerializer(serializers.ModelSerializer):
    modules = serializers.StringRelatedField(many=True)

    class Meta:
        model = LearningPath
        fields = ['path_name', 'modules']

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['module_name', 'topic', 'video_link', 'blog_link']

class QuizSerializer(serializers.ModelSerializer):
    questions = serializers.StringRelatedField(many=True)

    class Meta:
        model = Quiz
        fields = ['quiz_name', 'questions']

class QuestionSerializer(serializers.ModelSerializer):
    answers = serializers.StringRelatedField(many=True)

    class Meta:
        model = Question
        fields = ['question_text', 'answers']

class ModuleProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleProgress
        fields = ['user', 'module', 'completed', 'completion_date', 'video_watched', 'quiz_completed']

class QuizProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizProgress
        fields = ['user', 'quiz', 'score', 'completed', 'completion_date']

class CourseProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseProgress
        fields = ['user', 'course', 'completed', 'completion_date', 'progress_percentage']