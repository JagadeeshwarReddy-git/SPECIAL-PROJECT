# AI-Based Social Media Analytics

A Streamlit-based project for analyzing social-media content and comments. The application includes YouTube analysis, text/file analysis, analytics, trend exploration, an AI assistant, reports, history, a dashboard, and video comparison.

> **Project note:** Features and setup below are based on the source-code package. Some features may require API credentials or locally running AI services.

## Features

- **YouTube Analyzer** – analyze YouTube video/comment data.
- **Text Analyzer** – analyze text supplied by the user.
- **File Analyzer** – load supported files for analysis.
- **Analytics** – view analysis results and visualizations.
- **Trend Analyzer** – explore trends in analyzed content.
- **AI Assistant** – AI-assisted analysis and explanations.
- **Reports** – generate or view analysis reports.
- **History** – access saved analysis history.
- **Dashboard** – view project analytics in one place.
- **Video Comparison** – compare selected YouTube videos.

The project uses Streamlit for its web interface and Python libraries for data processing, NLP, machine learning, visualization, YouTube/Google API access, and file parsing.

## Technology Stack

- Python
- Streamlit
- Pandas, NumPy, SciPy
- scikit-learn
- Transformers, PyTorch, Sentence Transformers, NLTK
- Matplotlib, Plotly, Altair
- Google API Python Client (YouTube/Google APIs)
- PRAW (Reddit API client)
- Requests, python-dotenv
- OpenPyXL, xlrd, pypdf, python-docx, python-pptx, Pillow
- PyYAML, pytesseract

See [`requirements.txt`](requirements.txt) for dependency version ranges.

## Project Structure

```text
SP PROJECT/
├── app.py
├── config.py
├── requirements.txt
├── database.py
├── auth/
├── components/
├── services/
├── views/
├── ui/
├── utils/
├── preprocessing/
├── evaluation/
├── reports/
├── assets/
├── data/
│   ├── raw/
│   └── cleaned/
└── analysis_details/
```

### Important folders

- `views/` – Streamlit page modules.
- `services/` – analysis, YouTube, summarization, chart, history, and report services.
- `components/`, `ui/` – reusable interface components.
- `auth/` – authentication-related modules.
- `preprocessing/` – text cleaning.
- `evaluation/` – sentiment evaluation scripts, sample data, and metrics.
- `reports/` – report-related code and project report assets.
- `assets/` – CSS and other interface assets.
- `data/` – raw and cleaned project datasets.
- `analysis_details/` – saved analysis detail records.

## Requirements

- Python **3.10 or newer recommended** (use a Python version compatible with the packages in `requirements.txt`).
- `pip`
- Internet connection for installing dependencies and using online APIs/models.
- A Google/YouTube API key for YouTube API features.
- If using the local Ollama-based AI functionality, install and run Ollama and download the model configured for your project. Check `services/ollama_service.py` for the model and connection settings.

## Installation

### 1. Download or clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd "SP PROJECT"
```

If you downloaded the ZIP instead, extract it and open the extracted `SP PROJECT` folder in VS Code.

### 2. Create a virtual environment

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Some machine-learning packages, particularly PyTorch and Transformers, may take time to install and may download model files on first use.

## Configuration

The application reads environment variables through `python-dotenv`. Create a `.env` file in the project root:

```env
YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY
```

Replace the placeholder with your own API key. Do not commit `.env` or publish API keys.

The project configuration also defines the application name/version, database filename, and maximum comments setting in `config.py`.

## Run the Application

From the project root (the directory containing `app.py`):

```bash
streamlit run app.py
```

Streamlit will display a local URL in the terminal, typically:

```text
http://localhost:8501
```

Open that URL in your browser. Stop the server with **Ctrl+C** in the terminal.

## How to Use

1. Start the application using the command above.
2. Choose a page from the sidebar.
3. Provide text, a file, or YouTube video details according to the selected analyzer.
4. Run the analysis and review the displayed results, charts, summaries, or reports.
5. Use History and Dashboard to review available saved analysis information.
6. Use Video Comparison to compare videos supported by the page.

The exact inputs and available controls depend on the selected page and configured API/AI services.

## Dataset and Data Files

The repository includes data files under `data/raw/` and `data/cleaned/`, including sample YouTube/video and comment datasets.

For the final public repository:
- Keep only datasets you are permitted to redistribute.
- Add the original dataset source URL and license/attribution here.
- If a dataset is too large or cannot be shared, provide its official download link and instructions instead of uploading it.
- Do not include private, personal, or API-derived data without permission.

**Dataset sources:**  
- Add dataset name and source URL: `TODO`
- Add dataset name and source URL: `TODO`

## Troubleshooting

- **`ModuleNotFoundError`**: Activate the virtual environment and run `pip install -r requirements.txt`.
- **YouTube/API error**: Confirm `YOUTUBE_API_KEY` is set correctly and that the API is enabled for the key.
- **AI summary unavailable**: Check the local AI service configuration and confirm the service/model is running if the project uses Ollama.
- **Streamlit command not found**: Run `python -m pip install -r requirements.txt`, then `python -m streamlit run app.py`.
- **Missing file or page import**: Run Streamlit from the project root and confirm the project folders were extracted together.
- **First run is slow**: NLP/AI libraries may download model weights on first use.

## Security and Privacy

- Never commit API keys, passwords, tokens, or private `.env` files.
- Review `.gitignore` before uploading the repository.
- Check `data/`, `analysis_details/`, and database files for personal or sensitive information before publishing.
- Use only datasets and content you have permission to process and share.

## Project Team

- **Project title:** AI-Based Social Media Analytics
- **Project team:** Add all student names and enrollment numbers
- **Project supervisor:** Add supervisor name
- **Institution:** Add college/university name
- **Academic year:** Add academic year

## GitHub Repository

- **Repository URL:** `TODO — add your GitHub repository link`
- **Dataset links:** Add verified dataset source links above.

## License

Add the license approved by your project team or institution. Do not claim an open-source license unless one has been selected and included in the repository.
