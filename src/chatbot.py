import os
import re
from collections import Counter, defaultdict

# Load variables from .env file
from dotenv import load_dotenv

# Used to log in to Hugging Face if token is available
from huggingface_hub import login

# Chroma vector database for storing and retrieving embeddings
from langchain_community.vectorstores import Chroma

# Hugging Face embedding model wrapper for LangChain
from langchain_huggingface import HuggingFaceEmbeddings

# CrossEncoder model used for reranking retrieved results
from sentence_transformers import CrossEncoder

# Load environment variables
load_dotenv()


class MediaPulseChatbot:
    def __init__(self, csv_path: str, persist_directory: str, collection_name: str):
        # Store important file / DB config
        self.csv_path = csv_path
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # Read Hugging Face token from .env
        hf_token = os.getenv("HF_TOKEN")

        # If token exists, try to login to Hugging Face
        if hf_token:
            try:
                login(token=hf_token, add_to_git_credential=False)
            except Exception:
                pass

        # Load embedding model name from .env, else use default BGE small model
        embedding_model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

        # Initialize embedding model
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)

        # Connect to existing Chroma vector database
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=self.collection_name,
        )

        # Load reranker model name from .env, else use default BGE reranker
        reranker_model_name = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-base")

        # Initialize reranker model
        self.reranker = CrossEncoder(reranker_model_name)

    def _clean_hashtag_string(self, text: str, limit: int = 4):
        """
        Extract hashtags from text, remove duplicates, and keep only top 'limit' hashtags.
        """
        tags = re.findall(r"#\w+", text or "")
        seen = []
        seen_lower = set()

        for tag in tags:
            low = tag.lower()
            if low not in seen_lower:
                seen.append(tag)
                seen_lower.add(low)

        return " ".join(seen[:limit])

    def _build_query(self, post_type: str, post_description: str, current_caption: str, current_hashtags: str):
        """
        Build a semantic search query from user inputs.
        This query is used for vector retrieval.
        """
        return (
            f"Find similar Instagram {post_type} posts. "
            f"Description: {post_description}. "
            f"Caption: {current_caption}. "
            f"Hashtags: {current_hashtags}. "
            f"Return the most relevant and high-performing matches."
        )

    def _score_post(self, meta: dict):
        """
        Calculate a custom score for each post using engagement metrics.
        Higher score = stronger post.
        """
        likes = float(meta.get("likes", 0) or 0)
        reach = float(meta.get("reach", 0) or 0)
        impressions = float(meta.get("impressions", 0) or 0)
        shares = float(meta.get("shares", 0) or 0)
        saves = float(meta.get("saves", 0) or 0)

        return likes + (reach * 0.05) + (impressions * 0.03) + (shares * 3) + (saves * 3)

    def _rerank_documents(self, query: str, docs, top_k: int = 8):
        """
        Rerank the retrieved documents using CrossEncoder.
        This improves relevance after vector search.
        """
        if not docs:
            return []

        # Create query-document pairs for reranking
        pairs = [(query, doc.page_content) for doc in docs]

        # Predict relevance scores
        scores = self.reranker.predict(pairs)

        # Zip docs with scores and sort descending
        scored_docs = list(zip(docs, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        # Return only top_k reranked documents
        return [doc for doc, _ in scored_docs[:top_k]]

    def _extract_keywords(self, text: str):
        """
        Extract useful words from text and remove common stopwords.
        Used for relevance checking, hashtag scoring, caption quality, etc.
        """
        words = re.findall(r"\b[a-zA-Z]{3,}\b", (text or "").lower())
        stopwords = {
            "the", "and", "for", "with", "this", "that", "from", "into", "your",
            "post", "caption", "hashtags", "about", "have", "more", "best",
            "instagram", "find", "similar", "return", "reel", "carousel"
        }
        return [word for word in words if word not in stopwords]

    def _is_relevant_to_description(self, meta: dict, post_description: str):
        """
        Check whether a retrieved post is relevant to the user's description.
        It compares description keywords with caption + hashtags.
        """
        text = f"{meta.get('caption', '')} {meta.get('hashtags', '')}".lower()
        keywords = self._extract_keywords(post_description)

        # If no keywords found, assume it is relevant
        if not keywords:
            return True

        # Return True if any keyword appears in caption/hashtags
        return any(word in text for word in keywords)

    def _best_caption(self, metas, post_description, current_caption=""):
        """
        Choose the best caption suggestion.
        Priority:
        1. Top-performing matched post caption
        2. Current caption (if available)
        3. Fallback generated caption
        """
        ranked = sorted(metas, key=self._score_post, reverse=True)
        top_caption = ranked[0].get("caption", "").strip() if ranked else ""

        if top_caption:
            # Use top matched caption if available
            return top_caption

        if current_caption and current_caption.strip():
            # If no matched caption, use current caption
            return current_caption.strip()

        # Final fallback if nothing useful exists
        return f"Capturing {post_description} with a fresh and engaging vibe ✨"

    def _best_hashtags(self, metas, current_hashtags, post_description="", limit=4):
        """
        Suggest the best hashtags using matched posts.
        Removes generic spammy hashtags and prioritizes keywords matching the description.
        """
        tag_counter = Counter()
        keywords = self._extract_keywords(post_description)

        # Hashtags to avoid because they are too generic
        generic_banned = {
            "#viral",
            "#trending",
            "#photooftheday",
            "#followforfollow",
            "#instagram",
            "#instagood",
            "#explorepage",
            "#reels",
            "#reelitfeelit"
        }

        # Count useful hashtags from matched posts
        for meta in metas:
            text = f"{meta.get('caption', '')} {meta.get('hashtags', '')}".lower()

            # Skip irrelevant posts if keywords exist
            if keywords and not any(word in text for word in keywords):
                continue

            tags = re.findall(r"#\w+", meta.get("hashtags", "") or "")

            for tag in tags:
                low = tag.lower()

                if low in generic_banned:
                    continue

                # Give higher weight to tags matching description keywords
                if keywords:
                    if any(word in low for word in keywords):
                        tag_counter[low] += 3
                    else:
                        tag_counter[low] += 1
                else:
                    tag_counter[low] += 1

        final_tags = []
        existing = set()

        # Keep relevant current hashtags first
        if current_hashtags:
            for tag in re.findall(r"#\w+", current_hashtags):
                low = tag.lower()
                if low not in existing:
                    if not keywords or any(word in low for word in keywords):
                        final_tags.append(tag)
                        existing.add(low)

        # Add most common ranked hashtags
        for tag, _ in tag_counter.most_common(limit):
            if tag.lower() not in existing:
                final_tags.append(tag)
                existing.add(tag.lower())
            if len(final_tags) >= limit:
                break

        # Fallback hashtags if nothing found
        if not final_tags:
            if "gym" in keywords or "fitness" in keywords or "workout" in keywords:
                final_tags = ["#gym", "#fitness", "#workout", "#fitlife"]
            elif "travel" in keywords or "trip" in keywords or "nature" in keywords:
                final_tags = ["#travel", "#nature", "#explore", "#wanderlust"]
            elif "food" in keywords or "recipe" in keywords:
                final_tags = ["#food", "#foodie", "#recipe", "#delicious"]
            else:
                final_tags = ["#content", "#creative", "#socialmedia", "#post"]

        return " ".join(final_tags[:limit])

    def _format_hour_label(self, hour_value):
        """
        Convert 24-hour numeric time into user-friendly label like '8 PM'.
        """
        try:
            hour = int(float(hour_value))
            if hour < 0 or hour > 23:
                return "8 PM"
            suffix = "AM" if hour < 12 else "PM"
            hour_12 = hour % 12
            if hour_12 == 0:
                hour_12 = 12
            return f"{hour_12} {suffix}"
        except Exception:
            return "8 PM"

    def _best_time_and_day(self, metas):
        """
        Find the best posting time and day using average performance of matched posts.
        """
        stats = defaultdict(list)

        for meta in metas:
            posting_hour = meta.get("posting_hour")
            day_of_week = str(meta.get("day_of_week", "Wednesday"))
            key = (posting_hour, day_of_week)

            # Group scores by (hour, day)
            stats[key].append(self._score_post(meta))

        if not stats:
            return "8 PM", "Wednesday"

        # Pick best hour/day using average score
        best_key = max(
            stats.items(),
            key=lambda item: sum(item[1]) / max(len(item[1]), 1)
        )[0]

        best_hour, best_day = best_key
        return self._format_hour_label(best_hour), best_day

    def _caption_quality_score(self, caption: str, metas):
        """
        Measure how strong a caption is compared to matched posts.
        Uses keyword overlap + post score weighting.
        """
        if not caption or not metas:
            return 0.0

        caption_words = set(self._extract_keywords(caption))
        if not caption_words:
            return 0.0

        scores = []

        for meta in metas:
            ref_text = f"{meta.get('caption', '')} {meta.get('hashtags', '')}"
            ref_words = set(self._extract_keywords(ref_text))

            if not ref_words:
                continue

            overlap = len(caption_words.intersection(ref_words))
            union = len(caption_words.union(ref_words))

            keyword_score = overlap / union if union else 0
            post_score = self._score_post(meta)

            # Weighted score using keyword similarity + post quality
            weighted_score = keyword_score * (1 + (post_score / 1000))
            scores.append(weighted_score)

        if not scores:
            return 0.0

        return sum(scores) / len(scores)

    def _estimate_uplift(self, metas, current_caption, suggested_caption):
        """
        Estimate likes and reach uplift based on matched post performance
        and caption quality improvement.
        """
        if not metas:
            return "N/A", "N/A"

        current_score = self._caption_quality_score(current_caption, metas)
        suggested_score = self._caption_quality_score(suggested_caption, metas)

        if suggested_score <= 0:
            return "N/A", "N/A"

        # Collect averages from matched posts
        likes_values = [float(meta.get("likes", 0) or 0) for meta in metas]
        reach_values = [float(meta.get("reach", 0) or 0) for meta in metas]
        impressions_values = [float(meta.get("impressions", 0) or 0) for meta in metas]
        shares_values = [float(meta.get("shares", 0) or 0) for meta in metas]
        saves_values = [float(meta.get("saves", 0) or 0) for meta in metas]

        avg_likes = sum(likes_values) / len(likes_values) if likes_values else 0
        avg_reach = sum(reach_values) / len(reach_values) if reach_values else 0
        avg_impressions = sum(impressions_values) / len(impressions_values) if impressions_values else 0
        avg_shares = sum(shares_values) / len(shares_values) if shares_values else 0
        avg_saves = sum(saves_values) / len(saves_values) if saves_values else 0

        # If current caption is too weak, create a softer baseline
        if current_score <= 0:
            current_score = suggested_score * 0.72

        # Compare current vs suggested quality
        improvement_ratio = (suggested_score - current_score) / max(current_score, 1e-6)

        # Build engagement strength from dataset
        engagement_strength = (
            avg_likes * 1.0
            + avg_reach * 0.02
            + avg_impressions * 0.01
            + avg_shares * 2.5
            + avg_saves * 2.5
        )

        # Convert engagement strength into uplift multipliers
        likes_factor = min(max(engagement_strength / 1000, 0.85), 2.0)
        reach_factor = min(max((avg_reach + avg_impressions * 0.3) / 4000, 0.9), 2.2)

        likes_uplift = improvement_ratio * 16 * likes_factor
        reach_uplift = improvement_ratio * 20 * reach_factor

        # Minimum uplift if suggestion is better
        if suggested_score > current_score:
            likes_uplift = max(likes_uplift, 2.5)
            reach_uplift = max(reach_uplift, 3.5)

        # No negative values
        likes_uplift = max(0.0, likes_uplift)
        reach_uplift = max(0.0, reach_uplift)

        # Keep within realistic range
        likes_uplift = min(likes_uplift, 38.0)
        reach_uplift = min(reach_uplift, 48.0)

        return f"+{likes_uplift:.1f}%", f"+{reach_uplift:.1f}%"

    def generate_recommendation(self, post_type, post_description, current_caption="", current_hashtags=""):
        """
        Main method:
        1. Build user query
        2. Retrieve similar posts from vector DB
        3. Rerank them
        4. Filter by type and relevance
        5. Generate best time, caption, hashtags, and uplift
        """
        query = self._build_query(post_type, post_description, current_caption, current_hashtags)

        # Retrieve documents from Chroma using MMR search
        retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 12, "fetch_k": 25, "lambda_mult": 0.3},
        )
        initial_docs = retriever.invoke(query)

        # Rerank retrieved documents
        reranked_docs = self._rerank_documents(query, initial_docs, top_k=8)
        metas = [dict(doc.metadata) for doc in reranked_docs]

        # Keep only documents matching content type
        type_filtered = [
            meta for meta in metas
            if meta.get("content_type", "").lower() == post_type.lower()
        ]
        if type_filtered:
            metas = type_filtered

        # Keep only posts relevant to description keywords
        relevant_filtered = [
            meta for meta in metas
            if self._is_relevant_to_description(meta, post_description)
        ]
        if relevant_filtered:
            metas = relevant_filtered

        # Fallback if nothing remains after filtering
        if not metas:
            metas = [dict(doc.metadata) for doc in reranked_docs[:5]]

        # Generate suggestions
        best_time, best_day = self._best_time_and_day(metas)
        best_caption = self._best_caption(metas, post_description, current_caption=current_caption)
        best_hashtags = self._best_hashtags(
            metas,
            current_hashtags,
            post_description,
            limit=4
        )

        # Calculate estimated uplift
        estimated_likes_uplift, estimated_reach_uplift = self._estimate_uplift(
            metas,
            current_caption,
            best_caption
        )

        # Create explanation for user
        reasons = [
            f"Top reranked similar posts performed better around {best_time}.",
            f"The strongest matching examples appeared more on {best_day}.",
            "Suggested caption is based on better-performing similar posts from your dataset.",
            "Suggested hashtags are chosen from the most relevant matching posts and limited to the best 3-4 tags.",
        ]

        # Final result returned to app.py
        return {
            "best_posting_time": best_time,
            "best_day": best_day,
            "current_caption": current_caption.strip(),
            "suggested_caption": best_caption,
            "suggested_hashtags": self._clean_hashtag_string(best_hashtags, limit=4),
            "reasons": reasons,
            "matched_examples_count": len(metas),
            "similar_posts": metas[:3],
            "estimated_likes_uplift": estimated_likes_uplift,
            "estimated_reach_uplift": estimated_reach_uplift,
        }