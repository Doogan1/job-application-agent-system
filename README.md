# Job Application Agent System

An automated system of AI agents that apply for jobs on your behalf, streamlining the job application process.

## Overview

This project creates a system of AI agents that handle various aspects of job applications, from finding opportunities to submitting applications and following up. The agents work together to automate repetitive tasks in the job application process, allowing you to focus on interview preparation and career development.

## Features

- Automated job opportunity discovery across multiple job boards (LinkedIn, Indeed, Glassdoor)
- Intelligent resume tailoring based on job description analysis
- AI-powered cover letter generation with company research
- Automated application submission via APIs and web forms
- Scheduled follow-up management
- Application tracking and analytics dashboard
- Interview preparation assistance

## Architecture Overview

The system follows a modular architecture with independent agents that communicate through well-defined interfaces:

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│  JobFinder  │────▶│ ResumeTailor │────▶│ LetterWriter │────▶│ ApplicationSubmit│
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────────┘
        │                   │                   │                      │
        │                   │                   │                      │
        ▼                   ▼                   ▼                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              Utility Services                                 │
│                                                                              │
│   ┌──────────┐        ┌───────────┐        ┌─────────────┐       ┌────────┐  │
│   │ Database │        │ API Client│        │ Doc Process │       │  ...   │  │
│   └──────────┘        └───────────┘        └─────────────┘       └────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

Key interfaces between components:
- **JobFinder → ResumeTailor**: JobFinder produces JobListing objects that ResumeTailor consumes
- **ResumeTailor → LetterWriter**: Resume objects are passed to generate targeted cover letters
- **LetterWriter → ApplicationSubmitter**: Completed application packages are passed for submission

All components interact with shared utility services for database operations, API access, and document processing.

For detailed architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Getting Started

### Prerequisites

- Python 3.8+
- Required Python packages (listed in requirements.txt)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/job-application-agent-system.git

# Navigate to the project directory
cd job-application-agent-system

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Copy the example configuration file:
   ```bash
   cp config.example.py config.py
   ```

2. Edit `config.py` with your personal information, job preferences, and API credentials.

### Usage

```bash
# Run the main application
python main.py

# For specific modules
python -m agents.job_finder
python -m agents.resume_tailor
python -m agents.letter_writer
python -m agents.application
```

## Project Structure

```
job-application-agent-system/
├── agents/                      # Individual agent modules
│   ├── __init__.py              # Package initialization
│   ├── job_finder.py            # Discovers job opportunities
│   ├── resume_tailor.py         # Customizes resume for specific jobs
│   ├── letter_writer.py         # Generates cover letters
│   └── application.py           # Handles submission process
├── data/                        # Data storage
│   ├── resumes/                 # Resume templates and generated resumes
│   ├── cover_letters/           # Cover letter templates and generated letters
│   └── job_listings/            # Stored job listings
├── utils/                       # Utility functions
│   ├── __init__.py              # Package initialization
│   ├── api_client.py            # API integration utilities
│   ├── database.py              # Database operations
│   └── document_processor.py    # Document handling utilities
├── .gitignore                   # Git ignore rules
├── config.example.py            # Example configuration template
├── LICENSE                      # License information
├── main.py                      # Main application entry point
├── README.md                    # Project documentation
├── ARCHITECTURE.md              # Detailed architecture documentation
└── requirements.txt             # Python dependencies
```

## Module Descriptions

### Agent Modules

- **job_finder.py**: Searches multiple job boards (LinkedIn, Indeed, Glassdoor) for job opportunities matching your criteria. Filters results based on preferences and saves them to a database.

- **resume_tailor.py**: Analyzes job descriptions to identify key requirements and customizes your resume to emphasize relevant skills and experiences for each application.

- **letter_writer.py**: Researches company information and generates personalized cover letters tailored to each job opportunity.

- **application.py**: Handles the actual submission of applications through various channels (APIs, email, web forms) and manages application tracking.

### Utility Modules

- **api_client.py**: Provides unified access to various APIs (job boards, AI text generation, etc.).

- **database.py**: Handles all database operations for storing and retrieving job listings, applications, and statistics.

- **document_processor.py**: Utilities for creating, parsing, and manipulating document files (DOCX, PDF).

## Data Storage

The system uses SQLite for data storage with automatic backups:

- Job listings database
- Application tracking
- Follow-up scheduling
- Performance statistics

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the LICENSE file included in this repository.

## Acknowledgments

- OpenAI API for text generation capabilities
- Python libraries: requests, python-docx, selenium, beautifulsoup4, nltk
- Job board platforms: LinkedIn, Indeed, Glassdoor

## Future Plans

- Add additional job board integrations
- Implement interview scheduling capabilities
- Add feedback analysis for application success rates
- Create web-based dashboard for monitoring applications
- Implement AI-powered interview preparation system

For a detailed development roadmap, see our [project Notion page](https://notion.io/your-project-roadmap-link).
