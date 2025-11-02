# Deploying Backend to Vercel

## Prerequisites
- Vercel CLI installed: `npm install -g vercel`
- Vercel account connected

## Steps to Deploy

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Login to Vercel (if not already):**
   ```bash
   vercel login
   ```

3. **Deploy to Vercel:**
   ```bash
   vercel --prod
   ```

4. **Important Notes:**
   - Templates (`templates/`) and fonts (`fonts/`) directories will be included in the deployment
   - Certificates are stored in `/tmp` on Vercel (serverless limitation)
   - Database is SQLite in `/tmp` - **not persistent between deployments**
   - For production, consider using a persistent database (PostgreSQL, MySQL)

## Environment Variables (Optional)
Set these in Vercel dashboard if needed:
- `PYTHON_VERSION=3.11`

## Vercel Configuration
The `vercel.json` file configures:
- Python runtime
- FastAPI app entry point
- CORS headers
- Maximum lambda size

## Testing After Deployment
Test the deployed API:
```bash
curl https://your-app.vercel.app/
```

Generate a test certificate:
```bash
curl -X POST "https://your-app.vercel.app/certificates/" \
  -H "Content-Type: application/json" \
  -d '{
    "participant_name": "Test User",
    "event_name": "Test Event",
    "date_issued": "2025-11-02",
    "certificate_type": "participation"
  }'
```

## Troubleshooting

### 500 Error
- Check Vercel function logs in dashboard
- Verify templates and fonts are included in deployment
- Ensure Python dependencies in `requirements.txt` are correct

### Template Not Found
- Make sure `templates/` directory exists with:
  - `participation_template.png`
  - `completion_template.png`

### Font Issues
- Verify `fonts/` directory contains Google Sans fonts:
  - `GoogleSans-Bold.ttf`
  - `GoogleSans-Regular.ttf`

## Persistent Storage Alternative
For production with persistent storage:
1. Use external database (Supabase, PlanetScale, etc.)
2. Store certificates in cloud storage (Cloudinary, AWS S3, Azure Blob)
3. Update `SQLALCHEMY_DATABASE_URL` in `app/database.py`
