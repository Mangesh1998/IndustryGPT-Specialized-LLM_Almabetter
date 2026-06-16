# Chronicles of India: History NCERT Chatbot (IndustryGPT)

An intelligent, context-aware chatbot trained and grounded on the Indian History NCERT textbooks (Classes 6–12). The project features a hybrid retrieval-augmented generation (RAG) local chatbot server, a gamified board-style practice quiz, an interactive chronological history timeline, and a step-by-step QLoRA instruction-tuning notebook designed for Google Colab.

---

## 🌟 Key Features

*   **Tutor Chat Interface**: Interactive conversation with a sepia-scroll parchment theme. The chatbot answers history questions accurately, citing specific NCERT books and chapters in its footer.
*   **Typo-Resistant Hybrid Retriever**: Preprocesses inputs, filters common stopwords, and spell-corrects historical terms (e.g. *hapmi* $\rightarrow$ *hampi*, *harapan* $\rightarrow$ *harappan*, *asoka* $\rightarrow$ *ashoka*). It ranks documents by combining `SentenceTransformer` (`all-MiniLM-L6-v2`) semantic embeddings with exact token title/chapter weights.
*   **Text-to-Speech (TTS)**: Synthesizes responses using the browser's native Web Speech API, allowing students to listen to historical facts read aloud by the AI tutor.
*   **Interactive History Timeline Map**: A vertical, animated timeline spanning Ancient, Medieval, and Modern Indian history. Clicking on any event automatically formats and sends a query to the tutor chatbot.
*   **NCERT Practice Arena**: A gamified multiple-choice quiz covering key topics. The interface provides instant feedback (green/red highlights), keeps track of scores, and reveals the exact NCERT textbook explanation.
*   **Google Colab Fine-Tuning Workflow**: A complete, self-contained Jupyter notebook (`NCERT_History_LLM_Fine_Tuning.ipynb`) demonstrating how to fine-tune a pre-trained **`Qwen/Qwen2.5-1.5B-Instruct`** model using QLoRA (4-bit quantization) on a T4 GPU within 25 epochs.

---

## 📂 Project Directory Structure

```
/
├── data/
│   ├── ncert_corpus.json                     # Preprocessed text chunks for the local RAG retriever
│   └── ncert_qa_dataset.json                 # Instruction-tuning Q&A dataset for model training
├── static/
│   ├── index.html                            # Frontend markup
│   ├── style.css                             # Custom parchment, gold glassmorphism styling
│   └── app.js                                # Frontend logic, quiz state, and speech synthesis
├── data_pipeline.py                          # Compiles NCERT fact text and generates Q&A datasets
├── NCERT_History_LLM_Fine_Tuning.ipynb       # Jupyter notebook for Google Colab training (QLoRA)
├── main.py                                   # FastAPI server with hybrid search and background model loading
├── requirements.txt                          # Python dependencies list
└── README.md                                 # Project documentation (this file)
```

---

## 🛠️ Installation and Setup

To run the chatbot and interactive web application on your local machine:

### 1. Clone the repository and navigate to its folder
```bash
git clone https://github.com/Mangesh1998/IndustryGPT-Specialized-LLM_Almabetter.git
cd IndustryGPT-Specialized-LLM_Almabetter
```

### 2. Install dependencies
Ensure you have Python 3.10+ installed. Install the required libraries:
```bash
pip install -r requirements.txt
```

### 3. Run the Data Pipeline
Compile the NCERT corpus and create the instruction training data:
```bash
python data_pipeline.py
```

### 4. Start the FastAPI Web Server
Run the application locally:
```bash
uvicorn main:app --port 8000
```
*Note: On startup, the server precomputes the semantic vector embeddings and loads a local generator model (`Qwen/Qwen2.5-0.5B-Instruct`) in a background thread to prevent startup blocking. You can immediately chat using the retrieval engine.*

### 5. Access the Web Application
Open your web browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🤖 Model Fine-Tuning Instructions (Google Colab)

To fine-tune a pre-trained model on your NCERT question-answer dataset:

1.  Open **[Google Colab](https://colab.research.google.com/)**.
2.  Set the runtime to **T4 GPU** (`Runtime > Change runtime type > T4 GPU`).
3.  Upload the training notebook **`NCERT_History_LLM_Fine_Tuning.ipynb`** and the dataset file **`data/ncert_qa_dataset.json`** to the session storage.
4.  Run the notebook cells sequentially:
    *   It will install bitsandbytes, peft, and trl.
    *   Load `Qwen/Qwen2.5-1.5B-Instruct` in 4-bit precision.
    *   Inject LoRA adapters into linear layers.
    *   Train for 10 epochs (limited under the 25-epoch capstone constraint).
    *   Save the final adapter weights to `./ncert_history_lora_adapter`.

---

## ⚙️ Tech Stack

*   **Backend**: Python, FastAPI, Uvicorn, SentenceTransformers (`all-MiniLM-L6-v2`), Transformers (`Qwen/Qwen2.5-0.5B-Instruct`), PyTorch, NumPy, Pandas.
*   **Frontend**: HTML5, Vanilla CSS3 (glassmorphism overlays, custom sepia/gold variables), Vanilla JavaScript (ES6), Web Speech API.
*   **ML Pipeline**: QLoRA, PEFT, TRL (`SFTTrainer`), BitsAndBytes (4-bit).
