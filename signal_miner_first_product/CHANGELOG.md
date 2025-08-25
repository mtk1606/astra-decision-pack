# GrowthSignal MVP - Changelog

All notable changes to the GrowthSignal MVP project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Robots.txt enforcement and rate limiting
- Enhanced PII detection and redaction
- Compliance dashboard and monitoring
- API layer for external integrations
- Async processing for multiple URLs
- Cloud storage integration

## [1.0.0] - 2024-01-15

### Added
- **Signal Mining Engine**: Multi-site web scraper with BeautifulSoup and structured data extraction
- **RAG Decision Pack Generator**: OpenAI embeddings + vector storage + GPT-4o-mini for automated hypothesis generation
- **Streamlit Multi-Page UI**: Dashboard, run detail viewer, Decision Pack editor with auto-generation
- **GitHub PR Automation**: Branch creation, file commits, PR generation with preview mode fallback
- **Compliance Framework**: Robots.txt respect, PII detection/redaction, data retention policies
- **Testing Infrastructure**: Unit tests with mocking, CI/CD pipeline, coverage reporting, security scanning
- **Marketing Assets**: Email templates, LinkedIn DMs, landing page hero, pilot onboarding questionnaire

### Changed
- **Architecture**: Evolved from basic signal miner to full-stack competitive intelligence platform
- **Data Flow**: Implemented end-to-end workflow from URL mining to PR creation
- **UI Experience**: Added auto-generation, editing, and approval workflows
- **Security**: Implemented environment variable management and API key security

### Technical Details
- **Signal Mining**: Headlines, lists, prices extraction with HTML snapshots
- **RAG Pipeline**: OpenAI text-embedding-3-small + Pinecone/FAISS fallback + GPT-4o-mini
- **Vector Storage**: Automatic fallback from Pinecone to local FAISS
- **Decision Packs**: Structured JSON with hypothesis, risks, assets, and execution steps
- **Provenance Tracking**: Model names, embedding times, citation tracking
- **GitHub Integration**: PyGithub API with graceful fallback to preview mode

## [0.9.0] - 2024-01-10

### Added
- **Streamlit UI Scaffold**: Basic multi-page structure with navigation
- **Dashboard Layout**: Run metrics and history display
- **Run Detail View**: Evidence viewer and basic Decision Pack editor
- **Settings Page**: URL management and configuration

### Changed
- **UI Framework**: Migrated from CLI-only to web-based interface
- **User Experience**: Added interactive elements and visual feedback
- **Navigation**: Implemented page-based navigation structure

## [0.8.0] - 2024-01-05

### Added
- **RAG Module**: `rfg/generate_pack.py` for Decision Pack generation
- **Vector Store Helper**: `rfg/pinecone_helper.py` with FAISS fallback
- **Prompt Templates**: `rfg/prompts/decision_pack_template.txt`
- **Decision Pack Schema**: Structured JSON output with required fields

### Changed
- **Architecture**: Added RAG processing layer between mining and UI
- **Data Processing**: Implemented OpenAI embeddings and vector similarity search
- **Output Format**: Structured Decision Packs with metadata and citations

## [0.7.0] - 2024-01-01

### Added
- **GitHub PR Executor**: `executor/pr_executor.py` for automation
- **PR Template**: `PR_Grok_Play.txt` for consistent PR formatting
- **Branch Naming**: Automatic branch creation with timestamps
- **Preview Mode**: Local file generation when GitHub unavailable

### Changed
- **Execution Layer**: Added automated PR creation workflow
- **File Management**: Structured output for Decision Packs and landing pages
- **Error Handling**: Graceful fallback from live PR to preview mode

## [0.6.0] - 2023-12-28

### Added
- **Testing Framework**: pytest configuration with coverage reporting
- **Unit Tests**: Mocked OpenAI and GitHub API tests
- **CI/CD Pipeline**: GitHub Actions workflow for automated testing
- **Code Quality**: flake8 linting and bandit security scanning

### Changed
- **Development Process**: Added automated quality gates
- **Test Coverage**: Minimum 80% coverage requirement
- **Security**: Added vulnerability scanning to CI pipeline

## [0.5.0] - 2023-12-25

### Added
- **Signal Mining CLI**: `signal_miner.py` with configurable parameters
- **Data Extraction**: Headlines, paragraphs, lists, and price detection
- **HTML Snapshots**: Audit trail for compliance and debugging
- **Error Handling**: Robust error handling for network and parsing issues

### Changed
- **Core Functionality**: Implemented web scraping with BeautifulSoup
- **Output Format**: Structured JSON with per-site results
- **User-Agent**: Respectful crawling headers

## [0.4.0] - 2023-12-20

### Added
- **Project Structure**: Organized directory layout for scalability
- **Requirements Management**: Separate requirements files for core and UI
- **Configuration Files**: URL allowlist and environment variable setup
- **Documentation**: Initial README and setup instructions

### Changed
- **Repository Organization**: Structured for modular development
- **Dependency Management**: Clear separation of concerns

## [0.3.0] - 2023-12-15

### Added
- **Initial Scaffold**: Basic project structure and dependencies
- **Python Environment**: Python 3.13 compatibility setup
- **Package Management**: pip requirements and virtual environment setup
- **Version Control**: Git repository with initial commit

### Changed
- **Project Foundation**: Established development environment
- **Tooling**: Set up Python development tools

## [0.2.0] - 2023-12-10

### Added
- **Project Concept**: GrowthSignal MVP requirements and specifications
- **Architecture Planning**: System design and component breakdown
- **Technology Selection**: OpenAI, Pinecone, Streamlit, GitHub API choices
- **Compliance Framework**: Robots.txt, PII handling, data retention policies

### Changed
- **Planning Phase**: Moved from concept to implementation planning

## [0.1.0] - 2023-12-05

### Added
- **Product Requirements**: MVP feature specification and acceptance criteria
- **Market Research**: Competitive intelligence platform concept
- **User Stories**: Growth team workflow and pain points
- **Success Metrics**: Experiment velocity and success rate improvements

### Changed
- **Project Initiation**: Started GrowthSignal MVP development

---

## Version History Summary

| Version | Date | Major Features | Status |
|---------|------|----------------|---------|
| 1.0.0 | 2024-01-15 | Full MVP with RAG, UI, and automation | ✅ Complete |
| 0.9.0 | 2024-01-10 | Streamlit UI scaffold and navigation | ✅ Complete |
| 0.8.0 | 2024-01-05 | RAG module and Decision Pack generation | ✅ Complete |
| 0.7.0 | 2024-01-01 | GitHub PR executor and automation | ✅ Complete |
| 0.6.0 | 2023-12-28 | Testing framework and CI/CD pipeline | ✅ Complete |
| 0.5.0 | 2023-12-25 | Signal mining CLI and data extraction | ✅ Complete |
| 0.4.0 | 2023-12-20 | Project structure and organization | ✅ Complete |
| 0.3.0 | 2023-12-15 | Development environment setup | ✅ Complete |
| 0.2.0 | 2023-12-10 | Architecture planning and design | ✅ Complete |
| 0.1.0 | 2023-12-05 | Product requirements and concept | ✅ Complete |

## Key Milestones

### MVP Completion (v1.0.0)
- **End-to-End Workflow**: URL mining → RAG generation → UI review → PR creation
- **Production Ready**: Testing, security, and compliance frameworks
- **Documentation**: Complete architecture, workflow, and security guides
- **Marketing Assets**: Email templates, LinkedIn DMs, landing page

### Core Development (v0.5.0 - v0.8.0)
- **Signal Mining**: Web scraping with structured data extraction
- **RAG Pipeline**: OpenAI embeddings + vector search + LLM generation
- **Automation**: GitHub PR creation with fallback preview mode
- **Testing**: Comprehensive test suite with CI/CD pipeline

### Foundation (v0.1.0 - v0.4.0)
- **Project Setup**: Development environment and project structure
- **Architecture**: System design and technology selection
- **Planning**: Requirements, compliance, and success metrics

## Breaking Changes

### None in Current Version
- All changes maintain backward compatibility
- New features are additive, not replacing existing functionality
- Schema evolution follows versioning strategy

## Deprecation Notices

### None Currently
- All features are actively supported
- No deprecation timeline established yet
- Future changes will include migration guides

## Migration Guides

### Not Applicable
- Current version is initial MVP release
- No previous production deployments to migrate from
- Future versions will include migration instructions

## Contributors

- **Lead Engineer**: System architecture, RAG implementation, testing framework
- **Product Team**: Requirements, user stories, success metrics
- **Design Team**: UI/UX, marketing assets, compliance policies

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*For detailed information about each version, see the corresponding release notes and documentation.*

