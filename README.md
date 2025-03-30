# Stock Portfolio Management Dashboard

A modern, dark-themed stock portfolio management dashboard built with Django.

## Features

- Real-time portfolio tracking and analytics
- Interactive stock charts and visualizations
- Portfolio allocation and risk analysis
- Watchlist management
- Multi-user collaboration
- Dark mode UI with modern aesthetics

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Visit http://localhost:8000 in your browser

## Project Structure

- `portfolio/` - Main project directory
- `dashboard/` - Main application
- `templates/` - HTML templates
- `static/` - CSS, JavaScript, and other static files
- `media/` - User-uploaded files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 