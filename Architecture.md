# Architecture Specification: AI-Powered Discovery Engine for Google Photos Retrieval

> **Document Version:** 1.0.0  
> **Status:** Approved Architecture Blueprint  
> **Reference Document:** [Problem statement.md](file:///c:/Users/ADMIN/Desktop/PRODUCT%20OWNER%20PROJECT%203/AI%20Discovery%20Engine/Problem%20statement.md)  
> **System Class:** Analytical Discovery & Qualitative-to-Quantitative Intelligence Engine

---

## 1. Executive Summary & Architectural Principles

The **AI-Powered Discovery Engine for Google Photos Retrieval** is a specialized research and intelligence platform. Its purpose is to aggregate thousands of publicly available user experiences across the web, extract structured insights regarding human memory and search friction, cluster them into verified problem spaces, and present an interactive analytical workbench for Product Managers.

### Guiding Architectural Principles

```
  ┌─────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
  │  Epistemic Integrity    │      │  Strict Discovery       │      │  Deterministic Schemas  │
  │  Every conclusion must  │ ───► │  Boundary: No premature │ ───► │  Structured Pydantic    │
  │  trace back to raw quote│      │  solutions generated    │      │  outputs across LLMs    │
  └─────────────────────────┘      └─────────────────────────┘      └─────────────────────────┘
```

1. **Epistemic Traceability (Layered Separation):** The system enforces strict isolation between:
   - **Layer 1:** Observed User Evidence (raw text, timestamps, verified links).
   - **Layer 2:** AI Interpretation (semantic tags, categorized memory cues, failure stages).
   - **Layer 3:** Opportunity Hypotheses (product opportunities for PM investigation).
2. **Strict Discovery Mandate:** The architecture is intentionally biased toward discovering failure modes, workarounds, and memory-search mismatches rather than jumping to solution generation.
3. **Reproducibility & Auditability:** Every insight, cluster, and visual chart must support a 1-click drill-down to its underlying evidence units with immutable IDs and URLs.
4. **Resilient Data Harvesting:** Multi-source ingestion workers operate with backoff, deduplication, and PII anonymization before passing data downstream.

---

## 2. High-Level System Architecture

The following diagram illustrates the end-to-end data pipeline from public source channels to the interactive dashboard.

```mermaid
flowchart TB
    subgraph Data_Sources["1. Multi-Channel Public Harvesters"]
        S1["Google Play Store API / Scraper"]
        S2["Apple App Store Scraper"]
        S3["Reddit API (r/googlephotos, etc.)"]
        S4["Google Photos Community Scraper"]
        S5["YouTube Comments / Public Forums"]
    end

    subgraph Ingestion_Layer["2. Ingestion & Preprocessing"]
        Q1["Message Queue / Job Broker (Redis / Celery)"]
        W1["Harvester Workers (Rate-limited, Backoff)"]
        P1["Data Cleaner & PII Sanitizer"]
        P2["Noise & Relevance Gate (Fast-Filter LLM)"]
    end

    subgraph Extraction_Engine["3. Multi-Dimensional LLM Extraction Engine"]
        E1["Context Normalizer"]
        E2["7-Dimension Structured Extraction\n(Groq LPU API / Llama 3.3 70B)"]
        E3["Confidence & Hallucination Auditor"]
    end

    subgraph Analytics_Clustering["4. Embedding & Clustering Engine"]
        EM1["Dense Semantic Embedder (Sentence Transformers)"]
        CL1["HDBSCAN / Hierarchical Semantic Clustering"]
        CS1["LLM Cluster Synthesizer & Schema Generator"]
        HY1["Hypothesis Validation & Correlation Engine"]
    end

    subgraph Storage_Layer["5. Dual Storage & Traceability Graph"]
        DB1[("Relational DB: PostgreSQL\n(Evidence, Metadata, Schemas)")]
        VDB[("Vector DB: Qdrant / Chroma\n(Embeddings, Similarity)")]
        FS[("Raw Archive Store: S3 / Local\n(Original Posts & Snapshots)")]
    end

    subgraph API_Presentation["6. Backend API & Interactive Workbench"]
        API["FastAPI Gateway / REST Endpoints"]
        D1["Dash 1: Source Overview"]
        D2["Dash 2: Retrieval Scenarios"]
        D3["Dash 3: Memory Patterns"]
        D4["Dash 4: Search Behaviors"]
        D5["Dash 5: 7-Stage Failure Map"]
        D6["Dash 6: Problem Clusters"]
        D7["Dash 7: Opportunity Areas"]
    end

    Data_Sources --> W1
    W1 --> Q1
    Q1 --> P1
    P1 --> P2
    P2 -->|Relevant Retrieval Posts| E1
    E1 --> E2
    E2 --> E3
    E3 --> DB1
    E3 --> FS
    E3 --> EM1
    EM1 --> VDB
    VDB --> CL1
    CL1 --> CS1
    CS1 --> DB1
    DB1 --> HY1
    HY1 --> API
    DB1 --> API
    VDB --> API
    API --> D1 & D2 & D3 & D4 & D5 & D6 & D7
```

---

## 3. Subsystem Decompositions & Component Specifications

### 3.1. Subsystem 1: Harvesting & Ingestion Pipeline

The ingestion layer orchestrates concurrent, rate-limited workers tailored to each public data channel.

```mermaid
sequenceDiagram
    participant Harvester as Source Harvester
    participant Queue as Redis Queue
    participant Worker as Normalization Worker
    participant DB as Raw Store (PostgreSQL)

    Harvester->>Harvester: Query public channel (keywords, threads, reviews)
    Harvester->>Queue: Push raw batch {source, raw_content, url, author, timestamp}
    Queue->>Worker: Dequeue message
    Worker->>Worker: Clean HTML / emojis / boilerplate
    Worker->>Worker: PII Masking (names, emails, phone numbers)
    Worker->>Worker: Compute deduplication hash (SHA-256)
    Worker->>DB: Upsert into raw_posts table (status: PENDING_EXTRACTION)
```

#### Key Ingestion Specifications:
- **Deduplication:** Hash calculation on `(normalized_text, source_channel, post_date)` prevents redundant processing.
- **Relevance Gate:** A lightweight binary classifier (DistilBERT or small LLM prompt) scores whether the post discusses an **actual photo retrieval experience or search problem** versus generic praises/app crashes. Only posts with a relevance score $\ge 0.70$ advance to LLM extraction.

---

### 3.2. Subsystem 2: Multi-Dimensional LLM Extraction Engine

This subsystem extracts the **7 mandatory discovery dimensions** defined in the Problem Statement using strict JSON schemas (via Pydantic and Instructor).

```mermaid
flowchart TD
    RawPost["Sanitized User Post"] --> PromptEngine["Prompt Orchestrator\n(Role: Expert Qualitative Researcher)"]
    PromptEngine --> LLM["Groq LPU API (Llama 3.3 70B Versatile)\nStructured JSON / Tool Calling Mode"]
    LLM --> Validator{"Pydantic Validation (Instructor)"}
    Validator -- Pass --> ExtractedRecord["Validated Evidence Record"]
    Validator -- Fail --> Fallback["Correction Prompt / Human Review Queue"]
    ExtractedRecord --> TraceabilityCheck["Attach Source URL + Quote Snippet"]
    TraceabilityCheck --> Persistence["Write to PostgreSQL & Vector Store"]
```

#### Extraction Schema (Pydantic / Structured Output)

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class RetrievalScenario(str, Enum):
    OLD_FAMILY = "Old family photo"
    CHILDHOOD = "Childhood photo"
    TRAVEL = "Travel / vacation photo"
    SPECIFIC_PERSON = "Photo with specific person"
    EVENT_MILESTONE = "Event / milestone"
    FOOD_DINING = "Food / dining"
    SCREENSHOT = "Screenshot (receipts, chats, info)"
    DOCUMENT_ID = "Document / physical paper"
    NATURE_SCENERY = "Nature / scenery"
    OTHER = "Other"

class FailurePoint(str, Enum):
    RECALL_DEFICIT = "Cannot recall enough information"
    QUERY_TRANSLATION_GAP = "Cannot express memory as search query"
    DIRECTIONAL_PARALYSIS = "Does not know what to search"
    SEMANTIC_MISMATCH = "Search interpretation does not match intent"
    TOO_MANY_RESULTS = "Too many results / no relevance sorting"
    IRRELEVANT_RESULTS = "Results are completely not relevant"
    RECOGNITION_DIFFICULTY = "Relevant photo difficult to recognize"
    REFINEMENT_IMPASSE = "Cannot refine a failed search"
    COGNITIVE_FATIGUE = "Search requires too much manual effort"
    OTHER = "Other"

class UserOutcome(str, Enum):
    SUCCESSFUL = "Successfully retrieved"
    RETRIEVED_HIGH_EFFORT = "Retrieved after multiple attempts"
    RETRIEVED_MANUAL_BROWSE = "Retrieved through manual browsing"
    RETRIEVED_ANOTHER_METHOD = "Retrieved using another method"
    ABANDONED = "Could not retrieve (abandoned)"
    UNKNOWN = "Outcome unknown"

class ExtractedEvidenceRecord(BaseModel):
    # Layer 1: Raw Grounding
    source_channel: str = Field(description="Platform source")
    source_url: str = Field(description="Direct URL to original post")
    post_date: Optional[str] = Field(description="ISO-8601 date string")
    verbatim_quote: str = Field(description="Exact excerpt describing retrieval")
    
    # Layer 2: Extracted Discovery Dimensions
    scenario_type: RetrievalScenario
    scenario_custom_description: Optional[str]
    
    remembered_clues: List[str] = Field(
        description="People, relationships, activities, settings, objects, feelings, approximate time"
    )
    forgotten_metadata: List[str] = Field(
        description="Exact date, GPS coordinates, person name, album name, filename"
    )
    search_behaviors: List[str] = Field(
        description="Search by face, search by place, timeline scroll, query iterations, etc."
    )
    failure_point: FailurePoint
    workarounds: List[str] = Field(
        description="Compensatory actions: external chat backup, asking relatives, brute-force scrolling"
    )
    user_outcome: UserOutcome
    
    # Epistemic Audit Guardrail
    ai_confidence_score: float = Field(ge=0.0, le=1.0)
    ai_interpretation_notes: str = Field(
        description="Explicit explanation of AI reasoning without altering user statements"
    )
```

#### Groq Client & Instructor Integration Pattern

```python
import os
from groq import Groq
import instructor

# Initialize Groq client with Instructor for deterministic Pydantic extraction
raw_groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
client = instructor.from_groq(raw_groq_client, mode=instructor.Mode.JSON)

def extract_discovery_dimensions(raw_text: str, source_url: str, post_date: str) -> ExtractedEvidenceRecord:
    """Extracts the 7 discovery dimensions using Groq LPU ultra-high-speed inference."""
    return client.chat.completions.create(
        model=os.environ.get("GROQ_MODEL_EXTRACTION", "llama-3.3-70b-versatile"),
        response_model=ExtractedEvidenceRecord,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a rigorous Qualitative Discovery Researcher analyzing Google Photos retrieval failures. "
                    "Extract observations into the requested schema without hallucinating missing details. "
                    "Never invent facts not present in the user text."
                ),
            },
            {
                "role": "user",
                "content": f"Source URL: {source_url}\nDate: {post_date}\nUser Post:\n{raw_text}",
            },
        ],
        temperature=0.1,
    )
```

---

### 3.3. Subsystem 3: Semantic Embedding & Problem Clustering Engine

To identify cross-source patterns without introducing human bias or arbitrary metrics, the engine combines dense vector representations with density-based clustering (HDBSCAN).

```mermaid
flowchart LR
    EVID["Extracted Evidence Records"] --> FEAT["Feature Synthesizer:\nText Representation of Failure + Memory Gap"]
    FEAT --> EMB["Dense Embedder\n(e.g., BAAI/bge-small-en-v1.5 / FastEmbed)"]
    EMB --> REDUCE["UMAP Dimensionality Reduction\n(Preserve Global & Local Structure)"]
    REDUCE --> CLUST["HDBSCAN Clustering\n(Identify Natural Density Clusters)"]
    CLUST --> SYNTH["Groq LPU Synthesizer (Llama 3.3 70B)\n(Extract Common Theme, Schema, Severity)"]
    SYNTH --> OUT["Problem Clusters + Evidence Links"]
```

#### Problem Cluster Synthesizer Specification
For every cluster $C_k$ identified by HDBSCAN:
1. **Representative Exemplars Extraction:** Select the 5 evidence records closest to the cluster centroid.
2. **Cluster Synthesis Prompt:** An LLM processes the aggregated records and outputs the mandatory schema:
   - `problem_name`: Descriptive, non-prescriptive title.
   - `description`: Detailed mechanics of how retrieval fails for this cluster.
   - `frequency`: Absolute and percentage occurrence across total analyzed dataset.
   - `severity_indicators`: User friction level, emotional frustration, estimated time lost.
   - `retrieval_impact`: Measurable effect on search abandonment.
   - `common_user_behavior`: Recurring patterns in how users reacted.
   - `common_workaround`: Workaround techniques discovered.
   - `sources_present`: Multi-source presence (e.g., Reddit + Play Store + Help Community).
   - `representative_evidence`: Array of canonical evidence records with direct URLs.
   - `potential_opportunity_area`: Formulated PM discovery hypothesis for further research.

---

### 3.4. Subsystem 4: Hypothesis Testing & Analytics Engine

The Problem Statement establishes an explicit research question:
> *Is there an empirical mismatch between how people naturally remember a photo (episodic, contextual) vs. how photo systems index/retrieve photos (exact metadata, formal keywords)?*

The Analytics Engine computes statistical proof:

```mermaid
flowchart TD
    subgraph Data_Inputs["Empirical Evidence Ingestion"]
        R_MEM["Remembered Clues Distribution:\nActivities, People, Environment, Emotion"]
        F_MET["Forgotten Metadata Distribution:\nExact Dates, Geotags, Filenames, Terminology"]
    end

    subgraph Correlation_Engine["Mismatch Validation Logic"]
        CONT["Contingency Table Analysis\n(Episodic Clues vs Metadata Recall)"]
        CHI["Chi-Squared Test of Independence / Cramér's V"]
        FUNNEL["7-Stage Funnel Dropout Calculation"]
    end

    subgraph Empirical_Outputs["Dashboard Visual Insights"]
        V1["Episodic vs Lexical Gap Ratio"]
        V2["Stage-by-Stage Failure Conversion Rate"]
        V3["Hypothesis Validation Confidence Score"]
    end

    R_MEM & F_MET --> CONT
    CONT --> CHI
    CHI --> V1
    CONT --> FUNNEL
    FUNNEL --> V2
    CHI & FUNNEL --> V3
```

#### Funnel Mathematics
The 7-stage retrieval journey is modeled as an empirical transition Markov chain:

$$P(\text{Success}) = \prod_{i=1}^{6} (1 - \lambda_i)$$

Where $\lambda_i$ is the dropout (failure) rate at stage $i$:
1. **Stage 1 (Memory $\rightarrow$ Query Formulation):** Drop rate where user cannot formulate a query ($\lambda_1$).
2. **Stage 2 (Query Formulation $\rightarrow$ Search Execution):** Query syntax error or search reluctance ($\lambda_2$).
3. **Stage 3 (Search Execution $\rightarrow$ Results Display):** Zero results returned ($\lambda_3$).
4. **Stage 4 (Results Display $\rightarrow$ Visual Recognition):** Too many results or irrelevant clutter ($\lambda_4$).
5. **Stage 5 (Visual Recognition $\rightarrow$ Query Refinement):** Failure to recognize thumbnail or refine terms ($\lambda_5$).
6. **Stage 6 (Query Refinement $\rightarrow$ Retrieval):** Abandonment after repeated failed refinements ($\lambda_6$).

---

## 4. Database & Storage Architecture

### 4.1. Relational Schema (PostgreSQL)

```mermaid
erDiagram
    DATA_SOURCE ||--o{ RAW_POST : produces
    RAW_POST ||--o| EXTRACTED_EVIDENCE : generates
    EXTRACTED_EVIDENCE }o--o{ PROBLEM_CLUSTER : belongs_to
    PROBLEM_CLUSTER ||--o{ OPPORTUNITY_AREA : informs

    DATA_SOURCE {
        uuid id PK
        varchar channel_name
        varchar base_url
        boolean is_active
        timestamp last_scraped_at
    }

    RAW_POST {
        uuid id PK
        uuid source_id FK
        text raw_text
        varchar canonical_url
        varchar post_author
        timestamp post_created_at
        varchar deduplication_hash UK
        float relevance_score
        varchar processing_status
    }

    EXTRACTED_EVIDENCE {
        uuid id PK
        uuid raw_post_id FK
        varchar scenario_type
        jsonb remembered_clues
        jsonb forgotten_metadata
        jsonb search_behaviors
        varchar failure_point
        jsonb workarounds
        varchar user_outcome
        text verbatim_quote
        float ai_confidence_score
        text ai_notes
        timestamp created_at
    }

    PROBLEM_CLUSTER {
        uuid id PK
        varchar problem_name
        text description
        int evidence_count
        float severity_score
        float retrieval_impact_rate
        jsonb common_behaviors
        jsonb common_workarounds
        jsonb source_distribution
        timestamp updated_at
    }

    CLUSTER_EVIDENCE_JUNCTION {
        uuid cluster_id FK
        uuid evidence_id FK
        float distance_to_centroid
    }

    OPPORTUNITY_AREA {
        uuid id PK
        uuid cluster_id FK
        varchar title
        text description
        text validation_hypothesis
        jsonb target_questions
    }
```

### 4.2. Vector Store Schema (Qdrant / Chroma)
- **Collection Name:** `photos_retrieval_evidence`
- **Vector Dimensions:** 1536 / 3072 (Dense cosine metric)
- **Payload Indexing:**
  - `scenario_type`: Keyword
  - `failure_point`: Keyword
  - `user_outcome`: Keyword
  - `source_channel`: Keyword
  - `cluster_id`: UUID

---

## 5. Frontend & Interactive Workbench Architecture

The presentation layer is built as a modular Single Page Application (Next.js / React with Tailwind CSS and Recharts/D3) connecting to the FastAPI backend. It fulfills the **7 required dashboards**:

```mermaid
graph TD
    subgraph UI_Shell["Interactive Discovery Workbench (UI Shell)"]
        NAV["Global Navigation & Source Filter Bar"]
        FILTERS["Filters: Date Range | Source Platforms | Failure Stage | Photo Scenario"]
    end

    subgraph Dashboards["7 Specialized Analytical Views"]
        D1["View 1: Source Overview\n(Source distribution, volume, canonical links)"]
        D2["View 2: Retrieval Scenarios\n(Photo types, difficulty cross-tabs, word clouds)"]
        D3["View 3: Memory Patterns\n(Co-occurrence heatmap: Remembered vs. Forgotten)"]
        D4["View 4: Search Behavior\n(Tactic distribution, query iteration sankey)"]
        D5["View 5: 7-Stage Failure Funnel\n(Step-by-step dropout rates & root causes)"]
        D6["View 6: Problem Clusters\n(Cluster cards, multi-source evidence inspector)"]
        D7["View 7: Opportunity Areas\n(Prioritized hypotheses, PM primary research questions)"]
    end

    NAV --> FILTERS
    FILTERS --> D1 & D2 & D3 & D4 & D5 & D6 & D7
```

### Component Details of the 7 Dashboards

| Dashboard View | Primary Visualizations | Interactive Capabilities |
| :--- | :--- | :--- |
| **1. Source Overview** | Donut chart of platforms, timeline ingestion line chart, data health KPIs. | Click platform to filter global state; click rows to inspect live web sources. |
| **2. Retrieval Scenarios** | Horizontal bar chart of scenario frequencies, stacked difficulty metrics. | Filter by scenario (e.g., "Childhood photos") to isolate downstream failure points. |
| **3. Memory Patterns** | Dual-axis correlation plot, co-occurrence matrix (Sensory cues vs. Missing metadata). | Hover to see verbatim user memory descriptions (e.g., "blue sweater", "cabin"). |
| **4. Search Behavior** | Sankey diagram of initial action $\rightarrow$ secondary action $\rightarrow$ outcome. | Track migration from search bar to timeline scrolling to abandonment. |
| **5. 7-Stage Failure Map** | Funnel chart displaying attrition across the 7 stages of photo retrieval. | Click any stage (e.g., "Semantic Mismatch") to view all matching evidence records. |
| **6. Problem Clusters** | Card grid with severity badges, radar charts of sources, centroid distance view. | Expand cluster card to view all associated quotes, URLs, and workarounds. |
| **7. Opportunity Areas** | Opportunity matrix (Severity vs. Evidence Volume), PM discovery synthesis. | Export discovery dossier for user research teams; copy research interview questions. |

---

## 6. Epistemic Traceability & Audit Layer

To prevent hallucinations and guarantee that findings are defensible in leadership reviews, the platform embeds a **3-Layer Epistemic Pipeline**:

```mermaid
flowchart TD
    subgraph L1["Layer 1: Observed Evidence (Objective Reality)"]
        Q["User Quote: 'I typed my dog's name and lake, but Google Photos just gave me random pictures of grass from 2021.'"]
        M["Metadata: Reddit r/googlephotos | 2024-03-12 | URL"]
    end

    subgraph L2["Layer 2: AI Interpretation (Structured Analysis)"]
        S["Scenario: Travel / Pet"]
        R["Remembered: Dog name, Lake setting"]
        F["Forgotten: Date, Geotag"]
        FP["Failure Point: Semantic Mismatch & Irrelevant Results"]
        C["Cluster: Unanchored Entity & Natural Setting Failure"]
    end

    subgraph L3["Layer 3: Opportunity Hypothesis (PM Strategic Direction)"]
        O["Hypothesis: Users anchor searches on associative relationships (Dog + Vacation) rather than visual object classes."]
        PR["Primary Research Question: How do users expect relational search operators to function without manual tagging?"]
    end

    L1 -->|Strict Parsing| L2
    L2 -->|Synthesis & Clustering| L3

    style L1 fill:#e8f5e9,stroke:#4caf50,stroke-width:2px;
    style L2 fill:#e3f2fd,stroke:#2196f3,stroke-width:2px;
    style L3 fill:#fff3e0,stroke:#ff9800,stroke-width:2px;
```

### Traceability Rules:
1. Every card in Dashboard 6 and 7 contains an audit badge showing: `Source Platform`, `Timestamp`, and `Verbatim Quote`.
2. AI-generated text is visually styled with distinctive typography and labels to distinguish it from direct user quotes.
3. Every API response returns both the interpretation and the reference `raw_post_id`.

---

## 7. Non-Functional Requirements & Guardrails

### 7.1. Performance & Scalability
- **Ingestion Throughput:** Supports asynchronous batching of up to 50,000 public posts per 24-hour cycle.
- **LLM Extraction Latency:** Sub-second async queue dispatch; batch token optimization with LLM prompt caching.
- **Query Performance:** Dashboard API aggregations respond in $< 250\text{ ms}$ via PostgreSQL materialized views and indexed JSONB columns.

### 7.2. Privacy, Compliance & Ethics
- **Public Data Only:** Scrapers exclusively read publicly accessible pages; no private user accounts, walled gardens, or authenticated user sessions are accessed.
- **PII Scrubbing:** Automated Regex + Named Entity Recognition (NER) strips emails, phone numbers, real names, and IP addresses prior to database storage.
- **Scraping Politeness:** Strict honoring of `robots.txt`, randomized request jitter, exponential backoff, and distributed user-agent rotation.

### 7.3. System Cost Optimization & Groq LPU Tiering
- **Tiered Groq Inference Strategy:**
  - *Tier 1 (Relevance & Noise Filter):* Groq `llama-3.1-8b-instant` (~800–1200 tokens/sec, near-zero cost) for sub-100ms binary gating of scraped posts.
  - *Tier 2 (7-Dimension Qualitative Extraction):* Groq `llama-3.3-70b-versatile` (~250–350 tokens/sec) with strict JSON schema validation via Instructor.
  - *Tier 3 (Cluster Synthesis & Executive Dossier):* Groq `llama-3.3-70b-versatile` for synthesising cluster definitions and answering the 8 PM discovery questions.
- **Rate Limit Management:** Built-in token-bucket rate limiter respecting Groq's Requests Per Minute (RPM) and Tokens Per Minute (TPM) quotas with automatic retry and exponential backoff.

---

## 8. Deployment & Infrastructure Blueprint

```mermaid
flowchart LR
    subgraph Host_Environment["Dockerized Infrastructure"]
        NGINX["NGINX Reverse Proxy / SSL"]
        FRONTEND["Next.js Web Client\n(Port 3000)"]
        BACKEND["FastAPI Application Server\n(Port 8000)"]
        REDIS["Redis Broker & Cache\n(Port 6379)"]
        CELERY["Celery Ingestion Workers"]
        POSTGRES[("PostgreSQL 16\n(Port 5432)")]
        QDRANT[("Qdrant Vector DB\n(Port 6333)")]
    end

    Internet((Public Internet)) --> NGINX
    NGINX --> FRONTEND
    NGINX --> BACKEND
    BACKEND --> REDIS
    BACKEND --> POSTGRES
    BACKEND --> QDRANT
    CELERY --> REDIS
    CELERY --> POSTGRES
```

### Environment Configuration (.env Specification)

```ini
# Application Configuration
APP_ENV=production
LOG_LEVEL=info
SECRET_KEY=generate_secure_random_key

# Database Connections
DATABASE_URL=postgresql://discovery_user:secure_pwd@postgres:5432/discovery_db
VECTOR_DB_URL=http://qdrant:6333
REDIS_URL=redis://redis:6379/0

# Groq API Configuration
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL_EXTRACTION=llama-3.3-70b-versatile
GROQ_MODEL_FAST_FILTER=llama-3.1-8b-instant
GROQ_MODEL_SYNTHESIS=llama-3.3-70b-versatile

# Harvester Rate Limits
MAX_REQUESTS_PER_MINUTE_REDDIT=30
MAX_REQUESTS_PER_MINUTE_PLAYSTORE=60
INGESTION_BATCH_SIZE=100
```

---

## 9. PM Executive Synthesis Module

The final layer of the architecture automates the synthesis of the 8 core discovery questions into an executive report format:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       EXECUTIVE DISCOVERY DOSSIER                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Hardest Photos to Retrieve: Childhood, Documents/IDs, Candid Moments     │
│ 2. What Users Naturally Remember: Atmosphere, People present, Activities    │
│ 3. What Users Lack: Exact calendar year, Geotag, Album assignment           │
│ 4. Search Under Incomplete Memory: Brute-force scrolling, synonym testing   │
│ 5. Primary Breakdown Stage: Semantic Mismatch & Directional Paralysis       │
│ 6. Dominant Workarounds: External messaging search (WhatsApp), Asking kin   │
│ 7. Cross-Channel Consistency: Play Store & Reddit share identical friction  │
│ 8. Priority Research Questions: Validation of Relational & Experiential UX   │
└─────────────────────────────────────────────────────────────────────────────┘
```

This completes the end-to-end technical and architectural design of the AI-Powered Discovery Engine.
