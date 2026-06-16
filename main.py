import os
import json
import threading
import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

app = FastAPI(title="Chronicles of India - History NCERT Chatbot")

# --- GLOBAL VARIABLES & STATE ---
corpus: List[Dict[str, Any]] = []
corpus_embeddings: Optional[np.ndarray] = None
retriever_model = None
generator_tokenizer = None
generator_model = None
model_loading_status = "Loading Retriever..."

# Define baseline question-answers for the Quiz
quiz_questions = [
    {
        "id": 1,
        "question": "Which of the following sites was exclusively devoted to craft production in the Harappan Civilisation?",
        "options": ["Mohenjodaro", "Harappa", "Chanhudaro", "Lothal"],
        "correct": 2,
        "explanation": "According to NCERT, Chanhudaro was a tiny settlement (less than 7 hectares) almost exclusively devoted to craft production, including bead-making, shell-cutting, metal-working, seal-making, and weight-making."
    },
    {
        "id": 2,
        "question": "Which empire's military conquests and virtues are described in the Sanskrit inscription 'Prayaga Prashasti'?",
        "options": ["Mauryan Empire", "Gupta Empire", "Mughal Empire", "Gupta Empire (Samudragupta)"],
        "correct": 3,
        "explanation": "The Prayaga Prashasti (also known as the Allahabad Pillar Inscription) was composed in Sanskrit by Harishena, the court poet of Samudragupta, describing his military achievements and divine status."
    },
    {
        "id": 3,
        "question": "The rulers of which state provided funds to preserve the Sanchi Stupa in situ during the 19th century?",
        "options": ["Gwalior", "Bhopal", "Hyderabad", "Mysore"],
        "correct": 1,
        "explanation": "The rulers of Bhopal, Shahjehan Begum and Sultan Jehan Begum, provided funding to preserve Sanchi Stupa in situ, building a museum and a guesthouse to keep the monument intact."
    },
    {
        "id": 4,
        "question": "Under the Delhi Sultanate, what were the governors of territories of varying sizes called?",
        "options": ["Mansabdars", "Muqtis / Iqtadars", "Zabtis", "Samanthas"],
        "correct": 1,
        "explanation": "Military commanders appointed as governors of territories of varying sizes were called iqtadars or muqtis, and their assigned territories were called iqtas."
    },
    {
        "id": 5,
        "question": "Who devised the Mahalwari Land Revenue Settlement in 1822 for the North-West Provinces of Bengal Presidency?",
        "options": ["Thomas Munro", "Lord Cornwallis", "Holt Mackenzie", "Lord Dalhousie"],
        "correct": 2,
        "explanation": "The Mahalwari Settlement was devised by Holt Mackenzie in 1822, where land revenue was collected from the village or group of villages called a 'mahal' and revised periodically."
    },
    {
        "id": 6,
        "question": "What was the immediate cause of the Revolt of 1857?",
        "options": ["The Doctrine of Lapse annexation policy", "High land tax rates", "Introduction of greased cartridges for the Enfield Rifle", "The Partition of Bengal"],
        "correct": 2,
        "explanation": "The immediate spark of the Revolt of 1857 was the introduction of the Enfield Rifle, whose cartridges were rumored to be greased with cow and pig fat, which offended both Hindu and Muslim sepoys."
    },
    {
        "id": 7,
        "question": "In which year did Viceroy Lord Curzon partition Bengal, triggering the Swadeshi and Boycott Movement?",
        "options": ["1900", "1905", "1911", "1920"],
        "correct": 1,
        "explanation": "Viceroy Lord Curzon partitioned Bengal in 1905, claiming it was for administrative convenience, which led to widespread nationalist protests and the Swadeshi Movement."
    },
    {
        "id": 8,
        "question": "Why did Mahatma Gandhi suspend the Non-Cooperation Movement in February 1922?",
        "options": ["Due to the Jallianwala Bagh Massacre", "Because of a violent clash at Chauri Chaura", "He was arrested by the British", "The British accepted the demands"],
        "correct": 1,
        "explanation": "Gandhi suspended the Non-Cooperation Movement in February 1922 after a violent clash at Chauri Chaura (Gorakhpur), where a crowd set fire to a police station, killing 22 policemen, violating his principle of Ahimsa (non-violence)."
    },
    {
        "id": 9,
        "question": "How many miles did Mahatma Gandhi and his followers march during the Dandi Salt March in 1930?",
        "options": ["100 miles", "150 miles", "240 miles", "300 miles"],
        "correct": 2,
        "explanation": "Mahatma Gandhi and his 78 followers marched 240 miles from Sabarmati Ashram to the coastal town of Dandi to break the salt monopoly law."
    },
    {
        "id": 10,
        "question": "Who was the revenue minister of Mughal Emperor Akbar who conducted a 10-year survey to implement the Zabt system?",
        "options": ["Birbal", "Raja Todar Mal", "Abul Fazl", "Man Singh"],
        "correct": 1,
        "explanation": "Akbar's revenue minister Raja Todar Mal carried out a careful survey of crop yields, prices, and cultivated areas from 1570 to 1580, laying the foundation of the Zabt system."
    }
]

# Historical Timeline of India (NCERT Map)
historical_timeline = [
    {
        "era": "Ancient",
        "date": "c. 2600 - 1900 BCE",
        "title": "Harappan Civilisation",
        "description": "The peak era of urban planning, mature crafts, and trade networks in the Indus Valley, featuring sites like Mohenjodaro, Harappa, and Chanhudaro.",
        "search_query": "Explain Harappan town planning and drainage system"
    },
    {
        "era": "Ancient",
        "date": "c. 1500 - 500 BCE",
        "title": "Vedic Period",
        "description": "Composition of the Rigveda, development of early agriculture, pastoralism, and early tribal kingdoms along the Ganges plains.",
        "search_query": "What is the Vedic period in Indian history?"
    },
    {
        "era": "Ancient",
        "date": "c. 600 BCE",
        "title": "Sixteen Mahajanapadas & Rise of Buddhism/Jainism",
        "description": "The growth of sixteen early oligarchic states, the rise of Magadha, and the spiritual teachings of Siddhartha Gautama (Buddha) and Vardhamana Mahavira.",
        "search_query": "Explain the Sixteen Mahajanapadas and why Magadha was powerful"
    },
    {
        "era": "Ancient",
        "date": "c. 321 - 185 BCE",
        "title": "Mauryan Empire",
        "description": "Founded by Chandragupta Maurya. Reached its peak under Ashoka, who promoted the policy of Dhamma and inscribed ethical codes on stone pillars.",
        "search_query": "What was Ashoka's policy of Dhamma?"
    },
    {
        "era": "Ancient",
        "date": "c. 320 - 550 CE",
        "title": "Gupta Empire",
        "description": "An era of classical arts, sciences, and Sanskrit literature (often documented in Prashastis like Samudragupta's Prayaga Prashasti).",
        "search_query": "What are Prashastis and how do they describe the Gupta Empire?"
    },
    {
        "era": "Medieval",
        "date": "1206 - 1526 CE",
        "title": "Delhi Sultanate",
        "description": "Rule of the Mamluk, Khalji, Tughluq, Sayyid, and Lodi dynasties in Northern India, featuring administrative, market, and land reforms.",
        "search_query": "Describe the Iqta system and Alauddin Khalji's market control reforms"
    },
    {
        "era": "Medieval",
        "date": "1336 - 1646 CE",
        "title": "Vijayanagara Empire",
        "description": "Founded in the Deccan by Harihara and Bukka, centered in Hampi. Reached its zenith under Krishna Deva Raya, featuring grand temple architecture.",
        "search_query": "Explain the Vijayanagara Empire and Krishna Deva Raya's contributions"
    },
    {
        "era": "Medieval",
        "date": "1526 - 1857 CE",
        "title": "Mughal Empire",
        "description": "Established by Babur in the Battle of Panipat. Expanded under Akbar (Zabt system, Mansabdari system), Jahangir, Shah Jahan, and Aurangzeb.",
        "search_query": "Explain the Mansabdari system and the Zabt system in the Mughal Empire"
    },
    {
        "era": "Medieval",
        "date": "c. 14th - 17th Century",
        "title": "Bhakti and Sufi Movements",
        "description": "A cultural renaissance emphasizing mystical devotion to a personal or formless god, led by saints like Kabir, Guru Nanak, and Chishti Sufis.",
        "search_query": "Explain Sufism, Chishti silsila, and Kabir's teachings"
    },
    {
        "era": "Modern",
        "date": "1757 CE",
        "title": "Battle of Plassey",
        "description": "Robert Clive defeats Siraj-ud-Daulah, marking the beginning of British East India Company's territorial expansion in Bengal.",
        "search_query": "How did the British win the Battle of Plassey?"
    },
    {
        "era": "Modern",
        "date": "1764 CE",
        "title": "Battle of Buxar & Diwani Rights",
        "description": "British victory leads to the Treaty of Allahabad (1765), granting the Company the right to collect land revenue (Diwani) of Bengal, Bihar, and Orissa.",
        "search_query": "What was the significance of the Battle of Buxar and Diwani rights?"
    },
    {
        "era": "Modern",
        "date": "1857 CE",
        "title": "Revolt of 1857 (Sepoy Mutiny)",
        "description": "First massive armed rebellion against Company rule, starting in Meerut and led by figures like Rani Lakshmibai, Nana Sahib, and Kunwar Singh.",
        "search_query": "What were the causes and key leaders of the Revolt of 1857?"
    },
    {
        "era": "Modern",
        "date": "1905 CE",
        "title": "Partition of Bengal & Swadeshi Movement",
        "description": "Bengal is partitioned by Lord Curzon. Nationalists launch the Swadeshi and Boycott Movement promoting local goods and self-reliance.",
        "search_query": "Explain the Partition of Bengal and the Swadeshi Movement"
    },
    {
        "era": "Modern",
        "date": "1920 - 1922 CE",
        "title": "Non-Cooperation Movement",
        "description": "Gandhi launches mass non-violent protests against the British. Suspended after Chauri Chaura violence in 1922.",
        "search_query": "What were the causes and suspension of the Non-Cooperation Movement?"
    },
    {
        "era": "Modern",
        "date": "1930 CE",
        "title": "Dandi Salt March (Civil Disobedience)",
        "description": "Gandhi marches 240 miles to Dandi to break the salt law, launching the nationwide Civil Disobedience movement.",
        "search_query": "Explain the Salt Satyagraha of 1930"
    },
    {
        "era": "Modern",
        "date": "1942 CE",
        "title": "Quit India Movement",
        "description": "Gandhi gives the historic call 'Do or Die' during World War II, triggering a nationwide rebellion for immediate independence.",
        "search_query": "Explain the Quit India Movement of 1942"
    },
    {
        "era": "Modern",
        "date": "1947 CE",
        "title": "Independence and Partition",
        "description": "India gains independence from British rule, but the subcontinent is partitioned into two sovereign states: India and Pakistan.",
        "search_query": "Describe the independence and partition of India in 1947"
    }
]

# --- STARTUP CORPUS AND MODELS LOADING ---
def load_corpus():
    global corpus
    try:
        corpus_path = "data/ncert_corpus.json"
        if os.path.exists(corpus_path):
            with open(corpus_path, "r", encoding="utf-8") as f:
                corpus = json.load(f)
            print(f"Successfully loaded NCERT corpus ({len(corpus)} items).")
        else:
            print("Corpus file not found! Please run data_pipeline.py first.")
    except Exception as e:
        print(f"Error loading corpus: {e}")

def load_models_async():
    global retriever_model, corpus_embeddings, generator_tokenizer, generator_model, model_loading_status
    
    # 1. Load Sentence Transformer (Retriever)
    try:
        model_loading_status = "Loading SentenceTransformer (Retriever)..."
        from sentence_transformers import SentenceTransformer
        retriever_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Precompute embeddings
        if corpus:
            texts_to_embed = [f"{item['chapter']} - {item['title']}: {item['content']}" for item in corpus]
            corpus_embeddings = retriever_model.encode(texts_to_embed, convert_to_numpy=True)
            print("Corpus embeddings pre-computed successfully!")
        
        model_loading_status = "Retriever Ready. Loading Local LLM Generator..."
    except Exception as e:
        print(f"Failed to load Retriever: {e}")
        model_loading_status = "Retriever failed. Attempting to load LLM..."

    # 2. Load Local LLM (Qwen 0.5B Instruct)
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        
        model_id = "Qwen/Qwen2.5-0.5B-Instruct"
        print(f"Loading local LLM model: {model_id}")
        generator_tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        # Load model on CPU/GPU depending on availability
        if torch.cuda.is_available():
            generator_model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16,
                device_map="auto"
            )
        else:
            generator_model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float32
            )
        print("Local LLM model loaded successfully!")
        model_loading_status = "All Models Loaded. Ready!"
    except Exception as e:
        print(f"Failed to load local LLM generator (Reason: {e}). Will use heuristic / API mode.")
        model_loading_status = "Retriever Ready. LLM running in Heuristic/API mode."

@app.on_event("startup")
def startup_event():
    load_corpus()
    # Run the model loading in a separate thread so the server starts instantly
    threading.Thread(target=load_models_async, daemon=True).start()

# --- REQUEST AND RESPONSE SCHEMAS ---
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, str]]
    model_status: str

# --- RETRIEVAL ENGINE (RAG) ---

def preprocess_and_tokenize(query: str) -> set:
    query_lower = query.lower()
    
    # Common NCERT keyword corrections / synonym mapping
    mappings = {
        "hapmi": "hampi",
        "hampy": "hampi",
        "harapa": "harappan",
        "harrappa": "harappan",
        "harappa": "harappan",
        "harapan": "harappan",
        "harappans": "harappan",
        "asoka": "ashoka",
        "ashok": "ashoka",
        "dhama": "dhamma",
        "dharma": "dhamma",
        "moghal": "mughal",
        "mugal": "mughal",
        "mansab": "mansabdari",
        "mansabdar": "mansabdari",
        "zabti": "zabt",
        "vijayanagar": "vijayanagara",
        "vijaynagar": "vijayanagara",
        "chisti": "chishti",
        "plassy": "plassey",
        "buxer": "buxar",
        "laxmibai": "lakshmibai",
        "gandi": "gandhi",
        "satyagrah": "satyagraha",
        "swadesi": "swadeshi",
        "aabout": "about"
    }
    
    # Clean punctuation and tokenize
    words = []
    for w in query_lower.split():
        w_clean = w.strip(".,?!;:()\"'")
        # Map word if matching
        w_mapped = mappings.get(w_clean, w_clean)
        words.append(w_mapped)
        
    # Remove common stopwords
    stopwords = {
        "tell", "me", "aabout", "about", "a", "an", "the", "is", "was", "in", "of", "and", "to", 
        "for", "with", "on", "at", "by", "what", "who", "where", "how", "why", "explain", 
        "describe", "discuss", "show", "give", "some", "details", "information", "history", "ncert"
    }
    
    filtered_words = {w for w in words if w not in stopwords and len(w) > 1}
    return filtered_words

def get_keyword_score(doc: Dict[str, Any], query_words: set) -> float:
    if not query_words:
        return 0.0
    
    # Preprocess title, content, and chapter of the doc
    doc_title_words = set(doc["title"].lower().split())
    doc_title_words = {w.strip(".,?!;:()\"'") for w in doc_title_words}
    
    doc_content_words = set(doc["content"].lower().split())
    doc_content_words = {w.strip(".,?!;:()\"'") for w in doc_content_words}
    
    doc_chapter_words = set(doc["chapter"].lower().split())
    doc_chapter_words = {w.strip(".,?!;:()\"'") for w in doc_chapter_words}
    
    # Match counts
    title_matches = len(query_words.intersection(doc_title_words))
    content_matches = len(query_words.intersection(doc_content_words))
    chapter_matches = len(query_words.intersection(doc_chapter_words))
    
    # Substring scoring for extra robustness (e.g. "1857" matching part of "1857-1859")
    substring_matches = 0
    for q_word in query_words:
        if q_word in doc["title"].lower():
            substring_matches += 1.5
        if q_word in doc["chapter"].lower():
            substring_matches += 1.0
        if q_word in doc["content"].lower():
            substring_matches += 0.5
            
    # Calculate weighted score
    score = 4.0 * title_matches + 2.0 * chapter_matches + 1.0 * content_matches + substring_matches
    return score

def retrieve_relevant_contexts(query: str, top_k: int = 2) -> List[Dict[str, Any]]:
    global retriever_model, corpus_embeddings, corpus
    
    # 1. Clean query and get search terms
    query_words = preprocess_and_tokenize(query)
    print(f"Preprocessed query search terms: {query_words}")
    
    if not corpus:
        return []
        
    # 2. Compute semantic similarities (if retriever is loaded)
    similarities = np.zeros(len(corpus))
    if retriever_model is not None and corpus_embeddings is not None:
        try:
            query_emb = retriever_model.encode(query, convert_to_numpy=True)
            norm_query = query_emb / np.linalg.norm(query_emb)
            norm_corpus = corpus_embeddings / np.linalg.norm(corpus_embeddings, axis=1, keepdims=True)
            similarities = np.dot(norm_corpus, norm_query)
        except Exception as e:
            print(f"Error computing semantic embeddings: {e}")
            similarities = np.zeros(len(corpus))
            
    # 3. Compute hybrid scores
    scored_docs = []
    for idx, doc in enumerate(corpus):
        k_score = get_keyword_score(doc, query_words)
        sem_score = similarities[idx]
        
        # Hybrid combination:
        # A keyword score of 1.0+ gives a massive boost to ensure we match exact terms,
        # while the semantic score resolves ties and provides semantic matching when keywords are fuzzy.
        # If retriever is not ready, sem_score is 0.0, which works perfectly.
        hybrid_score = sem_score + 1.5 * k_score
        
        scored_docs.append((hybrid_score, doc))
        
    # Sort descending by score
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    
    # Return top_k docs that have a score > 0.15 (to filter out complete noise)
    results = []
    for score, doc in scored_docs[:top_k]:
        if score > 0.15:
            results.append(doc)
            
    return results

# --- GENERATION ENGINE ---
def generate_response_local(prompt: str) -> str:
    global generator_model, generator_tokenizer
    if generator_model is None or generator_tokenizer is None:
        raise RuntimeError("Local LLM not loaded yet")
    
    import torch
    inputs = generator_tokenizer(prompt, return_tensors="pt")
    # Move to model device
    inputs = {k: v.to(generator_model.device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = generator_model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.3,
            do_sample=True,
            pad_token_id=generator_tokenizer.eos_token_id
        )
    
    # Decode and slice out prompt
    decoded = generator_tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract only the response part
    response_part = decoded[len(generator_tokenizer.decode(inputs['input_ids'][0], skip_special_tokens=True)):]
    return response_part.strip()

def generate_response_heuristic(contexts: List[Dict[str, Any]], query: str) -> str:
    # Highly descriptive heuristic summarizing the retrieved NCERT context directly
    if not contexts:
        return ("I searched the History NCERT books, but I couldn't find a direct match for your question. "
                "Could you please rephrase it or ask something related to Ancient, Medieval, or Modern Indian history?")
    
    primary = contexts[0]
    ans = f"Based on NCERT History ({primary['class']}, Chapter: '{primary['chapter']}'), here is the relevant information:\n\n"
    ans += f"**{primary['title']}**\n{primary['content']}\n\n"
    
    if len(contexts) > 1:
        secondary = contexts[1]
        ans += f"Additionally, in relation to this, NCERT ({secondary['class']}, Chapter: '{secondary['chapter']}') states:\n"
        ans += f"*{secondary['content']}*"
    
    return ans

# --- ENDPOINTS ---

@app.get("/api/status")
def get_status():
    return {"status": model_loading_status}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages list is empty")
    
    # Get last user query
    user_query = request.messages[-1].content
    
    # 1. Retrieve context
    retrieved_docs = retrieve_relevant_contexts(user_query, top_k=2)
    
    # 2. Build Sources metadata
    sources = []
    for doc in retrieved_docs:
        sources.append({
            "class": doc["class"],
            "chapter": doc["chapter"],
            "title": doc["title"]
        })
    
    # 3. Generate answer
    answer = ""
    # Try using the local LLM if loaded
    if generator_model is not None and generator_tokenizer is not None:
        try:
            # Build Context String
            context_str = "\n\n".join([f"NCERT Source [{doc['class']} - {doc['chapter']}]: {doc['content']}" for doc in retrieved_docs])
            system_prompt = (
                "You are an expert history tutor trained on Indian History NCERT textbooks. "
                "Your task is to answer the user's question accurately using ONLY the facts provided in the NCERT Context. "
                "Do not make up any facts, names, or terms (for example, do not invent terms like 'haras' or 'cittas'). "
                "If the context does not explicitly contain the answer, say 'I cannot find that in the NCERT text.' and summarize what the context does contain. "
                "Keep your answers concise, direct, factual, and complete. Do not cutoff mid-sentence."
            )
            prompt = (
                f"<|im_start|>system\n{system_prompt}\n\n"
                f"NCERT Context:\n{context_str}<|im_end|>\n"
                f"<|im_start|>user\n{user_query}<|im_end|>\n"
                f"<|im_start|>assistant\n"
            )
            answer = generate_response_local(prompt)
        except Exception as e:
            print(f"Error in local LLM generation: {e}. Falling back to heuristic.")
            answer = generate_response_heuristic(retrieved_docs, user_query)
    else:
        # Heuristic retrieval-based formatting (extremely robust and guaranteed to work)
        answer = generate_response_heuristic(retrieved_docs, user_query)
        
    return ChatResponse(
        answer=answer,
        sources=sources,
        model_status=model_loading_status
    )

@app.get("/api/quiz")
def get_quiz():
    # Return 5 random questions
    indices = np.random.choice(len(quiz_questions), 5, replace=False)
    selected_questions = [quiz_questions[int(idx)] for idx in indices]
    return selected_questions

@app.get("/api/timeline")
def get_timeline():
    return historical_timeline

# --- STATIC FILES SERVING ---
# We serve the frontend files from the 'static' directory.
# If index.html doesn't exist, we will create it next.
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

@app.get("/")
def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

# Mount remaining static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")
