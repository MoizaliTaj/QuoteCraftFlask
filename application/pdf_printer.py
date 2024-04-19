from fpdf import FPDF
from num2words import num2words
from PIL import Image
import math
import os 

current_dir = os.path.abspath(os.path.dirname(__file__))
base = os.path.join(current_dir, "../")

def problem_character_exits(character):
    if ord(character) > 256:
        return True
    else:
        return False

def remove_problem_character(input_string):
    output_string = ''
    for char in input_string:
        if problem_character_exits(char):
            pass
        else:
            output_string += char
    return output_string

def number_formatter(numberString):
    number = float(numberString) + 0.0000000001
    numberString = "{:.2f}".format(number)
    crossed_decimal = False
    output = ""
    for i in range(len(numberString)):
        output += numberString[i]
        if numberString[i] == ".":
            crossed_decimal = True
        if not crossed_decimal:
            remaining_number = numberString[i+1:].split('.')[0]
            if remaining_number.isdigit():
                if len(remaining_number) % 3 == 0:
                    output += ","
    return output

def number_to_words(number_input):
    pre_decimal = int(number_input)
    post_decimal = int(((number_input % 1) + 0.000001) *100)
    if post_decimal > 0:
        return "Dirham " + num2words(pre_decimal).title() + " And " + num2words(post_decimal).title() + " Fils Only"
    else:
        return "Dirham " + num2words(pre_decimal).title() + " Only"

def printer_invoice(invoice_details, customer_details, salesman_data, footer_print_date_time, invoice_content, pdf_file_name, print_type):
    pdf = PDF()
    pdf.setup_object(invoice_details, customer_details, salesman_data, footer_print_date_time, invoice_content, pdf_file_name, print_type)
    pdf.add_page()
    pdf.table()
    pdf_file_name = base + 'static/pdf_files/' + pdf_file_name
    pdf.output(pdf_file_name)

class PDF(FPDF):
    font = 'Arial'
    salesman_data = {}
    customer_data = {}
    invoice_details = {}
    date_print = ""
    footer_print_date_time = ""
    master_y_accumulated = 0
    data = ""
    total = ""
    vat = ""
    total_with_vat = ""
    width_details = ""
    bottom_blank_width = ""
    bottom_title_width = ""
    table_header_required = True
    title_heading = ''
    table_header_list = ''
    print_type = ''

    def setup_object(self, invoice_details, customer_details, salesman_data, footer_print_date_time, invoice_content, pdf_file_name, print_type):
        self.print_type = print_type
        self.salesman_data = salesman_data
        self.customer_data = customer_details

        self.invoice_details = invoice_details
        date_print = self.invoice_details.date
        date_print = date_print[8:] + '-' + date_print[5:7] + '-' + date_print[:4]
        self.date_print = date_print
        self.footer_print_date_time = footer_print_date_time

        if print_type != 'without_quantity':
            self.table_header_list = ['image_path', 'Sr.', 'Code', 'Description', 'Quantity', 'Unit', 'Unit Price', 'Total', ]
        else:
            self.table_header_list = ['image_path', 'Sr.', 'Code', 'Description', 'Unit', 'Unit Price',]
        if print_type == 'normal_proforma_only':
            self.title_heading = 'Proforma Invoice'
        else:
            self.title_heading = 'Proforma Invoice / Quotation'
        grand_total_without_vat = 0
        data = []
        counter = 1
        for row in invoice_content:
            grand_total_without_vat += float(row.total)
            if print_type != 'without_quantity':
                if len(row.size):
                    data.append([row.image_path, counter, remove_problem_character(row.code), remove_problem_character(row.description + ", " + row.size), number_formatter(row.quantity), remove_problem_character(row.unit), number_formatter(row.price), number_formatter(row.total), ])
                else:
                    data.append([row.image_path, counter, remove_problem_character(row.code), remove_problem_character(row.description), number_formatter(row.quantity), remove_problem_character(row.unit), number_formatter(row.price), number_formatter(row.total), ])
            else:
                if len(row.size):
                    data.append([row.image_path, counter, remove_problem_character(row.code), remove_problem_character(row.description + ", " + row.size), remove_problem_character(row.unit), number_formatter(row.price)])
                else:
                    data.append([row.image_path, counter, remove_problem_character(row.code), remove_problem_character(row.description), remove_problem_character(row.unit), number_formatter(row.price), ])

            counter += 1
        grand_total_without_vat = round(grand_total_without_vat, 2)
        vat = round(grand_total_without_vat * 0.05, 2)
        grand_total_with_vat = round(grand_total_without_vat * 1.05, 2)

        self.data = data
        self.total = grand_total_without_vat
        self.vat = vat
        self.total_with_vat = grand_total_with_vat
        self.set_font("Times", "B", 8)
        self.width_details = self.colum_width_calculator(self.data, self.total, self.vat, self.total_with_vat, 8, 1.5)
        self.bottom_blank_width = self.width_details[1] + self.width_details[2] + self.width_details[3] + self.width_details[4]
        self.bottom_title_width = self.width_details[5] + self.width_details[6]

    def colum_width_calculator(self, data, total, vat, total_with_vat, font,offset):
        data = [self.table_header_list] + data
        if self.print_type != 'without_quantity':
            max_width_info = [0,0,0,0,0,0,0,0]
            self.set_font(self.font, "", font)
            for row in data:
                cell_counter = 0
                for cell in row:
                    if cell_counter == 0:
                        pass
                    else:
                        if max_width_info[cell_counter] < self.get_string_width(str(cell)) + offset:
                            max_width_info[cell_counter] = self.get_string_width(str(cell)) + offset
                    cell_counter += 1
            if max_width_info[7] < self.get_string_width(number_formatter(total)) + offset:
                max_width_info[7] = self.get_string_width(number_formatter(total)) + offset
            if max_width_info[7] < self.get_string_width(number_formatter(vat)) + offset:
                max_width_info[7] = self.get_string_width(number_formatter(vat)) + offset
            if max_width_info[7] < self.get_string_width(number_formatter(total_with_vat)) + offset:
                max_width_info[7] = self.get_string_width(number_formatter(total_with_vat)) + offset
            total_width = 0
            for vals in max_width_info:
                total_width += vals
            width_without_description = total_width - max_width_info[3]
            max_width_info[3] = (self.w - 13 - width_without_description)
            return max_width_info
        else:
            max_width_info = [0,0,0,0,0,0,0,0]
            self.set_font(self.font, "", font)
            for row in data:
                cell_counter = 0
                for cell in row:
                    if cell_counter == 0:
                        pass
                    else:
                        if max_width_info[cell_counter] < self.get_string_width(str(cell)) + offset:
                            max_width_info[cell_counter] = self.get_string_width(str(cell)) + offset
                    cell_counter += 1
            total_width = 0
            for vals in max_width_info:
                total_width += vals
            width_without_description = total_width - max_width_info[3]
            max_width_info[3] = (self.w - 13 - width_without_description)
            return max_width_info

    def header_and_customer_details_printer(self):
        self.image(base + 'static/media/header.png', x=6.5, y=5, w=self.w - 13)
        self.set_y(34)
        self.set_text_color(0, 0, 0)
        self.set_font(self.font, '', 10.5)
        self.set_x((self.w - self.get_string_width('Mob: ' + self.salesman_data.mobile_number + ' | ' + 'Tel: ' + self.salesman_data.landline_no + ' | ' + 'Email: ' + self.salesman_data.email_id + ' | ' + 'TRN 100000000000001')) / 2)
        self.cell(self.get_string_width('Mob: ' + self.salesman_data.mobile_number), 0, 'Mob: ' + self.salesman_data.mobile_number, 0, 0, 'C', link="tel: " + self.salesman_data.mobile_number)
        self.cell(self.get_string_width(' | '), 0, ' | ', 0, 0, 'C')
        self.cell(self.get_string_width('Tel: ' + self.salesman_data.landline_no), 0, 'Tel: ' + self.salesman_data.landline_no, 0, 0, 'C', link="tel: " + self.salesman_data.landline_no)
        self.cell(self.get_string_width(' | '), 0, ' | ', 0, 0, 'C')
        self.cell(self.get_string_width('Email: ' + self.salesman_data.email_id), 0, 'Email: ' + self.salesman_data.email_id, 0, 0, 'C', link="mailto: " + self.salesman_data.email_id)
        self.cell(self.get_string_width(' | '), 0, ' | ', 0, 0, 'C')
        self.cell(self.get_string_width('TRN 100000000000001'), 0, 'TRN 100000000000001', 0, 0, 'C',)
        self.ln(6)
        self.set_font(self.font, '', 13)
        self.cell(0, 0, self.title_heading,0, 0, 'C')
        self.ln(-2)
        self.set_font(self.font, '', 10)
        self.set_x(0)
        self.cell(self.w-6.5, 0, 'Date: ' + self.date_print, 0, 0, 'R')
        self.ln(4.5)
        self.set_x(0)
        self.cell(self.w-6.5, 0, 'Reference # ' + str(self.invoice_details.invoice_id), 0, 0, 'R')
        self.ln(4.0)
        self.set_x(6.5)
        self.set_font(self.font, '', 10)
        self.cell(self.get_string_width('Customer Name: '), 0, 'Customer Name: ', 0, 0, 'L')
        self.set_font(self.font, 'B', 10)
        self.cell(self.get_string_width(self.customer_data.customer_name + " "), 0, self.customer_data.customer_name, 0, 0, 'L')
        if (len(self.invoice_details.attention_to) > 0):
            self.set_font(self.font, '', 9)
            self.cell(0, 0, '(' + self.invoice_details.attention_to + ')', 0, 0, 'L')
        self.ln(4.5)
        if (len(self.customer_data.contact_number) > 0):
            self.set_font(self.font, '', 10)
            self.set_x(6.5)
            self.cell(self.get_string_width('Contact Number: '), 0, 'Contact Number: ', 0, 0, 'L')
            self.set_font(self.font, 'B', 10)
            self.cell(0, 0, str(self.customer_data.contact_number), 0, 0, 'L')
            self.ln(4.5)
        if (len(self.invoice_details.payment_terms) > 0):
            self.set_font(self.font, '', 10)
            self.set_x(6.5)
            self.cell(self.get_string_width('Payment Terms: '), 0, 'Payment Terms: ', 0, 0, 'L')
            self.set_font(self.font, 'B', 10)
            self.cell(0, 0, str(self.invoice_details.payment_terms), 0, 0, 'L')
            self.ln(4.5)
        self.ln(-1)

    def table_headings_creator(self,cell_height, font_size):
        self.set_x(6.5)
        cell_counter = 0
        for item in self.table_header_list:
            if cell_counter != 0:
                self.set_font(self.font, "B", font_size)
                self.set_fill_color(0, 46, 155)
                self.set_text_color(255, 255, 255)
                self.cell(self.width_details[cell_counter], cell_height, str(item), border=1, align='C', fill=True)
            cell_counter += 1
        self.ln()

    def print_total_amount_details(self, cell_height, font_size):
        if (self.get_y() > 259):
            self.add_page()
        self.set_x(6.5+self.bottom_blank_width)
        self.set_font(self.font, "B", font_size)
        self.set_fill_color(0, 46, 155)
        self.set_text_color(255, 255, 255)
        self.cell(self.bottom_title_width, cell_height, "Total", border=1, align='C', fill=True)

        self.set_font(self.font, "", font_size)
        self.set_text_color(0, 0, 0)
        self.cell(self.width_details[7], cell_height, number_formatter(self.total), border=1, align='R', fill=False)
        self.ln()

        if self.print_type != 'without_vat':
            self.set_x(6.5+self.bottom_blank_width)
            self.set_font(self.font, "B", font_size)
            self.set_fill_color(0, 46, 155)
            self.set_text_color(255, 255, 255)
            self.cell(self.bottom_title_width, cell_height, "VAT", border=1, align='C', fill=True)

            self.set_font(self.font, "", font_size)
            self.set_text_color(0, 0, 0)
            self.cell(self.width_details[7], cell_height, number_formatter(self.vat), border=1, align='R', fill=False)
            self.ln()

            self.set_x(6.5+self.bottom_blank_width)
            self.set_font(self.font, "B", font_size)
            self.set_fill_color(0, 46, 155)
            self.set_text_color(255, 255, 255)
            self.cell(self.bottom_title_width, cell_height, "Total With VAT", border=1, align='C', fill=True)

            self.set_font(self.font, "", font_size)
            self.set_text_color(0, 0, 0)
            self.cell(self.width_details[7], cell_height, number_formatter(self.total_with_vat), border=1, align='R', fill=False)



        self.set_font("Times", "", font_size+2)
        self.set_text_color(0, 0, 0)

        if self.print_type != 'without_vat':
            amount_string = 'Amount In Words: ' + number_to_words(self.total_with_vat)
            self.ln(-12)
        else:
            self.ln(-8)
            amount_string = 'Amount In Words: ' + number_to_words(self.total)
        amount_string_lines = []
        words = amount_string.split()
        current_line = ""

        for word in words:
            if self.get_string_width(current_line + " " + word) < self.bottom_blank_width:
                current_line += " " + word
            else:
                amount_string_lines.append(current_line.strip())
                current_line = word
        if current_line:
            amount_string_lines.append(current_line.strip())

        for line_string in amount_string_lines:
            self.set_xy(6.5, self.get_y()+4)
            self.cell(self.bottom_blank_width, cell_height, line_string, border=0, align='L', fill=False)

    def print_narration_details(self, cell_height,font_size):
        self.set_font(self.font, "", font_size)
        if len(self.invoice_details.narration_external) > 0:
            narration_lines = []
            temp_line = ''
            for char in self.invoice_details.narration_external:
                if (char == '\n' or char == '\r') and temp_line:
                    narration_lines.append(temp_line.strip())
                    temp_line = ''
                else:
                    temp_line += char
            if temp_line:
                narration_lines.append(temp_line.strip())
                temp_line = ''

            self.ln(2*cell_height)
            self.set_x(6.5)
            self.cell(self.w-13, cell_height*len(narration_lines), '', border=0, align='L', fill=False)
            for line in narration_lines:
                self.set_x(6.5)
                self.cell(self.w-13, cell_height, line, border=0, align='L', fill=False)
                self.ln()

    def header(self):
        self.header_and_customer_details_printer()
        if self.table_header_required:
            self.table_headings_creator(5,8)
            self.master_y_accumulated = self.get_y()

    def table(self):
        cell_height = 5
        image_height = 50
        self.set_font(self.font, "", 8)
        for row in self.data:
            self.set_x(6.5)
            if row[1] % 2 == 0:
                self.set_fill_color(255, 255, 255)
            else:
                self.set_fill_color(243, 241, 241)

            def description_split_lines(description):
                description_lines = []
                words = description.split()
                current_line = ""
                for word in words:
                    if self.get_string_width(current_line + " " + word) < (self.width_details[3] - 1):
                        current_line += " " + word
                    else:
                        description_lines.append(current_line.strip())
                        current_line = word
                if current_line:
                    description_lines.append(current_line.strip())
                return description_lines

            description_lines = description_split_lines(str(row[3]))
            description_line_length = len(description_lines)
            if row[0]:
                image = Image.open(base + 'static/' + row[0])
                width, height = image.size
                image_max_height = 50
                image_max_width = self.width_details[3]
                width_change_percent = (abs(image_max_width - width) / image_max_width) * 100
                height_change_percent = (abs(image_max_height - height) / image_max_height) * 100
                def calculate_revised_size(original_width, original_height, new_width):
                    aspect_ratio = original_width / original_height
                    revised_size = int(new_width / aspect_ratio)
                    return revised_size

                if width_change_percent > height_change_percent:
                    image_max_height = calculate_revised_size(width, height, image_max_width)
                else:
                    image_max_height = 50
                row_height = (description_line_length*cell_height) + (image_max_height + 0)
            else:
                row_height = description_line_length * cell_height
            self.set_text_color(0, 0, 0)
            self.cell(self.width_details[1], row_height, str(row[1]), border=1, align='R', fill=True)
            self.cell(self.width_details[2], row_height, str(row[2]), border=1, align='L', fill=True)
            self.cell(self.width_details[3], row_height, '', border=1, align='L', fill=True)
            if self.print_type != 'without_quantity':
                self.cell(self.width_details[4], row_height, str(row[4]), border=1, align='R', fill=True)
                self.cell(self.width_details[5], row_height, str(row[5]), border=1, align='C', fill=True)
                self.cell(self.width_details[6], row_height, str(row[6]), border=1, align='R', fill=True)
                self.cell(self.width_details[7], row_height, str(row[7]), border=1, align='R', fill=True)
            else:
                self.cell(self.width_details[4], row_height, str(row[4]), border=1, align='C', fill=True)
                self.cell(self.width_details[5], row_height, str(row[5]), border=1, align='R', fill=True)
            current_row_y = self.get_y()
            if row[0]:
                image = Image.open(base + 'static/' + row[0])
                width, height = image.size
                image_max_height = 50
                image_max_width = self.width_details[3]
                width_change_percent = (abs(image_max_width - width) / image_max_width) * 100
                height_change_percent = (abs(image_max_height - height) / image_max_height) * 100
                def calculate_revised_size(original_width, original_height, new_width):
                    aspect_ratio = original_width / original_height
                    revised_size = int(new_width / aspect_ratio)
                    return revised_size

                if width_change_percent > height_change_percent:
                    self.image(base + 'static/' + row[0], w=image_max_width-1, x=self.width_details[1] + self.width_details[2] + 6.5 + 0.2, y=current_row_y + 0.4)
                    image_max_height = calculate_revised_size(width, height, image_max_width)
                else:
                    self.image(base + 'static/' + row[0], h=image_max_height,x=self.width_details[1]+self.width_details[2]+6.5+0.2, y=current_row_y+0.4)
                self.set_xy(self.width_details[1]+self.width_details[2]+6.5, current_row_y+image_max_height+1)
                for lines in description_lines:
                    self.cell(self.width_details[3], cell_height, str(lines), border=0, align='L', fill=False)
                    self.set_xy(self.width_details[1]+self.width_details[2]+6.5,self.get_y()+cell_height)
            else:
                self.set_xy(self.width_details[1]+self.width_details[2]+6.5, current_row_y)
                for lines in description_lines:
                    self.cell(self.width_details[3], cell_height, str(lines), border=0, align='L', fill=False)
                    self.set_xy(self.width_details[1]+self.width_details[2]+6.5,self.get_y()+cell_height)
            self.master_y_accumulated += row_height
            self.set_xy(6.5,self.master_y_accumulated)

        self.table_header_required = False
        if self.print_type != 'without_quantity':
            self.print_total_amount_details(cell_height,8)
        self.print_narration_details(cell_height,8)

    def footer(self):
        self.set_y(-12)
        self.set_x(6.5)
        self.set_text_color(0, 0, 0)
        self.cell(self.w-13, 0, '', 'T', 1, 'C')
        self.ln(2)
        self.set_x(6.5)
        self.set_font(self.font, 'B', 8)
        self.cell(self.w-13, 0, 'Page %s' % self.page_no(), 0, 0, 'C')
        self.ln(2)
        self.set_x(6.5)
        self.set_font('Arial', '', 8)
        self.cell(self.w-13, 0, 'Salesman Name: ' + self.salesman_data.salesman_name, 0, 0, 'L')
        self.ln(3.5)
        self.set_x(6.5)
        self.set_font('Arial', '', 7)
        self.cell(self.w-13, 0, 'Printed on ' + self.footer_print_date_time + ' | All the above prices are in UAE Dirhams. | Above quoted items are subject to prior sales. |', 0, 0, 'L')
