from flask import Flask, render_template, request, send_from_directory, redirect
import easyocr
import os
import cv2
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# -------- UPLOAD FOLDER --------
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# -------- TEMPORARY REPORTS LIST --------
reports_list = []

# -------- OCR --------
reader = easyocr.Reader(['en'])

# -------- GROQ CLIENT --------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# -------- AI FUNCTION --------
# -------- AI FUNCTION --------
def get_ai_response(text):
    try:
        prompt = f"""
You are a medical information assistant.

Identify the medicine from the extracted text and provide clear,
simple and useful information.

Return EXACTLY these five lines and nothing else:

Medicine Name: [medicine name]
Use: [main medical uses of the medicine]
Dosage: [dosage information from the label; if not available, write "As directed by the physician"]
Side Effects: [common side effects]
ALERT: [important safety information]

IMPORTANT RULES:
1. Use the extracted text to identify the medicine.
2. You may use your general medical knowledge to explain the common uses
   and common side effects of the identified medicine.
3. Do NOT invent a specific dosage. If the label does not provide a
   specific dosage, write "As directed by the physician".
4. Keep the language simple and easy to understand.
5. Do not use markdown, bullets, asterisks, or code blocks.
6. Do not add any extra explanation outside the five required lines.
7. For ALERT, include important precautions such as prescription use
   or relevant safety warnings.

Extracted Text:
{text}
"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        ai_response = response.choices[0].message.content

        print("\n===== GROQ RESPONSE =====")
        print(ai_response)
        print("=========================\n")

        return ai_response

    except Exception as e:
        print("Groq Error:", e)
        return f"Error: {str(e)}"


# -------- FORMAT FUNCTION --------
def format_output(text):

    data = {
        "name": "",
        "use": "",
        "dosage": "",
        "effects": "",
        "alert": ""
    }

    current_field = None

    for line in text.splitlines():

        # Remove unnecessary markdown formatting
        line = line.strip()
        line = line.replace("**", "")
        line = line.replace("__", "")
        line = line.replace("`", "")
        line = line.strip()

        if not line:
            continue

        lower_line = line.lower()

        # Medicine Name
        if lower_line.startswith("medicine name"):

            data["name"] = line.split(":", 1)[-1].strip()
            current_field = "name"

        # Use
        elif lower_line.startswith("use") or lower_line.startswith("uses"):

            data["use"] = line.split(":", 1)[-1].strip()
            current_field = "use"

        # Dosage
        elif lower_line.startswith("dosage"):

            data["dosage"] = line.split(":", 1)[-1].strip()
            current_field = "dosage"

        # Side Effects
        elif lower_line.startswith("side effects"):

            data["effects"] = line.split(":", 1)[-1].strip()
            current_field = "effects"

        # Alert / Warning
        elif lower_line.startswith("alert") or lower_line.startswith("warning"):

            data["alert"] = line.split(":", 1)[-1].strip()
            current_field = "alert"

        # Handle multiline responses
        else:

            if current_field == "use":
                data["use"] += " " + line

            elif current_field == "dosage":
                data["dosage"] += " " + line

            elif current_field == "effects":
                data["effects"] += " " + line

            elif current_field == "alert":
                data["alert"] += " " + line

    # Remove extra spaces
    for key in data:
        data[key] = data[key].strip()

    return data


# -------- HOME ROUTE --------
@app.route("/", methods=["GET", "POST"])
def home():

    data = {}

    if request.method == "POST":

        file = request.files.get("image")

        if file:

            # Save uploaded image
            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                file.filename
            )

            file.save(filepath)

            # -------- IMAGE PROCESSING --------
            img = cv2.imread(filepath)

            gray = cv2.cvtColor(
                img,
                cv2.COLOR_BGR2GRAY
            )

            gray = cv2.GaussianBlur(
                gray,
                (5, 5),
                0
            )

            # Save processed image
            processed_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                "processed.png"
            )

            cv2.imwrite(
                processed_path,
                gray
            )

            # -------- OCR --------
            result = reader.readtext(processed_path)

            extracted_text = ""

            for detection in result:
                extracted_text += detection[1] + " "

            print("\n===== EXTRACTED TEXT =====")
            print(extracted_text)
            print("==========================\n")

            # -------- AI ANALYSIS --------
            if extracted_text.strip() != "":

                ai_output = get_ai_response(
                    extracted_text
                )

                data = format_output(
                    ai_output
                )

            else:

                print("No text detected in image.")

    return render_template(
        "index.html",
        data=data
    )


# -------- REPORTS ROUTE --------
@app.route("/reports", methods=["GET", "POST"])
def reports():

    if request.method == "POST":

        file = request.files.get("file")

        if file:

            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                file.filename
            )

            file.save(filepath)

            reports_list.append(
                (
                    len(reports_list),
                    file.filename
                )
            )

    return render_template(
        "reports.html",
        reports=reports_list
    )


# -------- VIEW FILE --------
@app.route("/uploads/<filename>")
def view_file(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# -------- DOWNLOAD FILE --------
@app.route("/download/<filename>")
def download_file(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=True
    )


# -------- DELETE FILE --------
@app.route("/delete/<int:id>")
def delete_file(id):

    if 0 <= id < len(reports_list):

        filename = reports_list[id][1]

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        if os.path.exists(filepath):
            os.remove(filepath)

        reports_list.pop(id)

    return redirect("/reports")


# -------- RUN APPLICATION --------
if __name__ == "__main__":
    app.run(debug=False)