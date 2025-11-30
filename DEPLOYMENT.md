# Deployment Instructions

## Local Development

### Prerequisites
- Python 3.10+
- PostgreSQL database

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/grocery_db"
export SESSION_SECRET="your-secret-key"

# Run the application
python app.py
```

The application will be available at `http://localhost:5000`

## Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--reuse-port", "app:app"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/grocery_db
      - SESSION_SECRET=your-secret-key
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=grocery_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### Run with Docker
```bash
docker-compose up -d
```

## Render Deployment

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --reuse-port app:app`
4. Add Environment Variables:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `SESSION_SECRET`: A secure random string
5. Deploy

## Railway Deployment

1. Create a new project on Railway
2. Add a PostgreSQL database
3. Deploy from GitHub
4. Railway will auto-detect Python
5. Set Start Command: `gunicorn --bind 0.0.0.0:$PORT --reuse-port app:app`
6. Add Environment Variables if needed

## PythonAnywhere Deployment

1. Create a free account on PythonAnywhere
2. Upload your code via Git or zip file
3. Create a virtual environment:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 grocery
   pip install -r requirements.txt
   ```
4. Configure WSGI file:
   ```python
   import sys
   path = '/home/yourusername/grocery_billing_system'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app as application
   ```
5. Set up PostgreSQL (requires paid plan) or use SQLite
6. Reload web app

## Security: Default Credentials

The application creates default demo accounts on first run:
- Admin: `admin` / `admin123`
- Cashier: `cashier` / `cashier123`

**For production deployment, you MUST set these environment variables:**
```bash
export ADMIN_PASSWORD="your-secure-admin-password"
export CASHIER_PASSWORD="your-secure-cashier-password"
```

## Production Checklist

- [ ] **CRITICAL: Set ADMIN_PASSWORD and CASHIER_PASSWORD environment variables**
- [ ] Set `DEBUG=False` in production
- [ ] Use strong `SESSION_SECRET`
- [ ] Configure HTTPS
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Delete or deactivate demo accounts after creating real admin accounts
