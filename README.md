# GeoNexus (SIH26227)

Semantic Retrieval and Multi-Temporal Change Analysis of Satellite Imagery.

## Overview
GeoNexus analyzes Sentinel-2 satellite imagery across multi-temporal intervals (2020-2026) to detect urban expansion, agricultural changes, water body shifts, and vegetation dynamics. It features an interactive Leaflet map interface and semantic retrieval powered by SentenceTransformer embeddings and FAISS index search.

## Tech Stack
- **Frontend**: React, Vite, Leaflet / React-Leaflet, Tailwind CSS
- **Backend**: FastAPI, Uvicorn, SQLite, OpenCV, NumPy, Rasterio
- **Semantic Search**: `all-MiniLM-L6-v2` (SentenceTransformer embedding model) + FAISS index search
- **Data Source**: Sentinel-2 L2A Multispectral Imagery

## Project Workflow
1. **Satellite Data Acquisition & Preprocessing**: Sentinel-2 band extraction (B02, B03, B04, B08, B11, B12).
2. **Spectral Index Calculation**: Computing NDVI, NDWI, and NDBI.
3. **Change Detection & Classification**: Delta index analysis and threshold-based polygon classification.
4. **Database Storage**: Vectorized change polygons stored in SQLite (`sih_changes.db`).
5. **Interactive Mapping & Semantic Retrieval**: FastAPI backend serving GeoJSON features and vector search results to the React frontend.

## Local Setup Commands

### Backend
```bash
cd backend
python -m venv venv
# Activate venv: venv\Scripts\activate (Windows) or source venv/bin/activate (Linux/Mac)
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Production Build (Frontend)
```bash
cd frontend
npm run build
```
