import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from huggingface_hub import login
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Better path handling
DEFAULT_CSV_PATH = BASE_DIR / "data" / "dataset" / "mediapulse-dataset.csv"
CSV_PATH = os.getenv("CSV_PATH", "").strip()
PERSIST_DIRECTORY = os.getenv("CHROMA_DIR", str(BASE_DIR / "chroma_db"))
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "mediapulse_dataset")
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
HF_TOKEN = os.getenv("HF_TOKEN")


def get_posting_time_from_hour(hour):
    if pd.isna(hour):
        return "Unknown"
    hour = int(hour)

    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Night"


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # If timestamp exists, convert it properly
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

        # Create day_of_week if missing or empty
        if "day_of_week" not in df.columns:
            df["day_of_week"] = df["timestamp"].dt.day_name()
        else:
            df["day_of_week"] = df["day_of_week"].replace("", pd.NA)
            df["day_of_week"] = df["day_of_week"].fillna(df["timestamp"].dt.day_name())

        # Create posting_hour if missing
        if "posting_hour" not in df.columns:
            df["posting_hour"] = df["timestamp"].dt.hour

        # Create posting_time if missing or empty
        if "posting_time" not in df.columns:
            df["posting_time"] = df["posting_hour"].apply(get_posting_time_from_hour)
        else:
            df["posting_time"] = df["posting_time"].replace("", pd.NA)
            df["posting_time"] = df["posting_time"].fillna(
                df["posting_hour"].apply(get_posting_time_from_hour)
            )

    else:
        # Fallback if timestamp does not exist
        if "day_of_week" not in df.columns:
            df["day_of_week"] = "Unknown"

        if "posting_time" not in df.columns:
            df["posting_time"] = "Unknown"

        if "posting_hour" not in df.columns:
            df["posting_hour"] = ""

    return df


def build_documents(df: pd.DataFrame):
    documents = []

    for _, row in df.iterrows():
        row_dict = row.fillna("").to_dict()

        page_content = f"""
            post_description: {row_dict.get('post_description', '')}
            caption: {row_dict.get('caption', '')}
            hashtags: {row_dict.get('hashtags', '')}
            content_type: {row_dict.get('content_type', '')}
            posting_time: {row_dict.get('posting_time', '')}
            day_of_week: {row_dict.get('day_of_week', '')}
            posting_hour: {row_dict.get('posting_hour', '')}
            """.strip()

        metadata = {
            "caption": row_dict.get("caption", ""),
            "hashtags": row_dict.get("hashtags", ""),
            "content_type": row_dict.get("content_type", ""),
            "post_description": row_dict.get("post_description", ""),
            "timestamp": str(row_dict.get("timestamp", "")),
            "posting_hour": row_dict.get("posting_hour", ""),
            "posting_time": row_dict.get("posting_time", ""),
            "day_of_week": row_dict.get("day_of_week", ""),
            "likes": float(row_dict.get("likes", 0) or 0),
            "comments": float(row_dict.get("comments", 0) or 0),
            "shares": float(row_dict.get("shares", 0) or 0),
            "saves": float(row_dict.get("saves", 0) or 0),
            "reach": float(row_dict.get("reach", 0) or 0),
            "impressions": float(row_dict.get("impressions", 0) or 0),
            "watch_time": float(row_dict.get("watch_time", 0) or 0),
            "followers": float(row_dict.get("followers", 0) or 0),
        }

        documents.append(Document(page_content=page_content, metadata=metadata))

    return documents


def main():
    if HF_TOKEN:
        try:
            login(token=HF_TOKEN, add_to_git_credential=False)
        except Exception:
            pass

    if CSV_PATH:
        csv_path = Path(CSV_PATH)
        if not csv_path.is_absolute():
            csv_path = BASE_DIR / csv_path

        if not csv_path.exists():
            if DEFAULT_CSV_PATH.exists():
                print(
                    f"Warning: CSV_PATH points to a missing file: {csv_path}\n"
                    f"Falling back to default dataset: {DEFAULT_CSV_PATH}"
                )
                csv_path = DEFAULT_CSV_PATH
            else:
                raise FileNotFoundError(
                    f"CSV file not found: {csv_path}\n"
                    f"Please set CSV_PATH in .env to a valid path or place the dataset at: {DEFAULT_CSV_PATH}"
                )
    else:
        csv_path = DEFAULT_CSV_PATH
        if not csv_path.exists():
            raise FileNotFoundError(
                f"Default CSV file not found: {csv_path}\n"
                f"Please set CSV_PATH in .env or place the dataset at: {DEFAULT_CSV_PATH}"
            )

    print(f"Reading CSV from: {csv_path}")
    df = pd.read_csv(csv_path)

    print(f"Rows loaded: {len(df)}")
    print("Preparing timestamp, posting_time, and day_of_week...")
    df = prepare_dataframe(df)

    documents = build_documents(df)

    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)

    # Create chroma_db folder automatically if it does not exist
    os.makedirs(PERSIST_DIRECTORY, exist_ok=True)

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIRECTORY,
    )

    print(f"Documents stored: {len(documents)}")
    print(f"Vector DB saved at: {PERSIST_DIRECTORY}")
    print("Build completed successfully!")


if __name__ == "__main__":
    main()