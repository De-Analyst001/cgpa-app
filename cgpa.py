import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
import hashlib
import uuid
import gc

# Try to import ReportLab for PDF generation
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.graphics.shapes import Drawing, Rect, Line
    from reportlab.graphics import renderPDF
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="FPT Academic Calculator Pro",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS - Emerald Green Professional Theme (FIXED FONT URL)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    /* Main emerald gradient - sophisticated green theme */
    .main-header {
        background: linear-gradient(135deg, #059669 0%, #047857 50%, #065f46 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2.5rem;
        box-shadow: 0 20px 50px rgba(5, 150, 105, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        border-radius: 50%;
    }
    
    .main-header h1 {
        font-weight: 800;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Glassmorphism cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 1.75rem;
        border-radius: 16px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
        border-left: 5px solid #10b981;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(16, 185, 129, 0.1);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(5, 150, 105, 0.15);
        border-left-color: #059669;
    }
    
    /* Enhanced grade badges with better contrast */
    .grade-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.35rem 1rem;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.875rem;
        letter-spacing: 0.025em;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 2px solid transparent;
    }
    
    .grade-a { 
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); 
        color: #065f46; 
        border-color: #34d399;
    }
    .grade-b { 
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); 
        color: #1e40af; 
        border-color: #60a5fa;
    }
    .grade-c { 
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); 
        color: #92400e; 
        border-color: #fbbf24;
    }
    .grade-d { 
        background: linear-gradient(135deg, #ffedd5 0%, #fed7aa 100%); 
        color: #9a3412; 
        border-color: #fb923c;
    }
    .grade-e { 
        background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); 
        color: #374151;  /* FIXED: Darker for better contrast */
        border-color: #6b7280;
    }
    .grade-f { 
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); 
        color: #991b1b; 
        border-color: #f87171;
    }
    
    /* Modern tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        padding: 0.75rem;
        border-radius: 16px;
        border: 1px solid #a7f3d0;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 0.875rem 1.75rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        border: 2px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255,255,255,0.8);
        transform: translateY(-1px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.4);
        border-color: #065f46;
    }
    
    /* Transcript header with deep emerald */
    .transcript-header {
        background: linear-gradient(135deg, #064e3b 0%, #059669 50%, #10b981 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(5, 150, 105, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .transcript-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    
    /* Student info card with subtle green tint */
    .student-info-card {
        background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
        border: 2px solid #bbf7d0;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }
    
    /* Enhanced buttons */
    .stButton>button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 16px rgba(5, 150, 105, 0.3) !important;
    }
    
    /* Primary button green theme */
    button[kind="primary"] {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        border: none !important;
    }
    
    /* Storage status indicator */
    .storage-status {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .storage-active {
        background: #d1fae5;
        color: #065f46;
    }
    .storage-inactive {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* Semester transcript card */
    .semester-transcript-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .semester-transcript-card:hover {
        border-color: #10b981;
        box-shadow: 0 8px 24px rgba(5, 150, 105, 0.15);
    }
    
    /* CGPA Display */
    .cgpa-display {
        font-size: 5rem;
        font-weight: 800;
        color: #059669;
        line-height: 1;
        margin: 1rem 0;
        text-shadow: 0 4px 12px rgba(5, 150, 105, 0.2);
    }
    
    /* Classification badges */
    .classification-badge {
        display: inline-block;
        padding: 0.75rem 1.5rem;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .first-class { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); color: white; }
    .second-upper { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; }
    .second-lower { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; }
    .third-class { background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%); color: white; }
    .fail { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; }
</style>
""", unsafe_allow_html=True)

# Data Management Configuration
DATA_FILE = "academic_records.csv"
STUDENT_INDEX_FILE = "student_index.csv"
BACKUP_DIR = "backups"

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

# Grading System Configuration - Grade Points Only (Updated with E = 1.0)
GRADING_SYSTEM = {
    'A': {'points': 5.0, 'remark': 'Excellent'},
    'B': {'points': 4.0, 'remark': 'Very Good'},
    'C': {'points': 3.0, 'remark': 'Good'},
    'D': {'points': 2.0, 'remark': 'Pass'},
    'E': {'points': 1.0, 'remark': 'Poor'},
    'F': {'points': 0.0, 'remark': 'Fail'}
}

DEGREE_CLASSIFICATION = {
    'First Class Honours': (4.50, 5.00),
    'Second Class Honours (Upper Division)': (3.50, 4.49),
    'Second Class Honours (Lower Division)': (2.40, 3.49),
    'Third Class Honours': (1.50, 2.39),
    'Fail': (0.00, 1.49)
}

DEPARTMENTS = [
    "Computer Science", 
    "Information Technology",
    "Engineering", 
    "Business", 
    "Science", 
    "Arts", 
    "Medicine", 
    "Law", 
    "Other"
]

# Initialize session state with persistent storage support
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'semesters' not in st.session_state:
    st.session_state.semesters = {}
if 'current_semester' not in st.session_state:
    st.session_state.current_semester = ""
if 'student_info' not in st.session_state:
    st.session_state.student_info = {
        'name': '',
        'matric_number': '',
        'department': 'Information Technology',
        'program': '',
        'student_id': ''
    }
if 'transcript_info' not in st.session_state:
    st.session_state.transcript_info = {
        'name': '',
        'matric_number': '',
        'department': 'Information Technology',
        'program': '',
        'session': '',
        'date_of_birth': ''
    }
if 'last_saved' not in st.session_state:
    st.session_state.last_saved = None
if 'storage_status' not in st.session_state:
    st.session_state.storage_status = "inactive"
if 'pdf_buffers' not in st.session_state:
    st.session_state.pdf_buffers = {}  # NEW: Store PDF buffers for download buttons

def generate_student_id(name, matric):
    """Generate unique student ID from name and matric number"""
    if name and matric:
        unique_string = f"{name.strip().lower()}_{matric.strip().upper()}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    return str(uuid.uuid4())[:12]

def get_student_file_path(student_id):
    """Get the CSV file path for a specific student"""
    return os.path.join(BACKUP_DIR, f"student_{student_id}.csv")

def validate_matric_number(matric):
    """Validate matric number format"""
    if not matric:
        return False, "Matric number is required"
    if len(matric) < 5:
        return False, "Matric number too short (min 5 characters)"
    if not any(c.isalnum() for c in matric):
        return False, "Matric number must contain alphanumeric characters"
    return True, "Valid"

def check_duplicate_course(semester_name, course_code):
    """Check if course already exists in semester"""
    if semester_name in st.session_state.semesters:
        existing_codes = [c['code'].upper() for c in st.session_state.semesters[semester_name]]
        return course_code.upper() in existing_codes
    return False

def save_to_csv():
    """Save all student data to CSV with automatic backup system."""
    if not st.session_state.student_info['name'] or not st.session_state.student_info['matric_number']:
        return False, "Please enter your name and matric number first"
    
    # Validate matric number
    is_valid, msg = validate_matric_number(st.session_state.student_info['matric_number'])
    if not is_valid:
        return False, msg
    
    try:
        if not st.session_state.student_info.get('student_id'):
            st.session_state.student_info['student_id'] = generate_student_id(
                st.session_state.student_info['name'],
                st.session_state.student_info['matric_number']
            )
        
        student_id = st.session_state.student_info['student_id']
        file_path = get_student_file_path(student_id)
        
        records = []
        timestamp = datetime.now().isoformat()
        
        for semester_name, courses in st.session_state.semesters.items():
            for course in courses:
                records.append({
                    'student_id': student_id,
                    'student_name': st.session_state.student_info['name'],
                    'matric_number': st.session_state.student_info['matric_number'],
                    'department': st.session_state.student_info['department'],
                    'program': st.session_state.student_info['program'],
                    'semester': semester_name,
                    'course_code': course['code'],
                    'course_title': course['title'],
                    'credits': course['credits'],
                    'grade': course['grade'],
                    'grade_points': course['grade_points'],
                    'remark': get_grade_remark(course['grade']),
                    'timestamp': timestamp,
                    'last_modified': timestamp
                })
        
        if records:
            df = pd.DataFrame(records)
            df.to_csv(file_path, index=False)
            update_student_index()
            
            # Create timestamped backup
            backup_filename = f"student_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            backup_path = os.path.join(BACKUP_DIR, backup_filename)
            df.to_csv(backup_path, index=False)
            
            cleanup_old_backups(student_id)
            
            st.session_state.last_saved = datetime.now()
            st.session_state.storage_status = "active"
            
            # Memory cleanup
            del df
            gc.collect()
            
            return True, f"Data saved successfully! ({len(records)} records)"
        
        return False, "No data to save"
        
    except Exception as e:
        return False, f"Error saving data: {str(e)}"

def update_student_index():
    """Update the master index of all students"""
    try:
        index_data = []
        
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith("student_") and not filename.count("_") > 1:
                file_path = os.path.join(BACKUP_DIR, filename)
                try:
                    df = pd.read_csv(file_path)
                    if not df.empty:
                        latest_record = df.iloc[-1]
                        index_data.append({
                            'student_id': latest_record['student_id'],
                            'name': latest_record['student_name'],
                            'matric_number': latest_record['matric_number'],
                            'department': latest_record['department'],
                            'program': latest_record['program'],
                            'last_modified': latest_record['timestamp'],
                            'total_semesters': df['semester'].nunique(),
                            'total_courses': len(df)
                        })
                except:
                    continue
        
        if index_data:
            index_df = pd.DataFrame(index_data)
            index_df.to_csv(STUDENT_INDEX_FILE, index=False)
            
    except Exception as e:
        print(f"Error updating index: {e}")

def cleanup_old_backups(student_id):
    """Keep only the last 5 backups for each student"""
    try:
        backups = []
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith(f"student_{student_id}_") and filename.count("_") > 1:
                file_path = os.path.join(BACKUP_DIR, filename)
                backups.append((file_path, os.path.getmtime(file_path)))
        
        backups.sort(key=lambda x: x[1], reverse=True)
        
        for file_path, _ in backups[5:]:
            try:
                os.remove(file_path)
            except:
                pass
    except:
        pass

def load_from_csv():
    """Load student data from CSV based on name and matric number."""
    name = st.session_state.student_info['name']
    matric = st.session_state.student_info['matric_number']
    
    if not name or not matric:
        return False, "Please enter your name and matric number to load data"
    
    try:
        student_id = generate_student_id(name, matric)
        file_path = get_student_file_path(student_id)
        
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            
            if not df.empty:
                latest = df.iloc[0]
                st.session_state.student_info['student_id'] = latest['student_id']
                st.session_state.student_info['department'] = latest['department']
                st.session_state.student_info['program'] = latest['program']
                
                st.session_state.transcript_info['name'] = latest['student_name']
                st.session_state.transcript_info['matric_number'] = latest['matric_number']
                st.session_state.transcript_info['department'] = latest['department']
                st.session_state.transcript_info['program'] = latest['program']
                
                semesters = {}
                for _, row in df.iterrows():
                    sem = row['semester']
                    if sem not in semesters:
                        semesters[sem] = []
                    semesters[sem].append({
                        'code': row['course_code'],
                        'title': row['course_title'],
                        'credits': row['credits'],
                        'grade': row['grade'],
                        'grade_points': row['grade_points']
                    })
                
                st.session_state.semesters = semesters
                st.session_state.storage_status = "active"
                
                # Cleanup
                del df
                gc.collect()
                
                cgpa, _, _ = calculate_cgpa(semesters)
                return True, f"Data loaded successfully! CGPA: {cgpa:.2f}"
        
        return find_and_migrate_data(name, matric)
        
    except Exception as e:
        return False, f"Error loading data: {str(e)}"

def find_and_migrate_data(name, matric):
    """Try to find data in old format or other student files"""
    try:
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            student_data = df[
                (df['matric_number'].str.upper() == matric.upper()) & 
                (df['student_name'].str.lower() == name.lower())
            ]
            
            if not student_data.empty:
                semesters = {}
                for _, row in student_data.iterrows():
                    sem = row['semester']
                    if sem not in semesters:
                        semesters[sem] = []
                    semesters[sem].append({
                        'code': row['course_code'],
                        'title': row['course_title'],
                        'credits': row['credits'],
                        'grade': row['grade'],
                        'grade_points': row['grade_points']
                    })
                
                st.session_state.semesters = semesters
                st.session_state.student_info['department'] = student_data.iloc[0]['department']
                st.session_state.student_info['program'] = student_data.iloc[0]['program']
                
                save_to_csv()
                st.session_state.storage_status = "active"
                
                cgpa, _, _ = calculate_cgpa(semesters)
                return True, f"Data migrated and loaded! CGPA: {cgpa:.2f}"
        
        return False, "No existing data found for this student"
        
    except Exception as e:
        return False, f"Error migrating data: {str(e)}"

def auto_save():
    """Automatically save data if student info is complete"""
    if (st.session_state.student_info['name'] and 
        st.session_state.student_info['matric_number'] and 
        st.session_state.semesters):
        success, _ = save_to_csv()
        return success
    return False

def get_all_students():
    """Get list of all students from index"""
    try:
        if os.path.exists(STUDENT_INDEX_FILE):
            df = pd.read_csv(STUDENT_INDEX_FILE)
            return df.to_dict('records')
    except:
        pass
    return []

def delete_student_data(student_id):
    """Permanently delete a student's data"""
    try:
        file_path = get_student_file_path(student_id)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        if os.path.exists(STUDENT_INDEX_FILE):
            df = pd.read_csv(STUDENT_INDEX_FILE)
            df = df[df['student_id'] != student_id]
            df.to_csv(STUDENT_INDEX_FILE, index=False)
        
        return True
    except Exception as e:
        return False

def get_grade_points(grade):
    """Get grade points from letter grade"""
    return GRADING_SYSTEM.get(grade.upper(), {}).get('points', 0.0)

def get_grade_remark(grade):
    """Get remark from letter grade"""
    return GRADING_SYSTEM.get(grade.upper(), {}).get('remark', 'Unknown')

def get_grade_class(grade):
    """Get CSS class for grade badge"""
    return f"grade-{grade.lower()}"

def get_classification(cgpa):
    """Get degree classification based on CGPA"""
    for classification, (min_val, max_val) in DEGREE_CLASSIFICATION.items():
        if min_val <= cgpa <= max_val:
            return classification
    return 'Fail'

def get_classification_class(classification):
    """Get CSS class for classification badge"""
    class_map = {
        'First Class Honours': 'first-class',
        'Second Class Honours (Upper Division)': 'second-upper',
        'Second Class Honours (Lower Division)': 'second-lower',
        'Third Class Honours': 'third-class',
        'Fail': 'fail'
    }
    return class_map.get(classification, 'fail')

def calculate_semester_gpa(courses):
    """Calculate GPA for a semester"""
    if not courses:
        return 0.0, 0
    
    total_weighted_points = 0
    total_credits = 0
    
    for course in courses:
        credits = course['credits']
        grade_points = course['grade_points']
        total_weighted_points += grade_points * credits
        total_credits += credits
    
    gpa = total_weighted_points / total_credits if total_credits > 0 else 0.0
    return round(gpa, 2), total_credits

def calculate_cgpa(semesters_dict):
    """Calculate CGPA as average of all semester GPAs"""
    if not semesters_dict:
        return 0.0, 0, 0
    
    semester_gpas = []
    total_credits = 0
    
    for semester_name, courses in semesters_dict.items():
        gpa, credits = calculate_semester_gpa(courses)
        if credits > 0:
            semester_gpas.append(gpa)
            total_credits += credits
    
    if not semester_gpas:
        return 0.0, 0, 0
    
    cgpa = sum(semester_gpas) / len(semester_gpas)
    return round(cgpa, 2), total_credits, len(semester_gpas)

def get_cgpa_evolution(semesters_dict):
    """Show how CGPA evolves as each semester is added"""
    if not semesters_dict:
        return []
    
    evolution = []
    semester_gpas = []
    
    sorted_semesters = sorted(semesters_dict.items())
    
    for semester_name, courses in sorted_semesters:
        gpa, _ = calculate_semester_gpa(courses)
        semester_gpas.append(gpa)
        cgpa_so_far = round(sum(semester_gpas) / len(semester_gpas), 2)
        evolution.append({
            'semester': semester_name,
            'semester_gpa': gpa,
            'cgpa': cgpa_so_far,
            'semesters_count': len(semester_gpas)
        })
    
    return evolution

def generate_pdf_transcript(transcript_type="full", specific_semester=None):
    """
    Generate professional PDF transcript with memory optimization
    transcript_type: "full" for all semesters, "semester" for specific semester
    """
    if not REPORTLAB_AVAILABLE:
        return None
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        topMargin=1*cm, 
        bottomMargin=1*cm,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#065f46'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.white,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    section_header = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#065f46'),
        spaceBefore=20,
        spaceAfter=10,
        fontName='Helvetica-Bold',
        borderColor=colors.HexColor('#10b981'),
        borderWidth=2,
        borderPadding=5
    )
    
    normal_style = styles["Normal"]
    normal_style.fontSize = 10
    normal_style.leading = 14
    
    # University Header
    uni_header = """
    <para alignment="center">
        <font size="28" color="#065f46"><b>FPT UNIVERSITY</b></font><br/>
        <font size="12" color="#6b7280">Federal University of Technology</font><br/>
        <font size="10" color="#9ca3af">Office of the Registrar | Academic Affairs Division</font>
    </para>
    """
    elements.append(Paragraph(uni_header, normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Decorative line
    elements.append(Table([['']], colWidths=[6.5*inch], style=TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 3, colors.HexColor('#059669')),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#10b981')),
    ])))
    elements.append(Spacer(1, 0.2*inch))
    
    # Document Title
    if transcript_type == "full":
        doc_title = "OFFICIAL ACADEMIC TRANSCRIPT"
    else:
        doc_title = f"SEMESTER TRANSCRIPT - {specific_semester.upper()}"
    
    elements.append(Paragraph(f"<b>{doc_title}</b>", title_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(f"Issued on: {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Student Information Box
    info_data = [
        ['STUDENT INFORMATION', ''],
        ['Full Name:', st.session_state.transcript_info.get('name', 'N/A') or st.session_state.student_info.get('name', 'N/A')],
        ['Matriculation Number:', st.session_state.transcript_info.get('matric_number', 'N/A') or st.session_state.student_info.get('matric_number', 'N/A')],
        ['Department:', st.session_state.transcript_info.get('department', 'N/A') or st.session_state.student_info.get('department', 'N/A')],
        ['Program of Study:', st.session_state.transcript_info.get('program', 'N/A') or st.session_state.student_info.get('program', 'N/A')],
    ]
    
    if st.session_state.transcript_info.get('session'):
        info_data.append(['Academic Session:', st.session_state.transcript_info['session']])
    if st.session_state.transcript_info.get('date_of_birth'):
        info_data.append(['Date of Birth:', st.session_state.transcript_info['date_of_birth']])
    
    info_table = Table(info_data, colWidths=[2.2*inch, 4.3*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#065f46')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fdf4')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#a7f3d0')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('PADDING', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Academic Records
    evolution = get_cgpa_evolution(st.session_state.semesters)
    cgpa, total_credits, num_semesters = calculate_cgpa(st.session_state.semesters)
    
    # Determine which semesters to include
    if transcript_type == "semester" and specific_semester:
        semesters_to_process = [(specific_semester, st.session_state.semesters.get(specific_semester, []))]
        specific_ev = next((e for e in evolution if e['semester'] == specific_semester), None)
    else:
        semesters_to_process = sorted(st.session_state.semesters.items())
    
    for idx, (semester_name, courses) in enumerate(semesters_to_process):
        if not courses:
            continue
            
        # Add page break for new semester (except first)
        if idx > 0:
            elements.append(PageBreak())
        
        # Semester header with professional styling
        sem_gpa, _ = calculate_semester_gpa(courses)
        
        sem_header_data = [[
            Paragraph(f"<b>{semester_name}</b>", header_style),
            Paragraph(f"<b>GPA: {sem_gpa:.2f}</b>", header_style)
        ]]
        sem_table = Table(sem_header_data, colWidths=[5*inch, 1.5*inch])
        sem_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#059669')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(sem_table)
        elements.append(Spacer(1, 0.1*inch))
        
        # Course table with professional styling
        course_data = [['Course Code', 'Course Title', 'Credits', 'Grade', 'Points', 'Weighted']]
        
        for course in courses:
            weighted = course['grade_points'] * course['credits']
            course_data.append([
                course['code'],
                Paragraph(course['title'], normal_style),
                str(course['credits']),
                course['grade'],
                f"{course['grade_points']:.1f}",
                f"{weighted:.1f}"
            ])
        
        # Add semester summary
        total_weighted = sum(c['grade_points'] * c['credits'] for c in courses)
        total_credits_sem = sum(c['credits'] for c in courses)
        course_data.append(['', '', '', '', 'SEMESTER GPA:', f"{sem_gpa:.2f}"])
        
        course_table = Table(course_data, colWidths=[1.1*inch, 2.9*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.8*inch])
        course_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d1fae5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#065f46')),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            # Body styling
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#e5e7eb')),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('PADDING', (0, 1), (-1, -2), 8),
            ('VALIGN', (0, 1), (-1, -2), 'MIDDLE'),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f9fafb')]),
            
            # Summary row styling
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecfdf5')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#065f46')),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            ('ALIGN', (-2, -1), (-1, -1), 'RIGHT'),
            ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.HexColor('#059669')),
        ]))
        elements.append(course_table)
        
        # CGPA info for this semester
        if transcript_type == "full":
            ev = next((e for e in evolution if e['semester'] == semester_name), None)
            if ev:
                cgpa_info = f"""
                <para alignment="right" spaceBefore="10" spaceAfter="10">
                    <font color="#6b7280" size="9">Cumulative GPA after this semester: </font>
                    <font color="#059669" size="11"><b>{ev['cgpa']:.2f}</b></font>
                    <font color="#6b7280" size="9"> ({get_classification(ev['cgpa'])})</font>
                </para>
                """
                elements.append(Paragraph(cgpa_info, normal_style))
        
        elements.append(Spacer(1, 0.2*inch))
    
    # Final Summary (only for full transcript)
    if transcript_type == "full":
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Table([['']], colWidths=[6.5*inch], style=TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#059669')),
        ])))
        elements.append(Spacer(1, 0.2*inch))
        
        summary_data = [
            ['ACADEMIC SUMMARY', ''],
            ['Total Semesters Completed:', str(num_semesters)],
            ['Total Credits Earned:', str(total_credits)],
            ['Cumulative Grade Point Average (CGPA):', f"{cgpa:.2f}"],
            ['Degree Classification:', get_classification(cgpa)],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#065f46')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f0fdf4')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d1fae5')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#a7f3d0')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, -2), (1, -2), 'Helvetica-Bold'),
            ('FONTNAME', (1, -1), (1, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (1, -2), (1, -2), colors.HexColor('#059669')),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('PADDING', (0, 1), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(summary_table)
    
    # Footer with signatures
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Table([['']], colWidths=[6.5*inch], style=TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.HexColor('#d1d5db')),
    ])))
    elements.append(Spacer(1, 0.2*inch))
    
    footer_text = f"""
    <para alignment="center" spaceBefore="10">
        <font size="8" color="#9ca3af">This is an official transcript generated by FPT Academic Calculator Pro on {datetime.now().strftime('%B %d, %Y at %H:%M')}</font><br/>
        <font size="8" color="#9ca3af">For verification purposes, contact the Academic Office with Student ID: {st.session_state.student_info.get('student_id', 'N/A')}</font><br/>
        <font size="7" color="#d1d5db">_________________________________</font>
    </para>
    """
    elements.append(Paragraph(footer_text, normal_style))
    
    # Build PDF with error handling
    try:
        doc.build(elements)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"PDF Generation Error: {str(e)}")
        return None
    finally:
        # Cleanup
        del elements
        gc.collect()

def generate_semester_html_transcript(semester_name, courses):
    """Generate HTML transcript for a specific semester"""
    sem_gpa, total_credits = calculate_semester_gpa(courses)
    
    courses_html = ""
    for course in courses:
        weighted = course['grade_points'] * course['credits']
        grade_class = get_grade_class(course['grade'])
        courses_html += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; font-weight: 600; color: #374151;">{course['code']}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; color: #4b5563;">{course['title']}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: center; color: #374151;">{course['credits']}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: center;">
                <span style="display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-weight: 700; font-size: 0.875rem; 
                    background: {'#d1fae5' if course['grade'] == 'A' else '#dbeafe' if course['grade'] == 'B' else '#fef3c7' if course['grade'] == 'C' else '#ffedd5' if course['grade'] == 'D' else '#f3f4f6' if course['grade'] == 'E' else '#fee2e2'}; 
                    color: {'#065f46' if course['grade'] == 'A' else '#1e40af' if course['grade'] == 'B' else '#92400e' if course['grade'] == 'C' else '#9a3412' if course['grade'] == 'D' else '#374151' if course['grade'] == 'E' else '#991b1b'};">
                    {course['grade']}
                </span>
            </td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: center; color: #374151;">{course['grade_points']:.1f}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: center; font-weight: 600; color: #059669;">{weighted:.1f}</td>
        </tr>
        """
    
    total_weighted = sum(c['grade_points'] * c['credits'] for c in courses)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Semester Transcript - {semester_name}</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            body {{ 
                font-family: 'Inter', sans-serif; 
                margin: 0; 
                padding: 40px; 
                background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
                color: #1f2937;
            }}
            .container {{ 
                max-width: 900px; 
                margin: 0 auto; 
                background: white; 
                padding: 50px; 
                border-radius: 16px; 
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
            }}
            .header {{ 
                text-align: center; 
                padding-bottom: 30px; 
                border-bottom: 3px solid #059669;
                margin-bottom: 30px;
            }}
            .university-name {{ 
                font-size: 32px; 
                font-weight: 800; 
                color: #065f46; 
                letter-spacing: -0.025em;
                margin-bottom: 8px;
            }}
            .university-sub {{ 
                font-size: 14px; 
                color: #6b7280; 
                font-weight: 500;
            }}
            .doc-title {{ 
                font-size: 24px; 
                font-weight: 700; 
                color: #1f2937; 
                margin: 25px 0 10px 0;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}
            .semester-badge {{
                display: inline-block;
                background: linear-gradient(135deg, #059669 0%, #047857 100%);
                color: white;
                padding: 12px 30px;
                border-radius: 9999px;
                font-size: 18px;
                font-weight: 700;
                margin: 20px 0;
                box-shadow: 0 10px 15px -3px rgba(5, 150, 105, 0.3);
            }}
            .info-section {{ 
                background: #f9fafb; 
                padding: 25px; 
                border-radius: 12px; 
                margin-bottom: 30px;
                border: 1px solid #e5e7eb;
            }}
            .info-grid {{ 
                display: grid; 
                grid-template-columns: 1fr 1fr; 
                gap: 20px; 
            }}
            .info-item {{ 
                display: flex; 
                flex-direction: column; 
            }}
            .info-label {{ 
                font-size: 12px; 
                color: #6b7280; 
                text-transform: uppercase; 
                letter-spacing: 0.05em;
                font-weight: 600;
                margin-bottom: 5px;
            }}
            .info-value {{ 
                font-size: 16px; 
                color: #111827; 
                font-weight: 600;
            }}
            table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin-top: 20px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                border-radius: 8px;
                overflow: hidden;
            }}
            th {{ 
                background: linear-gradient(135deg, #059669 0%, #047857 100%);
                color: white;
                padding: 16px; 
                text-align: left; 
                font-weight: 600; 
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}
            th:last-child, td:last-child {{
                text-align: center;
            }}
            .summary-row {{
                background: #ecfdf5 !important;
                font-weight: 700;
                color: #065f46;
            }}
            .gpa-highlight {{
                font-size: 28px;
                color: #059669;
                font-weight: 800;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                text-align: center;
                color: #9ca3af;
                font-size: 12px;
            }}
            @media print {{
                body {{ background: white; }}
                .container {{ box-shadow: none; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="university-name">FPT UNIVERSITY</div>
                <div class="university-sub">Federal University of Technology • Academic Affairs Division</div>
                <div class="doc-title">Official Semester Transcript</div>
                <div class="semester-badge">{semester_name}</div>
            </div>
            
            <div class="info-section">
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Student Name</span>
                        <span class="info-value">{st.session_state.transcript_info.get('name', st.session_state.student_info.get('name', 'N/A'))}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Matric Number</span>
                        <span class="info-value">{st.session_state.transcript_info.get('matric_number', st.session_state.student_info.get('matric_number', 'N/A'))}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Department</span>
                        <span class="info-value">{st.session_state.transcript_info.get('department', st.session_state.student_info.get('department', 'N/A'))}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Program</span>
                        <span class="info-value">{st.session_state.transcript_info.get('program', st.session_state.student_info.get('program', 'N/A'))}</span>
                    </div>
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Course Code</th>
                        <th>Course Title</th>
                        <th style="text-align: center;">Credits</th>
                        <th style="text-align: center;">Grade</th>
                        <th style="text-align: center;">Points</th>
                        <th style="text-align: center;">Weighted</th>
                    </tr>
                </thead>
                <tbody>
                    {courses_html}
                    <tr class="summary-row">
                        <td colspan="2" style="padding: 16px; text-align: right; border-top: 2px solid #059669;">Semester Summary</td>
                        <td style="padding: 16px; text-align: center; border-top: 2px solid #059669;">{total_credits}</td>
                        <td colspan="2" style="padding: 16px; text-align: right; border-top: 2px solid #059669;">Semester GPA:</td>
                        <td style="padding: 16px; text-align: center; border-top: 2px solid #059669;">
                            <span class="gpa-highlight">{sem_gpa:.2f}</span>
                        </td>
                    </tr>
                </tbody>
            </table>
            
            <div class="footer">
                <p>Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
                <p>This is an official document. For verification, contact the Academic Office.</p>
                <p style="margin-top: 10px; font-size: 10px;">Student ID: {st.session_state.student_info.get('student_id', 'N/A')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def generate_complete_html_transcript(all_courses, final_cgpa, classification):
    """Generate HTML for complete transcript showing all semesters separately"""
    # Group courses by semester
    sem_data = {}
    for course in all_courses:
        sem = course.get('semester', 'Unknown')
        if sem not in sem_data:
            sem_data[sem] = []
        sem_data[sem].append(course)
    
    sem_sections = ""
    for sem_name, courses in sorted(sem_data.items()):
        sem_gpa, sem_credits = calculate_semester_gpa(courses)
        
        courses_rows = ""
        for c in courses:
            weighted = c['grade_points'] * c['credits']
            courses_rows += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">{c['code']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">{c['title']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: center;">{c['credits']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: center;">{c['grade']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: center;">{weighted:.1f}</td>
            </tr>
            """
        
        sem_sections += f"""
        <div style="margin-bottom: 30px; border: 2px solid #e5e7eb; border-radius: 12px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #059669 0%, #047857 100%); color: white; padding: 15px; font-weight: 700; font-size: 1.1rem;">
                {sem_name} - GPA: {sem_gpa:.2f}
            </div>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #f0fdf4;">
                        <th style="padding: 10px; text-align: left;">Code</th>
                        <th style="padding: 10px; text-align: left;">Title</th>
                        <th style="padding: 10px; text-align: center;">Credits</th>
                        <th style="padding: 10px; text-align: center;">Grade</th>
                        <th style="padding: 10px; text-align: center;">Weighted</th>
                    </tr>
                </thead>
                <tbody>
                    {courses_rows}
                </tbody>
            </table>
        </div>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Complete Academic Transcript</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            body {{ font-family: 'Inter', sans-serif; margin: 0; padding: 40px; background: #f0fdf4; color: #1f2937; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 50px; border-radius: 16px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15); }}
            .header {{ text-align: center; padding-bottom: 30px; border-bottom: 3px solid #059669; margin-bottom: 30px; }}
            .university-name {{ font-size: 32px; font-weight: 800; color: #065f46; margin-bottom: 8px; }}
            .summary-box {{ background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); border: 2px solid #059669; border-radius: 12px; padding: 25px; margin: 30px 0; text-align: center; }}
            .cgpa-big {{ font-size: 48px; font-weight: 800; color: #059669; }}
            .classification-badge {{ display: inline-block; background: #059669; color: white; padding: 10px 25px; border-radius: 9999px; font-weight: 700; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="university-name">FPT UNIVERSITY</div>
                <div style="color: #6b7280; font-size: 14px;">Complete Academic Transcript</div>
                <div style="margin-top: 20px; font-size: 12px; color: #9ca3af;">{st.session_state.transcript_info.get('name', 'N/A')} | {st.session_state.transcript_info.get('matric_number', 'N/A')}</div>
            </div>
            
            {sem_sections}
            
            <div class="summary-box">
                <div style="font-size: 14px; color: #065f46; font-weight: 600; margin-bottom: 10px;">FINAL ACADEMIC SUMMARY</div>
                <div class="cgpa-big">{final_cgpa:.2f}</div>
                <div style="font-size: 18px; color: #374151; margin-top: 5px;">Cumulative GPA</div>
                <div class="classification-badge">{classification}</div>
            </div>
            
            <div style="text-align: center; margin-top: 40px; color: #9ca3af; font-size: 12px;">
                <p>Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
                <p>Student ID: {st.session_state.student_info.get('student_id', 'N/A')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

# NEW: Initialize app function that was missing
def initialize_app():
    """Initialize app state and load any existing data"""
    if not st.session_state.initialized:
        # Try to load data if name/matric exist in session
        if st.session_state.student_info.get('name') and st.session_state.student_info.get('matric_number'):
            load_from_csv()
        st.session_state.initialized = True

# Initialize app
initialize_app()

# Enhanced Header with green theme and storage status
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; font-size: 3rem; position: relative; z-index: 1;">🎓 FPT Academic Calculator Pro</h1>
        <p style="margin:0.75rem 0 0 0; opacity: 0.95; font-size: 1.25rem; position: relative; z-index: 1; font-weight: 400;">
            Professional GPA/CGPA Calculator with Persistent Storage
        </p>
    </div>
    """, unsafe_allow_html=True)

with header_col2:
    status_class = "storage-active" if st.session_state.storage_status == "active" else "storage-inactive"
    status_icon = "💾" if st.session_state.storage_status == "active" else "⚠️"
    status_text = "Auto-Save On" if st.session_state.storage_status == "active" else "Not Saved"
    
    st.markdown(f"""
    <div style="margin-top: 1rem; text-align: right;">
        <span class="storage-status {status_class}">
            {status_icon} {status_text}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.last_saved:
        st.caption(f"Last saved: {st.session_state.last_saved.strftime('%H:%M:%S')}")

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); 
                padding: 1.5rem; border-radius: 16px; margin-bottom: 1.5rem; 
                border: 2px solid #a7f3d0;">
        <h2 style="color: #065f46; margin: 0; font-size: 1.5rem;">👤 Student Profile</h2>
        <p style="color: #059669; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Your data persists automatically</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.student_info.get('student_id'):
        st.caption(f"Student ID: `{st.session_state.student_info['student_id']}`")
    
    st.session_state.student_info['name'] = st.text_input(
        "Full Name", 
        value=st.session_state.student_info['name'],
        placeholder="Enter your full name"
    )
    
    # NEW: Matric number validation
    matric_col1, matric_col2 = st.columns([3, 1])
    with matric_col1:
        st.session_state.student_info['matric_number'] = st.text_input(
            "Matric Number", 
            value=st.session_state.student_info['matric_number'],
            placeholder="e.g., FPT/2023/001"
        )
    with matric_col2:
        if st.session_state.student_info['matric_number']:
            is_valid, val_msg = validate_matric_number(st.session_state.student_info['matric_number'])
            if is_valid:
                st.markdown("✅", unsafe_allow_html=True)
            else:
                st.markdown("❌", unsafe_allow_html=True)
                st.caption(val_msg)
    
    st.session_state.student_info['department'] = st.selectbox(
        "Department",
        DEPARTMENTS,
        index=DEPARTMENTS.index(st.session_state.student_info['department']) if st.session_state.student_info['department'] in DEPARTMENTS else 0
    )
    
    st.session_state.student_info['program'] = st.text_input(
        "Program of Study",
        value=st.session_state.student_info['program'],
        placeholder="e.g., B.Sc. Computer Science"
    )
    
    st.divider()
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
                padding: 1rem; border-radius: 12px; margin-bottom: 1rem; 
                border: 1px solid #7dd3fc;">
        <h3 style="color: #0369a1; margin: 0; font-size: 1.1rem;">💾 Data Management</h3>
        <p style="color: #0ea5e9; margin: 0.25rem 0 0 0; font-size: 0.8rem;">Persistent CSV Storage</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Now", use_container_width=True):
            success, msg = save_to_csv()
            if success:
                st.success(msg)
            else:
                st.warning(msg)
    
    with col2:
        if st.button("📂 Load Data", use_container_width=True):
            success, msg = load_from_csv()
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.warning(msg)
    
    auto_save_enabled = st.toggle("Auto-save on change", value=True)
    
    if st.button("🗑️ Clear All Data", type="secondary"):
        if st.session_state.student_info.get('student_id'):
            delete_student_data(st.session_state.student_info['student_id'])
        st.session_state.semesters = {}
        st.session_state.student_info = {k: '' for k in st.session_state.student_info if k != 'department'}
        st.session_state.student_info['department'] = 'Information Technology'
        st.session_state.transcript_info = {k: '' for k in st.session_state.transcript_info}
        st.session_state.transcript_info['department'] = 'Information Technology'
        st.session_state.storage_status = "inactive"
        st.session_state.last_saved = None
        st.rerun()
    
    with st.expander("📋 View All Stored Students"):
        students = get_all_students()
        if students:
            for student in students:
                st.markdown(f"""
                <div style="padding: 0.75rem; background: #f0fdf4; border-radius: 8px; margin-bottom: 0.5rem; border: 1px solid #a7f3d0;">
                    <strong>{student['name']}</strong><br>
                    <small>{student['matric_number']} • {student['total_semesters']} semesters • {student['total_courses']} courses</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No students stored yet")
    
    st.divider()
    
    with st.expander("📊 Grading Scale Reference"):
        grade_df = pd.DataFrame([
            {
                'Grade': grade,
                'Points': info['points'],
                'Remark': info['remark']
            }
            for grade, info in GRADING_SYSTEM.items()
        ])
        st.dataframe(grade_df, hide_index=True, use_container_width=True)
    
    with st.expander("🎓 Degree Classification"):
        class_df = pd.DataFrame([
            {
                'Classification': cls,
                'CGPA Range': f"{rng[0]:.2f} - {rng[1]:.2f}"
            }
            for cls, rng in DEGREE_CLASSIFICATION.items()
        ])
        st.dataframe(class_df, hide_index=True, use_container_width=True)

# Main Content Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📚 Semester Manager", 
    "📊 Analytics Dashboard", 
    "📋 Transcript & Evolution",
    "⚙️ Academic Tools"
])

# Tab 1: Semester Manager
with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); 
                    padding: 1.5rem; border-radius: 16px; border: 2px solid #bbf7d0; 
                    margin-bottom: 1rem;">
            <h3 style="color: #065f46; margin: 0;">📝 Semester Management</h3>
            <p style="color: #059669; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Create and manage your semesters</p>
        </div>
        """, unsafe_allow_html=True)
        
        semester_options = list(st.session_state.semesters.keys()) + ["+ Create New Semester"]
        selected = st.selectbox("Select Semester", semester_options)
        
        if selected == "+ Create New Semester":
            new_semester = st.text_input("New Semester Name", placeholder="e.g., 100 Level First Semester")
            if new_semester and st.button("Create Semester", type="primary"):
                if new_semester not in st.session_state.semesters:
                    st.session_state.semesters[new_semester] = []
                    st.session_state.current_semester = new_semester
                    if auto_save_enabled:
                        auto_save()
                    st.rerun()
        else:
            st.session_state.current_semester = selected
        
        if st.session_state.current_semester and st.session_state.current_semester in st.session_state.semesters:
            courses = st.session_state.semesters[st.session_state.current_semester]
            total_credits = sum(c['credits'] for c in courses)
            
            st.markdown(f"""
            <div class="metric-card" style="margin-top: 1rem;">
                <div style="color: #6b7280; font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Current Credit Load</div>
                <div style="font-size: 2rem; font-weight: 800; color: #065f46; margin-top: 0.25rem;">{total_credits} <span style="font-size: 1rem; color: #9ca3af; font-weight: 500;">units</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced credit load validation
            if total_credits < 15:
                st.warning("⚠️ Below minimum (15)")
            elif total_credits > 24:
                st.error("❌ Exceeds maximum (24)")
            elif total_credits > 21:
                st.info("ℹ️ Requires CGPA ≥ 3.00 approval")
            else:
                st.success("✅ Within normal range")
            
            if courses:
                gpa, _ = calculate_semester_gpa(courses)
                st.markdown(f"""
                <div class="metric-card" style="margin-top: 0.75rem; border-left-color: #f59e0b;">
                    <div style="color: #6b7280; font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Semester GPA</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #b45309; margin-top: 0.25rem;">{gpa:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        if st.session_state.current_semester and st.session_state.current_semester != "+ Create New Semester":
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
                        padding: 1.25rem 1.5rem; border-radius: 12px; 
                        border-left: 4px solid #0ea5e9; margin-bottom: 1.5rem;">
                <h3 style="color: #0369a1; margin: 0; font-size: 1.25rem;">📖 {st.session_state.current_semester}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("➕ Add New Course", expanded=True):
                col_code, col_title, col_credits, col_grade = st.columns([1.5, 2.5, 1, 1])
                
                with col_code:
                    course_code = st.text_input("Course Code", placeholder="CSC 101", key="add_course_code")
                
                with col_title:
                    course_title = st.text_input("Course Title", placeholder="Introduction to Programming", key="add_course_title")
                
                with col_credits:
                    credits = st.number_input("Credits", min_value=1, max_value=6, value=3, key="add_credits")
                
                with col_grade:
                    grade = st.selectbox("Grade", ['A', 'B', 'C', 'D', 'E', 'F'], index=0, key="add_grade")
                
                grade_points = get_grade_points(grade)
                remark = get_grade_remark(grade)
                
                info_col1, info_col2 = st.columns(2)
                with info_col1:
                    st.info(f"Grade Points: **{grade_points}**")
                with info_col2:
                    st.info(f"Remark: **{remark}**")
                
                calc_preview = grade_points * credits
                st.success(f"Weighted Points: **{grade_points} × {credits} = {calc_preview}**")
                
                # NEW: Check for duplicates before adding
                if st.button("Add Course", type="primary", use_container_width=True):
                    if course_code and course_title:
                        # Check for duplicate
                        if check_duplicate_course(st.session_state.current_semester, course_code):
                            st.error(f"❌ Course {course_code} already exists in this semester!")
                        else:
                            new_course = {
                                'code': course_code.upper(),
                                'title': course_title,
                                'credits': credits,
                                'grade': grade,
                                'grade_points': grade_points
                            }
                            st.session_state.semesters[st.session_state.current_semester].append(new_course)
                            
                            if auto_save_enabled:
                                auto_save()
                            
                            st.success(f"✅ Added {course_code}!")
                            st.rerun()
                    else:
                        st.error("Please fill in course code and title")
            
            if st.session_state.semesters[st.session_state.current_semester]:
                st.divider()
                st.markdown("""
                <h3 style="color: #1f2937; margin-bottom: 1rem;">📋 Registered Courses & Calculations</h3>
                """, unsafe_allow_html=True)
                
                header_cols = st.columns([2, 3, 1, 1, 1, 1.5, 0.5])
                header_cols[0].markdown("**Code**")
                header_cols[1].markdown("**Title**")
                header_cols[2].markdown("**Units**")
                header_cols[3].markdown("**Grade**")
                header_cols[4].markdown("**GP**")
                header_cols[5].markdown("**Weighted**")
                
                st.divider()
                
                total_weighted = 0
                total_credits = 0
                
                for idx, course in enumerate(st.session_state.semesters[st.session_state.current_semester]):
                    grade_class = get_grade_class(course['grade'])
                    weighted = course['grade_points'] * course['credits']
                    total_weighted += weighted
                    total_credits += course['credits']
                    
                    cols = st.columns([2, 3, 1, 1, 1, 1.5, 0.5])
                    
                    cols[0].markdown(f"**{course['code']}**")
                    cols[1].markdown(f"{course['title']}")
                    cols[2].markdown(f"{course['credits']}")
                    cols[3].markdown(f'<span class="grade-badge {grade_class}">{course["grade"]}</span>', unsafe_allow_html=True)
                    cols[4].markdown(f"{course['grade_points']}")
                    cols[5].markdown(f"{course['grade_points']} × {course['credits']} = {weighted}")
                    
                    if cols[6].button("🗑️", key=f"del_{idx}", help="Delete course"):
                        st.session_state.semesters[st.session_state.current_semester].pop(idx)
                        if auto_save_enabled:
                            auto_save()
                        st.rerun()
                
                st.divider()
                
                gpa = round(total_weighted / total_credits, 2) if total_credits > 0 else 0.0
                
                calc_summary = f"""
                <div style="background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); 
                            border: 2px solid #10b981; border-radius: 16px; padding: 2rem; margin-top: 1.5rem;
                            box-shadow: 0 10px 30px rgba(5, 150, 105, 0.1);">
                    <h4 style="margin-top: 0; color: #065f46; font-size: 1.25rem; margin-bottom: 1rem;">📐 Semester GPA Calculation</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                        <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #a7f3d0;">
                            <div style="color: #6b7280; font-size: 0.875rem;">Total Weighted Points</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #065f46;">{total_weighted}</div>
                        </div>
                        <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #a7f3d0;">
                            <div style="color: #6b7280; font-size: 0.875rem;">Total Credit Units</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #065f46;">{total_credits}</div>
                        </div>
                    </div>
                    <div style="background: white; padding: 1.25rem; border-radius: 8px; border: 2px solid #059669; text-align: center;">
                        <div style="color: #6b7280; font-size: 0.875rem; margin-bottom: 0.5rem;">GPA Calculation</div>
                        <div style="font-size: 1.25rem; color: #374151; margin-bottom: 0.5rem;">{total_weighted} ÷ {total_credits}</div>
                        <div style="font-size: 2.5rem; font-weight: 800; color: #059669;">{gpa:.2f}</div>
                    </div>
                </div>
                """
                
                st.markdown(calc_summary, unsafe_allow_html=True)

# Tab 2: Analytics Dashboard
with tab2:
    if st.session_state.semesters:
        cgpa, total_credits, num_semesters = calculate_cgpa(st.session_state.semesters)
        classification = get_classification(cgpa)
        classification_class = get_classification_class(classification)
        
        cgpa_html = f"""
        <div style="text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%); 
                    border-radius: 24px; margin-bottom: 2.5rem; border: 2px solid #a7f3d0; 
                    box-shadow: 0 20px 50px rgba(5, 150, 105, 0.1); position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; right: 0; height: 6px; 
                        background: linear-gradient(90deg, #10b981, #059669, #047857);"></div>
            <div style="font-size: 1rem; color: #6b7280; margin-bottom: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em;">Cumulative GPA (CGPA)</div>
            <div class="cgpa-display">{cgpa:.2f}</div>
            <div style="margin-top: 1.5rem;">
                <span class="classification-badge {classification_class}">{classification}</span>
            </div>
            <div style="margin-top: 1rem; color: #6b7280; font-size: 1rem; font-weight: 500;">
                Average of {num_semesters} Semester(s) • {total_credits} Total Credits
            </div>
        </div>
        """
        
        st.markdown(cgpa_html, unsafe_allow_html=True)
        
        st.subheader("📈 CGPA Evolution by Semester")
        
        evolution = get_cgpa_evolution(st.session_state.semesters)
        
        if evolution:
            fig = go.Figure()
            
            semesters_list = [e['semester'] for e in evolution]
            cgpa_list = [e['cgpa'] for e in evolution]
            semester_gpa_list = [e['semester_gpa'] for e in evolution]
            
            fig.add_trace(go.Bar(
                name='Semester GPA',
                x=semesters_list,
                y=semester_gpa_list,
                marker_color='#10b981',
                opacity=0.8,
                marker_line_color='#059669',
                marker_line_width=2
            ))
            
            fig.add_trace(go.Scatter(
                name='CGPA (Cumulative)',
                x=semesters_list,
                y=cgpa_list,
                mode='lines+markers',
                line=dict(color='#f59e0b', width=4),
                marker=dict(size=14, color='#f59e0b', symbol='diamond', line=dict(color='#fff', width=2))
            ))
            
            fig.update_layout(
                title=dict(
                    text='Academic Performance Trajectory',
                    font=dict(size=20, color='#065f46', family='Plus Jakarta Sans'),
                    x=0.5
                ),
                xaxis_title="Semester",
                yaxis_title="GPA",
                yaxis_range=[0, 5],
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Plus Jakarta Sans", color='#374151'),
                legend=dict(
                    orientation="h", 
                    yanchor="bottom", 
                    y=1.02, 
                    xanchor="center", 
                    x=0.5,
                    bgcolor='rgba(255,255,255,0.9)',
                    bordercolor='#e5e7eb',
                    borderwidth=1
                ),
                height=500,
                hovermode='x unified'
            )
            
            fig.add_hline(y=4.50, line_dash="dash", line_color="#fbbf24", annotation_text="First Class", annotation_position="right")
            fig.add_hline(y=3.50, line_dash="dash", line_color="#3b82f6", annotation_text="2nd Upper", annotation_position="right")
            fig.add_hline(y=2.40, line_dash="dash", line_color="#10b981", annotation_text="2nd Lower", annotation_position="right")
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📊 Semester-by-Semester Breakdown")
            
            evol_data = []
            for i, ev in enumerate(evolution, 1):
                evol_data.append({
                    'S/N': i,
                    'Semester': ev['semester'],
                    'Semester GPA': f"{ev['semester_gpa']:.2f}",
                    'CGPA After This Semester': f"{ev['cgpa']:.2f}",
                    'Classification': get_classification(ev['cgpa'])
                })
            
            evol_df = pd.DataFrame(evol_data)
            st.dataframe(evol_df, hide_index=True, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🥧 Grade Distribution")
            
            all_grades = []
            for courses in st.session_state.semesters.values():
                for course in courses:
                    all_grades.append(course['grade'])
            
            if all_grades:
                grade_counts = pd.Series(all_grades).value_counts().reset_index()
                grade_counts.columns = ['Grade', 'Count']
                
                color_map = {'A': '#10b981', 'B': '#3b82f6', 'C': '#f59e0b', 'D': '#f97316', 'E': '#6b7280', 'F': '#ef4444'}
                
                fig = px.pie(grade_counts, values='Count', names='Grade', 
                            color='Grade', color_discrete_map=color_map,
                            hole=0.5)
                fig.update_traces(
                    textinfo='percent+label', 
                    textfont_size=14,
                    marker=dict(line=dict(color='#ffffff', width=3))
                )
                fig.update_layout(
                    showlegend=False, 
                    font=dict(family="Plus Jakarta Sans"),
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📈 Performance Metrics")
            
            all_courses = []
            for sem_name, courses in st.session_state.semesters.items():
                for course in courses:
                    all_courses.append({
                        'grade': course['grade'],
                        'points': course['grade_points'],
                        'credits': course['credits']
                    })
            
            if all_courses:
                df_courses = pd.DataFrame(all_courses)
                
                avg_grade_points = df_courses['points'].mean()
                total_courses = len(df_courses)
                passed = len(df_courses[df_courses['grade'] != 'F'])
                failed = len(df_courses[df_courses['grade'] == 'F'])
                
                metric_html = f"""
                <div class="metric-card" style="margin-bottom: 1rem;">
                    <div style="color: #6b7280; font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Average Grade Points</div>
                    <div style="font-size: 3rem; font-weight: 800; color: #065f46; margin-top: 0.5rem;">{avg_grade_points:.2f}</div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
                    <div class="metric-card" style="text-align: center;">
                        <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">Total</div>
                        <div style="font-size: 2rem; font-weight: 800; color: #1f2937; margin-top: 0.25rem;">{total_courses}</div>
                    </div>
                    <div class="metric-card" style="text-align: center; border-left-color: #10b981;">
                        <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">Passed</div>
                        <div style="font-size: 2rem; font-weight: 800; color: #059669; margin-top: 0.25rem;">{passed}</div>
                    </div>
                    <div class="metric-card" style="text-align: center; border-left-color: #ef4444;">
                        <div style="color: #6b7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">Failed</div>
                        <div style="font-size: 2rem; font-weight: 800; color: #dc2626; margin-top: 0.25rem;">{failed}</div>
                    </div>
                </div>
                """
                
                st.markdown(metric_html, unsafe_allow_html=True)

# Tab 3: Transcript & Evolution - ENHANCED WITH INDIVIDUAL SEMESTER DOWNLOADS
with tab3:
    if st.session_state.semesters:
        
        # Enhanced Transcript Information Section
        st.markdown("""
        <div class="transcript-header">
            <h2 style="margin: 0; font-size: 2rem; position: relative; z-index: 1;">📜 ACADEMIC TRANSCRIPTS</h2>
            <p style="margin: 0.75rem 0 0 0; opacity: 0.95; position: relative; z-index: 1; font-size: 1.1rem;">Download individual semester or complete transcript</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Pre-fill with sidebar data if available
        if not st.session_state.transcript_info['name'] and st.session_state.student_info['name']:
            st.session_state.transcript_info['name'] = st.session_state.student_info['name']
        if not st.session_state.transcript_info['matric_number'] and st.session_state.student_info['matric_number']:
            st.session_state.transcript_info['matric_number'] = st.session_state.student_info['matric_number']
        if not st.session_state.transcript_info['department'] and st.session_state.student_info['department']:
            st.session_state.transcript_info['department'] = st.session_state.student_info['department']
        if not st.session_state.transcript_info['program'] and st.session_state.student_info['program']:
            st.session_state.transcript_info['program'] = st.session_state.student_info['program']
        
        with st.container():
            st.markdown('<div class="student-info-card">', unsafe_allow_html=True)
            st.subheader("✏️ Student Information for Transcript")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.session_state.transcript_info['name'] = st.text_input(
                    "Full Name *",
                    value=st.session_state.transcript_info['name'],
                    placeholder="Enter your full name",
                    key="transcript_name"
                )
                
                st.session_state.transcript_info['matric_number'] = st.text_input(
                    "Matric Number *",
                    value=st.session_state.transcript_info['matric_number'],
                    placeholder="e.g., FPT/2023/001",
                    key="transcript_matric"
                )
                
                st.session_state.transcript_info['department'] = st.selectbox(
                    "Department *",
                    DEPARTMENTS,
                    index=DEPARTMENTS.index(st.session_state.transcript_info['department']) if st.session_state.transcript_info['department'] in DEPARTMENTS else 1,
                    key="transcript_dept"
                )
            
            with col2:
                st.session_state.transcript_info['program'] = st.text_input(
                    "Program of Study *",
                    value=st.session_state.transcript_info['program'],
                    placeholder="e.g., B.Sc. Information Technology",
                    key="transcript_program"
                )
                
                st.session_state.transcript_info['session'] = st.text_input(
                    "Academic Session",
                    value=st.session_state.transcript_info['session'],
                    placeholder="e.g., 2020/2021 - 2023/2024",
                    key="transcript_session"
                )
                
                st.session_state.transcript_info['date_of_birth'] = st.text_input(
                    "Date of Birth",
                    value=st.session_state.transcript_info['date_of_birth'],
                    placeholder="e.g., January 15, 2000",
                    key="transcript_dob"
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Check if required fields are filled
        required_filled = all([
            st.session_state.transcript_info['name'],
            st.session_state.transcript_info['matric_number'],
            st.session_state.transcript_info['department'],
            st.session_state.transcript_info['program']
        ])
        
        if not required_filled:
            st.warning("⚠️ Please fill in all required fields (marked with *) to generate transcripts.")
        
        st.divider()
        
        # INDIVIDUAL SEMESTER TRANSCRIPTS SECTION
        st.subheader("📄 Individual Semester Transcripts")
        
        evolution = get_cgpa_evolution(st.session_state.semesters)
        
        # Display each semester with download options
        for idx, (semester_name, courses) in enumerate(sorted(st.session_state.semesters.items())):
            if not courses:
                continue
                
            sem_gpa, sem_credits = calculate_semester_gpa(courses)
            ev = next((e for e in evolution if e['semester'] == semester_name), None)
            
            with st.container():
                st.markdown(f"""
                <div class="semester-transcript-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <div>
                            <h4 style="margin: 0; color: #065f46; font-size: 1.25rem;">{semester_name}</h4>
                            <p style="margin: 0.25rem 0 0 0; color: #6b7280; font-size: 0.9rem;">
                                {len(courses)} Courses • {sem_credits} Credits • GPA: <strong>{sem_gpa:.2f}</strong>
                            </p>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 2rem; font-weight: 800; color: #059669;">{sem_gpa:.2f}</div>
                            <div style="font-size: 0.875rem; color: #6b7280;">GPA</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Quick preview of courses
                with st.expander(f"View Courses ({len(courses)})"):
                    preview_df = pd.DataFrame([
                        {
                            'Code': c['code'],
                            'Title': c['title'],
                            'Credits': c['credits'],
                            'Grade': c['grade'],
                            'Points': c['grade_points']
                        }
                        for c in courses
                    ])
                    st.dataframe(preview_df, hide_index=True, use_container_width=True)
                
                # Download buttons for this semester
                dl_col1, dl_col2, dl_col3 = st.columns(3)
                
                # CSV Download
                with dl_col1:
                    sem_csv_data = pd.DataFrame([
                        {
                            'Semester': semester_name,
                            'Course Code': c['code'],
                            'Course Title': c['title'],
                            'Credits': c['credits'],
                            'Grade': c['grade'],
                            'Grade Points': c['grade_points'],
                            'Weighted Score': c['grade_points'] * c['credits'],
                            'Semester GPA': sem_gpa
                        }
                        for c in courses
                    ]).to_csv(index=False)
                    
                    st.download_button(
                        label="📄 Download CSV",
                        data=sem_csv_data,
                        file_name=f"transcript_{semester_name.replace(' ', '_')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        disabled=not required_filled,
                        key=f"sem_csv_{idx}"
                    )
                
                # HTML Download
                with dl_col2:
                    sem_html = generate_semester_html_transcript(semester_name, courses)
                    st.download_button(
                        label="🌐 Download HTML",
                        data=sem_html,
                        file_name=f"transcript_{semester_name.replace(' ', '_')}.html",
                        mime="text/html",
                        use_container_width=True,
                        disabled=not required_filled,
                        key=f"sem_html_{idx}"
                    )
                
                # PDF Download - FIXED with proper state management
                with dl_col3:
                    if REPORTLAB_AVAILABLE:
                        pdf_key = f"pdf_{semester_name.replace(' ', '_')}_{idx}"
                        
                        # Generate PDF button
                        if st.button(f"📕 Generate PDF", use_container_width=True, disabled=not required_filled, key=f"gen_pdf_{idx}"):
                            try:
                                with st.spinner(f"Generating PDF for {semester_name}..."):
                                    pdf_buffer = generate_pdf_transcript(transcript_type="semester", specific_semester=semester_name)
                                    if pdf_buffer:
                                        st.session_state.pdf_buffers[pdf_key] = pdf_buffer.getvalue()
                                        st.success("PDF generated! Click download below.")
                                        st.rerun()
                                    else:
                                        st.error("Error generating PDF")
                            except Exception as e:
                                st.error(f"PDF Error: {str(e)}")
                        
                        # Show download button if PDF is in buffer
                        if pdf_key in st.session_state.pdf_buffers:
                            st.download_button(
                                label="⬇️ Download PDF",
                                data=st.session_state.pdf_buffers[pdf_key],
                                file_name=f"transcript_{semester_name.replace(' ', '_')}.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                                key=f"dl_pdf_{idx}"
                            )
                    else:
                        st.info("Install ReportLab: pip install reportlab")
                
                st.divider()
        
        # COMPLETE TRANSCRIPT SECTION
        st.subheader("📚 Complete Academic Transcript")
        
        cgpa, total_credits, num_semesters = calculate_cgpa(st.session_state.semesters)
        classification = get_classification(cgpa)
        
        # Summary stats
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        with summary_col1:
            st.metric("Total Semesters", num_semesters)
        with summary_col2:
            st.metric("Total Credits", total_credits)
        with summary_col3:
            st.metric("Final CGPA", f"{cgpa:.2f}")
        with summary_col4:
            st.metric("Classification", classification)
        
        # Complete transcript downloads
        st.markdown("### Download Complete Transcript")
        
        comp_col1, comp_col2, comp_col3 = st.columns(3)
        
        # Full CSV
        with comp_col1:
            full_transcript_data = []
            for ev in evolution:
                sem_name = ev['semester']
                courses = st.session_state.semesters[sem_name]
                for c in courses:
                    full_transcript_data.append({
                        'Semester': sem_name,
                        'Semester GPA': ev['semester_gpa'],
                        'CGPA': ev['cgpa'],
                        'Course Code': c['code'],
                        'Course Title': c['title'],
                        'Credits': c['credits'],
                        'Grade': c['grade'],
                        'Grade Points': c['grade_points']
                    })
            
            full_csv = pd.DataFrame(full_transcript_data).to_csv(index=False)
            st.download_button(
                label="📄 Complete CSV",
                data=full_csv,
                file_name=f"complete_transcript_{st.session_state.transcript_info.get('matric_number', 'student')}.csv",
                mime="text/csv",
                use_container_width=True,
                disabled=not required_filled,
                key="full_csv"
            )
        
        # Full HTML - FIXED with proper complete transcript generation
        with comp_col2:
            # Prepare all courses with semester info
            all_courses_flat = []
            for sem_name, courses in sorted(st.session_state.semesters.items()):
                for c in courses:
                    all_courses_flat.append({**c, 'semester': sem_name})
            
            full_html = generate_complete_html_transcript(all_courses_flat, cgpa, classification)
            
            st.download_button(
                label="🌐 Complete HTML",
                data=full_html,
                file_name=f"complete_transcript_{st.session_state.transcript_info.get('matric_number', 'student')}.html",
                mime="text/html",
                use_container_width=True,
                disabled=not required_filled,
                key="full_html"
            )
        
        # Full PDF - FIXED with proper state management
        with comp_col3:
            if REPORTLAB_AVAILABLE:
                full_pdf_key = "full_transcript_pdf"
                
                if st.button("📕 Generate Complete PDF", type="primary", use_container_width=True, disabled=not required_filled, key="gen_full_pdf"):
                    try:
                        with st.spinner("Generating complete transcript PDF..."):
                            pdf_buffer = generate_pdf_transcript(transcript_type="full")
                            if pdf_buffer:
                                st.session_state.pdf_buffers[full_pdf_key] = pdf_buffer.getvalue()
                                st.success("Complete PDF generated!")
                                st.rerun()
                            else:
                                st.error("Error generating PDF")
                    except Exception as e:
                        st.error(f"PDF Error: {str(e)}")
                
                if full_pdf_key in st.session_state.pdf_buffers:
                    st.download_button(
                        label="⬇️ Download Complete PDF",
                        data=st.session_state.pdf_buffers[full_pdf_key],
                        file_name=f"complete_transcript_{st.session_state.transcript_info.get('matric_number', 'student')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key="dl_full_pdf"
                    )
            else:
                st.info("Install ReportLab for PDF generation")
        
        # CGPA Evolution Display
        st.divider()
        st.subheader("🎯 CGPA Evolution Tracker")
        
        for ev in evolution:
            with st.expander(f"📖 {ev['semester']} - GPA: {ev['semester_gpa']:.2f} | CGPA: {ev['cgpa']:.2f}", expanded=False):
                courses = st.session_state.semesters[ev['semester']]
                
                calc_details = []
                total_weighted = 0
                total_credits = 0
                
                for c in courses:
                    weighted = c['grade_points'] * c['credits']
                    total_weighted += weighted
                    total_credits += c['credits']
                    calc_details.append({
                        'Course': c['code'],
                        'Units': c['credits'],
                        'Grade': c['grade'],
                        'GP': c['grade_points'],
                        'Weighted': weighted
                    })
                
                calc_df = pd.DataFrame(calc_details)
                st.dataframe(calc_df, hide_index=True, use_container_width=True)
                
                st.markdown(f"**Calculation:** Sum of Weighted Points ({total_weighted}) ÷ Total Units ({total_credits}) = **{ev['semester_gpa']:.2f}** GPA")
                st.info(f"**CGPA Update:** After {ev['semesters_count']} semester(s), your CGPA = {ev['cgpa']:.2f} ({get_classification(ev['cgpa'])})")
        
    else:
        st.info("📚 No data to generate transcript. Please add courses first.")

# Tab 4: Academic Tools
with tab4:
    st.subheader("⚙️ Academic Tools")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); 
                    padding: 1.5rem; border-radius: 16px; border: 2px solid #bbf7d0; 
                    height: 100%;">
            <h3 style="color: #065f46; margin: 0 0 1rem 0;">🎯 GPA Calculator</h3>
            <p style="color: #059669; margin: 0 0 1.5rem 0; font-size: 0.9rem;">Calculate semester GPA manually</p>
        """, unsafe_allow_html=True)
        
        num_courses = st.number_input("Number of courses", 1, 10, 3, key="calc_num")
        
        total_weighted = 0
        total_credits = 0
        
        for i in range(int(num_courses)):
            st.markdown(f"<p style='font-weight: 600; color: #374151; margin: 1rem 0 0.5rem 0;'>Course {i+1}</p>", unsafe_allow_html=True)
            c_col, g_col = st.columns(2)
            with c_col:
                credits = st.number_input("Credits", 1, 6, 3, key=f"calc_c_{i}")
            with g_col:
                grade = st.selectbox("Grade", ['A', 'B', 'C', 'D', 'E', 'F'], key=f"calc_g_{i}")
            
            gp = get_grade_points(grade)
            weighted = gp * credits
            total_weighted += weighted
            total_credits += credits
            st.caption(f"Weighted: {gp} × {credits} = {weighted}")
            st.divider()
        
        if total_credits > 0:
            calc_gpa = total_weighted / total_credits
            st.success(f"**Calculated GPA:** {calc_gpa:.2f}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); 
                    padding: 1.5rem; border-radius: 16px; border: 2px solid #fcd34d; 
                    height: 100%;">
            <h3 style="color: #92400e; margin: 0 0 1rem 0;">📊 CGPA Projector</h3>
            <p style="color: #b45309; margin: 0 0 1.5rem 0; font-size: 0.9rem;">Project your CGPA based on future performance</p>
        """, unsafe_allow_html=True)
        
        if st.session_state.semesters:
            current_cgpa, _, num_sems = calculate_cgpa(st.session_state.semesters)
            st.info(f"Current CGPA: **{current_cgpa:.2f}** ({num_sems} semesters)")
            
            projected_gpas = []
            num_future = st.number_input("Number of future semesters to project", 1, 8, 2)
            
            for i in range(int(num_future)):
                gpa = st.slider(f"Semester {num_sems + i + 1} GPA", 
                              0.0, 5.0, 3.5, 0.1, 
                              key=f"proj_{i}")
                projected_gpas.append(gpa)
            
            all_gpas = []
            for sem_name, courses in st.session_state.semesters.items():
                gpa, _ = calculate_semester_gpa(courses)
                all_gpas.append(gpa)
            all_gpas.extend(projected_gpas)
            
            projected_cgpa = sum(all_gpas) / len(all_gpas)
            new_classification = get_classification(projected_cgpa)
            
            st.success(f"""
            **Projected CGPA:** {projected_cgpa:.2f}  
            **Classification:** {new_classification}  
            **Total Semesters:** {len(all_gpas)}
            """)
        else:
            st.warning("Add some courses first")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; color: #6b7280; padding: 2rem; margin-top: 2rem; 
            border-top: 2px solid #e5e7eb; background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%); 
            border-radius: 16px 16px 0 0;">
    <p style="margin: 0; font-weight: 600; color: #374151; font-size: 1.1rem;">FPT Academic Calculator Pro</p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">Professional Manual Grade Entry System with Persistent Storage</p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; color: #9ca3af;">Individual semester transcripts now available</p>
</div>
""", unsafe_allow_html=True)

# Auto-save
if auto_save_enabled and st.session_state.semesters and st.session_state.student_info['name'] and st.session_state.student_info['matric_number']:
    auto_save()