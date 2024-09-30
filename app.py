from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from pdf2image import convert_from_path
import os
from datetime import datetime

# Mendefinisikan ukuran halaman F4 (210 x 330 mm)
FOLIO = (8.27 * 72, 13 * 72)  # Ukuran dalam points (1 inci = 72 points)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Ganti dengan kunci rahasia Anda

class PRDForm(FlaskForm):
    title = StringField('Judul', validators=[DataRequired()])
    content = TextAreaField('Konten', validators=[DataRequired()])
    page_size = SelectField('Ukuran Halaman', choices=[('A4', 'A4'), ('F4', 'F4'), ('Letter', 'Letter')])
    submit = SubmitField('Buat PDF')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = PRDForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        page_size = form.page_size.data

        # Menentukan ukuran halaman
        if page_size == 'A4':
            size = A4
        elif page_size == 'Letter':
            size = LETTER
        elif page_size == 'F4':
            size = FOLIO

        # Membuat PDF
        pdf_filename = f"{title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join('static/output/pdf', pdf_filename)

        doc = SimpleDocTemplate(pdf_path, pagesize=size)
        elements = []
        styles = getSampleStyleSheet()

        # Menambahkan judul
        title_paragraph = Paragraph(f"<b><i>{title}</i></b>", styles['Title'])
        elements.append(title_paragraph)
        elements.append(Spacer(1, 12))

        # Menambahkan konten (menggunakan HTML)
        content_paragraph = Paragraph(content.replace('\n', '<br/>'), styles['BodyText'])
        elements.append(content_paragraph)

        # Menyusun dokumen
        doc.build(elements)

        # Mengonversi PDF menjadi gambar untuk preview
        images = convert_from_path(pdf_path)
        preview_image_filename = f'preview_{title}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        preview_image_path = os.path.join('static/output/image', preview_image_filename)

        # Menyimpan gambar preview
        if images:
            images[0].save(preview_image_path, 'PNG')

        return redirect(url_for('preview', pdf_filename=pdf_filename, preview_image=preview_image_filename))

    return render_template('index.html', form=form)

@app.route('/preview')
def preview():
    pdf_filename = request.args.get('pdf_filename')
    preview_image = request.args.get('preview_image')
    return render_template('preview.html', pdf_filename=pdf_filename, preview_image=preview_image)

@app.route('/download/<pdf_filename>')
def download(pdf_filename):
    return send_file(os.path.join('static/output/pdf', pdf_filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
