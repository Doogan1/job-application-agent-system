#!/usr/bin/env python3
"""
Resume Tailor Agent

This agent customizes resumes for specific job listings to increase relevance.
"""

import logging
import os
from typing import Dict, Any, List
import time
from pathlib import Path

from agents.job_finder import JobListing

logger = logging.getLogger(__name__)

class ResumeTailor:
    """Agent that tailors resumes for specific job opportunities"""
    
    def __init__(self, config):
        """Initialize with configuration"""
        self.config = config
        self.template_path = config.RESUME["template_path"]
        self.output_directory = config.RESUME["output_directory"]
        self.skills = config.RESUME["skills"]
        self.education = config.RESUME["education"]
        self.experience = config.RESUME["experience"]
        self.user_info = config.USER
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_directory, exist_ok=True)
        
        logger.info("ResumeTailor initialized")
    
    def create_resume(self, job: JobListing) -> Dict[str, Any]:
        """Create a tailored resume for a specific job listing"""
        logger.info(f"Creating tailored resume for {job.title} at {job.company}")
        
        # Generate a safe filename
        safe_company = "".join(c if c.isalnum() else "_" for c in job.company)
        safe_title = "".join(c if c.isalnum() else "_" for c in job.title)
        filename = f"{safe_company}_{safe_title}.docx"
        output_path = Path(self.output_directory) / filename
        
        # Analyze job description to find key skills and requirements
        key_terms = self._analyze_job_description(job.description)
        logger.info(f"Identified {len(key_terms)} key terms in job description")
        
        # Reorder skills based on relevance to the job
        prioritized_skills = self._prioritize_skills(key_terms)
        
        # Generate the resume using a template
        resume_data = self._generate_resume(job, prioritized_skills, key_terms)
        
        # Create the actual resume file
        self._create_resume_file(resume_data, output_path)
        
        # Return information about the created resume
        return {
            "path": str(output_path),
            "skills_used": prioritized_skills[:5],  # Top 5 skills used
            "key_terms": key_terms[:5],  # Top 5 key terms identified
            "filename": filename
        }
    
    def _analyze_job_description(self, description: str) -> List[str]:
        """Analyze job description to extract key skills and terms"""
        # In a real implementation, this would use NLP or AI to extract key terms
        # For this example, we'll simulate the process
        
        logger.info("Analyzing job description for key terms")
        time.sleep(1)  # Simulate analysis
        
        # This could use the OpenAI API in a real implementation
        return ["python", "data analysis", "communication", "teamwork", "problem solving"]
    
    def _prioritize_skills(self, key_terms: List[str]) -> List[str]:
        """Prioritize user skills based on relevance to job keywords"""
        # Sort skills to put the most relevant ones first
        return sorted(self.skills, key=lambda s: self._relevance_score(s, key_terms), reverse=True)
    
    def _relevance_score(self, skill: str, key_terms: List[str]) -> float:
        """Calculate relevance score of a skill to the key terms"""
        # This is a simple implementation - a real one would be more sophisticated
        skill_lower = skill.lower()
        return sum(1.0 if term.lower() in skill_lower else 0.0 for term in key_terms)
    
    def _generate_resume(self, job: JobListing, prioritized_skills: List[str], key_terms: List[str]) -> Dict[str, Any]:
        """Generate resume content based on job details and prioritized skills"""
        # In a real implementation, this might use templates and document generation libraries
        # We'll just return a data structure for now
        
        # Customize experience descriptions based on job requirements
        tailored_experience = []
        for exp in self.experience:
            tailored_desc = []
            for desc in exp["description"]:
                # Emphasize descriptions that match key terms
                if any(term.lower() in desc.lower() for term in key_terms):
                    tailored_desc.append(desc)
                else:
                    tailored_desc.append(desc)
            
            tailored_experience.append({
                **exp,
                "description": tailored_desc
            })
        
        return {
            "user_info": self.user_info,
            "skills": prioritized_skills,
            "education": self.education,
            "experience": tailored_experience,
            "job_title": job.title,
            "company": job.company
        }
    
    def _create_resume_file(self, resume_data: Dict[str, Any], output_path: Path) -> None:
        """Create the actual resume file from the resume data"""
        # In a real implementation, this would use docx or similar library
        # to create a formatted document
        
        logger.info(f"Creating resume file at {output_path}")
        time.sleep(1)  # Simulate file creation
        
        # Create a placeholder file for now
        with open(output_path, "w") as f:
            f.write(f"Resume for {resume_data['job_title']} at {resume_data['company']}\n")
            f.write("\n--- This is a placeholder file ---\n")
            f.write("\nIn the real implementation, this would be a formatted .docx document\n")
        
        logger.info(f"Resume created successfully")

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
        date_posted="2025-04-30"
    )
    
    tailor = ResumeTailor(config)
    resume = tailor.create_resume(test_job)
    print(f"Created resume: {resume['path']}")
