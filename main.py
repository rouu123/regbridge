"""
Run: python main.py

Loops through a comprehensive list of AI-related topics and indexes papers from
all configured sources into Qdrant.

Edit LIMIT_PER_SOURCE / AI_TOPICS / SOURCES below as needed.
"""

from normalize import Paper
from embed import embed_texts
from store import store_paper, ensure_qdrant_collection, load_existing_keys_from_qdrant

from sources import semantic_scholar, arxiv, openalex, core, springer, doaj

LIMIT_PER_SOURCE = 35

# Comprehensive AI-related topics
AI_TOPICS = [
    # Core AI
    #"artificial intelligence",
    #"machine learning",
    #"deep learning",
    #"neural networks",
    #"computational intelligence",
    #"intelligent systems",
    #"cognitive computing",
    "symbolic AI",
    "hybrid AI",

    # Large Language Models & Foundation Models
    "large language models",
    "foundation models",
    "transformers",
    "generative AI",
    "generative models",
    "language models",
    "instruction tuning",
    "fine tuning",
    "parameter efficient fine tuning",
    "LoRA",
    "prompt engineering",
    "prompt tuning",
    "in context learning",
    "chain of thought",
    "reasoning models",

    # NLP
    "natural language processing",
    "text classification",
    "named entity recognition",
    "information extraction",
    "information retrieval",
    "question answering",
    "text summarization",
    "machine translation",
    "dialogue systems",
    "chatbots",
    "semantic search",
    "text generation",
    "sentiment analysis",
    "topic modeling",

    # RAG & Retrieval
    "retrieval augmented generation",
    "RAG",
    "dense retrieval",
    "sparse retrieval",
    "vector databases",
    "embeddings",
    "semantic retrieval",
    "document retrieval",
    "knowledge retrieval",

    # Computer Vision
    "computer vision",
    "image classification",
    "object detection",
    "instance segmentation",
    "semantic segmentation",
    "image segmentation",
    "image recognition",
    "image generation",
    "image captioning",
    "visual question answering",
    "face recognition",
    "face detection",
    "pose estimation",
    "action recognition",
    "medical image analysis",
    "OCR",
    "optical character recognition",

    # Speech & Audio
    "speech recognition",
    "automatic speech recognition",
    "speech synthesis",
    "text to speech",
    "speech to text",
    "speaker recognition",
    "speaker verification",
    "voice cloning",
    "audio classification",
    "audio generation",
    "music generation",

    # Reinforcement Learning
    "reinforcement learning",
    "deep reinforcement learning",
    "offline reinforcement learning",
    "online reinforcement learning",
    "multi agent reinforcement learning",
    "inverse reinforcement learning",

    # Learning Paradigms
    "supervised learning",
    "unsupervised learning",
    "semi supervised learning",
    "self supervised learning",
    "few shot learning",
    "zero shot learning",
    "one shot learning",
    "continual learning",
    "lifelong learning",
    "transfer learning",
    "meta learning",
    "active learning",
    "curriculum learning",
    "federated learning",

    # Neural Architectures
    "graph neural networks",
    "graph learning",
    "graph transformers",
    "graph embeddings",
    "convolutional neural networks",
    "CNN",
    "recurrent neural networks",
    "RNN",
    "LSTM",
    "GRU",
    "attention mechanisms",

    # Generative Models
    "diffusion models",
    "stable diffusion",
    "latent diffusion",
    "GAN",
    "generative adversarial networks",
    "variational autoencoders",
    "VAE",
    "autoregressive models",
    "flow matching",

    # Multi-Agent Systems
    "agentic AI",
    "AI agents",
    "autonomous agents",
    "multi agent systems",
    "multi agent collaboration",
    "planning",
    "reasoning",
    "tool use",
    "function calling",

    # Robotics
    "robotics",
    "robot learning",
    "autonomous systems",
    "autonomous driving",
    "self driving cars",
    "robot perception",
    "robot navigation",
    "SLAM",

    # Explainability & Responsible AI
    "explainable AI",
    "XAI",
    "interpretable machine learning",
    "AI fairness",
    "AI ethics",
    "AI safety",
    "AI alignment",
    "trustworthy AI",
    "responsible AI",
    "bias mitigation",

    # Optimization
    "optimization",
    "hyperparameter optimization",
    "neural architecture search",
    "Bayesian optimization",

    # Probabilistic AI
    "Bayesian learning",
    "probabilistic graphical models",
    "probabilistic machine learning",
    "causal inference",
    "causal discovery",

    # Knowledge Representation
    "knowledge graphs",
    "knowledge representation",
    "ontology learning",
    "semantic web",
    "reasoning systems",

    # Data Mining
    "data mining",
    "pattern recognition",
    "clustering",
    "classification",
    "dimensionality reduction",
    "anomaly detection",
    "outlier detection",
    "recommendation systems",

    # Time Series
    "time series forecasting",
    "forecasting",
    "predictive analytics",

    # Biomedical AI
    "bioinformatics",
    "computational biology",
    "medical AI",
    "clinical decision support",
    "drug discovery AI",

    # Security
    "AI cybersecurity",
    "malware detection",
    "fraud detection",
    "intrusion detection",

    # Edge AI
    "edge AI",
    "TinyML",
    "on device AI",

    # Hardware
    "AI accelerators",
    "TPU",
    "GPU computing",

    # Multimodal
    "multimodal AI",
    "vision language models",
    "vision transformers",
    "video understanding",
    "video generation",

    # Emerging Topics
    "world models",
    "neural rendering",
    "3D vision",
    "digital twins",
    "foundation agents",
    "AI copilots",
]

# Comment out any source you don't have API keys for / don't want to hit.
SOURCES = {
    "semantic_scholar": semantic_scholar.fetch,
    "arxiv": arxiv.fetch,
    "openalex": openalex.fetch,
    #"core": core.fetch,
    "doaj": doaj.fetch,
}


def collect(query: str, limit: int) -> list[Paper]:
    all_papers: list[Paper] = []
    seen_keys: set[str] = set()

    for name, fetch_fn in SOURCES.items():
        try:
            results = fetch_fn(query, limit)
        except Exception as e:
            print(f"[{name}] skipped due to error: {e}")
            continue

        added = 0
        for paper in results:
            key = paper.dedupe_key()
            if key in seen_keys:
                continue
            seen_keys.add(key)
            all_papers.append(paper)
            added += 1

        print(f"[{name}] fetched {len(results)}, added {added} new", flush=True)

    return all_papers

def run(limit: int = LIMIT_PER_SOURCE) -> None:
    ensure_qdrant_collection()

    # Pre-load existing keys from Qdrant so re-runs don't re-embed known papers
    seen_global: set[str] = load_existing_keys_from_qdrant()
    print(f"Loaded {len(seen_global)} existing paper keys from Qdrant.")

    total_added = 0

    for topic in AI_TOPICS:
        print(f"\n{'=' * 80}")
        print(f"Searching topic: {topic}")
        print(f"{'=' * 80}")

        papers = collect(topic, limit)

        topic_new_papers: list[Paper] = []
        for paper in papers:
            key = paper.dedupe_key()
            if key in seen_global:
                continue

            seen_global.add(key)
            topic_new_papers.append(paper)

        print(f"Found {len(topic_new_papers)} new unique papers.")

        if not topic_new_papers:
            continue

        texts = [(p.abstract or p.title or "").strip() for p in topic_new_papers]
        texts = [t if t else "Untitled" for t in texts]

        print(f"Embedding {len(texts)} papers...")
        embeddings = embed_texts(texts)

        print("Storing in Qdrant...")
        for paper, embedding in zip(topic_new_papers, embeddings):
            store_paper(paper, embedding)

        total_added += len(topic_new_papers)

    print(f"\nDone. Added and stored {total_added} new unique papers.")


if __name__ == "__main__":
    run()