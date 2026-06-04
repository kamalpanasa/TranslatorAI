# Multilingual Translation Backend API

A production-grade, containerized FastAPI backend for multilingual text, image (OCR), audio (transcription), and document (PDF, Excel, Word, CSV) translation. The translation pipeline uses the **Facebook NLLB-200-3.3B** model for high-fidelity translations across 200 languages, and **OpenAI Whisper** for transcription.

## Features

- **Text Translation**: Sentence-aware translation using HuggingFace Transformers.
- **Audio Translation**: Transcription using Whisper, followed by NLLB translation.
- **Image Translation**: Text extraction using Tesseract OCR, followed by NLLB translation, and overlay reconstruction.
- **Document Translation**: Coordinates file layout extraction, cell/paragraph mapping, translation, and file rebuilding for:
  - Layout-preserved PDFs (PyMuPDF)
  - MS Word DOCX (python-docx)
  - Excel Spreadsheets XLSX (openpyxl)
  - Tabular datasets CSV (pandas)
- **History & Favorites**: Stores and retrieves past user translations using Supabase.
- **Authentication**: JWT validation integrated with Supabase Auth (with a local database fallback for development).

---

## Tech Stack

- **Framework**: FastAPI (Asynchronous Python)
- **Inference Engines**: PyTorch, Transformers, SentencePiece, Sacremoses
- **Audio Transcription**: OpenAI Whisper
- **OCR Engine**: Tesseract OCR (via `pytesseract`)
- **Database / Storage**: Supabase (via `supabase-py` SDK)

---

## Supabase Database Setup

To activate database features, run the following SQL scripts in your Supabase SQL Editor:

```sql
-- 1. Create Translation History Table
CREATE TABLE public.history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    input_text TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    source_lang VARCHAR(50) NOT NULL,
    target_lang VARCHAR(50) NOT NULL,
    file_name VARCHAR(255),
    file_type VARCHAR(50) DEFAULT 'text',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable RLS for history
ALTER TABLE public.history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow users access to their own history entries" ON public.history
    FOR ALL USING (auth.uid() = user_id);

-- 2. Create Favorites Bookmarks Table
CREATE TABLE public.favorites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    history_id UUID REFERENCES public.history(id) ON DELETE SET NULL,
    input_text TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    source_lang VARCHAR(50) NOT NULL,
    target_lang VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable RLS for favorites
ALTER TABLE public.favorites ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow users access to their own favorites entries" ON public.favorites
    FOR ALL USING (auth.uid() = user_id);
```

---

## Local Development Installation

### System Pre-requisites
1. **FFmpeg**: Required for audio processing. Add `ffmpeg` to your system path.
2. **Tesseract OCR**: Required for image translation. Install Tesseract and note the executable path.

### Step-by-Step Runbook

1. **Clone & Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/Scripts/activate # Windows
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in the values:
   ```bash
   copy .env.example .env
   ```
   *Note: Make sure `TESSERACT_CMD` matches the path to your local `tesseract.exe` (on Windows).*

3. **Verify Installation**:
   Run the test runner to check local logic:
   ```bash
   python test_run.py
   ```

4. **Launch Development Server**:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

5. **API Documentation**:
   Access the Swagger console at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## Docker Deployment

To launch the containerized application stack (which installs FFmpeg, Tesseract, and Python libraries inside Linux automatically):

```bash
docker-compose up --build
```

The API will expose port `8000` (e.g. Health Check at [http://localhost:8000/health](http://localhost:8000/health)).

---

## API Endpoints List

### Authentication
- `POST /api/v1/auth/register` - Create user profile.
- `POST /api/v1/auth/login` - Sign in and get JWT token.
- `POST /api/v1/auth/logout` - Clear active session.

### Translation
- `POST /api/v1/translate/text` - Translates text strings.
- `POST /api/v1/translate/audio` - Upload audio to transcribe and translate.
- `POST /api/v1/translate/image` - Upload image to extract text via OCR and translate.
- `POST /api/v1/translate/pdf` - Reconstruct translated PDF.
- `POST /api/v1/translate/docx` - Reconstruct translated Word Document.
- `POST /api/v1/translate/excel` - Reconstruct translated Excel sheet.
- `POST /api/v1/translate/csv` - Reconstruct translated CSV dataset.

### Core Lists & Logs
- `GET /api/v1/languages` - Fetch NLLB language codes.
- `GET /api/v1/history` - Fetch user translation log history (Auth).
- `DELETE /api/v1/history/{id}` - Delete user history item (Auth).
- `POST /api/v1/favorites` - Bookmark a translation (Auth).
- `GET /api/v1/favorites` - Fetch user bookmarks (Auth).
- `DELETE /api/v1/favorites/{id}` - Delete bookmark item (Auth).
