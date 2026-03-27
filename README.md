# Flask
A minimal [Flask](https://flask.palletsprojects.com/) web application, served by [Gunicorn](https://docs.gunicorn.org/), and ready to deploy on [Railway](https://railway.app/?referralCode=alphasec) or Vercel.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/igzwwg?referralCode=alphasec)

## Stack
 
- **[Flask](https://flask.palletsprojects.com/)** — Python web framework
- **[Gunicorn](https://docs.gunicorn.org/)** — production WSGI server
- **[Bootstrap 4](https://getbootstrap.com/docs/4.6/)** — frontend styling
 
## Project Structure
 
```
├── main.py              # App entry point and route definitions
├── templates/
│   └── index.html       # Jinja2 HTML template
├── static/
│   └── css/styles.css   # Custom styles
├── requirements.txt     # Python dependencies
├── Procfile             # Railway / Heroku process definition
└── vercel.json          # Vercel deployment config
```
 
## Run Locally
 
```bash
# Clone the repo
git clone https://github.com/alphasecio/flask.git
cd flask
 
# Install dependencies
pip install -r requirements.txt
 
# Start the development server
python main.py
```
 
The app will be available at `http://localhost:5000`.
 
## Deploy to Railway / Vercel
 
* **Railway** — click the button above, or follow the [step-by-step guide](https://alphasec.io/how-to-deploy-a-python-flask-app-on-railway/).
* **Vercel** — `vercel.json` is included for zero-config deployment via the Vercel CLI or GitHub integration.
 
## Extending This Template
 
Add new routes in `main.py`:
 
```python
@app.route('/about')
def about():
    return render_template('about.html')
```
 
Add Python packages to `requirements.txt` and they'll be installed automatically on the next deploy.
