# 🍔 Foodie with DJ Agno

**An AI-Powered SaaS Backend for Restaurant Customer Service**

This project is a high-performance Django REST Framework backend that powers intelligent, RAG-capable AI agents for restaurants. Built with **Django**, **Agno (formerly Phidata)**, and **ChromaDB**, it allows each restaurant to have its own dedicated AI assistant that knows its specific menu, ingredients, and policies.

---

## 🧠 Core Architecture: RAG & Agents

This project distinguishes itself by implementing a robust **Multi-Tenant RAG (Retrieval-Augmented Generation)** architecture. Here is a deep dive into how the AI and data retrieval systems are managed.

### 1. The Agent Framework (Agno)
We use **[Agno](https://github.com/agno-agi/agno)** (formerly Phidata) as the orchestration framework for our AI agents. Agno provides the structure for:
-   **Knowledge Base Integration**: Seamless connection to vector databases.
-   **Memory Management**: handling conversation context.
-   **Tool Use**: Enabling the agent to perform specific actions (like searching the database).

### 2. Multi-Tenant RAG Implementation
Unlike simple RAG systems that dump all data into one index, this project implements strict **data isolation** for a SaaS model.

*   **Vector Database**: We use **ChromaDB** for storing vector embeddings.
*   **Dynamic Collections**:
    *   Each restaurant gets its **own dedicated collection** in ChromaDB.
    *   The collection name is dynamically generated using the restaurant's unique ID: `restaurant_{restaurant_uid}`.
    *   This ensures that when a user asks about "Pizza" at *Restaurant A*, the AI never accidentally retrieves menu items from *Restaurant B*.

**Code Reference**: `core/chat/knowledge.py`
```python
def get_restaurant_knowledge(restaurant_uid: str) -> Knowledge:
    # ...
    collection_name = f"restaurant_{restaurant_uid}"
    vector_db = get_chroma_db(collection_name)
    # ...
```

### 3. The "Restaurant Agent"
The `RestaurantAgent` is a specialized class designed to act as a professional customer service representative.

*   **Model**: Powered by OpenAI's `gpt-4o-mini` for a balance of speed and intelligence.
*   **Instructions**: The agent is prompted to:
    *   ALWAYS search the knowledge base first for menu/price info.
    *   Never hallucinate information not present in the derived context.
    *   Handle allergy queries by strictly checking ingredient lists.
*   **Context Injection**: When a user queries, the relevant "chunks" of menu data are retrieved from ChromaDB and injected directly into the LLM's system prompt before it generates an answer.

**Code Reference**: `core/chat/agent.py`

### 4. Smart Memory & Summarization
To keep costs low and context windows manageable, we use a **Rolling Summary** technique instead of sending the entire chat history every time.

1.  **Thread Storage**: The `Thread` model in Django stores the current `summary`.
2.  **Update Loop**: After every turn (User Message + AI Response), a secondary "Summarizer Agent" runs.
3.  **Optimization**: This agent reads the *old summary* + *new interaction* and compresses it into a *new summary*.
4.  **Result**: The main agent always knows the user's name and dietary preferences from 100 messages ago, without processing 100 messages worth of tokens.

---

## 🛠️ Technology Stack

*   **Backend Framework**: Django 5 + Django REST Framework (DRF)
*   **AI Framework**: Agno (v2)
*   **Vector Database**: ChromaDB (Running locally in Docker via persistent volume)
*   **LLM Provider**: OpenAI (GPT-4o-mini)
*   **Task Queue**: Celery + Redis (For background processing, future embedding updates)
*   **Database**: PostgreSQL
*   **Containerization**: Docker & Docker Compose

---

## 📂 Project Structure

```
├── core/
│   ├── chat/              # 🧠 THE BRAIN: Agent & RAG Logic
│   │   ├── agent.py       # RestaurantAgent & Summarizer definitions
│   │   ├── knowledge.py   # ChromaDB connection & Collection management
│   │   └── views.py       # API Endpoint coupling Django with Agno
│   ├── restaurants/       # Standard Django app for Restaurant models
│   ├── chroma_data/       # 💾 Persistent storage for Vector Embeddings
│   └── ...
├── docker-compose.yml     # Orchestration for Web, DB, Redis, Celery
└── verify_chat.py         # Script to test the Agent API
```

---

## 🚀 Getting Started

### Prerequisites
*   Docker & Docker Compose
*   OpenAI API Key

### 1. Setup Environment
Create a `.env` file in the root directory:

```env
# Core Django
DJANGO_ENV=local
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Docker)
DATABASE_TYPE=postgres
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Redis & Celery
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# AI & RAG
OPENAI_API_KEY=sk-your-openai-key-here
CHROMA_DB_PATH=chroma_data
```

### 2. Run with Docker
Start the entire stack (Django, Postgres, Redis, Celery):

```bash
docker-compose up --build
```

### 3. Initialize Data
Once the containers are running, apply migrations and create a superuser:

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create admin user
docker-compose exec web python manage.py createsuperuser
```

---

## 🔌 API Usage

### Chat with an Agent
**Endpoint**: `POST /api/chat/<restaurant_uid>/`

**Reference**: `core/chat/views.py`

#### 1. Start a New Conversation
```json
// POST /api/chat/123-abc-456/
{
  "message": "Do you have any vegan pizzas?"
}
```

**Response:**
```json
{
  "thread_uid": "uuid-of-new-thread",
  "ai_response": "Yes! We have the 'Garden Delight' pizza which features...",
  "created_at": "2024-03-20T10:00:00Z"
}
```

#### 2. Continue Conversation
Pass the `thread_uid` to maintain memory (context).

```json
// POST /api/chat/123-abc-456/
{
  "thread_uid": "uuid-of-new-thread",
  "message": "How much does that cost?"
}
```

---

## 🧪 Testing
We have provided a verification script to test the interaction flow:

```bash
# Edit the script to add a valid RESTAURANT_UID first!
python verify_chat.py
```

---

## 📜 License
This project is licensed under the MIT License.
