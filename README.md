# VidSnapAI (VideoSnap) 🎬✨

VidSnapAI is an AI-assisted video reel generator web application built with **Python** and **Flask**. It allows creators to upload multiple video clips, provide a text script for voiceover generation, and stitch them into engaging short-form video content (Instagram Reels / Shorts).

---

## 🚀 Features

- **Hero Landing Page (`/`)**: Modern showcase highlighting features and featured reels.
- **Reel Creation Studio (`/create`)**:
  - Multi-file video upload support with dynamic clip adding.
  - Script input area for text-to-speech / AI voiceover generation.
  - Unique UUID generation per creation session for organized asset tracking.
- **Gallery Showcase (`/gallery`)**: Browse and preview previously generated video reels.
- **Responsive UI**: Built with Bootstrap 5, FontAwesome icons, and custom CSS styling.

---

## 📁 Project Structure

```text
videoSnap/
├── main.py              # Flask application backend routes & server entrypoint
├── generate_process.py  # Background worker script for processing uploaded clips
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation and getting started guide
├── templates/           # Jinja2 HTML templates
│   ├── base.html        # Main layout with navbar & footer
│   ├── index.html       # Landing page
│   ├── create.html      # Video upload & reel creation form
│   ├── gallery.html     # Reel showcase gallery
│   └── 404.html         # Custom 404 error page
├── static/              # Static web assets
│   ├── css/             # Custom stylesheets (style.css, create.css, gallery.css)
│   ├── songs/           # Background music audio assets (.mp3)
│   ├── reels/           # Processed and rendered reels (.mp4)
│   └── *.jpg            # Featured showcase images & thumbnails
└── user_uploads/        # Directory containing uploads grouped by session UUID
```

---

## 🛠️ Prerequisites

- **Python 3.8+** installed on your system.
- *(Optional but recommended)* A virtual environment manager (`venv`).

---

## ⚡ Getting Started

### 1. Open the Project Directory

Open your terminal in the project directory:
```powershell
cd c:\Users\ShrikantBhatt\Desktop\Workspace\Python\Python-tut\videoSnap
```

### 2. Set Up a Virtual Environment (Recommended)

Create and activate a virtual environment to isolate project packages:

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
.\venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install the required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```
*(Or install Flask directly: `pip install flask`)*

### 4. Run the Application

Start the Flask development server:
```bash
python main.py
```

By default, the application runs in debug mode and is accessible at:
👉 **http://127.0.0.1:5000**

---

## 🧭 Routes & Endpoints

| Route | HTTP Methods | Description |
|---|---|---|
| `/` | `GET` | Home landing page with feature cards and reel showcase. |
| `/create` | `GET`, `POST` | Upload video clips, enter voiceover text, and submit creation job. |
| `/gallery` | `GET` | Showcase gallery displaying generated video reels. |
| *Any unmatched URL* | `*` | Custom 404 page (`404.html`) with navigation back to Home/Create. |

---

## 🔮 Upcoming Pipeline Features

- [ ] **File Saving & Storage**: Persist uploaded clips into `user_uploads/<uuid>/`.
- [ ] **AI Voiceover Synthesis**: Generate audio speech from input text (e.g., using `gTTS`, `pyttsx3`, or cloud TTS APIs).
- [ ] **Video Stitching & Processing**: Concat clips, resize to 9:16 vertical ratio, overlay audio using `moviepy` or `ffmpeg`.
- [ ] **Dynamic Gallery**: Automatically list generated MP4 files from `static/reels/`.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
