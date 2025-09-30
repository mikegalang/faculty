import streamlit as st
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.errors import ConnectionFailure
import os
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import io
from reportlab.lib.pagesizes import landscape, letter

st.markdown("""
<style>
/* ===== DataFrame Table Styling ===== */

/* Header */
[data-testid="stDataFrame"] thead tr th {
    background-color: #1976d2;   /* deep blue header */
    color: white;                /* white text */
    font-weight: bold;
    text-align: center;
    font-size: 14px;
    border-bottom: 2px solid #1565c0;
    position: sticky;
    top: 0;
    z-index: 1;
}

/* Table Body */
[data-testid="stDataFrame"] tbody tr:nth-child(even) {
    background-color: #f9f9f9;   /* light gray for even rows */
}
[data-testid="stDataFrame"] tbody tr:nth-child(odd) {
    background-color: #ffffff;   /* white for odd rows */
}

/* Hover Effect */
[data-testid="stDataFrame"] tbody tr:hover {
    background-color: #e3f2fd;   /* light blue on hover */
    transition: background-color 0.3s ease;
}

/* Cells */
[data-testid="stDataFrame"] tbody td {
    text-align: center;
    font-size: 13px;
    padding: 8px;
    border: 1px solid #ddd;
}

/* Index column hidden */
[data-testid="stDataFrame"] tbody th {
    display: none;
}
</style>
""", unsafe_allow_html=True)

##############################################

def get_mongo_client():

    load_dotenv()

    mongo_uri = os.getenv("MONGODB_URI")

    client = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=5000,   # Fail fast if can't connect
        socketTimeoutMS=20000,           # Time before dropping socket
        connectTimeoutMS=10000,          # Time to establish connection
        retryWrites=True,
        tls=True            )  # replace with your Mongo URI
    
    try:
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas successfully!")
    except ConnectionFailure as e:
        print("❌ Could not connect to MongoDB:", e)

    #client = MongoClient("mongodb+srv://admin:admin@cluster0.dzuvnix.mongodb.net/mit261n")  # replace with your Mongo URI
    return client

def df_to_pdf(dataframe, title="Grade Distribution Report", subtitle=None):
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=30,
        rightMargin=30,
        topMargin=30,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    subtitle_style = styles["Heading3"]

    elements = []

    # Title
    elements.append(Paragraph(title, title_style))
    if subtitle:
        elements.append(Paragraph(subtitle, subtitle_style))
    elements.append(Spacer(1, 12))  # add some space before the table

    # Convert DataFrame → list of lists
    table_data = [list(dataframe.columns)] + dataframe.values.tolist()
    table = Table(table_data)

    # Styling
    style = TableStyle([
        # ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976d2")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.aliceblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ])
    table.setStyle(style)

    # Alternate row colors
    for i in range(1, len(table_data)):
        bg_color = colors.whitesmoke if i % 2 == 0 else colors.lightgrey
        style.add("BACKGROUND", (0, i), (-1, i), bg_color)
    table.setStyle(style)

    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

def df_to_pdf_tracker(dataframe, title="Student Progress Report", subtitle=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=20,
        rightMargin=20,
        topMargin=30,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    subtitle_style = styles["Heading3"]

    elements = []
    elements.append(Paragraph(title, title_style))
    if subtitle:
        elements.append(Paragraph(subtitle, subtitle_style))
    elements.append(Spacer(1, 12))

    # Convert DataFrame → list of lists
    table_data = [list(dataframe.columns)] + dataframe.values.tolist()

    # Auto-fit columns (equal widths)
    page_width, page_height = landscape(letter)
    max_table_width = page_width - (doc.leftMargin + doc.rightMargin)
    col_count = len(table_data[0])
    col_widths = [max_table_width / col_count] * col_count

    table = Table(table_data, colWidths=col_widths)

    # Styling
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976d2")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ])
    table.setStyle(style)

    # Alternate row colors
    for i in range(1, len(table_data)):
        bg_color = colors.whitesmoke if i % 2 == 0 else colors.lightgrey
        style.add("BACKGROUND", (0, i), (-1, i), bg_color)
    table.setStyle(style)

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_pdf_heatmap(df, teacher_name):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)

    # Report Title and Subtitle
    elements = []
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    subtitle_style = styles["Heading3"]

    title = "Subject Difficulty Heatmap"
    subtitle = f"Performance Summary for {teacher_name}"

    # Title
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(subtitle, subtitle_style))
    elements.append(Spacer(1, 12))  # add some space before the table

    # Convert DataFrame to list of lists (for ReportLab Table)
    data = [df.columns.tolist()] + df.values.tolist()

    # Create table
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976d2")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 9),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_pdf_intervention(df, teacher_name):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30
    )

    # Report Title and Subtitle
    elements = []
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    subtitle_style = styles["Heading3"]

    title = "Intervention Candidates List"
    subtitle = f"Student Performance For {teacher_name}"

    # Title
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(subtitle, subtitle_style))
    elements.append(Spacer(1, 12))  # add some space before the table

    if df.empty:
        elements.append(Paragraph("No students found at risk.", styles["Normal"]))
    else:
        # Convert DataFrame to list of lists
        data = [df.columns.tolist()] + df.values.tolist()

        # Fit to page width
        page_width = A4[0] - 60
        num_cols = len(data[0])
        col_widths = [page_width / num_cols] * num_cols

        col_widths = [50, 100, 80, 100, 50, 50, 100]  # widths in points for each column
        #table = Table(data, repeatRows=1, colWidths=col_widths)

        # Create table
        table = Table(data, repeatRows=1, colWidths=col_widths)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976d2")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 9),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ]))

        # Zebra striping
        for i in range(1, len(data)):
            if i % 2 == 0:
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, i), (-1, i), colors.whitesmoke)
                ]))

        elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_pdf_submission(summary_df, teacher_name):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30
    )

    elements = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph(f"📑 Grade Submission Summary for {teacher_name}", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))

    if summary_df.empty:
        elements.append(Paragraph("No records found.", styles["Normal"]))
    else:
        # Convert DataFrame to list of lists
        data = [summary_df.columns.tolist()] + summary_df.values.tolist()

        # Fit to page width
        page_width = A4[0] - 60
        num_cols = len(data[0])
        col_widths = [page_width / num_cols] * num_cols

        col_widths = [50, 80, 100, 50, 50, 50, 50]  # widths in points for each column

        # Report Title and Subtitle
        elements = []
        styles = getSampleStyleSheet()
        title_style = styles["Heading1"]
        subtitle_style = styles["Heading3"]

        title = "Grade Submission Summary"
        subtitle = f"For {teacher_name}"

        # Title
        elements.append(Paragraph(title, title_style))
        elements.append(Paragraph(subtitle, subtitle_style))
        elements.append(Spacer(1, 12))  # add some space before the table
        

        # Create table
        table = Table(data, repeatRows=1, colWidths=col_widths)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976d2")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 9),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ]))

        # Zebra striping for readability
        for i in range(1, len(data)):
            if i % 2 == 0:
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, i), (-1, i), colors.whitesmoke)
                ]))

        elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def faculty_get_teacher_subjects_with_semester(teacher_name: str):
    pipeline = [
        # Unwind SubjectCodes with index to align with Grades and Teachers
        {
            "$unwind": {
                "path": "$SubjectCodes",
                "includeArrayIndex": "idx"
            }
        },
        # Align Grades and Teachers by index
        {
            "$project": {
                "SubjectCode": "$SubjectCodes",
                "Teacher": { "$arrayElemAt": ["$Teachers", "$idx"] },
                "SemesterID": 1
            }
        },
        # Match documents where the teacher matches
        {
            "$match": {
                "Teacher": { "$regex": teacher_name, "$options": "i" }  # Case-insensitive search
            }
        },
        # Lookup semester info from 'semesters' collection
        {
            "$lookup": {
                "from": "new_semesters",
                "localField": "SemesterID",
                "foreignField": "_id",
                "as": "sem_info"
            }
        },
        { "$unwind": "$sem_info" },
        # Final projection
        {
            "$project": {
                "_id": 0,
                "SubjectCode": 1,
                "Teacher": 1,
                "SchoolYear": "$sem_info.SchoolYear",
                "Semester": "$sem_info.Semester"
            }
        },
        # Optional: Remove duplicates
        {
            "$group": {
                "_id": {
                    "SubjectCode": "$SubjectCode",
                    "Teacher": "$Teacher",
                    "SchoolYear": "$SchoolYear",
                    "Semester": "$Semester"
                }
            }
        },
        # Flatten group output
        {
            "$project": {
                "_id": 0,
                "SubjectCode": "$_id.SubjectCode",
                "Teacher": "$_id.Teacher",
                "SchoolYear": "$_id.SchoolYear",
                "Semester": "$_id.Semester"
            }
        },
        # Optional: sort results
        {
            "$sort": {
                "SchoolYear": 1,
                "Semester": 1,
                "SubjectCode": 1
            }
        }
    ]

    return list(gradesCollection.aggregate(pipeline))

def faculty_get_student_grades_by_subject_teacher(subject_code, teacher_name, semester_id):
    #st.write(f"{subject_code} --- {teacher_name} --- {semester_id}")
    pipeline = [
        {
            "$match": {
                "SubjectCodes": subject_code,
                "Teachers": teacher_name,
                "SemesterID": semester_id


            }
        },
        {
            "$project": {
                "StudentID": 1,
                "SubjectIndex": { "$indexOfArray": ["$SubjectCodes", subject_code] },
                "Grades": 1,
                "Teachers": 1
            }
        },
        {
            "$project": {
                "StudentID": 1,
                "Grade": { "$arrayElemAt": ["$Grades", "$SubjectIndex"] }
            }
        },
        {
            "$lookup": {
                "from": "new_students",
                "localField": "StudentID",
                "foreignField": "_id",
                "as": "student_info"
            }
        },
        {
            "$unwind": "$student_info"
        },
        {
            "$project": {
                "_id": 1,
                "Name": "$student_info.Name",
                "Course" : "$student_info.Course",
                "YearLevel" : "$student_info.YearLevel",
                "Grade": 1
            }
        }
    ]

    results =pd.DataFrame(gradesCollection.aggregate(pipeline))

    # results['Status'] = np.where(results['Grade'] >= 75, 'Pass', 'Fail')

    if "Grade" not in results.columns:
        results["Grade"] = None

    # Convert to numeric (invalid → NaN)
    #results["Grade"] = pd.to_numeric(results["Grade"], errors="coerce")

    conditions = [
        results["Grade"].isna(),             # Grade is NaN / empty
        results["Grade"] >= 75,              # Passing grade
        results["Grade"] < 75                # Failing grade
    ]

    choices = [
        "Missing Grade",
        "Pass",
        "Fail"
    ]

    results["Status"] = np.select(conditions, choices, default="Missing Grade")
    #results["Grade"] = results["Grade"].where(~results["Grade"].isna(), "")

    # results["Grade"] = pd.to_numeric(results["Grade"], errors="coerce")

    # # Format only non-NaN values
    # results["Grade"] = results["Grade"].apply(
    #     lambda x: f"{x:.2f}" if pd.notna(x) else x
    # )

    
    return results

def faculty_highlight_low_grades(val):
    if isinstance(val, (int, float)) and val < 75:
        return 'background-color: tomato;'  # light red
    return ''

def render_bar_graph_grades_count():
    graph1Data = studentList['Grade'].value_counts().reset_index()
    graph1Data.columns = ['Grade', 'count']

    #st.write(graph1Data)
    # Plot the bar chart
    plt.figure(figsize=(8, 4))
    bars = plt.bar(graph1Data['Grade'], graph1Data['count'], color='#1976d2')

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 0.1, str(height),
                ha='center', va='bottom', fontsize=8, fontweight='regular')


    plt.xlabel('Grade')
    plt.ylabel('Frequency')
    plt.title('Grade Distribution for ' + selectedSubject)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(plt)

def render_bar_graph_passing_count():
    graph2Data = studentList['Status'].value_counts().reset_index()
    graph2Data.columns = ['Status', 'count']

    #st.write(graph1Data)
    # Plot the bar chart
    # Define colors by status
    colors = graph2Data['Status'].map({
        "Pass": "#1976d2",         # green
        "Fail": "red",         # blue
        "Missing Grade": "orange" # red
    })

    plt.figure(figsize=(8, 4))
    bars = plt.bar(graph2Data['Status'], graph2Data['count'], color=colors)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 0.1, str(height),
                ha='center', va='bottom', fontsize=8, fontweight='regular')

    plt.xlabel('Grade')
    plt.ylabel('Frequency')
    plt.title('Pass vs Fail for ' + selectedSubject)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(plt)



####################################################################
######## MAIN APP
####################################################################
# Page Config
st.set_page_config(layout="wide", page_title="Faculty Module")


# --- Initialize session state ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- Demo credentials (replace with DB or API later) ---
USERNAME = "admin"
PASSWORD = "12345"

# --- Login Form ---
if not st.session_state.authenticated:
    st.markdown("## 🔐 Login to Faculty Module")

    with st.form("login_form"):

        client = get_mongo_client()
        db = client["mit261n"]  
        gradesCollection = db["new_grades"]


        # -------------------------------
        # Input: Teacher name
        # -------------------------------
        # Extract teacher names (flattened list)
        teacher_list = []
        for doc in gradesCollection.find({}, {"Teachers": 1}):
            teacher_list.extend(doc.get("Teachers", []))
        teacher_list = sorted(set(teacher_list))

        session_teacher = st.selectbox("Select Teacher", teacher_list)

        #username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")

    if login_btn:
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.session_state.session_teacher = session_teacher
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

# --- Protected Content ---
else:
    st.title(f"Welcome, {st.session_state.session_teacher}!")

    client = get_mongo_client()
    db = client["mit261n"]  
    subjectsCollection = db["new_subjects"]  
    studentsCollection = db["new_students"]  
    semestersCollection = db["new_semesters"]  
    gradesCollection = db["new_grades"]

    tabs = [
        "Home",
        "Class Grade Distribution", 
        "Student Progress Tracker",
        "Subject Difficulty Heatmap",
        "Intervention Candidates List",
        "Grade Submission Status",
        "Custom Query Builder",
        "Student Grade Analytics",
        "Logout"
        ]
    # Insert containers separated into tabs:
    #active_tab = st.tabs(tabs)
    selected_tab = st.session_state.get("active_tab", 0)

    tab_index = st.radio("📌 Navigate:", tabs, index=selected_tab, horizontal=True, label_visibility="collapsed")
    #st.session_state.active_tab = tabs.index(tab_index)


    # You can also use "with" notation:
    #with tab_home:
    if tab_index == "Home":

        # Bottom-aligned columns
        col1, col2 = st.columns(2)

        # You can also use "with" notation:
        with col2:
            st.subheader("My Subjects")
            teacher_name = st.session_state.session_teacher
            # Case-insensitive regex match
            query = {"Teacher": {"$regex": teacher_name, "$options": "i"}}
            results = list(subjectsCollection.find(query, {"_id": 1, "Description": 1, "Units": 1, "Teacher": 1}))

            if results:
                df = pd.DataFrame(results)
                # Rename Mongo _id to SubjectCode for clarity
                df = df.rename(columns={"_id": "SubjectCode"})
                #st.success(f"✅ Found {len(df)} subject(s) for teacher: {teacher_name}")
                st.dataframe(df, use_container_width=True)
                
            else:
                st.warning("⚠️ No subjects found for that teacher.")

        with col1:
            st.subheader("Semesters List")

            results = list(
                semestersCollection.find(
                    {}, {"_id": 1, "Semester": 1, "SchoolYear": 1}
                ).sort([("_id", 1), ("SchoolYear", 1)])
            )

            if results:
                df = pd.DataFrame(results)
                df = df.rename(columns={"_id": "SemesterID"})
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("⚠️ No semesters found in the database.")
            
        
        
            

    #with tab_class_grade_distribution:
    elif tab_index == "Class Grade Distribution":
        #st.write("tab_class_grade_distribution")
        st.subheader("Class Grade Distribution")
            
        #teachers = gradesCollection.distinct("Teachers")
        #semesters = gradesCollection.distinct("SemesterID")
        semesters = list(semestersCollection.find({}, {"_id": 1, "Semester": 1, "SchoolYear": 1}))
        semesters = sorted(semesters, key=lambda x: x["SchoolYear"], reverse=True)  # optional: newest first

        # --- Build labels ---
        semester_labels = [f'{s["SchoolYear"]} - {s["Semester"]}' for s in semesters]
        sem_map = {f'{s["SchoolYear"]} - {s["Semester"]}': s["_id"] for s in semesters}


        # display the controls
        col1, col2 = st.columns(2)
        with col1:
            #teacher_input = st.selectbox("Select Teacher", teachers)
            #semester_input = st.selectbox("Select Semester", semesters)

            semester_input_desc = st.selectbox("📅 Select Semester", semester_labels)
            semester_input = sem_map[semester_input_desc]

            
        with col2:          
            teacher_input = st.session_state.session_teacher
            

        if teacher_input and semester_input:
            # Query Grades collection
            data = list(gradesCollection.find({
                "Teachers": teacher_input,
                "SemesterID": semester_input
            }))

            #st.table(data)

            # Normalize arrays into rows
            records = []
            for doc in data:
                subject_codes = doc.get("SubjectCodes", [])
                grades = doc.get("Grades", [])
                teachers = doc.get("Teachers", [])

                for i in range(len(subject_codes)):
                    teacher = teachers[i] if i < len(teachers) else None
                    if teacher == teacher_input:   # ✅ keep only the selected teacher
                        records.append({
                            "StudentID": doc.get("StudentID"),
                            "SubjectCode": subject_codes[i],
                            "Grade": grades[i] if i < len(grades) else None,
                            "Teacher": teacher,
                            "SemesterID": doc.get("SemesterID")
                        })
                    
            df = pd.DataFrame(records)
            #st.table(df)

            if df.empty:
                st.warning("⚠️ No records found for the selected teacher and semester.")
            else:
                # Optional join with Subjects collection to get Subject Description
                subj_map = {}
                for subj in subjectsCollection.find({}):
                    subj_map[subj["_id"]] = subj.get("Description", "")

                #df["Description"] = df["SubjectCodes"].map(subj_map)
                df["SubjectDescription"] = df["SubjectCode"].map(subj_map)

                # Define bins
                bins = [0, 74, 79, 84, 89, 94, 100]
                labels = ["Below 75", "75-79", "80-84", "85-89", "90-94", "95-100"]

                df["GradeRange"] = pd.cut(df["Grade"], bins=bins, labels=labels, include_lowest=True)
                
                # ✅ Mark missing/null grades as "No Grade"
                df["GradeRange"] = df["GradeRange"].cat.add_categories(["No Grade"])
                df["GradeRange"] = df["GradeRange"].fillna("No Grade")

                # Pivot table
                pivot = pd.pivot_table(
                    df,
                    index=["SubjectCode", "SubjectDescription"],
                    columns=["GradeRange"],
                    values="StudentID",
                    aggfunc="count",
                    fill_value=0,
                )

                # Add total
                pivot["Total"] = pivot.sum(axis=1)

                # remove row with zero total
                pivot = pivot[pivot["Total"] > 0]

                # Reorder columns
                ordered_cols = ["95-100", "90-94", "85-89", "80-84", "75-79", "Below 75", "No Grade", "Total"]
                pivot = pivot.reindex(columns=ordered_cols, fill_value=0)

                # Reset index for display
                pivot = pivot.reset_index()

                st.dataframe(pivot)


                # --- Histogram ---
                labels = pivot["SubjectCode"].tolist()

                data_series = [
                    ("95-100", pivot["95-100"].tolist()),
                    ("90-94", pivot["90-94"].tolist()),
                    ("85-89", pivot["85-89"].tolist()),
                    ("80-84", pivot["80-84"].tolist()),
                    ("75-79", pivot["75-79"].tolist()),
                    ("Below 75", pivot["Below 75"].tolist()),
                    ("No Grade", pivot["No Grade"].tolist()),
                ]

                # ✅ Colors
                colors_bar = [
                    "#2ecc71",  # green (95-100)
                    "#27ae60",  # dark green (90-94)
                    "#3498db",  # blue (85-89)
                    "#f1c40f",  # yellow (80-84)
                    "#e67e22",  # orange (75-79)
                    "#e74c3c",  # red (Below 75)
                    "#95a5a6"   # gray (No Grade)
                ]

                x = np.arange(len(labels))         # subject positions
                n_groups = len(data_series)        # 7 ranges
                width = 0.8 / n_groups             # auto width so they fit

                fig, ax = plt.subplots(figsize=(12, 6))

                rects = []
                # Plot each grade range with proper offset and color
                for i, (name, data) in enumerate(data_series):
                    offset = (i - n_groups/2) * width + width/2
                    r = ax.bar(x + offset, data, width, label=name, color=colors_bar[i])
                    rects.append(r)

                # ✅ Labels & title
                ax.set_ylabel("Number of Students")
                ax.set_title("Grade Distribution per Subject")
                ax.set_xticks(x)
                ax.set_xticklabels(labels, rotation=45, ha="right")
                ax.legend(title="Grade Range", bbox_to_anchor=(1.05, 1), loc="upper left")

                # ✅ Add value labels
                for r in rects:
                    ax.bar_label(r, padding=2, fontsize=8)

                fig.tight_layout()
                st.pyplot(fig)

                # Print to PDF
                subtitle = f"Teacher: {teacher_input} | Semester: {semester_input}"
                pdf_buffer = df_to_pdf(pivot, title="Grade Distribution per Subject", subtitle=subtitle)

                st.download_button(
                    label="📥 Download as PDF",
                    data=pdf_buffer,
                    file_name="grade_distribution.pdf",
                    mime="application/pdf",
                )


    #with tab_student_progress_tracker:
    elif tab_index == "Student Progress Tracker":

                
        # Input filters
        filter_type = st.radio("Filter by:", ["Subject", "Course", "YearLevel", "Student ID"])

        if filter_type == "Subject":
            subjects = subjectsCollection.distinct("Description")
            selected_value = st.selectbox("Select Subject", subjects)

        elif filter_type == "Course":
            courses = studentsCollection.distinct("Course")
            selected_value = st.selectbox("Select Course", courses)

        elif filter_type == "YearLevel":
            years = studentsCollection.distinct("YearLevel")
            selected_value = st.selectbox("Select Year Level", years)

        elif filter_type == "Student ID":
            selected_value = st.text_input("Enter Student ID: ")

        if selected_value:

            if filter_type == "YearLevel":
                year_level = selected_value   # <-- parameter

                pipeline = [
                    # --- Step 1: Join grades → students (filter by YearLevel) ---
                    {
                        "$lookup": {
                            "from": "new_students",
                            "localField": "StudentID",
                            "foreignField": "_id",
                            "as": "StudentInfo"
                        }
                    },
                    {"$unwind": "$StudentInfo"},
                    {"$match": {"StudentInfo.YearLevel": year_level}},

                    # --- Step 2: Unwind arrays ---
                    {"$unwind": {"path": "$SubjectCodes", "includeArrayIndex": "idx"}},

                    # --- Step 3: Align subject, grade, teacher ---
                    {
                        "$project": {
                            "StudentID": 1,
                            "SemesterID": 1,
                            "SubjectCode": "$SubjectCodes",
                            "Grade": {"$arrayElemAt": ["$Grades", "$idx"]},
                            "Teacher": {"$arrayElemAt": ["$Teachers", "$idx"]},
                            "Name": "$StudentInfo.Name",
                            "Course": "$StudentInfo.Course",
                            "YearLevel": "$StudentInfo.YearLevel"
                        }
                    },

                    # --- Step 4: Lookup subject units ---
                    {
                        "$lookup": {
                            "from": "new_subjects",
                            "localField": "SubjectCode",
                            "foreignField": "_id",
                            "as": "SubjectInfo"
                        }
                    },
                    {"$unwind": "$SubjectInfo"},

                    # --- Step 5: Map % grade → 4.0 scale GPA ---
                    {
                        "$addFields": {
                            "GPApoint": {
                                "$switch": {
                                    "branches": [
                                        {"case": {"$gte": ["$Grade", 97]}, "then": 4.0},
                                        {"case": {"$gte": ["$Grade", 93]}, "then": 4.0},
                                        {"case": {"$gte": ["$Grade", 90]}, "then": 3.7},
                                        {"case": {"$gte": ["$Grade", 87]}, "then": 3.3},
                                        {"case": {"$gte": ["$Grade", 83]}, "then": 3.0},
                                        {"case": {"$gte": ["$Grade", 80]}, "then": 2.7},
                                        {"case": {"$gte": ["$Grade", 77]}, "then": 2.3},
                                        {"case": {"$gte": ["$Grade", 73]}, "then": 2.0},
                                        {"case": {"$gte": ["$Grade", 70]}, "then": 1.7},
                                        {"case": {"$gte": ["$Grade", 67]}, "then": 1.3},
                                        {"case": {"$gte": ["$Grade", 65]}, "then": 1.0}
                                    ],
                                    "default": 0.0
                                }
                            }
                        }
                    },

                    # --- Step 6: Weighted GPA ---
                    {
                        "$addFields": {
                            "weightedGrade": {"$multiply": ["$GPApoint", "$SubjectInfo.Units"]},
                            "units": "$SubjectInfo.Units"
                        }
                    },

                    # --- Step 7: GPA per student per semester ---
                    {
                        "$group": {
                            "_id": {
                                "StudentID": "$StudentID",
                                "Name": "$Name",
                                "Course": "$Course",
                                "YearLevel": "$YearLevel",
                                "SemesterID": "$SemesterID"
                            },
                            "totalWeighted": {"$sum": "$weightedGrade"},
                            "totalUnits": {"$sum": "$units"}
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "StudentID": "$_id.StudentID",
                            "Name": "$_id.Name",
                            "Course": "$_id.Course",
                            "YearLevel": "$_id.YearLevel",
                            "SemesterID": "$_id.SemesterID",
                            "GPA": {"$round": [{"$divide": ["$totalWeighted", "$totalUnits"]}, 2]}
                        }
                    },

                    # --- Step 8: Collect semester GPAs ---
                    {
                        "$group": {
                            "_id": {
                                "StudentID": "$StudentID",
                                "Name": "$Name",
                                "Course": "$Course",
                                "YearLevel": "$YearLevel"
                            },
                            "semesters": {
                                "$push": {
                                    "k": {"$concat": [{"$toString": "$SemesterID"}, "_GPA"]},
                                    "v": "$GPA"
                                }
                            }
                        }
                    },

                    # --- Step 9: Sort semesters ---
                    {
                        "$addFields": {
                            "semesters": {
                                "$sortArray": {"input": "$semesters", "sortBy": {"k": 1}}
                            }
                        }
                    },
                    {"$addFields": {"semesterMap": {"$arrayToObject": "$semesters"}}},

                    # --- Step 10: Trend (compare first vs last GPA) ---
                    {
                        "$addFields": {
                            "sortedGPAs": {
                                "$map": {
                                    "input": {"$objectToArray": "$semesterMap"},
                                    "as": "sem",
                                    "in": "$$sem.v"
                                }
                            }
                        }
                    },
                    {
                        "$addFields": {
                            "Overall Trend": {
                                "$switch": {
                                    "branches": [
                                        {
                                            "case": {"$lt": [
                                                {"$arrayElemAt": ["$sortedGPAs", 0]},
                                                {"$arrayElemAt": ["$sortedGPAs", -1]}
                                            ]},
                                            "then": "📈 Improving"
                                        },
                                        {
                                            "case": {"$gt": [
                                                {"$arrayElemAt": ["$sortedGPAs", 0]},
                                                {"$arrayElemAt": ["$sortedGPAs", -1]}
                                            ]},
                                            "then": "📉 Declining"
                                        }
                                    ],
                                    "default": "➡ Stable"
                                }
                            }
                        }
                    },

                    # --- Step 11: Flatten output ---
                    {
                        "$replaceRoot": {
                            "newRoot": {
                                "$mergeObjects": [
                                    {
                                        "StudentID": "$_id.StudentID",
                                        "Name": "$_id.Name",
                                        "Course": "$_id.Course",
                                        "YearLevel": "$_id.YearLevel"
                                    },
                                    "$semesterMap",
                                    {"Overall Trend": "$Overall Trend"}
                                ]
                            }
                        }
                    },

                    # --- Step 12: Sort final results ---
                    {"$sort": {"StudentID": 1}}
                ]


                st.subheader("📑 Progress Tracker by Year / Level")

                with st.spinner("Loading data..."):
                    data = list(gradesCollection.aggregate(pipeline))
                    st.dataframe(data)
            
            if filter_type == "Student ID":
                student_id = int(selected_value)   # <-- parameter
            
                pipeline = [
                    # Step 1: Filter by StudentID
                    {"$match": {"StudentID": student_id}},

                    # Step 2: Join with students
                    {
                        "$lookup": {
                            "from": "new_students",
                            "localField": "StudentID",
                            "foreignField": "_id",   # adjust if it's actually "_id"
                            "as": "StudentInfo"
                        }
                    },
                    {"$unwind": "$StudentInfo"},

                    # Step 3: Unwind arrays
                    {"$unwind": {"path": "$SubjectCodes", "includeArrayIndex": "idx"}},

                    # Step 4: Project aligned Grade
                    {
                        "$project": {
                            "StudentID": 1,
                            "SemesterID": 1,
                            "SubjectCode": "$SubjectCodes",
                            "Grade": {"$arrayElemAt": ["$Grades", "$idx"]},
                            "Name": "$StudentInfo.Name"
                        }
                    },

                    # Step 5: Join with subjects
                    {
                        "$lookup": {
                            "from": "new_subjects",
                            "localField": "SubjectCode",
                            "foreignField": "_id",
                            "as": "SubjectInfo"
                        }
                    },
                    {"$unwind": "$SubjectInfo"},

                    # Step 6: Join with semesters
                    {
                        "$lookup": {
                            "from": "new_semesters",
                            "localField": "SemesterID",
                            "foreignField": "_id",
                            "as": "SemesterInfo"
                        }
                    },
                    {"$unwind": {"path": "$SemesterInfo", "preserveNullAndEmptyArrays": True}},

                    # Step 7: Convert raw % → GPA points
                    {
                        "$addFields": {
                            "GPApoint": {
                                "$switch": {
                                    "branches": [
                                        {"case": {"$gte": ["$Grade", 97]}, "then": 4.0},
                                        {"case": {"$gte": ["$Grade", 93]}, "then": 4.0},
                                        {"case": {"$gte": ["$Grade", 90]}, "then": 3.7},
                                        {"case": {"$gte": ["$Grade", 87]}, "then": 3.3},
                                        {"case": {"$gte": ["$Grade", 83]}, "then": 3.0},
                                        {"case": {"$gte": ["$Grade", 80]}, "then": 2.7},
                                        {"case": {"$gte": ["$Grade", 77]}, "then": 2.3},
                                        {"case": {"$gte": ["$Grade", 73]}, "then": 2.0},
                                        {"case": {"$gte": ["$Grade", 70]}, "then": 1.7},
                                        {"case": {"$gte": ["$Grade", 67]}, "then": 1.3},
                                        {"case": {"$gte": ["$Grade", 65]}, "then": 1.0}
                                    ],
                                    "default": 0.0
                                }
                            },
                            "Units": "$SubjectInfo.Units"
                        }
                    },

                    # Step 8: Add weighted GPA contribution
                    {
                        "$addFields": {
                            "weightedGrade": {"$multiply": ["$GPApoint", "$Units"]}
                        }
                    },

                    # Step 9: Compute Semester GPA
                    {
                        "$group": {
                            "_id": {
                                "StudentID": "$StudentID",
                                "SemesterID": "$SemesterID",
                                "SemesterName": "$SemesterInfo.SemesterName",
                                "SchoolYear": "$SemesterInfo.SchoolYear",
                                "Name": "$Name"
                            },
                            "totalWeighted": {"$sum": "$weightedGrade"},
                            "totalUnits": {"$sum": "$Units"},
                            "subjects": {
                                "$push": {
                                    "Units": "$Units",
                                    "Grade": "$Grade",
                                    "GPApoint": "$GPApoint"
                                }
                            }
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "StudentID": "$_id.StudentID",
                            "Name": "$_id.Name",
                            "SemesterID": "$_id.SemesterID",
                            "SemesterName": "$_id.SemesterName",
                            "SchoolYear": "$_id.SchoolYear",
                            "SemesterGPA": {"$round": [{"$divide": ["$totalWeighted", "$totalUnits"]}, 2]},
                            "subjects": 1
                        }
                    },

                    # Step 10: Unwind subjects back to rows
                    {"$unwind": "$subjects"},
                    {
                        "$project": {
                            "StudentID": 1,
                            "Name": 1,
                            "SemesterID": 1,
                            "SemesterName": 1,
                            "SchoolYear": 1,
                            "Units": "$subjects.Units",
                            "Grade": "$subjects.Grade",
                            "SemesterGPA": 1
                        }
                    },

                    {"$sort": {"SemesterID": 1}}
                ]

                results = list(gradesCollection.aggregate(pipeline))

                import pandas as pd
                df = pd.DataFrame(results, columns=[
                    "StudentID", "Name", "SemesterID", "SchoolYear", "Units", "Grade", "SemesterGPA"
                ])
                st.dataframe(df)

            student_filter = {}
            student_map = {s["_id"]: s for s in studentsCollection.find(student_filter)}
                

            if filter_type == "Subject":
                
                subj_doc = subjectsCollection.find_one({"Description": selected_value})
                subject_code = subj_doc["_id"] if subj_doc else None
                if subject_code:
                    data = list(gradesCollection.find({"SubjectCodes": subject_code}))
                else:
                    data = []

                # Normalize arrays
            
                records = []
                for doc in data:
                    subject_codes = doc.get("SubjectCodes", [])
                    grades = doc.get("Grades", [])
                    for i in range(len(subject_codes)):
                        records.append({
                            "StudentID": doc.get("StudentID"),
                            "SubjectCode": subject_codes[i],
                            "Grade": grades[i] if i < len(grades) else None,
                            "SemesterID": doc.get("SemesterID")
                        })

                df = pd.DataFrame(records)

                if df.empty:
                    st.warning("⚠️ No records found.")
                else:
                    # --------------------------
                    # PROCESS DATA
                    # --------------------------
                    # Compute average grade per student per semester
                    avg_per_sem = df.groupby(["StudentID", "SemesterID"])["Grade"].mean().reset_index()

                    # Pivot: one row per student, semesters as columns
                    pivot = avg_per_sem.pivot(index="StudentID", columns="SemesterID", values="Grade").reset_index()

                    # Merge with student names
                    pivot["Name"] = pivot["StudentID"].map(lambda x: student_map.get(x, {}).get("Name", "Unknown"))

                    # Compute trend (compare first vs last semester grade)
                    with st.spinner("Loading data..."):
                        trends = []
                        for _, row in pivot.iterrows():
                            grades_series = row.drop(["StudentID", "Name"]).dropna()
                            if len(grades_series) >= 2:
                                first = grades_series.iloc[0]
                                last = grades_series.iloc[-1]
                                if last > first:
                                    trends.append("↑ Improving")
                                elif last < first:
                                    trends.append("↓ Declining")
                                else:
                                    trends.append("→ Stable")
                            else:
                                trends.append("–")
                    pivot["Overall Trend"] = trends

                    # Move Name next to StudentID
                    cols = ["StudentID", "Name"] + [c for c in pivot.columns if c not in ["StudentID", "Name", "Overall Trend"]] + ["Overall Trend"]
                    result = pivot[cols]

                    # --------------------------
                    # DISPLAY
                    # --------------------------
                    st.subheader("📑 Student Grade Trends by Semester")
                    st.dataframe(result)
                    
            elif filter_type == "Course":
                
                data = list(gradesCollection.find({"StudentID": {"$in": list(student_map.keys())}}))

                records = []
                for doc in data:
                    subject_codes = doc.get("SubjectCodes", [])
                    grades = doc.get("Grades", [])
                    for i in range(len(subject_codes)):
                        records.append({
                            "StudentID": doc.get("StudentID"),
                            "SubjectCode": subject_codes[i],
                            "Grade": grades[i] if i < len(grades) else None,
                            "SemesterID": doc.get("SemesterID")
                        })

                df = pd.DataFrame(records)

                if df.empty:
                    st.warning("⚠️ No records found.")
                else:
                    # --------------------------
                    # PROCESS DATA
                    # --------------------------
                    # Compute average grade per student per semester
                    avg_per_sem = df.groupby(["StudentID", "SemesterID"])["Grade"].mean().reset_index()

                    # Pivot: one row per student, semesters as columns
                    pivot = avg_per_sem.pivot(index="StudentID", columns="SemesterID", values="Grade").reset_index()

                    # Merge with student names
                    pivot["Name"] = pivot["StudentID"].map(lambda x: student_map.get(x, {}).get("Name", "Unknown"))

                    # Compute trend (compare first vs last semester grade)
                    with st.spinner("Loading data..."):
                        trends = []
                        for _, row in pivot.iterrows():
                            grades_series = row.drop(["StudentID", "Name"]).dropna()
                            if len(grades_series) >= 2:
                                first = grades_series.iloc[0]
                                last = grades_series.iloc[-1]
                                if last > first:
                                    trends.append("↑ Improving")
                                elif last < first:
                                    trends.append("↓ Declining")
                                else:
                                    trends.append("→ Stable")
                            else:
                                trends.append("–")
                    pivot["Overall Trend"] = trends

                    # Move Name next to StudentID
                    cols = ["StudentID", "Name"] + [c for c in pivot.columns if c not in ["StudentID", "Name", "Overall Trend"]] + ["Overall Trend"]
                    result = pivot[cols]

                    # --------------------------
                    # DISPLAY
                    # --------------------------
                    st.subheader("📑 Student Grade Trends by Semester")
                    st.dataframe(result)
                    
        # st.subheader("Student Progress Tracker")
            
        # # # Input filters
        # filter_type = st.radio("Filter by:", ["Subject", "Course", "YearLevel"])

        # if filter_type == "Subject":
        #     subjects = subjectsCollection.distinct("Description")
        #     selected_value = st.selectbox("Select Subject", subjects)

        # elif filter_type == "Course":
        #     courses = studentsCollection.distinct("Course")
        #     selected_value = st.selectbox("Select Course", courses)

        # else:  # YearLevel
        #     years = studentsCollection.distinct("YearLevel")
        #     selected_value = st.selectbox("Select Year Level", years)



        # if selected_value:
        #     # Build student filter if Course or YearLevel
        #     student_filter = {}
        #     if filter_type == "Course":
        #         student_filter["Course"] = selected_value
        #     elif filter_type == "YearLevel":
        #         student_filter["YearLevel"] = selected_value

        #     student_map = {s["_id"]: s for s in studentsCollection.find(student_filter)}

        #     # Query Grades
        #     if filter_type == "Subject":
        #         subj_doc = subjectsCollection.find_one({"Description": selected_value})
        #         subject_code = subj_doc["_id"] if subj_doc else None
        #         if subject_code:
        #             data = list(gradesCollection.find({"SubjectCodes": subject_code}))
        #         else:
        #             data = []
        #     else:
        #         data = list(gradesCollection.find({"StudentID": {"$in": list(student_map.keys())}}))

        #     # Normalize arrays
        #     records = []
        #     for doc in data:
        #         subject_codes = doc.get("SubjectCodes", [])
        #         grades = doc.get("Grades", [])
        #         for i in range(len(subject_codes)):
        #             records.append({
        #                 "StudentID": doc.get("StudentID"),
        #                 "SubjectCode": subject_codes[i],
        #                 "Grade": grades[i] if i < len(grades) else None,
        #                 "SemesterID": doc.get("SemesterID")
        #             })

        #     df = pd.DataFrame(records)

        #     if df.empty:
        #         st.warning("⚠️ No records found.")
        #     else:
        #         # --------------------------
        #         # PROCESS DATA
        #         # --------------------------
        #         # Compute average grade per student per semester
        #         avg_per_sem = df.groupby(["StudentID", "SemesterID"])["Grade"].mean().reset_index()

        #         # Pivot: one row per student, semesters as columns
        #         pivot = avg_per_sem.pivot(index="StudentID", columns="SemesterID", values="Grade").reset_index()

        #         # Merge with student names
        #         pivot["Name"] = pivot["StudentID"].map(lambda x: student_map.get(x, {}).get("Name", "Unknown"))

        #         # Compute trend (compare first vs last semester grade)
        #         trends = []
        #         for _, row in pivot.iterrows():
        #             grades_series = row.drop(["StudentID", "Name"]).dropna()
        #             if len(grades_series) >= 2:
        #                 first = grades_series.iloc[0]
        #                 last = grades_series.iloc[-1]
        #                 if last > first:
        #                     trends.append("↑ Improving")
        #                 elif last < first:
        #                     trends.append("↓ Declining")
        #                 else:
        #                     trends.append("→ Stable")
        #             else:
        #                 trends.append("–")
        #         pivot["Overall Trend"] = trends

        #         # Move Name next to StudentID
        #         cols = ["StudentID", "Name"] + [c for c in pivot.columns if c not in ["StudentID", "Name", "Overall Trend"]] + ["Overall Trend"]
        #         result = pivot[cols]

        #         # --------------------------
        #         # DISPLAY
        #         # --------------------------
        #         st.subheader("📑 Student Grade Trends by Semester")
        #         st.dataframe(result)


        #         # --- PDF Export ---
        #         subtitle = f"Filter: {filter_type} = {selected_value}"
        #         pdf_buffer = df_to_pdf_tracker(result, title="📑 Student Grade Trends by Semester", subtitle=subtitle)

        #         st.download_button(
        #             label="📥 Download Report as PDF",
        #             data=pdf_buffer,
        #             file_name="student_progress.pdf",
        #             mime="application/pdf",
        #         )






    #with tab_subject_difficulty_heatmap:
    elif tab_index == "Subject Difficulty Heatmap":
        
        teacher_input = st.session_state.session_teacher

        if teacher_input:
            # -------------------------------
            # Query Grades for selected teacher
            # -------------------------------
            data = list(gradesCollection.find({"Teachers": teacher_input}))

            pipeline = [
                {"$match": {"Teachers": teacher_input}},  # filter teacher early

                # Turn each Subject/Grade/Teacher into a separate document
                {"$unwind": {"path": "$SubjectCodes", "includeArrayIndex": "idx"}},
                {"$unwind": {"path": "$Grades", "includeArrayIndex": "gidx"}},
                {"$unwind": {"path": "$Teachers", "includeArrayIndex": "tidx"}},

                # Only keep aligned subject-grade-teacher triples
                {"$match": {"$expr": {"$eq": ["$idx", "$tidx"]}}},
                {"$match": {"$expr": {"$eq": ["$idx", "$gidx"]}}},
                {"$match": {"Teachers": teacher_input}},

                # Project clean fields
                {"$project": {
                    "_id": 0,
                    "StudentID": 1,
                    "CourseCode": "$SubjectCodes",
                    "Grade": "$Grades",
                    "Teacher": "$Teachers"
                }}
            ]

            with st.spinner("Loading to dataframe..."):
                data = list(gradesCollection.aggregate(pipeline))
                df = pd.DataFrame(data)


            if df.empty:
                st.warning("⚠️ No records found for this teacher.")
            else:
                # -------------------------------
                # Map course descriptions
                # -------------------------------
                subj_map = {s["_id"]: s.get("Description", "") for s in subjectsCollection.find({})}
                df["CourseDescription"] = df["CourseCode"].map(subj_map)

                # -------------------------------
                # Fail / Dropout Calculation
                # -------------------------------
                df["Success"] = df["Grade"].apply(lambda x: 1 if (x is not None and x >= 75) else 0)
                df["Fail"] = df["Grade"].apply(lambda x: 1 if (x is not None and x < 75) else 0)
                #df["Dropout"] = df["Grade"].apply(lambda x: 1 if x is None else 0)
                #df["Dropout"] = df["Grade"].apply(lambda g: sum(pd.isnull(x) for x in g)).sum()
                df["Dropout"] = df["Success"] - df["Fail"]

                summary = df.groupby(["CourseCode", "CourseDescription"]).agg(
                    total=("StudentID", "count"),
                    success=("Success", "sum"),
                    fail=("Fail", "sum"),
                    dropout=("Dropout", "sum")
                ).reset_index()

                summary["Success Rate (%)"] = (summary["success"] / summary["total"] * 100).round(2)
                summary["Fail Rate (%)"] = (summary["fail"] / summary["total"] * 100).round(2)
                summary["Dropout Rate (%)"] = (summary["dropout"] / summary["total"] * 100).round(2)

                # -------------------------------
                # Difficulty Level classification
                # -------------------------------
                def classify_difficulty(rate):
                    if rate >= 40:
                        return "Very Hard"
                    elif rate >= 25:
                        return "Hard"
                    elif rate >= 10:
                        return "Moderate"
                    else:
                        return "Easy"

                summary["Difficulty Level"] = summary["Fail Rate (%)"].apply(classify_difficulty)

                # -------------------------------
                # Final Table
                # -------------------------------
                result = summary[[
                    "CourseCode", "CourseDescription", "Success Rate (%)",  "Fail Rate (%)", "Dropout Rate (%)", "Difficulty Level"
                ]]

                st.subheader(f"📑 Performance Summary for {teacher_input}")
                with st.spinner("Rendering table..."):
                    st.table(result)

                st.info("Difficulty Level is determined through the Fail Rate. If less than 10, then Easy, if 10-24 thn Moderate, if 25-39 then Hard, if 40 above then it is Difficult")

                # PDF Export button
                pdf_buffer = generate_pdf_heatmap(result, teacher_input)
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_buffer,
                    file_name=f"performance_summary_{teacher_input}.pdf",
                    mime="application/pdf"
                )
                





    elif tab_index == "Intervention Candidates List":
        
        teacher_input = st.session_state.session_teacher
        
        if teacher_input:
            # -------------------------------
            # Query Grades for this teacher
            # -------------------------------
            data = list(gradesCollection.find({"Teachers": teacher_input}))

            with st.spinner("Loading data..."):
                records = []
                for doc in data:
                    student_id = doc.get("StudentID")
                    subject_codes = doc.get("SubjectCodes", [])
                    grades = doc.get("Grades", [])
                    teachers = doc.get("Teachers", [])
                    semester = doc.get("SemesterID")

                    for i in range(len(subject_codes)):
                        if teachers[i] == teacher_input:  # keep only subjects taught by this teacher
                            
                            records.append({
                                "StudentID": student_id,
                                "SubjectCode": subject_codes[i],
                                "CurrentGrade": grades[i] if i < len(grades) else None,
                                "Semester": semester
                            })

                df = pd.DataFrame(records)

            if df.empty:
                st.warning("⚠️ No student records found for this teacher.")
            else:
                # -------------------------------
                # Map student names
                # -------------------------------
                student_map = {s["_id"]: s.get("Name", "") for s in studentsCollection.find({})}
                df["StudentName"] = df["StudentID"].map(student_map)

                # Map subject descriptions
                subj_map = {s["_id"]: s.get("Description", "") for s in subjectsCollection.find({})}
                df["SubjectDescription"] = df["SubjectCode"].map(subj_map)

                # -------------------------------
                # Risk Flag
                # -------------------------------
                def risk_flag(grade):
                    if pd.isna(grade) or grade == "": 
                        return "Missing Grade"
                    elif grade < 75:
                        return "At Risk (<75)"
                    else:
                        return "Safe"

                df["RiskFlag"] = df["CurrentGrade"].apply(risk_flag)

                # -------------------------------
                # Final table
                # -------------------------------
                result = df[[
                    "StudentID", "StudentName", "SubjectCode", "SubjectDescription", "Semester", "CurrentGrade", "RiskFlag"
                ]]

                result_unsafe = result[result["RiskFlag"] != "Safe"]

                with st.spinner("Loading data..."):
                    st.subheader(f"📑 Student Performance for {teacher_input}")
                    st.dataframe(result_unsafe)

                st.info("List only show students and their respective subjects with RiskFlag of At Risk (<75) and Missing Grades. ")

                if not result_unsafe.empty:
                    pdf_buffer = generate_pdf_intervention(result_unsafe, teacher_input)
                    st.download_button(
                        label="📥 Download Intervention List (PDF)",
                        data=pdf_buffer,
                        file_name=f"intervention_candidates_{teacher_input}.pdf",
                        mime="application/pdf"
                    )





    elif tab_index == "Grade Submission Status":
        st.write("tab_grade_submission_status")

        teacher_input = st.session_state.session_teacher

        if teacher_input:
            # -------------------------------
            # Query Grades for selected teacher
            # -------------------------------
            data = list(gradesCollection.find({"Teachers": teacher_input}))

            records = []
            for doc in data:
                student_id = doc.get("StudentID")
                subject_codes = doc.get("SubjectCodes", [])
                grades = doc.get("Grades", [])
                teachers = doc.get("Teachers", [])

                for i in range(len(subject_codes)):
                    if teachers[i] == teacher_input:  # Only subjects taught by this teacher
                        records.append({
                            "StudentID": student_id,
                            "SubjectCode": subject_codes[i],
                            "Grade": grades[i] if i < len(grades) else None,
                            "SemesterID": doc.get("SemesterID") 
                        })

            df = pd.DataFrame(records)

            if df.empty:
                st.warning("⚠️ No student records found for this teacher.")
            else:
                # -------------------------------
                # Map subject descriptions
                # -------------------------------
                subj_map = {s["_id"]: s.get("Description", "") for s in subjectsCollection.find({})}
                df["SubjectDescription"] = df["SubjectCode"].map(subj_map)

                # -------------------------------
                # Submission stats
                # -------------------------------
                #df["Submitted"] = df["Grade"].apply(lambda x: 1 if x is not None else 0)
                df["Submitted"] = df["Grade"].apply(
                    lambda x: 1 if pd.notnull(x) and x != "" else 0
                )

                summary = df.groupby(
                    ["SemesterID", "SubjectCode", "SubjectDescription"]
                ).agg(
                    TotalStudents=("StudentID", "count"),
                    SubmittedGrades=("Submitted", "sum")
                ).reset_index()

                summary["NoGrades"] = summary["TotalStudents"] - summary["SubmittedGrades"]

                summary["SubmissionRate (%)"] = (summary["SubmittedGrades"] / summary["TotalStudents"] * 100).round(2)

                # -------------------------------
                # Final table
                # -------------------------------
                # result = summary[[
                #     "SubjectCode", "SubjectDescription", "SemesterID", "SubmittedGrades", "TotalStudents", "SubmissionRate (%)"
                # ]]
                result = summary[[
                    "SemesterID", "SubjectCode", "SubjectDescription",
                    "SubmittedGrades", "NoGrades", "TotalStudents", "SubmissionRate (%)"
                ]]

                st.subheader(f"📑 Grade Submission Summary for {teacher_input}")
                st.dataframe(result)

                st.info("Page shows list of subjects, under the selected teacher, together with its submission rate. Teacher may need to revisit subjects with high number of no grades or submission rate not reaching 100%.")

                if not result.empty:
                    pdf_buffer = generate_pdf_submission(result, teacher_input)
                    st.download_button(
                        label="📥 Download Grade Submission Report (PDF)",
                        data=pdf_buffer,
                        file_name=f"grade_submission_{teacher_input}.pdf",
                        mime="application/pdf"
                    )






    elif tab_index == "Custom Query Builder":
        
            
        # Checkboxes for filters
        filter_subject = st.checkbox("Filter by SubjectCode")
        filter_teacher = st.checkbox("Filter by TeacherName")
        filter_student = st.checkbox("Filter by StudentName")

        query = {}

        # Input fields depending on selected filters
        if filter_subject:
            subject_code = st.text_input("Enter Subject Code")
            if subject_code:
                #query["SubjectCodes"] = subject_code
                query["SubjectCodes"] = {"$in": [subject_code]}

        if filter_teacher:
            teacher_name = st.text_input("Enter Teacher Name")
            if teacher_name:
                query["Teachers"] = teacher_name

        if filter_student:
            student_name = st.text_input("Enter Student Name")
            if student_name:
                student_doc = studentsCollection.find_one({"Name": {"$regex": student_name, "$options": "i"}})
                if student_doc:
                    query["StudentID"] = student_doc["_id"]
                else:
                    st.warning("⚠️ No student found with that name.")

        # -----------------------------
        # Query Execution
        # -----------------------------
        if st.button("🔍 Search"):

            if not (filter_subject or filter_teacher or filter_student):
                st.warning("⚠️ Please select at least one filter before searching.")
            elif not query:
                st.info("ℹ️ No filter value entered yet.")
            else:
                
                with st.spinner("⏳ Fetching records..."):
                    data = list(gradesCollection.find(query))
                records = []

                with st.spinner("⏳ Building table to display data. One moment please..."):
                    for doc in data:
                        student_id = doc.get("StudentID")
                        subject_codes = doc.get("SubjectCodes", [])
                        grades = doc.get("Grades", [])
                        teachers = doc.get("Teachers", [])
                        semester_id = doc.get("SemesterID")   

                        # lookup student name
                        student_doc = studentsCollection.find_one({"_id": student_id})
                        student_name = student_doc["Name"] if student_doc else "Unknown"

                        # CASE 1: Both SubjectCode + Teacher filter applied
                        if filter_subject and subject_code and filter_teacher and teacher_name:
                            for i, subj_code in enumerate(subject_codes):
                                teacher = teachers[i] if i < len(teachers) else None
                                if subj_code == subject_code and teacher == teacher_name:
                                    grade = grades[i] if i < len(grades) else None
                                    subj_doc = subjectsCollection.find_one({"_id": subj_code})
                                    subj_desc = subj_doc["Description"] if subj_doc else "Unknown"

                                    records.append({
                                        "StudentID": student_id,
                                        "StudentName": student_name,
                                        "SubjectCode": subj_code,
                                        "SubjectDescription": subj_desc,
                                        "Teacher": teacher,
                                        "Grade": grade,
                                        "SemesterID": semester_id
                                    })

                        # CASE 2: Only Subject filter applied
                        elif filter_subject and subject_code:
                            if subject_code in subject_codes:
                                idx = subject_codes.index(subject_code)
                                grade = grades[idx] if idx < len(grades) else None
                                teacher = teachers[idx] if idx < len(teachers) else None
                                subj_doc = subjectsCollection.find_one({"_id": subject_code})
                                subj_desc = subj_doc["Description"] if subj_doc else "Unknown"

                                records.append({
                                    "StudentID": student_id,
                                    "StudentName": student_name,
                                    "SubjectCode": subject_code,
                                    "SubjectDescription": subj_desc,
                                    "Teacher": teacher,
                                    "Grade": grade,
                                    "SemesterID": semester_id
                                })

                        # CASE 3: Only Teacher filter applied
                        elif filter_teacher and teacher_name:
                            for i, teacher in enumerate(teachers):
                                if teacher == teacher_name:
                                    subj_code = subject_codes[i] if i < len(subject_codes) else None
                                    grade = grades[i] if i < len(grades) else None
                                    subj_doc = subjectsCollection.find_one({"_id": subj_code})
                                    subj_desc = subj_doc["Description"] if subj_doc else "Unknown"

                                    records.append({
                                        "StudentID": student_id,
                                        "StudentName": student_name,
                                        "SubjectCode": subj_code,
                                        "SubjectDescription": subj_desc,
                                        "Teacher": teacher,
                                        "Grade": grade,
                                        "SemesterID": semester_id
                                    })

                        # CASE 4: No subject/teacher filter → show all
                        else:
                            for i, subj_code in enumerate(subject_codes):
                                grade = grades[i] if i < len(grades) else None
                                teacher = teachers[i] if i < len(teachers) else None
                                subj_doc = subjectsCollection.find_one({"_id": subj_code})
                                subj_desc = subj_doc["Description"] if subj_doc else "Unknown"

                                records.append({
                                    "StudentID": student_id,
                                    "StudentName": student_name,
                                    "SubjectCode": subj_code,
                                    "SubjectDescription": subj_desc,
                                    "Teacher": teacher,
                                    "Grade": grade,
                                    "SemesterID": semester_id
                                })

                                
                    df = pd.DataFrame(records)

                    if df.empty:
                        st.warning("⚠️ No records found.")
                    else:
                        st.dataframe(df)



    elif tab_index == "Student Grade Analytics":
        
        
        teacher_name = st.session_state.session_teacher

        if teacher_name:
            with st.spinner("⏳ Fetching teachers subjects..."):
                subjects = faculty_get_teacher_subjects_with_semester(teacher_name)

            #st.write(subjects)

            if not subjects:
                st.warning(f"No subjects found for teacher: {teacher_name}")
            else:
                df = pd.DataFrame(subjects)
                st.success(f"Found {len(df)} subject(s) taught by {teacher_name}")
                
                # Optional: Show as radio box
                subject_list = [
                    f"{row['SubjectCode']} ({row['Semester']} - {row['SchoolYear']})"
                    for _, row in df.iterrows()
                ]

                # Create a mapping from label to ID or full row
                label_to_row = {
                    label: row
                    for label, (_, row) in zip(subject_list, df.iterrows())
                }

                selectSubjectName = ""
                selectedSubject = st.radio("Select a subject + semester:", subject_list)

                if selectedSubject:
                    st.success(f"You selected: {selectedSubject}")

                    #selectSubjectName = label_to_row[selectedSubject].SubjectCode
                    selected_row = label_to_row[selectedSubject]
                    selectSubjectCode = selected_row.SubjectCode
                    selectSemester = selected_row.Semester
                    selectSchoolYear = selected_row.SchoolYear

                    semester_obj = semestersCollection.find_one({
                        "Semester": selectSemester,      # e.g., "1st Semester"
                        "SchoolYear": selectSchoolYear   # e.g., "2025-2026"
                    })

                    if semester_obj:
                        semester_id = semester_obj["_id"]
                        #st.write(f"Found Semester ID: {semester_id}")
                    #else:
                        #st.warning(f"No semester found for {selectSemester} - {selectSchoolYear}")
                                
                    #st.success(f"Semester = {selectSemester}; Year = {selectSchoolYear  }")
                
                studentList = faculty_get_student_grades_by_subject_teacher(selectSubjectCode, teacher_name, semester_id)

                if studentList.empty:
                    st.warning(f"No students found for teacher: {teacher_name} for subject {selectedSubject}")
                else:
                    ordered_columns = ['_id', 'Name', 'Course', "YearLevel", 'Grade', 'Status']
                    df = studentList[ordered_columns].rename(columns={"_id": "StudentID"})
                    df = df.reset_index(drop=True)
                    styled_df = df.style.applymap(faculty_highlight_low_grades, subset=['Grade'])

                    with st.spinner("⏳ Processing student records..."):
                        st.dataframe(styled_df)


                    # get summary
                    highest_grade = df['Grade'].max()
                    lowest_grade = df['Grade'].min()
                    mean_grade = df['Grade'].mean()
                    median_grade = df['Grade'].median()

                    df_summary = pd.DataFrame(columns=["Mean", "Median", "Highest", "Lowest"])
                    new_row = pd.DataFrame([{"Mean" : mean_grade, "Median": median_grade, "Highest": highest_grade, "Lowest" : lowest_grade}])

                    # Insert at index 0
                    df_summary = pd.concat([new_row, df_summary], ignore_index=True)
                    styled_df_summary = df_summary.style.format({'Mean': '{:.2f}', 'Median': '{:.2f}', 'Highest': '{:.2f}', 'Lowest': '{:.2f}'})
                    st.dataframe(styled_df_summary)


                    # result set for graph1
                    render_bar_graph_grades_count()
                    
                    # result set for graph2
                    render_bar_graph_passing_count()



    elif tab_index == "Logout":
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()


    




