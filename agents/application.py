#!/usr/bin/env python3
"""
Application Submitter Agent

This agent handles the actual submission of job applications.
"""

import logging
import time
import json
import os
import sqlite3
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from pathlib import Path

from agents.job_finder import JobListing

logger = logging.getLogger(__name__)

@dataclass
class ApplicationResult:
    """Data class for application submission results"""
    success: bool
    job_id: str
    submission_date: str
    confirmation_id: Optional[str] = None
    error: Optional[str] = None
    notes: Optional[str] = None

class ApplicationSubmitter:
    """Agent that submits job applications"""
    
    def __init__(self, config):
        """Initialize with configuration"""
        self.config = config
        self.user_info = config.USER
        self.auto_submit = config.APPLICATION.get("auto_submit", False)
        self.daily_limit = config.APPLICATION.get("daily_limit", 10)
        self.follow_up = config.APPLICATION.get("follow_up", {})
        self.db_path = config.STORAGE.get("database_path", "data/application_database.sqlite")
        
        # Initialize database
        self._init_database()
        
        logger.info(f"ApplicationSubmitter initialized (auto_submit={self.auto_submit}, daily_limit={self.daily_limit})")
    
    def submit(self, job: JobListing, resume: Dict[str, Any], cover_letter: Dict[str, Any]) -> ApplicationResult:
        """Submit a job application with resume and cover letter"""
        logger.info(f"Preparing to submit application for {job.title} at {job.company}")
        
        # Check daily application limit
        if not self._check_daily_limit():
            error_msg = f"Daily application limit of {self.daily_limit} reached"
            logger.warning(error_msg)
            return ApplicationResult(
                success=False,
                job_id=job.id,
                submission_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                error=error_msg
            )
        
        # Determine submission method
        submission_method = self._determine_submission_method(job)
        logger.info(f"Using submission method: {submission_method}")
        
        if self.auto_submit:
            # Perform actual submission
            result = self._perform_submission(job, resume, cover_letter, submission_method)
        else:
            # Just prepare the application without submitting
            logger.info("Auto-submit is disabled, preparing application without submitting")
            result = ApplicationResult(
                success=True,
                job_id=job.id,
                submission_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                notes="Application prepared but not submitted (auto-submit disabled)"
            )
        
        # Record the application in database
        self._record_application(job, resume, cover_letter, result)
        
        # Schedule follow-up if enabled and application was successful
        if self.follow_up.get("enabled", False) and result.success:
            self._schedule_follow_up(job, result)
        
        return result
    
    def _init_database(self) -> None:
        """Initialize SQLite database for storing application records"""
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        logger.info(f"Initializing application database at {self.db_path}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL,
            job_title TEXT NOT NULL,
            company TEXT NOT NULL,
            submission_date TEXT NOT NULL,
            success INTEGER NOT NULL,
            confirmation_id TEXT,
            error TEXT,
            notes TEXT,
            resume_path TEXT NOT NULL,
            cover_letter_path TEXT NOT NULL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS follow_ups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            scheduled_date TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            completed_date TEXT,
            notes TEXT,
            FOREIGN KEY (application_id) REFERENCES applications (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _check_daily_limit(self) -> bool:
        """Check if daily application limit has been reached"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM applications WHERE submission_date LIKE ? AND success = 1",
            (f"{today}%",)
        )
        count = cursor.fetchone()[0]
        
        conn.close()
        
        return count < self.daily_limit
    
    def _determine_submission_method(self, job: JobListing) -> str:
        """Determine the best method to submit the application"""
        # In a real implementation, this would analyze the job listing URL/platform
        # to determine the submission method (form, email, API, etc.)
        
        if job.application_url and "linkedin" in job.application_url.lower():
            return "linkedin_api"
        elif job.application_url and "indeed" in job.application_url.lower():
            return "indeed_api"
        elif job.application_url and "glassdoor" in job.application_url.lower():
            return "glassdoor_api"
        elif job.application_url and "email" in job.application_url.lower():
            return "email"
        else:
            return "website_form"
    
    def _perform_submission(self, job: JobListing, resume: Dict[str, Any], cover_letter: Dict[str, Any], method: str) -> ApplicationResult:
        """Perform the actual submission of the application"""
        # In a real implementation, this would use different methods based on the platform
        
        logger.info(f"Submitting application for {job.title} at {job.company} via {method}")
        
        try:
            # Simulate submission process
            time.sleep(2)
            
            if method == "linkedin_api":
                # Implement LinkedIn API submission
                return self._submit_linkedin(job, resume, cover_letter)
            elif method == "indeed_api":
                # Implement Indeed API submission
                return self._submit_indeed(job, resume, cover_letter)
            elif method == "glassdoor_api":
                # Implement Glassdoor API submission
                return self._submit_glassdoor(job, resume, cover_letter)
            elif method == "email":
                # Implement email submission
                return self._submit_email(job, resume, cover_letter)
            else:
                # Implement web form submission
                return self._submit_web_form(job, resume, cover_letter)
        
        except Exception as e:
            logger.error(f"Error submitting application: {e}")
            return ApplicationResult(
                success=False,
                job_id=job.id,
                submission_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                error=str(e)
            )
    
    def _submit_linkedin(self, job: JobListing, resume: Dict[str, Any], cover_letter: Dict[str, Any]) -> ApplicationResult:
        """Submit application via LinkedIn API"""
        # Implement LinkedIn submission logic
        confirmation_id = f"LI{int(time.time())}"
        return ApplicationResult(
            success=True,
            job_id=job.id,
            submission_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            confirmation_id=confirmation_id,
            notes="Submitted via LinkedIn API"
        )
    
    def _submit_indeed(self, job: JobListing, resume: Dict[str, Any], cover_letter: Dict[str, Any]) -> ApplicationResult:
        """Submit application via Indeed API"""
        # Implement Indeed submission logic
        confirmation_id = f"IN{int(time.time())}"
        return ApplicationResult(
            success=True,
            job_id=job.id,
            submission_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            confirmation_id=confirmation_id,
            notes="Submitted via Indeed API"
        )
    
    def _submit_glassdoor(self, job: JobListing, resume: Dict[str, Any], cover_letter: Dict[str, Any]) -> ApplicationResult:
        """Submit application via Glassdoor API"""
        # Implement Glassdoor submission logic
        confirmation_id = f"GD{int(time.time())}"
        return ApplicationResult(
            success=True,
            job_id=job.id,
            submission_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            confirmation_id=confirmation_id,
            notes="Submitted via Glassdoor API"
        )
    
    def _submit_email(self, job: JobListing, resume: Dict[str, Any], cover_letter: Dict[str, Any]) -> ApplicationResult:
        """Submit application via email"""
        # Implement email submission logic
        confirmation_id = f"EM{int(time.time())}"
        return ApplicationResult(
            success=True,
            job_id=job.id,
            submission_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            confirmation_id=confirmation_id,
            notes="Submitted via email"
        )
    
    def _submit_web_form(self, job: JobListing, resume: Dict[str, Any], cover_letter: Dict[str, Any]) -> ApplicationResult:
        """Submit application via web form"""
        # Implement web form submission logic (potentially using Selenium)
        confirmation_id = f"WF{int(time.time())}"
        return ApplicationResult(
            success=True,
            job_id=job.id,
            submission_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            confirmation_id=confirmation_id,
            notes="Submitted via web form"
        )
    
    def _record_application(self, job: JobListing, resume: Dict[str, Any], cover_letter: Dict[str, Any], result: ApplicationResult) -> None:
        """Record application details in the database"""
        logger.info(f"Recording application for {job.title} at {job.company} in database")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO applications (
            job_id, job_title, company, submission_date, success, 
            confirmation_id, error, notes, resume_path, cover_letter_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job.id, job.title, job.company, result.submission_date, 
            1 if result.success else 0, result.confirmation_id, result.error, 
            result.notes, resume.get("path", ""), cover_letter.get("path", "")
        ))
        
        conn.commit()
        conn.close()
    
    def _schedule_follow_up(self, job: JobListing, result: ApplicationResult) -> None:
        """Schedule a follow-up for a submitted application"""
        if not self.follow_up.get("enabled", False):
            return
        
        logger.info(f"Scheduling follow-up for {job.title} at {job.company}")
        
        # Calculate follow-up date
        delay_days = self.follow_up.get("delay_days", 7)
        today = datetime.now()
        follow_up_date = today.replace(day=today.day + delay_days).strftime("%Y-%m-%d")
        
        # Get application ID
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id FROM applications WHERE job_id = ? AND submission_date = ?",
            (job.id, result.submission_date)
        )
        app_id = cursor.fetchone()[0]
        
        # Schedule follow-up
        cursor.execute('''
        INSERT INTO follow_ups (application_id, scheduled_date, notes)
        VALUES (?, ?, ?)
        ''', (
            app_id, follow_up_date, f"Automated follow-up for {job.title} at {job.company}"
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Follow-up scheduled for {follow_up_date}")

if __name__ == "__main__":
    # For standalone testing
    import sys
    sys.path.append("..")
    import config
    
    logging.basicConfig(level=logging.INFO)
    
    # Create a test job listing
    test_job = JobListing(
        id="test123",
        title="Python Developer",
        company="Example Corp",
        location="Remote",
        description="Looking for a Python developer with data analysis skills...",
        url="https://example.com/jobs/123",
        date_posted="2025-04-30",
        application_url="https://linkedin.com/jobs/123/apply"
    )
    
    # Create a test resume and cover letter
    test_resume = {
        "path": "data/resumes/generated/Example_Corp_Python_Developer.docx",
        "skills_used": ["Python", "Data Analysis", "Machine Learning"]
    }
    
    test_cover_letter = {
        "path": "data/cover_letters/generated/cover_letter_Example_Corp_Python_Developer.docx"
    }
    
    submitter = ApplicationSubmitter(config)
    result = submitter.submit(test_job, test_resume, test_cover_letter)
    print(f"Submission result: {result}")
