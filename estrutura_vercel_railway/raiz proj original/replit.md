# Legal Pro - Sistema Jurídico Multi-Agente

## Overview
Legal Pro is an advanced multi-agent AI system designed to revolutionize legal practice. It integrates 368 specialized agents across 22 legal areas, offering comprehensive capabilities such as audio/video transcription, deep document analysis, mind map generation, 557 professional legal templates, and synthetic legal processes with authentic Brazilian data. The system includes a complete CPFL/RGE Smart Legal Analytics module with Excel export functionality for 6 report types, a hearings management system, and a RAG legal agent. Its primary purpose is to provide precise legal analysis and high-level professional insights, leveraging cutting-edge AI technologies and vector databases, with a business vision to transform legal practice.

## User Preferences
Estilo de comunicação preferido: Linguagem simples e cotidiana.

## System Architecture

### Performance Optimization
- **Cache System**: Comprehensive caching for Zoom API tokens/data and BERT analysis to reduce redundant calls.
- **Lazy Loading**: Advanced lazy loading for API clients, Zoom module, BERT models, and deferred heavy operations to optimize startup time.
- **Startup Optimization**: `startup_optimizer.py` manages lazy modules and deferred operations, ensuring fast server readiness (<1s) with background initialization of heavy modules.
- **Deployment Health Check System**: Robust health checks (`/`, `/health`, `/healthz`, `/readyz`) respond in milliseconds, ensuring deployment safety and responsiveness during initialization.

### UI/UX Decisions
- **Frontend Framework**: Flask 3.0 with responsive Bootstrap 5 templates.
- **Styling**: Dark theme with `#3b576f` primary palette; standardized color system across 24 legal areas.
- **UI Visualizations**: Interactive dashboards and reports utilize Chart.js.

### Technical Implementations
- **Core Framework**: Flask 3.0 with a modular backend.
- **Relational Database**: PostgreSQL 16 (Neon Cloud) with 81 tables; supports SQLite, local PostgreSQL (Docker), and Neon.
- **Vector Database**: Qdrant Cloud for semantic search and RAG.
- **ORM**: SQLAlchemy.
- **Multi-Agent System**: 368 agents (330 active) in a hierarchical structure across 22 legal areas with custom vector bases.
- **Dynamic Forms**: JSONB-based dynamic forms for 15 legal areas with mirrored Python/JavaScript schemas.
- **Authentication and Permissions**: Flask-Login based system with Master, Admin, and Lawyer access levels.

### Feature Specifications
- **Hybrid Transcription System**: AssemblyAI and OpenAI Whisper for audio processing.
- **Mind Map Generation**: Interactive mind maps from various inputs using GPT-4o and Mermaid.js.
- **Legal Template System**: 557 professional templates with a visual editor, dynamic variables, and DOCX export.
- **Cash Flow Operacional Module**: Database-driven management of operational cash flow, no hardcoding.
- **Document Comparison**: Utilizes `diff_match_patch` for DOCX, TXT, PDF comparison, with optional AI contextual analysis.
- **Legal Process Management**: Comprehensive system for managing legal processes including financial, risk, and geographical analysis.
- **AI Analysis System**: 4 types of AI analysis (Estratégica, Técnica, Estatística, Preditiva) generate JSON and DOCX output using GPT-4o.
- **CPFL/RGE Smart Legal Analytics**: 6 executive reports, dashboards, and Excel/PDF export for energy sector processes.
- **CPFL Legal Agent**: RAG system using Qdrant and OpenAI embeddings for CPFL processes.
- **CPFL Hearings Module**: Manages judicial hearing schedules with interactive filters and Excel export.
- **Fintechs Analytics**: Dashboards for major fintech companies with Chart.js visualizations and PDF/Excel exports.
- **Contextual Multi-Agent Workflows**: Executes workflows with user-provided context.
- **Judit Platform Integration**: Monitoring and querying of Brazilian judicial processes.
- **Statistical Legal Models**: Recommendation system for defenses and ML-based predictions.
- **Area-Specific Legal Assistants**: 18 main assistants with lazy loading and interactive chat.
- **Conversation Management System**: Save, export (TXT), clear, and load chat sessions with agents.
- **Synthetic Legal Data Generation**: Creates mass synthetic processes with authentic Brazilian data.
- **Database Administration System**: Web-based interface at `/admin/database` for database mode switching, sync, backup/restore, and real-time monitoring.
- **Zoom Meetings Integration**: Complete Zoom API integration for managing meetings, recordings, webinars, participants, and user profiles, with robust caching.
- **Análise Legal BERTimbau**: Advanced NLP for legal document analysis (entity extraction, classification, summarization, problem detection) optimized for Brazilian Portuguese, with intelligent caching.

## External Dependencies

### AI Providers
- **OpenAI**: GPT-5, GPT-4o, Whisper, text-embedding-3-large.
- **Anthropic**: Claude Sonnet 4, Claude 3.5 Sonnet, Claude Opus 4.
- **Google**: Gemini 2.5 Flash, Gemini 2.5 Pro, Gemini 1.5 Pro.
- **DeepSeek**: DeepSeek Chat, DeepSeek Reasoner, DeepSeek Coder.
- **AssemblyAI**: Primary audio transcription.

### Databases
- **Neon (PostgreSQL)**: Relational database hosting.
- **Qdrant Cloud**: Vector database.

### Libraries and Tools
- **Python**: Flask, SQLAlchemy, psycopg2-binary, gunicorn, PyPDF2, python-docx, reportlab, diff-match_patch, beautifulsoup4, openai-whisper, assemblyai, pydub, soundfile, gtts, pandas, numpy, plotly, textblob, vadersentiment, qdrant-client, requests, python-dotenv, schedule, tqdm, colorama, psutil.
- **JavaScript**: Chart.js, d3-geo, topojson-client, recharts, leaflet, react-leaflet, react-leaflet-markercluster, leaflet.heat, geolib, lucide-react, xlsx.