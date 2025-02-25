<div align="center">
   <a href="https://github.com/Sang-Buster/AeroLex-Editor">
      <img src="/frontend/public/favicon.png" width=20% alt="logo">
   </a>
   <h1>AeroLex Editor</h1>
   <h6><small>A powerful web-based editor for transcription and subtitle files with real-time audio/video sync capabilities</small></h6>
   <p><b>#Air Traffic Control Communication &emsp; #Automatic Speech Recognition &emsp; #Aviation &emsp; #NLP &emsp; #LLM &emsp; #Whisper &emsp; #Ollama </b></p>
</div>

<div align="center">

<a href="https://github.com/Sang-Buster/AeroLex-Editor">
  <img src="/README.assets/web.png" width=100% alt="webui">
</a>

## 🔍 Table of Contents

</div>

- [🔍 Table of Contents](#-table-of-contents)
- [✨ Features](#-features)
  - [Frontend Features](#frontend-features)
  - [Backend Features](#backend-features)
- [👨‍💻 Tech Stack](#-tech-stack)
  - [Frontend](#frontend)
  - [Backend](#backend)
- [🚀 Getting Started](#-getting-started)
  - [Frontend Setup](#frontend-setup)
  - [Backend Setup](#backend-setup)
- [📁 Project Structure](#-project-structure)
- [🤝 Contributing](#-contributing)

<div align="center">

## ✨ Features

</div>

### Frontend Features
- 🎬 Real-time audio/video sync with transcripts
- 📝 Live editing of transcriptions
- 🎯 Word-level playback tracking
- 🎨 Confidence score visualization
- 📊 Multiple export formats (SRT, VTT, JSON, Plaintext)
- 🔄 Subtitle track offset adjustment
- 🖥️ Local-first processing - all data stays in your browser

### Backend Features
- 🎤 Speech-to-text using Whisper
- 🤖 Text analysis and summarization with Ollama
- 📝 Multiple subtitle format support
- 🔄 Format conversion utilities

<div align="center">

## 👨‍💻 Tech Stack

</div>

### Frontend
- SvelteKit
- TypeScript
- TailwindCSS
- Media Web APIs

### Backend
- Whisper ASR
- Ollama
- Spacy

<div align="center">

## 🚀 Getting Started

</div>

### Frontend Setup
1. **Install Node.js using nvm:**
```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# Reload shell configuration
source ~/.bashrc  # or source ~/.zshrc

# Install and use Node.js
nvm install node
nvm use node

# Install dependencies
cd frontend
npm install
```

2. **Available Commands:**
```bash
# Development
npm run dev          # Start development server with vite
npm run build        # Build for production
npm run preview      # Preview production build

# Testing
npm run test         # Run tests
npm run test:watch   # Run tests in watch mode

# Type Checking & Formatting
npm run check        # Run svelte-check
npm run format       # Format code with prettier
```

### Backend Setup
1. **Install uv:**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. **Create and activate virtual environment:**
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
cd backend
uv pip install -r requirements.txt
```

4. **Install `ruff` and `pre-commit`:**
```bash
uv pip install ruff pre-commit
```
   - `pre-commit` helps maintain code quality by running automated checks before commits are made.
   - `ruff` is a modern Python code formatter and linter.

5. **Install git hooks:**
```bash
pre-commit install --hook-type commit-msg --hook-type pre-commit --hook-type pre-push
```

   These hooks perform different checks at various stages:
   - `commit-msg`: Ensures commit messages follow the conventional format
   - `pre-commit`: Runs Ruff linting and formatting checks before each commit
   - `pre-push`: Performs final validation before pushing to remote

6. **Code Linting & Formatting:**
```bash
# Linting
ruff check              # Run ruff linter
ruff check --select I   # Check import order
ruff check --fix        # Auto-fix linting issues
ruff check --select I --fix  # Auto-fix import order

# Formatting
ruff format            # Format code
```

<div align="center">

## 📁 Project Structure

</div>

```
📦wscribe-editor
┣ 📂frontend
┃ ┣ 📂public
┃ ┣ 📂src
┃ ┣ 📂static
┃ ┗ 📂tests
┣ 📂backend
┣ 📂README.assets
┣ 📄.gitignore
┣ 📄.pre-commit-config.yaml
┣ 📄.pre-commit_msg_template.py
┣ 📄README.md
┗ 📄LICENSE
```

<div align="center">

## 🤝 Contributing

</div>

We welcome contributions! To contribute:
1. Fork the repository
2. Create a new branch (`feature/amazing_feature`)
3. Commit your changes
4. Push to the branch
5. Open a Pull Request
