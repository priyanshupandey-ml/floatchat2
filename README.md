# FloatChat: Ocean Data Processing and RAG System

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)
![ChromaDB](https://img.shields.io/badge/VectorDB-Chroma-green.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

---

## Overview

FloatChat is an end-to-end system for processing oceanographic ARGO float data and enabling natural language querying over it using a Retrieval-Augmented Generation (RAG) pipeline.

It converts raw NetCDF ocean data into structured profiles, stores them in a relational database, generates embeddings for semantic search, and provides an interactive dashboard with geospatial visualization and a chat-based query interface.

---

## Key Features

- Batch processing of ARGO NetCDF files
- Profile-based normalization of oceanographic data
- Storage in PostgreSQL with duplicate control
- Embedding generation for semantic retrieval
- Vector search using ChromaDB
- RAG-based question answering system
- Interactive Streamlit dashboard
- Geospatial visualization of float trajectories
- Export support (CSV / structured data formats)

---

## System Architecture
NetCDF Files
↓
Data Loader
↓
Normalization Layer (Profile Builder)
↓
PostgreSQL (Structured Storage)
↓
Profile Summarization
↓
Embedding Model
↓
Chroma Vector Database
↓
RAG Retrieval System
↓
Streamlit Dashboard (UI + Chat + Visualization)


---

## Project Structure
FloatChat/
│
├── Data_pipeline.py # NetCDF ingestion and processing
├── profile_summary.py # Profile aggregation and summarization
├── vector_store.py # ChromaDB integration
├── embeddings.py # Embedding model interface
├── retrive.py # RAG query engine
├── app.py # Streamlit dashboard
│
├── chroma_db/ # Persistent vector database
├── uploaded_data/ # Temporary file storage
├── requirements.txt
└── README.md


---

## Data Flow

### 1. Data Ingestion
- Users upload NetCDF files or folders
- Files are parsed using Xarray
- Data is converted into structured profiles

### 2. Storage Layer
- Profiles are stored in PostgreSQL
- Duplicate prevention using `profile_id`
- Metadata includes cycle, location, depth, and measurements

### 3. Summarization
Each profile is converted into a structured summary containing:
- Depth statistics
- Temperature range
- Salinity range
- Location and timestamp

### 4. Embedding Generation
- Profile summaries are converted into embeddings
- Stored in ChromaDB for semantic retrieval

### 5. RAG System
- User queries are embedded
- Relevant profiles are retrieved
- LLM generates final response using retrieved context

---

## Dashboard Features

### 1. Data Overview
- Total profiles loaded
- Summary statistics
- Tabular data view

### 2. Geospatial Visualization
- Float trajectory mapping using latitude and longitude
- Interactive ocean profile exploration

### 3. Analytics
- Temperature vs depth trends
- Salinity distribution
- Profile-based filtering

### 4. Chat Interface
Users can ask natural language questions such as:
- Maximum depth observed in dataset
- Temperature range of a specific float
- Salinity variation across cycles
- Deepest ocean profile recorded

---

## Installation

### 1. Clone Repository
git clone https://github.com/your-username/floatchat.git
cd floatchat
### 2. Install Dependencies
pip install -r requirements.txt


### 3. Setup PostgreSQL
Create database:
ocean_db


Update credentials in code if required.

### 4. Run Application
streamlit run app.py


---

## Example Usage

### Upload Data
- Upload ARGO NetCDF files through UI

### Process Data
- System automatically parses and stores profiles

### Query System
Example queries:
- What is the maximum depth observed?
- Which float recorded the lowest temperature?
- Show salinity variation across profiles

---

## Technologies Used

- Python
- Xarray
- Pandas
- PostgreSQL
- SQLAlchemy
- ChromaDB
- LangChain
- Streamlit
- Plotly
- Folium

---

## Future Enhancements

- Real-time ARGO float ingestion
- 3D ocean visualization (CesiumJS)
- Advanced anomaly detection in ocean data
- Multi-source integration (satellite + BGC + gliders)
- Cloud deployment (AWS/GCP)
- API layer using FastAPI

---

## Notes

- Each profile is uniquely identified using `profile_id`
- Duplicate handling is managed at database level
- Embeddings are generated only for new profiles
- System is extensible for other oceanographic datasets

---

