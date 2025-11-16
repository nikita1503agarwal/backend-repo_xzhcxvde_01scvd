import os
from typing import List, Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Program, Faculty as FacultySchema, Event as EventSchema, Admission as AdmissionSchema, Pyq as PyqSchema

app = FastAPI(title="National Institute of Jalandhar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Utilities & Seed Data
# -----------------------------
class HealthResponse(BaseModel):
    message: str


def seed_demo_data():
    """Seed minimal demo data if collections are empty for first-time preview."""
    if db is None:
        return
    try:
        # Programs
        if db["program"].count_documents({}) == 0:
            create_document("program", Program(name="B.Tech Computer Science", department="CSE", level="UG", duration_years=4, description="Core CS curriculum with electives in AI/ML", semesters=8))
            create_document("program", Program(name="M.Tech Data Science", department="CSE", level="PG", duration_years=2, description="Advanced DS/ML program", semesters=4))
        # Faculty
        if db["faculty"].count_documents({}) == 0:
            create_document("faculty", FacultySchema(name="Dr. A. Sharma", designation="Professor", department="CSE", email="asharma@nijt.ac.in", research_areas=["AI", "Computer Vision"]))
            create_document("faculty", FacultySchema(name="Dr. R. Kaur", designation="Assistant Professor", department="ECE", email="rkaur@nijt.ac.in", research_areas=["VLSI", "Embedded Systems"]))
        # Events
        if db["event"].count_documents({}) == 0:
            from datetime import date, timedelta
            today = date.today()
            create_document("event", EventSchema(title="AI Symposium 2025", description="Talks & workshops on AI", category="seminar", start_date=today, end_date=today, location="Auditorium"))
            create_document("event", EventSchema(title="TechFest", description="Annual technical fest", category="cultural", start_date=today + timedelta(days=30), end_date=today + timedelta(days=32), location="Campus Grounds"))
        # Admissions
        if db["admission"].count_documents({}) == 0:
            create_document("admission", AdmissionSchema(year=2025, program="B.Tech", status="Open", notes="Apply via national counseling portal"))
        # PYQs
        if db["pyq"].count_documents({}) == 0:
            create_document("pyq", PyqSchema(program="BTECH CSE", department="CSE", course_code="CS101", course_title="Programming Fundamentals", semester=1, year=2023, exam_type="End", file_url="https://example.com/pyq/cs101_2023_end.pdf"))
    except Exception:
        # Non-fatal in case DB is not available or other issues
        pass


seed_demo_data()


# -----------------------------
# Basic routes
# -----------------------------
@app.get("/", response_model=HealthResponse)
def read_root():
    return {"message": "NIJT Backend is running"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# -----------------------------
# Content APIs
# -----------------------------
@app.get("/api/programs", response_model=List[Program])
def list_programs():
    docs = get_documents("program") if db else []
    return [Program(**{k: v for k, v in d.items() if k not in ["_id", "created_at", "updated_at"]}) for d in docs]


@app.get("/api/faculty", response_model=List[FacultySchema])
def list_faculty(department: Optional[str] = None):
    filter_q = {"department": department} if (department and db) else {}
    docs = get_documents("faculty", filter_q) if db else []
    return [FacultySchema(**{k: v for k, v in d.items() if k not in ["_id", "created_at", "updated_at"]}) for d in docs]


@app.get("/api/events", response_model=List[EventSchema])
def list_events(category: Optional[str] = None):
    filter_q = {"category": category} if (category and db) else {}
    docs = get_documents("event", filter_q) if db else []
    return [EventSchema(**{k: v for k, v in d.items() if k not in ["_id", "created_at", "updated_at"]}) for d in docs]


@app.get("/api/admissions", response_model=List[AdmissionSchema])
def list_admissions(status: Optional[str] = None):
    filter_q = {"status": status} if (status and db) else {}
    docs = get_documents("admission", filter_q) if db else []
    return [AdmissionSchema(**{k: v for k, v in d.items() if k not in ["_id", "created_at", "updated_at"]}) for d in docs]


@app.get("/api/pyqs", response_model=List[PyqSchema])
def list_pyqs(
    program: Optional[str] = None,
    department: Optional[str] = None,
    semester: Optional[int] = Query(None, ge=1, le=12),
    course_code: Optional[str] = None,
    year: Optional[int] = None,
    exam_type: Optional[str] = None,
    search: Optional[str] = Query(None, description="Search in course code or title")
):
    if db is None:
        return []

    filter_q = {}
    if program:
        filter_q["program"] = program
    if department:
        filter_q["department"] = department
    if semester is not None:
        filter_q["semester"] = semester
    if course_code:
        filter_q["course_code"] = course_code
    if year is not None:
        filter_q["year"] = year
    if exam_type:
        filter_q["exam_type"] = exam_type

    docs = get_documents("pyq", filter_q)

    # Apply simple search client-side if provided
    if search:
        s = search.lower()
        docs = [d for d in docs if s in (d.get("course_code", "").lower() + " " + d.get("course_title", "").lower())]

    return [PyqSchema(**{k: v for k, v in d.items() if k not in ["_id", "created_at", "updated_at"]}) for d in docs]


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
