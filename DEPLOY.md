# Deploy to GitHub

## Prerequisites

- Git installed
- GitHub account

## Steps

### 1. Configure Git (if not already done)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 2. Create initial commit (if not done)

```bash
cd c:\Users\sbpra\New_RAG
git add -A
git commit -m "Initial commit: RAG pipeline + AI podcast generation"
```

### 3. Create a new repository on GitHub

1. Go to [github.com/new](https://github.com/new)
2. Name your repo (e.g. `New_RAG` or `ai-rag-podcast`)
3. Choose Public or Private
4. **Do not** initialize with README, .gitignore, or license (we already have them)
5. Click Create repository

### 4. Push to GitHub

Copy the commands GitHub shows, or run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your GitHub username and repository name.

### 5. Using SSH instead of HTTPS

If you use SSH keys:

```bash
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

---

## What's excluded from the repo

- `.env` (secrets) – never commit; use `.env.example` as template
- `venv/` – Python virtual environment
- `chroma_db/` – vector store data
- `ai_podcast/output/*.mp3` – generated audio
