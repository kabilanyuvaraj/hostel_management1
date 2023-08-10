# from flask import Flask, render_template, request, send_file
# from fpdf import FPDF

# app = Flask(__name__)

# class PDF(FPDF):
#     def header(self):
#         self.set_font('Arial', 'B', 12)
#         self.cell(0, 10, 'Monthly Report', 0, 1, 'C')
    
#     def footer(self):
#         self.set_y(-15)
#         self.set_font('Arial', 'I', 8)
#         self.cell(0, 10, 'Page %s' % self.page_no(), 0, 0, 'C')

# @app.route('/generate_pdf', methods=['POST'])
# def generate_pdf():
#     # Get form data
#     name = 'Mukesh'
#     age = 18
#     email = 'mukeshraja@gmail.com'

#     # Create PDF object
#     pdf = PDF()
#     pdf.add_page()

#     # Add content to PDF
#     pdf.set_font('Arial', '', 12)
#     pdf.cell(0, 10, f'Name: {name}', ln=True)
#     pdf.cell(0, 10, f'Age: {age}', ln=True)
#     pdf.cell(0, 10, f'Email: {email}', ln=True)

#     # Define PDF file name and path
#     pdf_file = 'output.pdf'  # Update with your desired file name and path

#     # Save PDF file
#     pdf.output(pdf_file)

#     # Return a response with the PDF file for download
#     return send_file(pdf_file, as_attachment=True)

# @app.route("/")
# def index():
#     return render_template("summa.html")

# if __name__ == '__main__':
#     app.run(debug=True)


from fpdf import FPDF
import webbrowser
from io import BytesIO
from tkinter import filedialog
import tkinter as tk

class FeeReceipt(FPDF):
    def header(self):
        # Add header information
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Hostel Fee Receipt", 0, 1, "C")
        self.cell(0, 10, "University Hostels", 0, 1, "C")
        self.cell(0, 10, "Contact: hostel@example.com", 0, 1, "C")
        self.cell(0, 10, "", ln=True)  # Add an empty line

    def footer(self):
    # Add footer information
        page_width = self.w
        page_height = self.h
        footer_height = 15  # You can adjust this value as needed
        self.set_y(page_height - footer_height)
        self.set_font("Arial", size=8)
        self.cell(page_width, 5, "Thank you for choosing our hostel!", 0, 0, "C")
        self.set_y(page_height - footer_height + 5)
        self.cell(page_width, 5, f"Receipt generated on: {self.get_current_date()}", 0, 0, "C")

    def get_current_date(self):
        # Helper method to get the current date
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_receipt_content(self, student_name, roll_number, hostel_name, mess_fees, room_rent, water_charges, electricity_bill):
        # Set font
        self.set_font("Arial", size=12)

        # Add student information
        self.cell(0, 10, f"Student Name: {student_name}", ln=True, align='L')
        self.cell(0, 10, f"Roll Number: {roll_number}", ln=True, align='L')
        self.cell(0, 10, f"Hostel Name: {hostel_name}", ln=True, align='L')
        self.cell(0, 10, "", ln=True)  # Add an empty line

        # Add fee details
        self.cell(0, 10, "Fee Details", ln=True, align='L')
        self.cell(0, 10, f"Mess Fees: {mess_fees}", ln=True, align='L')
        self.cell(0, 10, f"Room Rent: {room_rent}", ln=True, align='L')
        self.cell(0, 10, f"Water Charges: {water_charges}", ln=True, align='L')
        self.cell(0, 10, f"Electricity Bill: {electricity_bill}", ln=True, align='L')
        self.cell(0, 10, "", ln=True)  # Add an empty line

        # Calculate the total fee
        total_fee = mess_fees + room_rent + water_charges + electricity_bill
        self.cell(0, 10, f"Total Fee: {total_fee}", ln=True, align='L')

def generate_fee_receipt():
    # Sample data for the receipt
    student_name = "John Doe"
    roll_number = "12345"
    hostel_name = "Hostel A"
    mess_fees = 5000
    room_rent = 10000
    water_charges = 500
    electricity_bill = 300

    # Create the receipt
    receipt = FeeReceipt()
    receipt.add_page()

    # Add receipt content
    receipt.add_receipt_content(student_name, roll_number, hostel_name, mess_fees, room_rent, water_charges, electricity_bill)

    # Save the PDF
    # receipt_file = "fee_receipt.pdf"

    root = tk.Tk()
    root.withdraw()
    receipt_file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if not receipt_file:
        print("File save canceled.")
        return
    receipt.output(receipt_file)
    print(f"Fee receipt generated: {receipt_file}")

    # receipt_pdf = BytesIO()
    # receipt.output(receipt_pdf)

    # # Save the PDF to a specific file location
    # receipt_file = "fee_receipt.pdf"
    # with open(receipt_file, "wb") as f:
    #     f.write(receipt_pdf.getvalue())

    # Show the PDF in the default PDF viewer
    webbrowser.open(receipt_file)

if __name__ == "__main__":
    generate_fee_receipt()
