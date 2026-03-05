from flask import Flask, request, render_template_string
import os

UPLOAD_FOLDER = "ReceivedFiles"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>AirSend</title>
<style>
body { font-family:sans-serif; text-align:center; margin-top:50px; }
input, button { padding:10px; font-size:16px; margin:10px; }
</style>
</head>
<body>
<h1>AirSend</h1>
<p>Send files from your phone to your PC over Wi-Fi</p>
<form method="POST" enctype="multipart/form-data">
<input type="file" name="file">
<input type="submit" value="Upload">
</form>
{% if message %}
<p style="color:green">{{ message }}</p>
{% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def upload_file():
    message = ""
    if request.method == "POST":
        f = request.files.get("file")
        if f:
            filepath = os.path.join(UPLOAD_FOLDER, f.filename)
            f.save(filepath)
            message = f"File '{f.filename}' uploaded successfully!"
    return render_template_string(HTML_PAGE, message=message)

if __name__ == "__main__":
    # Manually set hotspot IP here (replace with your real hotspot IP)
    HOTSPOT_IP = "192.168.137.1"
    PORT = 8000
    URL = f"http://{HOTSPOT_IP}:{PORT}"
    print(f"AirSend running at {URL}")

    # Show QR code
    import qrcode
    qr = qrcode.QRCode(border=1)
    qr.add_data(URL)
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").show()

    # Start server
    app.run(host="0.0.0.0", port=PORT, threaded=True)