# file_server_qr_airsend.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
import os
import socket
import qrcode

UPLOAD_FOLDER = "ReceivedFiles"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve the upload form with app name AirSend
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
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
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        if ctype == 'multipart/form-data':
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST'})
            file_item = form['file']
            if file_item.filename:
                filename = os.path.basename(file_item.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                with open(filepath, 'wb') as f:
                    f.write(file_item.file.read())
                self.send_response(200)
                self.end_headers()
                self.wfile.write(f"File '{filename}' uploaded successfully!".encode())
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"No file uploaded")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid request")

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

if __name__ == '__main__':
    PORT = 8000
    local_ip = get_local_ip()
    url = f"http://{local_ip}:{PORT}"
    print(f"AirSend Server running at {url}")

    # Generate and show QR code on PC
    qr = qrcode.QRCode(border=1)
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img.show()

    # Start HTTP server
    server = HTTPServer(('0.0.0.0', PORT), SimpleHTTPRequestHandler)
    server.serve_forever()