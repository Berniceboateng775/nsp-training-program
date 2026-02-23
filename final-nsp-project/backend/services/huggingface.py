"""
Hugging Face Inference API client.
Provides mock responses when HF_API_TOKEN is not set.
Replace mock functions with real API calls once model is deployed.
"""

import os
import random
import httpx
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")
HF_MODEL_ENDPOINT = os.getenv(
    "HF_MODEL_ENDPOINT",
    "https://api-inference.huggingface.co/models/gpt2"
)


async def query_model(prompt: str) -> str:
    """Send a prompt to the Hugging Face model and return the response."""
    if not HF_API_TOKEN:
        return await mock_chat_response(prompt)
    
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True
        }
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(HF_MODEL_ENDPOINT, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "I couldn't generate a response.")
            return str(result)
        else:
            return f"Model error ({response.status_code}). Please try again."


# ─── Mock Responses (used when HF API is not configured) ──

MOCK_BOOK_DATABASE = [
    {
        "title": "The Night Circus",
        "author": "Erin Morgenstern",
        "genre": "Fantasy",
        "description": "A breathtaking, mesmerizing tale of a mysterious competition between two young magicians, set within a fantastical circus that only appears at night.",
        "rating": 4.6
    },
    {
        "title": "Project Hail Mary",
        "author": "Andy Weir",
        "genre": "Science Fiction",
        "description": "A lone astronaut must save humanity from extinction in this gripping interstellar adventure filled with wit, science, and an unlikely friendship.",
        "rating": 4.8
    },
    {
        "title": "The Song of Achilles",
        "author": "Madeline Miller",
        "genre": "Historical Fiction",
        "description": "A devastating retelling of the Iliad through the eyes of Patroclus, exploring love, destiny, and the cost of glory in ancient Greece.",
        "rating": 4.7
    },
    {
        "title": "Piranesi",
        "author": "Susanna Clarke",
        "genre": "Fantasy",
        "description": "A man lives in a mysterious house of infinite halls and staircases, filled with statues and an ocean. A haunting meditation on memory and reality.",
        "rating": 4.3
    },
    {
        "title": "Klara and the Sun",
        "author": "Kazuo Ishiguro",
        "genre": "Literary Fiction",
        "description": "An Artificial Friend named Klara observes the world from a store window, waiting to be chosen. A profound exploration of love, sacrifice, and consciousness.",
        "rating": 4.2
    },
    {
        "title": "The Invisible Life of Addie LaRue",
        "author": "V.E. Schwab",
        "genre": "Fantasy",
        "description": "A young woman makes a Faustian bargain to live forever but is cursed to be forgotten by everyone she meets — until she walks into a bookshop and the boy behind the counter remembers her name.",
        "rating": 4.5
    },
    {
        "title": "Circe",
        "author": "Madeline Miller",
        "genre": "Mythology",
        "description": "The story of the witch Circe, daughter of the titan Helios, who discovers her powers of sorcery and is banished to a deserted island where gods, heroes, and monsters shape her fate.",
        "rating": 4.7
    },
    {
        "title": "A Gentleman in Moscow",
        "author": "Amor Towles",
        "genre": "Historical Fiction",
        "description": "A Russian count sentenced to house arrest in a luxury hotel for the rest of his life discovers that an extraordinary existence can be found within the most confined of circumstances.",
        "rating": 4.6
    },
    {
        "title": "The House in the Cerulean Sea",
        "author": "TJ Klune",
        "genre": "Fantasy",
        "description": "A caseworker is sent to evaluate a magical orphanage on a remote island and discovers a found family that changes everything he thought he knew about the world.",
        "rating": 4.5
    },
    {
        "title": "Anxious People",
        "author": "Fredrik Backman",
        "genre": "Contemporary Fiction",
        "description": "A failed bank robbery turns into a hostage situation that brings together the most unexpected people, revealing that everyone has a story worth understanding.",
        "rating": 4.3
    },
    {
        "title": "Mexican Gothic",
        "author": "Silvia Moreno-Garcia",
        "genre": "Horror",
        "description": "A glamorous socialite ventures to a crumbling gothic mansion in the Mexican countryside to rescue her newlywed cousin, uncovering terrifying secrets within its walls.",
        "rating": 4.1
    },
    {
        "title": "The Midnight Library",
        "author": "Matt Haig",
        "genre": "Contemporary Fiction",
        "description": "Between life and death, Nora finds a library containing books that let her live alternate versions of her life, each exploring a different choice she could have made.",
        "rating": 4.2
    }
]

MOCK_CHAT_RESPONSES = {
    "recommend": [
        "Based on your love for immersive storytelling, I'd highly recommend **The Night Circus** by Erin Morgenstern. The atmospheric world-building and the slow-burn romance between the two competing magicians would captivate you. The prose is lyrical and every chapter feels like stepping into a dream.",
        "If you're in the mood for something that blends mythology with feminist power, **Circe** by Madeline Miller is extraordinary. Miller brings the ancient world to life with such intimacy — Circe's journey from overlooked goddess to powerful witch is deeply moving.",
        "I think you'd absolutely love **A Gentleman in Moscow** by Amor Towles. It's a masterclass in finding beauty and meaning within constraints. The Count's wit and grace under pressure make every page a delight."
    ],
    "summarize": [
        "This passage explores the tension between individual desire and societal expectation. The protagonist is at a crossroads — torn between the familiar safety of conformity and the terrifying freedom of self-expression. The author uses the metaphor of a locked garden to represent untapped potential, suggesting that growth requires the courage to step beyond established boundaries.",
        "The central theme here is the nature of memory and identity. The narrator questions whether we are defined by our experiences or by the stories we tell about them. There's a beautiful interplay between past and present, with the recurring motif of water symbolizing both forgetting and renewal.",
        "This chapter marks a turning point in the narrative. The protagonist's discovery challenges everything they believed, and the author masterfully builds tension through short, fragmented sentences that mirror the character's psychological state. The dialogue reveals more through what's left unsaid."
    ],
    "emotion": [
        "I detect strong undertones of **melancholy** and **nostalgia** in this passage, layered with a quiet sense of **hope**. The author crafts a bittersweet atmosphere — there's grief for what was lost, but also an emerging acceptance and forward-looking resilience.",
        "The emotional landscape here is complex: primarily **tension** and **anticipation**, with undercurrents of **longing**. The pacing creates an almost breathless quality, and the imagery evokes both danger and desire in equal measure.",
        "This text radiates **warmth** and **tenderness**, with moments of gentle **humor**. The emotional core is about connection and belonging — the characters finding comfort in each other's presence despite external chaos."
    ],
    "default": [
        "That's a fascinating question about literature. The beauty of reading is that every person brings their own experiences and emotions to a text, creating a unique interpretation. What draws you to this particular aspect of the story?",
        "I appreciate you exploring that idea. Literature has this remarkable ability to help us understand ourselves and others across time and culture. The themes you're noticing are central to how this author constructs meaning in their work.",
        "As a reading companion, I find that the most rewarding literary experiences come from sitting with ambiguity rather than rushing to conclusions. This text invites multiple readings, and each one reveals new layers of meaning."
    ]
}


async def mock_chat_response(message: str) -> str:
    """Generate contextual mock responses based on message intent."""
    msg_lower = message.lower()
    
    if any(w in msg_lower for w in ["recommend", "suggest", "book", "read next", "what should"]):
        return random.choice(MOCK_CHAT_RESPONSES["recommend"])
    elif any(w in msg_lower for w in ["summarize", "summary", "explain", "chapter", "meaning"]):
        return random.choice(MOCK_CHAT_RESPONSES["summarize"])
    elif any(w in msg_lower for w in ["emotion", "feel", "mood", "tone", "sentiment"]):
        return random.choice(MOCK_CHAT_RESPONSES["emotion"])
    else:
        return random.choice(MOCK_CHAT_RESPONSES["default"])


async def mock_recommendations(query: str = None, genres: list = None, mood: str = None) -> list:
    """Return filtered mock book recommendations."""
    books = MOCK_BOOK_DATABASE.copy()
    
    if genres:
        genre_lower = [g.lower() for g in genres]
        filtered = [b for b in books if b["genre"].lower() in genre_lower]
        if filtered:
            books = filtered
    
    selected = random.sample(books, min(4, len(books)))
    
    reasons = [
        "This deeply resonates with your reading preferences and current mood.",
        "The narrative style and thematic depth align beautifully with your taste.",
        "Readers with similar preferences have rated this exceptionally high.",
        "The emotional complexity of this work matches what you're looking for.",
    ]
    
    return [
        {
            "title": b["title"],
            "author": b["author"],
            "genre": b["genre"],
            "description": b["description"],
            "reason": reasons[i % len(reasons)],
            "rating": b["rating"],
            "cover_url": None
        }
        for i, b in enumerate(selected)
    ]


async def mock_emotion_analysis(text: str) -> dict:
    """Analyze text for emotions and themes (mock)."""
    emotions = {
        "joy": round(random.uniform(0.1, 0.9), 2),
        "sadness": round(random.uniform(0.05, 0.6), 2),
        "tension": round(random.uniform(0.1, 0.7), 2),
        "romance": round(random.uniform(0.05, 0.5), 2),
        "mystery": round(random.uniform(0.1, 0.6), 2),
        "hope": round(random.uniform(0.1, 0.8), 2),
        "fear": round(random.uniform(0.05, 0.4), 2)
    }
    
    # Normalize so they sum to ~1
    total = sum(emotions.values())
    emotions = {k: round(v / total, 2) for k, v in emotions.items()}
    
    theme_pool = [
        "Coming of Age", "Love & Loss", "Identity", "Power & Corruption",
        "Nature vs Nurture", "Redemption", "Isolation", "Family Bonds",
        "Self-Discovery", "Social Justice", "Fate vs Free Will", "Mortality"
    ]
    themes = random.sample(theme_pool, 3)
    
    dominant = max(emotions, key=emotions.get)
    summaries = {
        "joy": "This passage radiates warmth and positivity, with an undercurrent of celebration and contentment that permeates the narrative voice.",
        "sadness": "A contemplative melancholy runs through this text, reflecting on loss and the passage of time with a delicate, almost poetic sensibility.",
        "tension": "The narrative pulses with underlying conflict and suspense, keeping the reader on edge through carefully constructed dramatic pressure.",
        "romance": "Tender and intimate, this passage explores the landscape of human connection with sensitivity and emotional depth.",
        "mystery": "An air of enigma pervades this text, with layers of meaning waiting to be uncovered beneath the surface narrative.",
        "hope": "Despite the challenges presented, this passage ultimately resonates with resilience and the belief in better possibilities ahead.",
        "fear": "A subtle unease permeates this writing, creating an atmosphere of vulnerability and the unknown that lingers beyond the page."
    }
    
    return {
        "emotions": emotions,
        "themes": themes,
        "summary": summaries.get(dominant, summaries["hope"])
    }
