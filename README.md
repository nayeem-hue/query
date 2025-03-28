# Wikipedia Q&A System

An AI-powered question-answering system that uses Wikipedia content to answer questions with spell checking and image support.

## Features
- Smart question answering using Wikipedia content
- Automatic spell checking and corrections
- Related images for visual context
- Google search integration for better results
- Fuzzy matching for similar topics
- Fully accessible design with:
  - Screen reader support
  - Keyboard navigation
  - High contrast mode
  - Text size controls
  - Multiple language support
  - Text-to-speech

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

## Deployment Options

### 1. Render (Recommended - Easiest)

1. Create a free account at [render.com](https://render.com)

2. Create a new Web Service:
   - Connect your GitHub repository
   - Select the Python runtime
   - Set the build command: `pip install -r requirements.txt`
   - Set the start command: `gunicorn app:app`
   - Choose a free instance type

3. Deploy:
   - Render will automatically deploy your application
   - You'll get a URL like `https://your-app-name.onrender.com`

### 2. Heroku

1. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

2. Login to Heroku:
```bash
heroku login
```

3. Create a new Heroku app:
```bash
heroku create your-app-name
```

4. Deploy your code:
```bash
git push heroku main
```

### 3. PythonAnywhere

1. Create a free account at [pythonanywhere.com](https://www.pythonanywhere.com)

2. Upload your code:
   - Use the Files tab to upload your project
   - Or clone from GitHub

3. Set up a web app:
   - Go to the Web tab
   - Choose Manual Configuration
   - Select Python 3.8 or higher
   - Set the working directory to your project folder
   - Set WSGI configuration file to use Flask

### 4. Google Cloud Platform (For scaling)

1. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)

2. Initialize and create a project:
```bash
gcloud init
gcloud app create
```

3. Deploy:
```bash
gcloud app deploy
```

## Environment Variables

Create a `.env` file with these variables:
```
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
```

## Making Your Site Discoverable

1. Add meta tags for SEO (already included in HTML)

2. Submit your site to search engines:
   - [Google Search Console](https://search.google.com/search-console)
   - [Bing Webmaster Tools](https://www.bing.com/webmasters)

3. Create a sitemap.xml:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://your-domain.com/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
```

4. Add robots.txt:
```
User-agent: *
Allow: /
Sitemap: https://your-domain.com/sitemap.xml
```

## Custom Domain Setup

1. Purchase a domain from a registrar (e.g., Namecheap, GoDaddy)

2. Set up DNS records:
   - Add an A record pointing to your hosting IP
   - Add a CNAME record for www subdomain

3. Configure SSL:
   - Most platforms offer free SSL with Let's Encrypt
   - Enable HTTPS redirection

## Monitoring and Analytics

1. Add Google Analytics:
```html
<!-- Add to your HTML head -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
```

2. Set up error monitoring:
   - [Sentry](https://sentry.io)
   - [Rollbar](https://rollbar.com)

## Performance Optimization

1. Enable caching:
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
```

2. Use a CDN for static files:
   - Cloudflare
   - AWS CloudFront

## Support and Updates

For support, please open an issue on GitHub or contact us at your-email@example.com

## License

This project is licensed under the MIT License - see the LICENSE file for details
