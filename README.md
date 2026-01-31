# The Semantic Cut

**Team:** Shot Ok
**Hackathon Submission**

A semantic search engine for movie footage that allows editors to find clips using natural language queries (e.g., "hesitant reaction before answering").

## 🧠 Core Architecture

### 1. Data Embedding Strategy
We utilize a **composite semantic representation** for every clip. Instead of just embedding raw dialogue, we combine:
- **Scene Context**: Location, Interior/Exterior status, Time of Day.
- **Visual Action**: The `Clip Description` describing what happens visually.
- **Dialogue**: All spoken lines within that clip.
- **Characters**: Names of actors involved.

### 2. Query Processing
1.  **Embedding**: Query -> 384-dim vector (`all-MiniLM-L6-v2`).
2.  **Vector Search**: Cosine similarity search via **Qdrant**.
3.  **Reranking**: Semantic ranking via Cross-Encoder (`ms-marco-MiniLM-L-6-v2`).
4.  **AI Explanation**: **Gemini 2.5 Flash** generates a summary of *why* the result matches the query.

## 🚀 How to Run

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Qdrant](https://qdrant.tech/) (Cloud or Docker)
- Google Gemini API Key

### 1. Backend Setup (`/app`)
1. Create a virtual environment and install dependencies:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Configure environment:
   - Copy `.env.example` to `.env`
   - Fill in `QDRANT_URL`, `QDRANT_API_KEY`, and `GEMINI_API_KEY`.
3. Start the Backend Server:
   ```powershell
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### 2. Ingest Data
Index the sample Godfather footage into the vector database:
```powershell
python index_godfather.py
```

### 3. Frontend Setup (`/web`)
1. Navigate to the web directory:
   ```powershell
   cd web
   ```
2. Install dependencies:
   ```powershell
   npm install
   ```
3. Start the Next.js Dev Server:
   ```powershell
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🧪 Verification
You can run the verification script to test the search directly from the terminal:
```powershell
python verify_search.py
```

## 📁 Project Structure
- `app/`: FastAPI Backend
  - `main.py`: API Endpoints
  - `services/`: Logic for Vector DB, LLM, and Models
  - `models/`: Pydantic Schemas
- `web/`: Next.js Frontend
- `data/`: Sample JSON data
- `index_godfather.py`: Data Ingestion Script
