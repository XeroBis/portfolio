# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django 5.1 portfolio website with a workout tracking application. The project uses PostgreSQL as the database, supports internationalization (English/French), and can be deployed via Docker or run locally with uv.

## Development Setup

### Package Management
This project uses **uv** for Python dependency management, not pip or poetry.

```bash
# Install dependencies
uv sync --extra dev

# Run Django commands
uv run python manage.py <command>
```


### Running the Application

**Local development (with Docker):**
```bash
make build    # Build and start dev containers
make up       # Start existing containers
make down     # Stop containers
```

**Production (with Docker):**
```bash
make prod-build    # Build and start production containers
make prod-up       # Start existing production containers
make prod-down     # Stop production containers
```

**Local development (without Docker):**
Ensure PostgreSQL is running locally with credentials matching your `.env` file, then:
```bash
uv run python manage.py runserver
```

## Common Commands

### Database Operations
```bash
make makemigrations              # Create new migrations
```

### Static Files
```bash
make static    # Collect static files (required before deployment)
```

### Internationalization
The project supports English and French translations:
```bash
make makemessages    # Extract messages for EN and FR
make comp            # Compile message files
```

### Code Quality & Testing

**Format code:**
```bash
make format    # Run black and isort
```

**Lint code:**
```bash
make lint      # Run flake8 on apps/ and mysite/
```

**Run all pre-commit checks:**
```bash
make checks    # Run all pre-commit hooks
```

Pre-commit hooks include: black, isort, flake8, mypy, bandit, django-upgrade, detect-secrets, and standard file checks.

## Project Architecture

### Structure
- `mysite/` - Django project settings and root URL configuration
- `apps/home/` - Home/landing page application
- `apps/workout/` - Workout tracking application (main feature)
- `locale/` - Translation files for i18n support

### Workout App Architecture

The workout app uses a **polymorphic exercise log system** to handle different exercise types:

**Core Models:**
- `Workout` - Represents a workout session with date, type, and duration
- `TypeWorkout` - Categorizes workouts (e.g., strength, cardio)
- `Exercice` - Exercise library with metadata (muscle groups, equipment, difficulty)
- `MuscleGroup` and `Equipment` - Many-to-many relationships with exercises

**Exercise Logging System:**
The app supports two logging approaches:

1. **Legacy aggregated logs** (being phased out):
   - `StrengthExerciseLog` - Aggregated strength data (sets × reps @ weight)
   - `CardioExerciseLog` - Aggregated cardio data (duration, distance)

2. **Series-based logs** (current approach):
   - `StrengthSeriesLog` - One row per set (exercise, series_number, reps, weight)
   - `CardioSeriesLog` - One row per interval (exercise, series_number, duration, distance)

**Polymorphic Design:**
`OneExercice` uses Django's `GenericForeignKey` to reference either type of exercise log. This allows different exercise types to be stored in specialized tables while maintaining a unified interface.

The `position` field in `OneExercice` determines the order of exercises within a workout.

### Important Configuration Details

**Database:** PostgreSQL is required (configured in `mysite/settings.py`)

**Settings Module:** `mysite.settings`

**Static Files:**
- Static files from both apps are collected into `staticfiles/` directory
- Template directories are explicitly configured in settings: `apps/home/templates/home` and `apps/workout/templates/workout`

**Timezone:** Set to "CET" (Central European Time)

**Security:** The project has development-appropriate security settings. SSL redirect, session cookies, and CSRF cookies are configured for non-secure connections in development.

### Management Commands

**Home app commands:**
- `clear_home_data` - Clear home app data
- `download_home_data` - Download external home data
- `ensure_superuser` - Create superuser if not exists
- `import_home_data` - Import home data from files
- `wait_for_db` - Wait for database to be ready (used in Docker)

**Workout app commands:**
- `clear_workout_data` - Clear workout data
- `export_workout_data` - Export workout data to JSON
- `import_workout_data` - Import workout data from JSON

### Template Tags
The workout app includes custom template filters in `apps/workout/templatetags/custom_filters.py`.

## Code Quality Standards

This project enforces strict code quality through pre-commit hooks:

- **Black** (line length: 88) - Code formatting (excludes migrations)
- **isort** (black profile) - Import sorting (excludes migrations)
- **flake8** - Linting with docstring and bugbear checks
- **mypy** - Type checking with django-stubs plugin (ignores migrations)
- **pylint** - Django-aware linting (disables docstring requirements)
- **bandit** - Security linting
- **django-upgrade** - Ensures Django 5.1+ compatible code

Configuration is centralized in `pyproject.toml`.

## Docker Deployment

Three Docker Compose configurations exist:
- `docker-compose.yml` - Development environment
- `docker-compose.prod.yml` - Production environment
- `docker-compose.nginx.yml` - Production with nginx

The Django service uses a custom Dockerfile in `dockerfiles/web/Dockerfile` and runs `entrypoint.sh` on startup.
