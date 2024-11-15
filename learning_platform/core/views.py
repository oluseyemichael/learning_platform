from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import Course, LearningPath, Module, Quiz, Question, ModuleProgress, QuizProgress, CourseProgress, LearningPathProgress
from .serializers import CourseSerializer, LearningPathSerializer, ModuleSerializer, QuizSerializer, UserSerializer, ModuleProgressSerializer, QuizProgressSerializer, CourseProgressSerializer
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import action,  api_view, permission_classes
from rest_framework import status
import logging
logger = logging.getLogger(__name__)

User = get_user_model()  # This will import the custom User model

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                user = serializer.save()
                user.is_active = False  # Mark user as inactive until they verify their email
                user.save()

                # Generate email verification token
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                # Construct the verification link
                verification_link = f"{settings.FRONTEND_URL}/verify-email?uid={uid}&token={token}"
                send_mail(
                    'Verify Your Account',
                    f'Hi, Welcome to pathED. Please click the following link to verify your account: {verification_link}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email]
                )

                return Response({
                    'message': 'Registration successful. Check your email to verify your account.',
                    'user': {
                        'username': user.username,
                        'email': user.email,
                    }
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': 'Registration failed',
                    'details': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    def get(self, request):
        uid = request.GET.get('uid')
        token = request.GET.get('token')
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': 'Email verified successfully.'})
        
        return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        # # Try to find user by email
        # try:
        #     user = User.objects.get(email=email)
        #     username = user.username
        # except User.DoesNotExist:
        #     return Response({
        #         'error': 'No account found with this email'
        #     }, status=status.HTTP_404_NOT_FOUND)
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user:
            if not user.is_active:
                return Response({
                    'error': 'Please verify your email to activate your account.'
                }, status=status.HTTP_403_FORBIDDEN)
                
            refresh = RefreshToken.for_user(user)
            return Response({
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                },
                'user': {
                    'username': user.username,
                    'email': user.email,
                }
            })
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f"{request.build_absolute_uri('/api/v1/reset-password-confirm/')}?uid={uid}&token={token}"
            
            send_mail(
                subject="Reset Your Password",
                message=f"Click the link to reset your password: {reset_url}",
                from_email="pathed.001@gmail.com",
                recipient_list=[user.email],
            )
            return Response({'message': 'Password reset email sent.'})
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

class PasswordResetConfirmView(APIView):
    def post(self, request):
        uid = request.GET.get('uid')
        token = request.GET.get('token')
        new_password = request.data.get('new_password')
        
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid link'}, status=status.HTTP_400_BAD_REQUEST)
        
        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password reset successful'})
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

# Course ViewSet
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]  # Protecting this route

# Learning Path ViewSet
class LearningPathViewSet(viewsets.ModelViewSet):
    queryset = LearningPath.objects.all()
    serializer_class = LearningPathSerializer
    permission_classes = [IsAuthenticated]

# Module ViewSet
class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]

# Quiz ViewSet
class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

# Module Progress ViewSet
class ModuleProgressViewSet(viewsets.ModelViewSet):
    queryset = ModuleProgress.objects.all()
    serializer_class = ModuleProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get('user')
        if user_id:
            return self.queryset.filter(user_id=user_id)
        return self.queryset

# Quiz Progress ViewSet
class QuizProgressViewSet(viewsets.ModelViewSet):
    queryset = QuizProgress.objects.all()
    serializer_class = QuizProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get('user')
        if user_id:
            return self.queryset.filter(user_id=user_id)
        return self.queryset

# Course Progress ViewSet
class CourseProgressViewSet(viewsets.ModelViewSet):
    queryset = CourseProgress.objects.all()
    serializer_class = CourseProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get('user')
        if user_id:
            return self.queryset.filter(user_id=user_id)
        return self.queryset

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    user_data = {
        "username": user.username,
        "email": user.email,
    }

    # Fetch course progress data for the user
    progress_data = CourseProgress.objects.filter(user=user)
    progress_serialized = CourseProgressSerializer(progress_data, many=True).data

    user_data["progress_data"] = progress_serialized
    return Response(user_data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_course_progress(request, course_id):
    user = request.user
    progress_percentage = request.data.get("progress_percentage", 0)

    # Update or create course progress for this user and course
    progress, created = CourseProgress.objects.update_or_create(
        user=user,
        course_id=course_id,
        defaults={"progress_percentage": progress_percentage}
    )

    # Recalculate and update progress status
    progress.calculate_progress()

    return Response({"message": "Progress updated successfully", "progress": CourseProgressSerializer(progress).data})

@api_view(['GET'])
def get_module_by_name(request, module_name):
    try:
         # Prefetch quizzes and their related questions and answers
        module = Module.objects.prefetch_related(
            Prefetch(
                'quizzes',
                queryset=Quiz.objects.prefetch_related('questions__answers')
            )
        ).get(module_name=module_name)
        serializer = ModuleSerializer(module)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Module.DoesNotExist:
        return Response({'error': 'Module not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Log the error for debugging
        print(f"Error fetching module: {str(e)}")
        return Response({'error': 'An unexpected error occurred'}, status=500)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_module_progress(request, module_id):
    try:
        module_progress, created = ModuleProgress.objects.update_or_create(
            user=request.user, module_id=module_id,
            defaults={'video_watched': True}
        )
        module_progress.calculate_progress()
        return Response(ModuleProgressSerializer(module_progress).data)
    except Module.DoesNotExist:
        return Response({"error": "Module not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_quiz_score(request, quiz_id):
    score = request.data.get("score", 0)
    try:
        quiz_progress, created = QuizProgress.objects.update_or_create(
            user=request.user, quiz_id=quiz_id,
            defaults={'score': score}
        )
        quiz_progress.calculate_progress()
        return Response(QuizProgressSerializer(quiz_progress).data)
    except Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_course_progress(request, course_id):
    try:
        course_progress = CourseProgress.objects.get(user=request.user, course_id=course_id)
        course_progress.calculate_progress()
        return Response(CourseProgressSerializer(course_progress).data)
    except CourseProgress.DoesNotExist:
        return Response({"error": "Course progress not found"}, status=status.HTTP_404_NOT_FOUND)