# airsend_modern.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import socket
from io import BytesIO
import qrcode

UPLOAD_FOLDER = "ReceivedFiles"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve the upload page
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"""
        <html>
        <head><title>AirSend</title></head>
        <body style='text-align:center; font-family:sans-serif;'>
        <h1>AirSend</h1>
        <p>Send files from your phone to your PC over Wi-Fi</p>
        <form enctype='multipart/form-data' method='post'>
            <input name='file' type='file'/>
            <input type='submit' value='Upload'/>
        </form>
        </body>
        </html>
        """)

    def do_POST(self):
        # Read raw POST data
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        # Find the filename in the body
        header, file_data = body.split(b"\r\n\r\n", 1)
        filename_line = [line for line in header.split(b"\r\n") if b"filename=" in line][0]
        filename = filename_line.split(b'filename="')[1].split(b'"')[0].decode()

        # Remove the trailing boundary
        file_content = file_data.rsplit(b"\r\n--", 1)[0]

        # Save file
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, 'wb') as f:
            f.write(file_content)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"File '{filename}' uploaded successfully!".encode())

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

if __name__ == "__main__":
    PORT = 8000
    local_ip = get_local_ip()
    url = f"http://{local_ip}:{PORT}"
    print(f"AirSend Server running at {url}")

    # Show QR code
    qr = qrcode.QRCode(border=1)
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img.show()

    server = HTTPServer(("0.0.0.0", PORT), SimpleHTTPRequestHandler)
    server.serve_forever()