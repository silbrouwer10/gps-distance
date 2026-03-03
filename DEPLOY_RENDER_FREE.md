# Deploy this copy for free (Render)

This folder is prepared to deploy on Render's **free web service**.

## 1) Push this folder to GitHub
Create a new repository and push the contents of this folder.

## 2) Create the Render service
1. In Render: New + -> Blueprint
2. Select your repository
3. Render will detect `render.yaml`
4. Deploy

## 3) Set environment values in Render
The blueprint already sets:
- `DEBUG=False`
- generated `SECRET_KEY`

Update `ALLOWED_HOSTS` to your real Render hostname if you changed the service name.

## 4) Notes about free hosting
- Free services can sleep after inactivity (cold starts).
- Free filesystem is ephemeral; uploaded/generated files may disappear after restart.
- SQLite is okay for small/demo use, but for production use a managed Postgres DB.

## 5) Local run from this copy
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
