# Publish the demo: GitHub + Render

GitHub shares the source code; Render runs the Python application and provides a public URL. This is a fictional-data demonstration only. Do not enter actual patient information.

## 1. Put the project on GitHub

1. Create a new **public** repository named `mri-prior-auth-demo` at https://github.com/new. Leave the README, license, and `.gitignore` starter options unchecked, because this project already includes its own files.
2. Extract the ZIP and open the inner `prior-auth-assistant` folder. Select its **contents**, including `.env.example`, `.gitignore`, `.python-version`, `data/`, `static/`, and `templates/`. On the empty GitHub repository page, choose **uploading an existing file** (or **Add file > Upload files**) and drag those selected contents into the page. Commit them. The repository root should directly show `web.py`, `requirements.txt`, and `README.md`, with `data/` as a folder. Do **not** upload `.env` or `.venv`.
3. Open `https://github.com/YOUR-USERNAME/mri-prior-auth-demo` to confirm the source is visible. This URL is also the assignment's repository link.

## 2. Run it on Render

1. Sign in at https://dashboard.render.com and choose **New > Web Service**. Connect GitHub and select the repository.
2. Set **Language** to `Python 3`, **Build Command** to `pip install -r requirements.txt`, and **Start Command** to:

   ```bash
   gunicorn --workers 1 --threads 1 --timeout 120 --bind 0.0.0.0:$PORT web:app
   ```

3. Select the **Free** instance type if available. In the service's **Environment** settings, add `GEMINI_API_KEY` with the real key from https://aistudio.google.com/api-keys. Keep the value in Render's environment settings, never in GitHub. The included `.python-version` selects Python 3.12. The optional `GEMINI_MODEL` defaults to `gemini-3.5-flash-lite`.
4. Deploy. When Render shows **Live**, open its `https://...onrender.com` URL. Test P001, then accept or reject the proposal. `/health` returns `ok` if the web server is running.

## Limits of this demo

The checkpointer lives in the single web process's memory. If Render restarts or spins down between proposal and review, that pending review is lost; start a new request. Free instances can spin down after inactivity and take time to start again. Anyone with the public URL can send fictional notes using your configured Gemini key, subject to your account's quota. For a durable or broadly used service, add persistent checkpoint storage, access controls, request limits, and proper deployment monitoring.
