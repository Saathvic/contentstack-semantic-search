# AGENTS.md

## Project Overview

This is a Contentstack Marketplace App that provides semantic, embeddings-based search across CMS content entries. The system uses sentence-transformers for generating embeddings, Pinecone as the vector database, and real-time synchronization via Contentstack webhooks to enable intelligent search that understands meaning and intent, not just keyword matches.

## Architecture

- **Backend**: Python Flask server handling webhooks and search API
- **Embeddings**: sentence-transformers (Hugging Face) for vector generation
- **Vector DB**: Pinecone for scalable similarity search
- **Frontend**: React app hosted via Contentstack Launch
- **CMS**: Contentstack for content management and webhook triggers
- **Sync**: Real-time indexing via Contentstack webhooks

## Getting Started

1. **Install dependencies:**
   - Backend: `pip install flask requests sentence-transformers pinecone-client`
   - Frontend: `npm install` (if using React/Next.js)
   - Set required environment variables for API keys.
2. **Local Sync Server:**
   Run the webhook sync server using:

```
python webhook_server.py
ngrok http 5000  # Use the printed URL for webhook setup
```

The endpoint `/webhook` must be public for Contentstack to trigger.
3. **Configure Contentstack Webhook:**
    - Set URL to ngrok/public URL + `/webhook`.
    - Enable events: entry created, updated, deleted.
    - Enable "Send Content in Payload" for full entry data.

## Query Rewriting with Gemini or Other LLMs

Modern semantic search benefits from **query rewriting or expansion**, where the user’s original query is reformulated into multiple related forms to better capture the intended meaning and increase recall.

- **Gemini or other LLMs** can take a user’s free-text query (e.g., "red high top sneakers with stripes") and generate multiple semantically related or paraphrased queries such as:
  - "red sneakers with white stripes"
  - "high-top shoes in red"
  - "striped red athletic shoes"
- These expanded queries are then converted to embeddings and used to search the vector database, increasing the chances of matching relevant entries.
- This technique mitigates ambiguity and improves coverage by broadening the query beyond strict keyword matches.

### Implementation Tips:

- Use LLM APIs to generate 3-5 related query rewrites.
- Combine embeddings from the original and rewritten queries for a composite search vector or run multiple queries and merge results by similarity.
- Balance precision and recall to avoid too broad or irrelevant matches.
- LLM rewriting can be performed just before generating vector embeddings in your search API backend.

## Build \& Test Commands

```bash
# Start webhook server locally
python webhook_server.py

# Expose locally via ngrok for webhook testing
ngrok http 5000

# Test embedding generation
python test_embeddings.py

# Run frontend (React)
npm start

# Test search functionality with curl
curl -X POST http://localhost:5000/search -d '{"query": "red sneakers"}' -H "Content-Type: application/json"
```

## Key Files \& Structure

- `webhook_server.py` - Flask server handling Contentstack webhooks
- `embeddings.py` - sentence-transformers embedding generation
- `search_api.py` - Search endpoint and Pinecone integration
- `query_rewriter.py` - Query rewriting using Gemini or other LLMs
- `frontend/` - React UI components for search interface
- `config.py` - Environment variables and configuration
- `requirements.txt` - Python dependencies

## Security

- Never commit API keys to version control
- Use environment variables for all credentials
- Validate webhook payloads before processing
- Implement rate limiting for search API in production
- Use HTTPS endpoints for webhook URLs

## Testing Instructions

- Create test entries in Contentstack with varied content
- Verify webhook calls reach Flask server via ngrok logs
- Test embedding generation with sample text
- Validate query rewriting produces useful alternatives
- Perform semantic searches and validate ranking and relevance
- Test real-time sync by updating entries in Contentstack

## Deployment Notes

- Deploy Flask backend to cloud provider with public HTTPS endpoint
- Update Contentstack webhook URL to production endpoint
- Deploy React frontend via Contentstack Launch
- Configure Pinecone index with appropriate dimensions for sentence-transformers model
- Monitor webhook delivery failures and search performance


## Module 1: Contentstack Content Setup

* Define content types and create sample entries in Contentstack CMS.

## Module 2: Content Fetch & Sync

* Fetch initial entries via Contentstack Delivery API.
* Set up Contentstack Webhooks for entry created/updated/deleted events.
* Build webhook backend (Flask/Node.js) to process payloads.
* Sync changes (via webhook) with semantic index in real time.

## Module 3: Embeddings Generation

* Generate vector embeddings from content text using sentence-transformers or similar.
* Prepare data for vector indexing.

## Module 4: Vector Database & Semantic Search

* Set up Pinecone or other vector DB.
* Insert/update/delete entry vectors in vector DB.
* Query vector DB for similarity search.

## Module 5: Query Expansion Using LLM (Gemini)

* Use Gemini or other LLM to rewrite user queries into multiple related expressions.
* Expand search space for better recall.

## Module 6: Search API Backend

* Develop REST API service to accept search queries.
* Generate query embeddings.
* Search vector DB and return ranked results.

## Module 7: Marketplace App UI

* Build React frontend hosted on Contentstack Launch.
* Allow search inputs, show results with filtering and pagination.

## Module 8: Testing, Deployment, & Monitoring

* End-to-end testing of syncing and search quality.
* Deploy backend & frontend.
* Monitor webhook health, indexing, and search API performance.
