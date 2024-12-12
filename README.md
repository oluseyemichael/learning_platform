# pathED-Backend

This repository contains the backend implementation for the All-in-One Self-Learning Platform. Built with Django and Django REST Framework (DRF), it provides APIs to manage users, courses, learning paths, quizzes, and progress tracking.

## Features

- **User Authentication**: Secure registration, login, and email verification using JWT.
- **Learning Paths**: Structured paths with modules covering topics such as web development and digital marketing.
- **Curated Content**: Integration with YouTube and web scraping services to fetch videos and blog links relevant to each topic.
- **Interactive Quizzes**: Auto-generated quizzes for each module with immediate scoring and feedback.
- **Progress Tracking**: Track module completion, video watched status, quiz scores, and overall course progress.
- **Scalability**: Modular architecture to add new features and learning paths as needed.

## Prerequisites

Before running the project, ensure you have the following installed:

- Python 3.8+
- PostgreSQL
- Virtualenv
- Git

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/oluseyemichael/pathED-Backend.git
   cd learning-platform
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   - Create a PostgreSQL database.
   - Update `DATABASES` in `settings.py` with your database credentials.

5. Apply migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /api/v1/register/` - User registration
- `POST /api/v1/login/` - User login
- `POST /api/v1/verify-email/` - Email verification

### Courses and Learning Paths
- `GET /api/v1/courses/` - List all courses
- `GET /api/v1/courses/{id}/` - Retrieve course details
- `GET /api/v1/learning-paths/{id}/` - Retrieve modules in a learning path

### Quizzes
- `GET /api/v1/quizzes/{module_id}/` - Retrieve quiz for a module
- `POST /api/v1/quizzes/{module_id}/submit/` - Submit quiz answers

### Progress Tracking
- `GET /api/v1/progress/` - Retrieve user progress
- `POST /api/v1/progress/update/` - Update progress

## Environment Variables

Set up a `.env` file in the project root with the following variables:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/dbname
EMAIL_HOST=smtp.your-email-provider.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_USE_TLS=True
YOUTUBE_API_KEY='your youtube api key'
SERPAPI_KEY='your serp api key'
```

## Testing

Run tests to ensure everything works as expected:
```bash
python manage.py test
```

## Deployment

This backend is configured for deployment on Heroku. Ensure you set up the required environment variables and a PostgreSQL database on Heroku.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes and commit them:
   ```bash
   git commit -m "Add your message here"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

For any issues or feature requests, please open an issue on the [GitHub repository](https://github.com/oluseyemichael/pathED-Backend).
