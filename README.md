# JOB LISTING API

A backend API for a job board application, inspired by platforms like Jobberman, enabling job seekers and recruiters to manage listings, applications, and company profiles. Built with **FastAPI**, **SQLModel**, **PostgreSQL**, **Celery**, **Redis**, and Dockerized for seamless deployment.

---

## 🚀 Features

- User authentication (JWT-based)
- Role-based access control (Admin, Employer, User)
- Job creation and listing
- Application submission
- Email notifications via SMTP
- Background task handling with Celery
- Dockerized for consistent environments
- Redis-backed task queue

---

## ⚙️ Tech Stack

- **Backend:** FastAPI + SQLModel
- **Database:** PostgreSQL
- **Task Queue:** Celery
- **Queue Broker:** Redis
- **Email:** SMTP (Gmail)
- **Containerization:** Docker & Docker Compose
- **Testing:** Pytest
- **CI/CD:** GitHub Actions

---

## 🛠️ Getting Started

### 1. Clone the Repo
```bash
git clone https://github.com/egcarson/job-api.git
cd job-api
```

### 2. Set Up Environment
Create a `.env` file:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/job_db
JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256
MAIL_USERNAME=your@mail.com
MAIL_PASSWORD=your_password
MAIL_SERVER=smtp.mailtrap.io
MAIL_PORT=2525
MAIL_STARTTLS=True
```

> ⚠️ Never commit your real credentials. Use environment variables.

---

### 3. Run with Docker
```bash
docker-compose up --build
```

Visit:
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 4. Running Tests
```bash
pytest -v
```

---

## 🚚 CI/CD (GitHub Actions)

CI pipeline is triggered on every push or PR to `main` branch. It:
- Installs dependencies
- Runs tests
- Deploys if test passes

---

## 🔐 Authentication

- JWT-based access
- `/login` returns `access_token` and `refresh_token`
- Protected endpoints require `Authorization: Bearer <token>`
- Token refresh supported via `/refresh_token`

---

## 🧪 Example API Flow

1. Register User → `/register`
2. Login → `/login` → `access_token`, `refresh_token`
3. Post Job → `/jobs` (Employer only)
4. Apply to Job → `/applications`

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss.

---

## 📄 License

MIT License.

---

## ✨ Author

Developed by [@Egcarson](https://github.com/Egcarson)
