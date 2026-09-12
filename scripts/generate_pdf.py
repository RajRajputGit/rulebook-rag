import fitz  # PyMuPDF
import os

def generate_pdf():
    os.makedirs("corpus", exist_ok=True)
    pdf_path = "corpus/examination_and_records_policy.pdf"
    
    doc = fitz.open()
    
    # Page 1
    page1 = doc.new_page()
    text_p1 = """OFFICIAL POLICY DOCUMENT: EXAMINATION & ACADEMIC RECORDS
Apex Institute of Higher Education & Research
Publication Date: September 2025 | Document Ref: REG-2025-EXAM-V2

================================================================================
SECTION 1: EXAMINATION CONDUCT AND ADMIT CARDS
================================================================================
1.1 Admit Card Issuance: Hall tickets and examination admit cards are generated
electronically 10 days prior to the commencement of final semester examinations.
Students must present a printed admit card along with a valid physical university
student ID card at the examination hall entrance.

1.2 Examination Hall Entry Rules: Students arriving more than 15 minutes after
the scheduled start of an examination will not be admitted into the examination
hall under any circumstances. No student may exit the examination hall during the
first 45 minutes of the examination session.

================================================================================
SECTION 2: SPECIAL ACCOMMODATIONS FOR DISABILITIES
================================================================================
2.1 Disability Support: Students requesting examination accommodations due to physical
or learning disabilities must register with the Office of Disability Services at
least 30 days before the start of the examination period.

2.2 Scribe and Extra Time Provisions: Approved candidates are eligible for 20 minutes
of extra time per hour of examination and may request a university-approved scribe.

================================================================================
SECTION 3: GRADE APPEALS AND RE-EVALUATION
================================================================================
3.1 Grade Review Petition: A student who believes a final semester grade was calculated
in error or with bias may submit a formal Grade Review Petition to the Office of
Academic Records within 14 calendar days of grade release.

3.2 Re-evaluation Surcharge: A non-refundable processing fee of $40 per course is
charged for answer script re-evaluation. If the re-evaluation results in a grade
change of one full letter grade or higher, the $40 fee is refunded to the student account.

================================================================================
SECTION 4: MEDICAL EXEMPTIONS FOR FINAL EXAMINATIONS
================================================================================
4.1 Notification Requirement: Students unable to maintain regular attendance due to severe
illness or hospitalization must report their medical absence to the Academic Registrar
within 5 working days of the onset of illness.

4.2 Medical Attendance Exemption Policy: Students who submit a valid, verified medical
certificate from a university-approved hospital within 5 working days are granted an
official attendance waiver, permitting them to sit for the final examination provided
their recorded attendance is at least 60%.
"""
    page1.insert_text((40, 40), text_p1, fontsize=9)

    # Page 2
    page2 = doc.new_page()
    text_p2 = """OFFICIAL POLICY DOCUMENT: EXAMINATION & ACADEMIC RECORDS (CONTINUED)

================================================================================
SECTION 5: LATE FEE REGULATIONS AND IMMEDIATE SURCHARGES
================================================================================
5.1 Late Payment Surcharges: A mandatory late payment penalty fee of $50 per week applies
immediately starting the day following the payment due date, with zero grace period
applicable under any circumstances. Late fees accrue automatically on student accounts
at 12:01 AM on the day after the due date.

5.2 Payment Hardship Appeals: Students facing severe financial hardship may request a
temporary payment extension by petitioning the Bursar's Office at least 5 business days
PRIOR to the published payment due date. Petitions submitted after the due date will not be entertained.

================================================================================
SECTION 6: TRANSCRIPT RECORD OF COURSE WITHDRAWALS
================================================================================
6.1 Transcript Record of Course Withdrawals: Any course from which a student withdraws
after Week 4 of the semester must remain permanently listed on the official academic transcript
with a recorded grade of 'W' (Withdrawn). No course dropped after Week 4 may be erased from transcript.

6.2 Impact on GPA: Grades of 'W' (Withdrawn) do not carry quality points and are not
computed into semester or cumulative GPA calculations. However, 'W' grades count as
attempted credits for financial aid SAP (Satisfactory Academic Progress) calculations.

================================================================================
SECTION 7: DEGREE VERIFICATION AND DIPLOMA REISSUANCE
================================================================================
7.1 Official Transcript Requests: Students and alumni may request official transcript
delivery via electronic PDF or sealed paper copies through the National Student Clearinghouse portal.
Standard processing time is 3 to 5 business days.

7.2 Replacement Diploma: A replacement diploma scroll may be issued upon submission of a
notarized Affidavit of Loss and payment of a $75 reissuance fee. All replacement diplomas
bear the word 'Duplicate' in small typography at the bottom margin.
"""
    page2.insert_text((40, 40), text_p2, fontsize=9)

    doc.save(pdf_path)
    doc.close()
    print(f"Generated clean PDF successfully at {pdf_path}")

if __name__ == "__main__":
    generate_pdf()
