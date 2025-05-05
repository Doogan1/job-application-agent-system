#!/usr/bin/env python3
"""
Database Utility

Provides centralized access to the system's database for storing and retrieving data.
"""

import logging
import sqlite3
import json
import os
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class Database:
    """Utility for database operations"""
    
    def __init__(self, config):
        """Initialize with configuration"""
        self.config = config
        self.db_path = config.STORAGE.get("database_path", "data/application_database.sqlite")
        self.backup_directory = config.STORAGE.get("backup_directory", "data/backups")
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(self.backup_directory, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        logger.info(f"Database initialized at {self.db_path}")
    
    def _init_database(self) -> None:
        """Initialize database schema if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create job_listings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_listings (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT NOT NULL,
            url TEXT NOT NULL,
            date_posted TEXT NOT NULL,
            date_discovered TEXT NOT NULL,
            salary_range TEXT,
            application_url TEXT,
            status TEXT DEFAULT 'discovered',
            source TEXT,
            data TEXT
        )
        ''')
        
        # Create applications table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL,
            submission_date TEXT NOT NULL,
            success INTEGER NOT NULL,
            confirmation_id TEXT,
            status TEXT DEFAULT 'submitted',
            resume_path TEXT,
            cover_letter_path TEXT,
            notes TEXT,
            FOREIGN KEY (job_id) REFERENCES job_listings (id)
        )
        ''')
        
        # Create follow_ups table
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
        
        # Create statistics table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            date TEXT PRIMARY KEY,
            jobs_discovered INTEGER DEFAULT 0,
            applications_submitted INTEGER DEFAULT 0,
            follow_ups_sent INTEGER DEFAULT 0,
            interviews_scheduled INTEGER DEFAULT 0,
            offers_received INTEGER DEFAULT 0
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_job_listing(self, job: Dict[str, Any]) -> bool:
        """
        Save a job listing to the database
        
        Args:
            job: Job listing data
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Saving job listing: {job.get('title')} at {job.get('company')}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert any complex data to JSON
            job_data = job.copy()
            if "requirements" in job_data or "benefits" in job_data or "company_details" in job_data:
                data_json = json.dumps({
                    "requirements": job_data.pop("requirements", None),
                    "benefits": job_data.pop("benefits", None),
                    "company_details": job_data.pop("company_details", None)
                })
            else:
                data_json = None
            
            # Check if the job already exists
            cursor.execute(
                "SELECT id FROM job_listings WHERE id = ?",
                (job.get("id"),)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing job
                cursor.execute('''
                UPDATE job_listings SET
                    title = ?,
                    company = ?,
                    location = ?,
                    description = ?,
                    url = ?,
                    date_posted = ?,
                    salary_range = ?,
                    application_url = ?,
                    data = ?
                WHERE id = ?
                ''', (
                    job.get("title", ""),
                    job.get("company", ""),
                    job.get("location", ""),
                    job.get("description", ""),
                    job.get("url", ""),
                    job.get("date_posted", ""),
                    job.get("salary_range", None),
                    job.get("application_url", None),
                    data_json,
                    job.get("id", "")
                ))
            else:
                # Insert new job
                cursor.execute('''
                INSERT INTO job_listings (
                    id, title, company, location, description, url, 
                    date_posted, date_discovered, salary_range, 
                    application_url, source, data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job.get("id", ""),
                    job.get("title", ""),
                    job.get("company", ""),
                    job.get("location", ""),
                    job.get("description", ""),
                    job.get("url", ""),
                    job.get("date_posted", ""),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    job.get("salary_range", None),
                    job.get("application_url", None),
                    job.get("source", None),
                    data_json
                ))
                
                # Update statistics
                self._update_statistic("jobs_discovered", 1)
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error saving job listing: {e}")
            return False
    
    def save_application(self, application: Dict[str, Any]) -> int:
        """
        Save an application record to the database
        
        Args:
            application: Application data
            
        Returns:
            ID of the inserted application record, or -1 if failed
        """
        logger.info(f"Saving application for job ID: {application.get('job_id')}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Insert application record
            cursor.execute('''
            INSERT INTO applications (
                job_id, submission_date, success, confirmation_id,
                status, resume_path, cover_letter_path, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                application.get("job_id", ""),
                application.get("submission_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                1 if application.get("success", False) else 0,
                application.get("confirmation_id", None),
                application.get("status", "submitted"),
                application.get("resume_path", None),
                application.get("cover_letter_path", None),
                application.get("notes", None)
            ))
            
            # Get the ID of the inserted record
            application_id = cursor.lastrowid
            
            # Update job listing status
            cursor.execute(
                "UPDATE job_listings SET status = ? WHERE id = ?",
                ("applied", application.get("job_id", ""))
            )
            
            # Update statistics if application was successful
            if application.get("success", False):
                self._update_statistic("applications_submitted", 1)
            
            conn.commit()
            conn.close()
            return application_id
            
        except Exception as e:
            logger.error(f"Error saving application: {e}")
            return -1
    
    def save_follow_up(self, follow_up: Dict[str, Any]) -> bool:
        """
        Save a follow-up record to the database
        
        Args:
            follow_up: Follow-up data
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Saving follow-up for application ID: {follow_up.get('application_id')}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert follow-up record
            cursor.execute('''
            INSERT INTO follow_ups (
                application_id, scheduled_date, completed, completed_date, notes
            ) VALUES (?, ?, ?, ?, ?)
            ''', (
                follow_up.get("application_id", 0),
                follow_up.get("scheduled_date", ""),
                1 if follow_up.get("completed", False) else 0,
                follow_up.get("completed_date", None),
                follow_up.get("notes", None)
            ))
            
            # Update statistics if follow-up was completed
            if follow_up.get("completed", False):
                self._update_statistic("follow_ups_sent", 1)
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error saving follow-up: {e}")
            return False
    
    def get_job_listings(self, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get job listings from the database
        
        Args:
            status: Filter by status (optional)
            limit: Maximum number of results
            
        Returns:
            List of job listings
        """
        logger.info(f"Getting job listings (status={status}, limit={limit})")
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if status:
                cursor.execute(
                    "SELECT * FROM job_listings WHERE status = ? ORDER BY date_discovered DESC LIMIT ?",
                    (status, limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM job_listings ORDER BY date_discovered DESC LIMIT ?",
                    (limit,)
                )
            
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            results = []
            for row in rows:
                job = dict(row)
                
                # Parse any JSON data
                if job.get("data"):
                    try:
                        extra_data = json.loads(job.pop("data"))
                        job.update(extra_data)
                    except json.JSONDecodeError:
                        pass
                
                results.append(job)
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting job listings: {e}")
            return []
    
    def get_applications(self, job_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get application records from the database
        
        Args:
            job_id: Filter by job ID (optional)
            limit: Maximum number of results
            
        Returns:
            List of application records
        """
        logger.info(f"Getting applications (job_id={job_id}, limit={limit})")
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if job_id:
                cursor.execute(
                    "SELECT * FROM applications WHERE job_id = ? ORDER BY submission_date DESC LIMIT ?",
                    (job_id, limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM applications ORDER BY submission_date DESC LIMIT ?",
                    (limit,)
                )
            
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            results = []
            for row in rows:
                results.append(dict(row))
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting applications: {e}")
            return []
    
    def get_pending_follow_ups(self, days: int = 1) -> List[Dict[str, Any]]:
        """
        Get pending follow-ups that are due within the specified number of days
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of follow-up records with application and job information
        """
        logger.info(f"Getting pending follow-ups for the next {days} days")
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Calculate date range
            today = datetime.now().strftime("%Y-%m-%d")
            future_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
            
            # Get pending follow-ups with application and job details
            cursor.execute('''
            SELECT f.*, a.job_id, a.submission_date, j.title, j.company
            FROM follow_ups f
            JOIN applications a ON f.application_id = a.id
            JOIN job_listings j ON a.job_id = j.id
            WHERE f.completed = 0
              AND f.scheduled_date BETWEEN ? AND ?
            ORDER BY f.scheduled_date ASC
            ''', (today, future_date))
            
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            results = []
            for row in rows:
                results.append(dict(row))
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting pending follow-ups: {e}")
            return []
    
    def get_statistics(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get daily statistics for the specified number of days
        
        Args:
            days: Number of days to retrieve
            
        Returns:
            List of daily statistics
        """
        logger.info(f"Getting statistics for the past {days} days")
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Calculate start date
            start_date = (datetime.now() - timedelta(days=days-1)).strftime("%Y-%m-%d")
            
            cursor.execute(
                "SELECT * FROM statistics WHERE date >= ? ORDER BY date ASC",
                (start_date,)
            )
            
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            results = []
            for row in rows:
                results.append(dict(row))
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return []
    
    def _update_statistic(self, field: str, increment: int = 1) -> None:
        """
        Update a statistic for the current date
        
        Args:
            field: Field to update
            increment: Value to increment by
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Try to insert a new record for today
            try:
                cursor.execute(
                    f"INSERT INTO statistics (date, {field}) VALUES (?, ?)",
                    (today, increment)
                )
            except sqlite3.IntegrityError:
                # Record for today already exists, update it
                cursor.execute(
                    f"UPDATE statistics SET {field} = {field} + ? WHERE date = ?",
                    (increment, today)
                )
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating statistic: {e}")
    
    def backup_database(self) -> str:
        """
        Create a backup of the database
        
        Returns:
            Path to the backup file, or empty string if failed
        """
        logger.info("Creating database backup")
        
        try:
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}.sqlite"
            backup_path = os.path.join(self.backup_directory, backup_filename)
            
            # Create a connection to the source database
            source_conn = sqlite3.connect(self.db_path)
            
            # Create a connection to the backup database
            backup_conn = sqlite3.connect(backup_path)
            
            # Copy data
            source_conn.backup(backup_conn)
            
            # Close connections
            source_conn.close()
            backup_conn.close()
            
            logger.info(f"Database backup created at {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creating database backup: {e}")
            return ""


if __name__ == "__main__":
    # For standalone testing
    import sys
    sys.path.append("..")
    import config
    
    logging.basicConfig(level=logging.INFO)
    
    db = Database(config)
    
    # Test saving a job listing
    job = {
        "id": "test_job_1",
        "title": "Python Developer",
        "company": "Example Corp",
        "location": "Remote",
        "description": "This is a test job description.",
        "url": "https://example.com/jobs/1",
        "date_posted": "2025-05-01",
        "source": "test"
    }
    
    db.save_job_listing(job)
    
    # Test getting job listings
    jobs = db.get_job_listings()
    print(f"Got {len(jobs)} job listings")
    for job in jobs:
        print(f"  - {job['title']} at {job['company']}")
