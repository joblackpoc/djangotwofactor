# **Masterpop New design**
**ยกเลิก media**  
**ยกเลิก staticfiles**  
**ยกเลิก virtualenv**  
**ยกเลิก database**  
# PDF Generator Application

A Django-based PDF generator application with user management and approval workflow.

## Features

- User authentication and authorization
- PDF generation from form input
- Document approval workflow
- Search and filter functionality
- Secure PDF storage and viewing
- Responsive design with Bootstrap 5
- Docker deployment ready

## Technology Stack

- Python 3.11
- Django 5.0
- PostgreSQL
- Redis
- Nginx
- Docker & Docker Compose
- Bootstrap 5
- WeasyPrint/pdfkit
- JavaScript/jQuery

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- PostgreSQL
- Redis

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pdf-generator.git
cd pdf-generator
```

2. Create and configure .env file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Build and run with Docker:
```bash
docker-compose up --build
```

4. Run migrations:
```bash
docker-compose exec web python manage.py migrate
```

5. Create superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

## Development Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup database:
```bash
python manage.py migrate
python manage.py createsuperuser
```

4. Run development server:
```bash
python manage.py runserver
```

## Testing

Run tests with:
```bash
python manage.py test
# or
pytest
```

## Security

This application implements several security measures:

- HTTPS only in production
- CSP (Content Security Policy)
- CSRF protection
- XSS protection
- SQL injection protection
- File upload validation
- Authentication and authorization
- Session security
- Input sanitization

## Production Deployment

1. Update environment variables in .env
2. Build and deploy with Docker:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. Configure Nginx SSL certificates
4. Setup backup system
5. Configure monitoring

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create pull request

## License

licensed under the MIT License - MASTERPOP