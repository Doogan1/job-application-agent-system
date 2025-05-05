#!/usr/bin/env python3
"""
Job Application Agent System - Configuration

Example configuration file. Copy to config.py and edit with your details.
"""

# User Information
USER = {
    "name": "Your Name",
    "email": "your.email@example.com",
    "phone": "+1 (555) 123-4567",
    "location": "City, State, Country",
    "linkedin": "https://linkedin.com/in/yourprofile",
    "github": "https://github.com/yourusername"
}

# Resume Configuration
RESUME = {
    "template_path": "data/resumes/template.docx",
    "output_directory": "data/resumes/generated",
    "skills": [
        "Python", "JavaScript", "SQL", "Data Analysis",
        "Machine Learning", "Web Development", "API Design"
    ],
    "education": [
        {
            "institution": "University Name",
            "degree": "Bachelor of Science in Computer Science",
            "graduation_date": "May 2020",
            "gpa": "3.8/4.0"
        }
    ],
    "experience": [
        {
            "company": "Previous Company",
            "position": "Software Engineer",
            "start_date": "June 2020",
            "end_date": "Present",
            "description": [
                "Developed and maintained web applications using Python and Django",
                "Implemented data processing pipelines that increased efficiency by 30%",
                "Collaborated with cross-functional teams on various projects"
            ]
        }
    ]
}

# Job Search Configuration
JOB_SEARCH = {
    "keywords": ["software engineer", "python developer", "data scientist", "machine learning engineer"],
    "locations": ["Remote", "San Francisco, CA", "New York, NY"],
    "job_boards": {
        "linkedin": {
            "enabled": True,
            "api_key": "your_linkedin_api_key"
        },
        "indeed": {
            "enabled": True,
            "api_key": "your_indeed_api_key"
        },
        "glassdoor": {
            "enabled": False,
            "api_key": "your_glassdoor_api_key"
        }
    },
    "filters": {
        "min_salary": 80000,
        "max_experience_years": 5,
        "preferred_job_types": ["Full-time", "Contract"],
        "exclude_keywords": ["senior", "lead", "manager", "10+ years"]
    }
}

# Application Settings
APPLICATION = {
    "auto_submit": True,  # Set to False to review before submission
    "daily_limit": 10,    # Maximum applications to submit per day
    "follow_up": {
        "enabled": True,
        "delay_days": 7,  # Days to wait before following up
        "template_path": "data/templates/follow_up_email.txt"
    }
}

# API Settings
API = {
    "openai": {
        "api_key": "your_openai_api_key",
        "model": "gpt-4"
    }
}

# Storage Settings
STORAGE = {
    "database_path": "data/application_database.sqlite",
    "backup_directory": "data/backups"
}

# Logging Settings
LOGGING = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR, or CRITICAL
    "log_directory": "logs"
}
