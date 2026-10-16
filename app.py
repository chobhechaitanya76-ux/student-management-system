
import streamlit as st
import json
import os

FILE = "students.json"


class Node:
    def __init__(self, student):
        self.student = student
        self.next = None


class StudentLinkedList:
    def __init__(self):
        self.head = None

    def add(self, student):
        if self.search(student["roll"]):
            return False
        node = Node(student)
        if not self.head:
            self.head = node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = node
        return True

    def all(self):
        result = []
        current = self.head
        while current:
            result.append(current.student)
            current = current.next
        return result

    def search(self, roll):
        current = self.head
        while current:
            if current.student["roll"] == str(roll):
                return current.student
            current = current.next
        return None

    def delete(self, roll):
        current = self.head
        previous = None
        while current:
            if current.student["roll"] == str(roll):
                if previous:
                    previous.next = current.next
                else:
                    self.head = current.next
                return True
            previous = current
            current = current.next
        return False

    def update(self, roll, name, course, marks):
        student = self.search(roll)
        if student:
            student["name"] = name
            student["course"] = course
            student["marks"] = marks
            return True
        return False


def load_students():
    data = []
    if os.path.exists(FILE):
        try:
            with open(FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            data = []
    linked = StudentLinkedList()
    for student in data:
        linked.add(student)
    return linked


def save_students():
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(students.all(), f, indent=2)


st.set_page_config(page_title="Student Management System", page_icon="🎓", layout="wide")
students = load_students()

st.title("🎓 Student Management System")
st.caption("Python • Singly Linked List • JSON Storage")

menu = st.sidebar.radio(
    "Choose Operation",
    ["Dashboard", "Add Student", "View Students",
     "Search Student", "Update Student", "Delete Student"]
)

records = students.all()

if menu == "Dashboard":
    st.subheader("Dashboard")
    a, b, c = st.columns(3)
    a.metric("Total Students", len(records))
    b.metric("Average Marks",
             f"{sum(s['marks'] for s in records) / len(records):.1f}"
             if records else "0")
    c.metric("Courses", len(set(s["course"] for s in records)))
    st.info("Use the sidebar to add, search, update or delete students.")
    if records:
        st.dataframe(records, use_container_width=True)

elif menu == "Add Student":
    st.subheader("➕ Add New Student")
    with st.form("add_form", clear_on_submit=True):
        roll = st.text_input("Roll Number")
        name = st.text_input("Student Name")
        course = st.text_input("Course")
        marks = st.number_input("Marks", min_value=0.0, max_value=100.0, step=1.0)
        submitted = st.form_submit_button("Add Student")
        if submitted:
            if not roll.strip() or not name.strip() or not course.strip():
                st.error("Please fill in all fields.")
            elif students.add({
                "roll": roll.strip(),
                "name": name.strip(),
                "course": course.strip(),
                "marks": marks
            }):
                save_students()
                st.success("Student added successfully!")
                st.rerun()
            else:
                st.error("This roll number already exists.")

elif menu == "View Students":
    st.subheader("📋 All Students")
    if records:
        sort_by = st.selectbox("Sort by", ["Roll Number", "Name", "Marks"])
        key = {"Roll Number": "roll", "Name": "name", "Marks": "marks"}[sort_by]
        ordered = sorted(records, key=lambda s: s[key])
        st.dataframe(ordered, use_container_width=True)
        st.download_button(
            "Download Student Data (JSON)",
            json.dumps(ordered, indent=2),
            file_name="students.json",
            mime="application/json"
        )
    else:
        st.info("No students added yet.")

elif menu == "Search Student":
    st.subheader("🔎 Search Student")
    roll = st.text_input("Enter Roll Number")
    if st.button("Search"):
        result = students.search(roll.strip())
        if result:
            st.success("Student found!")
            st.json(result)
        else:
            st.warning("Student not found.")

elif menu == "Update Student":
    st.subheader("✏️ Update Student")
    roll = st.text_input("Roll Number to Update")
    existing = students.search(roll.strip()) if roll.strip() else None

    if existing:
        st.write("Current details:", existing)
        with st.form("update_form"):
            name = st.text_input("Student Name", value=existing["name"])
            course = st.text_input("Course", value=existing["course"])
            marks = st.number_input(
                "Marks", min_value=0.0, max_value=100.0,
                value=float(existing["marks"]), step=1.0
            )
            submitted = st.form_submit_button("Save Changes")
            if submitted:
                students.update(roll.strip(), name.strip(), course.strip(), marks)
                save_students()
                st.success("Student updated successfully!")
                st.rerun()
    else:
        st.caption("Enter an existing roll number to view and update details.")

elif menu == "Delete Student":
    st.subheader("🗑️ Delete Student")
    roll = st.text_input("Roll Number to Delete")
    if st.button("Delete Student", type="primary"):
        if students.delete(roll.strip()):
            save_students()
            st.success("Student deleted successfully!")
            st.rerun()
        else:
            st.error("Student not found.")
