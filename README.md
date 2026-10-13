# Gadget Lending Portal — DevOps CAT-II

A Flask + SQLite mini project for student registration/login, gadget inventory, borrowing requests, administrator approval/rejection, return confirmation, and lending history.

## Pages
- `/register` — student registration
- `/login` — login
- `/inventory` — view available gadgets and submit a borrowing request
- `/requests` — student's requests (admin can view all requests here)
- `/admin/requests` — admin approval/rejection
- `/returns` — confirm the return of approved loans
- `/history` — lending history
- `/admin/gadgets` — admin adds gadgets to inventory

## Default demo admin
- Email: `admin@devapps.local`
- Password: `Admin123!`

Change these values using environment variables before sharing or deploying the project. This is a classroom demo, not a production-ready system.

## Run locally
1. Install Python 3.10+.
2. Create and activate a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the application:
   ```bash
   python app.py
   ```
5. Open `http://127.0.0.1:5000`.

The SQLite database is created automatically. Sample gadgets are inserted on first startup.

## Run with Docker Compose
```bash
docker compose up --build -d
docker compose ps
docker compose logs -f
```
Open `http://localhost:5000`. Stop it with `docker compose down`. Data persists in the `gadget_data` named volume.

## DevOps workflow
1. Create a Git repository and commit the starter project.
2. Create feature branches (for example `feature/auth`, `feature/borrowing`, `feature/admin-returns`) and merge after testing.
3. Configure Jenkins to checkout the repository and run the build/test commands. A GitHub Actions workflow is also included as a basic CI check.
4. Build and run the Docker image locally, then verify the pages.
5. Capture evidence: commit history, branches/merge, CI build, Docker image/container, and functional tests.

## Important note about returns
For this demo, a student can confirm the return of their own approved loan, and an admin can confirm any approved loan. The available quantity is restored when a return is confirmed.
