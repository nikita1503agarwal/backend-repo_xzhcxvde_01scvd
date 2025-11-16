"""
Database Schemas for National Institute of Jalandhar Website

Each Pydantic model represents a collection in your MongoDB database.
The collection name is the lowercase of the class name.

Use these across the backend to validate incoming/outgoing data.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import date

# ----------------------------
# Core content models
# ----------------------------

class Program(BaseModel):
    """
    Academic programs offered by the institute
    Collection: "program"
    """
    name: str = Field(..., description="Program name, e.g., B.Tech Computer Science")
    department: str = Field(..., description="Department name")
    level: str = Field(..., description="UG/PG/PhD")
    duration_years: int = Field(..., ge=1, le=6)
    description: Optional[str] = Field(None)
    semesters: int = Field(..., ge=1, le=12)

class Faculty(BaseModel):
    """
    Faculty information
    Collection: "faculty"
    """
    name: str
    designation: str
    department: str
    email: Optional[str] = None
    phone: Optional[str] = None
    photo_url: Optional[HttpUrl] = None
    research_areas: List[str] = []

class Event(BaseModel):
    """
    Institute events, seminars, workshops
    Collection: "event"
    """
    title: str
    description: Optional[str] = None
    category: str = Field(..., description="seminar/workshop/cultural/sports/other")
    start_date: date
    end_date: Optional[date] = None
    location: str
    link: Optional[HttpUrl] = None

class Admission(BaseModel):
    """
    Admissions announcements and details
    Collection: "admission"
    """
    year: int
    program: str
    status: str = Field(..., description="Open/Closed/Upcoming")
    application_deadline: Optional[date] = None
    brochure_url: Optional[HttpUrl] = None
    apply_url: Optional[HttpUrl] = None
    notes: Optional[str] = None

class Pyq(BaseModel):
    """
    Previous Year Question papers metadata
    Collection: "pyq"
    """
    program: str = Field(..., description="Program short name, e.g., BTECH CSE")
    department: str
    course_code: str
    course_title: str
    semester: int = Field(..., ge=1, le=12)
    year: int
    exam_type: str = Field(..., description="Mid/End/Back/Supplementary")
    file_url: HttpUrl

# ----------------------------
# Example generic models (kept for reference)
# ----------------------------

class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
