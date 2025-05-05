#!/usr/bin/env python3
"""
Job Application Agent System - Main Module

This is the entry point for the Job Application Agent System.
It coordinates and manages all agent activities.
"""

import os
import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import agents
from agents.job_finder import JobFinder
from agents.resume_tailor import ResumeTailor
from agents.letter_writer import LetterWriter
from agents.application import ApplicationSubmitter

# Import config
try:
    import config
    logger.info("Configuration loaded successfully")
except ImportError:
    logger.error("Configuration file not found. Please create a config.py file")
    print("Error: Configuration file not found. Please copy config.example.py to config.py and edit it")
    sys.exit(1)

def main():
    """Main function to run the job application agent system"""
    logger.info("Starting Job Application Agent System")
    
    # Initialize agents
    job_finder = JobFinder(config)
    resume_tailor = ResumeTailor(config)
    letter_writer = LetterWriter(config)
    application_submitter = ApplicationSubmitter(config)
    
    # Start job finding process
    jobs = job_finder.find_jobs()
    
    # Process each job
    for job in jobs:
        logger.info(f"Processing job: {job.title} at {job.company}")
        
        # Tailor resume
        resume = resume_tailor.create_resume(job)
        
        # Generate cover letter
        cover_letter = letter_writer.create_letter(job, resume)
        
        # Submit application
        result = application_submitter.submit(job, resume, cover_letter)
        
        if result.success:
            logger.info(f"Successfully applied to {job.title} at {job.company}")
        else:
            logger.error(f"Failed to apply to {job.title} at {job.company}: {result.error}")
    
    logger.info("Job Application Agent System completed")

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    try:
        main()
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)
