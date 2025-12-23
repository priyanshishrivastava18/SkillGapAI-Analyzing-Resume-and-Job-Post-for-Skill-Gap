from flask import Flask, render_template, request
import os
import PyPDF2
import docx

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf", "docx"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------- File Check ----------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------- Text Extraction ----------
def extract_text(filepath):
    ext = filepath.rsplit(".", 1)[1].lower()
    text = ""

    if ext == "txt":
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

    elif ext == "pdf":
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""

    elif ext == "docx":
        document = docx.Document(filepath)
        for para in document.paragraphs:
            text += para.text + "\n"

    return text.strip()


# ---------- Route ----------
@app.route("/", methods=["GET", "POST"])
def index():
    resume_text = ""
    jd_text = ""
    message = ""

    if request.method == "POST":
        doc_type = request.form.get("doc_type")
        file = request.files.get("document")

        if not file or file.filename == "":
            message = "❌ No file selected"

        elif not allowed_file(file.filename):
            message = "❌ Only TXT, PDF, DOCX allowed"

        else:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)
            extracted_text = extract_text(filepath)

            if doc_type == "resume":
                resume_text = extracted_text
                message = "✅ Resume uploaded successfully"
            else:
                jd_text = extracted_text
                message = "✅ Job Description uploaded successfully"

    return render_template(
        "index.html",
        resume_text=resume_text,
        jd_text=jd_text,
        message=message
    )


if __name__ == "__main__":
    app.run(debug=True)

