import sqlite3
import os
import sys
from pathlib import Path
from werkzeug.security import generate_password_hash

# Ensure root directory is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import Config
from backend.database import init_tables

def seed_database():
    init_tables()
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # Check if already seeded
    cur.execute("SELECT COUNT(*) FROM users;")
    if cur.fetchone()[0] > 0:
        print("Database already contains data. Skipping initial seeding.")
        conn.close()
        return

    print("Seeding initial database...")

    # 1. Seed Users
    hashed_admin = generate_password_hash("admin123")
    hashed_inst = generate_password_hash("institution123")
    hashed_default = generate_password_hash("password123")

    users_data = [
        ("Deransiya Dorin J", "admin@aicte.gov.in", hashed_admin, "Cloud Architect", "Central Administration", "Cloud Architect & Lead Admin", None, "Active", "2026-10-24 12:30:00"),
        ("Priya Singh", "priya.singh@aicte.gov.in", hashed_default, "Admin", "Grievance Cell", "Senior Grievance Officer", None, "Active", "2026-10-24 10:15:00"),
        ("Amit Patel", "amit.patel@aicte.gov.in", hashed_default, "Reviewer", "Approval Bureau", "Compliance Officer", None, "Active", "2026-10-23 16:00:00"),
        ("Sneha Desai", "sneha.desai@aicte.gov.in", hashed_default, "Reviewer", "Administration Bureau", "Administrative Officer", None, "Active", "2026-10-22 14:30:00"),
        ("Vikram Joshi", "vikram.joshi@aicte.gov.in", hashed_default, "Analyst", "Policy & Planning", "Policy Analyst", None, "Active", "2026-10-21 09:00:00"),
        ("Karthik Nair", "karthik.nair@aicte.gov.in", hashed_default, "Viewer", "Grievance Cell", "Junior Cell Assistant", None, "Active", "2026-10-20 13:45:00"),
        ("Dr. Ramesh Kumar (Principal)", "principal@abcit.edu.in", hashed_inst, "Institution", "Engineering", "Principal", "AICTE-IN-78234", "Active", "2026-10-24 11:00:00")
    ]

    cur.executemany("""
    INSERT INTO users (name, email, password_hash, role, department, designation, institution_ref, status, last_login)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, users_data)

    # 2. Seed Bureaus
    bureaus_data = [
        ("bureau-1", "Approval Bureau", "Dr. Rajesh Sharma", "approval@aicte-india.org", "Handles complaints related to institutional approvals, renewals, and compliance with AICTE norms."),
        ("bureau-2", "Administration Bureau", "Ms. Sunita Agarwal", "admin@aicte-india.org", "Manages administrative complaints including faculty issues, institutional management, and operational concerns."),
        ("bureau-3", "Policy & Planning", "Prof. Anil Mehta", "policy@aicte-india.org", "Addresses issues related to curriculum standards, policy compliance, and strategic planning matters."),
        ("bureau-4", "Grievance Cell", "Dr. Meera Nair", "grievance@aicte-india.org", "Primary cell for handling student and stakeholder grievances including fee disputes, examination issues, and general complaints."),
        ("bureau-5", "Regional Office", "Mr. Kapil Bhatia", "regional@aicte-india.org", "Coordinates regional-level investigations, site inspections, and compliance monitoring across zones.")
    ]

    cur.executemany("""
    INSERT INTO bureaus (id, name, head, email, description)
    VALUES (?, ?, ?, ?, ?);
    """, bureaus_data)

    # 3. Seed 20 Realistic Fictional Complaints
    complaints_data = [
        ("AIC-2026-0001", "ABC Institute of Technology", "AICTE-IN-78234", "Engineering", "Maharashtra", "Pune", "Dr. Ramesh Kumar", "ramesh.kumar@abcit.edu.in", "+91-9876543210", "Infrastructure", "bureau-1", "High", "In Progress", "Inadequate laboratory equipment in engineering department", "The engineering department laboratories lack essential equipment required for practical sessions as per AICTE norms. Students are unable to complete mandatory experiments for multiple courses. This affects the quality of technical education being provided.", 1, 7, "2026-09-15", "2026-10-20", None),
        ("AIC-2026-0002", "XYZ College of Engineering", "AICTE-IN-45621", "Engineering", "Tamil Nadu", "Chennai", "Mr. Suresh Babu", "suresh.b@xyzce.edu.in", "+91-9123456780", "Fee Disputes", "bureau-4", "Critical", "Under Review", "Unauthorized fee hike by management", "The institution has implemented a 40% fee increase without prior approval from the Fee Regulation Committee. Multiple students and parents have raised concerns about the sudden and unauthorized fee hike.", 1, None, "2026-10-01", "2026-10-18", None),
        ("AIC-2026-0003", "PQR Technical University", "AICTE-IN-33201", "University", "Karnataka", "Bengaluru", "Prof. Anita Sharma", "anita.s@pqrtu.edu.in", "+91-9988776655", "Faculty Issues", "bureau-2", "High", "New", "Faculty shortage in Computer Science department", "The Computer Science department currently operates with only 8 faculty members against the required strength of 20 as per AICTE norms. This severely impacts teaching quality and student outcomes.", 1, None, "2026-10-20", "2026-10-20", None),
        ("AIC-2026-0004", "LMN School of Management", "AICTE-IN-56789", "Management", "Delhi", "New Delhi", "Mr. Vikram Singh", "vikram.s@lmnsm.edu.in", "+91-9876501234", "Affiliation", "bureau-1", "Medium", "Resolved", "Affiliation renewal delays causing student uncertainty", "The institution affiliation renewal has been pending for over 6 months, causing uncertainty among current students regarding the validity of their degrees.", 1, None, "2026-07-10", "2026-09-30", "Affiliation has been renewed and formal extension order issued to the institution."),
        ("AIC-2026-0005", "DEF Polytechnic", "AICTE-IN-11234", "Polytechnic", "Uttar Pradesh", "Lucknow", "Dr. Priya Patel", "priya.p@defpoly.edu.in", "+91-9812345670", "Curriculum", "bureau-3", "Medium", "In Progress", "Non-compliance with curriculum standards", "The institution has not updated its curriculum as per the latest AICTE model curriculum guidelines. Several courses still follow outdated syllabi from 2019.", 1, None, "2026-08-22", "2026-10-15", None),
        ("AIC-2026-0006", "GHI Engineering College", "AICTE-IN-67890", "Engineering", "Rajasthan", "Jaipur", "Mr. Arjun Mehra", "arjun.m@ghiec.edu.in", "+91-9900112233", "Placement", "bureau-2", "Low", "Resolved", "Placement cell not functional despite AICTE mandate", "The placement cell is non-functional with no dedicated staff or infrastructure. No campus placement drives have been conducted in the last 2 academic years.", 1, None, "2026-06-05", "2026-08-20", "Institution appointed dedicated Placement Officer and conducted 4 campus hiring drives."),
        ("AIC-2026-0007", "JKL Institute of Technology", "AICTE-IN-99887", "Engineering", "Gujarat", "Ahmedabad", "Dr. Neha Gupta", "neha.g@jklit.edu.in", "+91-9876012345", "Examination", "bureau-4", "Critical", "Overdue", "Irregular examination practices reported", "Multiple reports of examination irregularities including leaked question papers and biased evaluation. Evidence has been submitted by affected students.", 1, None, "2026-08-01", "2026-10-10", None),
        ("AIC-2026-0008", "MNO College of Pharmacy", "AICTE-IN-44556", "Pharmacy", "Madhya Pradesh", "Bhopal", "Mr. Sanjay Verma", "sanjay.v@mnocp.edu.in", "+91-9111222333", "Infrastructure", "bureau-5", "Critical", "In Progress", "Building safety standards not met", "The main academic block does not meet fire safety and structural safety norms. No fire exits, outdated fire extinguishers, and visible structural cracks on the 3rd floor.", 1, None, "2026-09-05", "2026-10-22", None),
        ("AIC-2026-0009", "STU Medical Engineering Institute", "AICTE-IN-77788", "Engineering", "Telangana", "Hyderabad", "Ms. Kavitha Reddy", "kavitha.r@stumei.edu.in", "+91-9444555666", "Fee Disputes", "bureau-4", "High", "Under Review", "Students forced to pay capitation fees", "Students are being forced to pay undisclosed capitation fees during the admission process. Receipts are not provided for these payments.", 1, None, "2026-10-10", "2026-10-21", None),
        ("AIC-2026-00010", "VWX School of Architecture", "AICTE-IN-22334", "Architecture", "West Bengal", "Kolkata", "Dr. Amitabh Roy", "amitabh.r@vwxsa.edu.in", "+91-9333444555", "Infrastructure", "bureau-2", "Medium", "New", "Lack of disabled-friendly facilities on campus", "The campus lacks ramps, elevators, accessible restrooms, and other facilities mandated under the Rights of Persons with Disabilities Act for differently-abled students.", 1, None, "2026-10-22", "2026-10-22", None),
        ("AIC-2026-00011", "Alpha Engineering Academy", "AICTE-IN-88901", "Engineering", "Kerala", "Thiruvananthapuram", "Mr. George Thomas", "george.t@aea.edu.in", "+91-9777888999", "Placement", "bureau-4", "Low", "Resolved", "Misleading placement statistics on website", "The institution publishes inflated placement statistics on its website and marketing materials. Actual placement rates are significantly lower than advertised figures.", 1, None, "2026-05-15", "2026-07-30", "Institution audited and mandated to display verified NIRF placement data."),
        ("AIC-2026-00012", "Beta Technical Institute", "AICTE-IN-55667", "Engineering", "Maharashtra", "Mumbai", "Ms. Sneha Joshi", "sneha.j@bti.edu.in", "+91-9222333444", "Other", "bureau-2", "Medium", "Overdue", "Delay in issuing transcripts and certificates", "Graduated students have been waiting for more than 8 months to receive their final transcripts and degree certificates. This is affecting their higher education and employment opportunities.", 1, None, "2026-07-20", "2026-09-15", None),
        ("AIC-2026-00013", "Apex Institute of Management", "AICTE-IN-12390", "Management", "Maharashtra", "Nagpur", "Dr. Alok Nath", "alok.n@apexmgt.edu.in", "+91-9823456781", "Affiliation", "bureau-1", "Medium", "Resolved", "Delayed intake approval notification", "Institution faced delays in publishing approved seat matrix for the academic year 2026-27.", 1, None, "2026-04-12", "2026-06-18", "Approval matrix updated on central portal."),
        ("AIC-2026-00014", "Zenith College of Engineering", "AICTE-IN-98124", "Engineering", "Karnataka", "Mysuru", "Prof. Harish Rao", "harish.r@zenith.edu.in", "+91-9845012345", "Faculty Issues", "bureau-2", "High", "In Progress", "Unpaid faculty salaries for four consecutive months", "Faculty members report non-payment of mandated salaries and PF contributions since May 2026.", 1, None, "2026-08-14", "2026-10-11", None),
        ("AIC-2026-00015", "National Institute of Pharmacy", "AICTE-IN-66778", "Pharmacy", "Tamil Nadu", "Coimbatore", "Dr. Senthil Kumar", "senthil@nipharma.edu.in", "+91-9442112233", "Infrastructure", "bureau-5", "High", "Under Review", "Animal house facility non-compliant with CPCSEA guidelines", "The experimental animal house facility lacks climate control and veterinary oversight.", 1, None, "2026-09-28", "2026-10-19", None),
        ("AIC-2026-00016", "Horizon Institute of Technology", "AICTE-IN-33445", "Engineering", "Uttar Pradesh", "Kanpur", "Mr. Deepak Mishra", "deepak@horizontech.edu.in", "+91-9721001122", "Fee Disputes", "bureau-4", "Critical", "In Progress", "Withholding caution deposit refunds from graduated batches", "The college has refused to refund security deposits worth Rs 25,000 per student to over 400 alumni.", 1, None, "2026-07-25", "2026-10-05", None),
        ("AIC-2026-00017", "Global Polytechnic College", "AICTE-IN-77889", "Polytechnic", "Gujarat", "Surat", "Mrs. Bhavna Dave", "bhavna@globalpoly.edu.in", "+91-9824003344", "Curriculum", "bureau-3", "Low", "Resolved", "Absence of practical credits in automation syllabus", "Curriculum structure missing AICTE mandatory 60-hour industrial internship.", 1, None, "2026-03-10", "2026-05-20", "Revised curriculum adopted with industry internship partner."),
        ("AIC-2026-00018", "Modern Academy of Architecture", "AICTE-IN-55443", "Architecture", "Delhi", "Delhi", "Ar. Tarun Bakshi", "tarun@modernarch.edu.in", "+91-9810112233", "Faculty Issues", "bureau-2", "Medium", "New", "Principal lacks mandatory 15 years professional experience", "Appointment in violation of AICTE notification F.No. 61-1/RIFD/7th CPC/2016-17.", 1, None, "2026-10-23", "2026-10-23", None),
        ("AIC-2026-00019", "Coastal Institute of Marine Studies", "AICTE-IN-99112", "Engineering", "Kerala", "Kochi", "Capt. V. Nambiar", "capt.nambiar@coastalmarine.edu.in", "+91-9847113355", "Infrastructure", "bureau-1", "Critical", "Overdue", "Marine simulator facility unserviceable for over 180 days", "Mandatory simulation hours cannot be fulfilled for current batch before DG Shipping inspection.", 1, None, "2026-06-20", "2026-09-12", None),
        ("AIC-2026-00020", "Kaveri Polytechnic", "AICTE-IN-44332", "Polytechnic", "Karnataka", "Mangaluru", "Mr. Praveen Shetty", "praveen@kaveripoly.edu.in", "+91-9945223344", "Examination", "bureau-4", "Medium", "Resolved", "Evaluation delay causing university admission cancellation", "Final semester exam evaluation was delayed by 70 days.", 1, None, "2026-05-02", "2026-07-15", "Re-evaluation expedited and provisional marksheets dispatched.")
    ]

    cur.executemany("""
    INSERT INTO complaints (
        id, institution, institution_id, institution_type, state, district,
        contact_person, email, phone, category, bureau_id, priority, status,
        subject, description, consent, created_by_user_id, submission_date, last_updated, resolution_details
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, complaints_data)

    # 4. Seed Complaint History
    history_data = [
        ("AIC-2026-0001", "Submitted", "Complaint registered successfully via online portal.", "Dr. Ramesh Kumar", "2026-09-15 10:30:00"),
        ("AIC-2026-0001", "Under Review", "Forwarded to Approval Bureau for verification.", "Deransiya Dorin J", "2026-09-18 14:00:00"),
        ("AIC-2026-0001", "In Progress", "Site inspection committee constituted.", "Dr. Rajesh Sharma", "2026-09-25 11:20:00"),

        ("AIC-2026-0002", "Submitted", "Complaint filed with fee vouchers attached.", "Mr. Suresh Babu", "2026-10-01 09:15:00"),
        ("AIC-2026-0002", "Under Review", "Case assigned to Grievance Cell.", "Deransiya Dorin J", "2026-10-05 16:45:00"),

        ("AIC-2026-0003", "Submitted", "Complaint registered.", "Prof. Anita Sharma", "2026-10-20 11:00:00"),

        ("AIC-2026-0004", "Submitted", "Affiliation renewal grievance lodged.", "Mr. Vikram Singh", "2026-07-10 12:00:00"),
        ("AIC-2026-0004", "Under Review", "Under scrutiny by Approval Bureau.", "Amit Patel", "2026-07-15 15:30:00"),
        ("AIC-2026-0004", "In Progress", "Document verification and committee hearing.", "Dr. Rajesh Sharma", "2026-08-01 11:00:00"),
        ("AIC-2026-0004", "Resolved", "Formal approval letter issued.", "Deransiya Dorin J", "2026-09-30 17:00:00"),

        ("AIC-2026-0007", "Submitted", "Evidence of paper leakage submitted.", "Dr. Neha Gupta", "2026-08-01 10:00:00"),
        ("AIC-2026-0007", "Under Review", "Grievance committee formed.", "Priya Singh", "2026-08-10 14:00:00"),

        ("AIC-2026-0008", "Submitted", "Emergency safety audit requested.", "Mr. Sanjay Verma", "2026-09-05 08:30:00"),
        ("AIC-2026-0008", "Under Review", "Expedited review initiated.", "Deransiya Dorin J", "2026-09-07 11:00:00"),
        ("AIC-2026-0008", "In Progress", "Regional inspection ordered.", "Mr. Kapil Bhatia", "2026-09-12 16:00:00")
    ]

    cur.executemany("""
    INSERT INTO complaint_history (complaint_id, status, note, created_by, created_at)
    VALUES (?, ?, ?, ?, ?);
    """, history_data)

    # 5. Seed Public Investigation Updates
    updates_data = [
        ("AIC-2026-0001", "Site inspection team formed and schedule confirmed for campus visit.", 1, "Approval Bureau", "2026-09-26 10:00:00"),
        ("AIC-2026-0001", "Preliminary report indicates equipment shortfall in 3 out of 5 electrical labs.", 1, "Approval Bureau", "2026-10-18 16:30:00"),
        ("AIC-2026-0002", "Show cause notice issued to institution regarding unauthorized fee structure.", 1, "Grievance Cell", "2026-10-12 11:00:00"),
        ("AIC-2026-0004", "Affiliation renewal officially ratified by regional council.", 1, "Approval Bureau", "2026-09-30 16:00:00"),
        ("AIC-2026-0008", "Fire safety department inspection conducted on October 10.", 1, "Regional Office", "2026-10-14 15:00:00")
    ]

    cur.executemany("""
    INSERT INTO investigation_updates (complaint_id, update_text, is_public, created_by, created_at)
    VALUES (?, ?, ?, ?, ?);
    """, updates_data)

    # 6. Seed Private Investigation Notes (CONFIDENTIAL - Admin only!)
    notes_data = [
        ("AIC-2026-0001", "Whistleblower interview scheduled confidentially. Lab attendance registers subpoenaed.", "Deransiya Dorin J", "2026-09-20 14:00:00"),
        ("AIC-2026-0002", "Fee committee records show no sanctioned fee revision since 2023. Possible fiscal penalty under review.", "Priya Singh", "2026-10-10 11:30:00"),
        ("AIC-2026-0007", "Internal examiner statement matches leaked Telegram question screenshots. Preparing statutory report.", "Priya Singh", "2026-09-01 10:15:00"),
        ("AIC-2026-0008", "Building occupancy certificate was renewed without physical site verification by local municipality.", "Deransiya Dorin J", "2026-09-15 17:00:00")
    ]

    cur.executemany("""
    INSERT INTO investigation_notes (complaint_id, note_text, created_by, created_at)
    VALUES (?, ?, ?, ?);
    """, notes_data)

    # 7. Seed Notifications
    notifs_data = [
        (1, "new", "New complaint received", "Complaint AIC-2026-00010 regarding lack of disabled-friendly facilities has been submitted.", "AIC-2026-00010", 0, "2026-10-24 10:00:00"),
        (1, "assigned", "Case assigned", "Complaint AIC-2026-0003 has been assigned to Administration Bureau.", "AIC-2026-0003", 0, "2026-10-24 11:15:00"),
        (1, "status", "Status updated", "Complaint AIC-2026-0008 status changed to In Progress.", "AIC-2026-0008", 0, "2026-10-24 12:30:00"),
        (1, "priority", "High-priority complaint", "Complaint AIC-2026-0008 requires immediate attention — building structural hazard.", "AIC-2026-0008", 1, "2026-10-23 08:00:00"),
        (1, "overdue", "Overdue complaint", "Complaint AIC-2026-0007 has exceeded the mandated 60-day resolution timeline.", "AIC-2026-0007", 1, "2026-10-23 09:30:00"),
        (1, "status", "Case resolved", "Complaint AIC-2026-0004 has been resolved — affiliation renewed.", "AIC-2026-0004", 1, "2026-09-30 17:00:00"),
        (1, "new", "New complaint received", "Complaint AIC-2026-0009 regarding capitation fees submitted.", "AIC-2026-0009", 1, "2026-10-21 15:00:00")
    ]

    cur.executemany("""
    INSERT INTO notifications (user_id, type, title, message, complaint_id, is_read, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, notifs_data)

    # 8. Seed Audit Logs
    audit_data = [
        ("Deransiya Dorin J", "Status Updated", "AIC-2026-0008", "Status changed from Under Review to In Progress.", "2026-10-24 12:30:00"),
        ("Deransiya Dorin J", "Case Assigned", "AIC-2026-0003", "Assigned to Administration Bureau.", "2026-10-24 11:15:00"),
        ("System", "Complaint Received", "AIC-2026-00010", "New complaint submitted via online portal by VWX School of Architecture.", "2026-10-24 10:00:00"),
        ("Priya Singh", "Priority Changed", "AIC-2026-0007", "Priority escalated from High to Critical due to exam leak evidence.", "2026-10-23 16:45:00"),
        ("Deransiya Dorin J", "Comment Added", "AIC-2026-0005", "Added investigation note: Institution asked to submit revised curriculum.", "2026-10-23 14:20:00"),
        ("System", "Overdue Alert", "AIC-2026-00012", "Case has exceeded AICTE citizen charter timeline of 60 days.", "2026-10-23 09:30:00"),
        ("Priya Singh", "Document Uploaded", "AIC-2026-0009", "Fee receipts and audit affidavit attached to case record.", "2026-10-22 17:00:00"),
        ("Deransiya Dorin J", "Case Resolved", "AIC-2026-0006", "Placement cell established. Show-cause closed with compliance warning.", "2026-10-22 11:30:00"),
        ("System", "Complaint Received", "AIC-2026-0009", "New complaint submitted regarding capitation fees.", "2026-10-21 15:00:00"),
        ("Priya Singh", "Bureau Reassigned", "AIC-2026-0001", "Reassigned from Regional Office to Approval Bureau.", "2026-10-21 10:00:00")
    ]

    cur.executemany("""
    INSERT INTO audit_logs (user_name, action, complaint_id, details, created_at)
    VALUES (?, ?, ?, ?, ?);
    """, audit_data)

    conn.commit()
    conn.close()
    print("Database seeded successfully with 20 complaints, users, bureaus, history, notes, and audit logs.")

if __name__ == '__main__':
    seed_database()
