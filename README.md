# MediaPulse AI: Engagement Forecasting Chatbot

**MediaPulse AI** is an intelligent assistant designed to help Instagram creators and businesses maximize their digital reach. By leveraging **Retrieval-Augmented Generation (RAG)** and semantic vector search, the system analyzes historical performance data to provide data-backed recommendations for posting times, captions, and hashtags.


## Features
* **Post Type Optimization**: Specialized analysis for **Reels**, **Posts**, and **Carousels**.
* **Predictive Engagement**: Generates estimated **Uplift %** for likes and reach based on content quality.
* **Semantic Matching**: Uses **BAAI/bge** embeddings to find the most relevant successful posts from your historical data.
* **Smart Content Refinement**: Suggests improved captions and filtered, high-performance hashtags.
* **Interactive UI**: A sleek **Streamlit** dashboard with a guided chat flow and dark/light mode support.



## Tech Stack
* **Framework**: [LangChain](https://www.langchain.com/) (RAG Orchestration)
* **Interface**: [Streamlit](https://streamlit.io/)
* **Vector Database**: [ChromaDB](https://www.trychroma.com/)
* **Embeddings**: `BAAI/bge-small-en-v1.5`
* **Reranker**: `BAAI/bge-reranker-base`
* **Data Handling**: Pandas & Python-Dotenv


## Project Structure
```
MediaPulse/
├── src/
│   ├── chatbot.py              # Core RAG logic & scoring algorithm
│   └── build_vectorstore.py    # Data indexing & embedding pipeline
│
├── chroma_db/                  # Vector database storage (initially empty)
│
├── data/
│   ├── Logo/                   # Store logos, icons, branding assets
│   │   └── logo.png
│   │
│   └── dataset/                # All datasets go here
│       └── mediapulse-dataset.csv
│
├── app.py                      # Streamlit UI & session state management
├── .env                        # Configuration (API tokens & paths)
├── requirements.txt            # Project dependencies
```


## Setup & Installation

### 1. Prerequisites
* Python 3.10+
* A HuggingFace Access Token (`HF_TOKEN`)

### 2. Install Dependencies
pip install -r requirements.txt


### 3. Configuration
Create a `.env` file in the root directory with the following:

```
HF_TOKEN=your_huggingface_token_here
CSV_PATH=data/mediapulse-dataset.csv
CHROMA_DIR=chroma_db
CHROMA_COLLECTION=mediapulse_dataset
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
RERANKER_MODEL=BAAI/bge-reranker-base
```
### 4. Build Vector Store
Run the script to index your CSV data into the ChromaDB vector database:

  python src/build_vectorstore.py


## How it Works: The Scoring Logic

MediaPulse AI doesn't just look for keywords; it uses a custom **Weighted Performance Score** to identify truly "successful" content:

Score = Likes + (Reach * 0.05) + (Impressions * 0.03) + (Shares * 3) + (Saves * 3)

The system retrieves similar posts, reranks them for relevance, and then compares your current caption to these high-performers to estimate your potential **Uplift**.

---

## Running the App
Start the interactive dashboard using Streamlit:

streamlit run app.py
