from flask import Flask, request, send_file
from PIL import Image
import numpy as np
import io

app = Flask(__name__)

def read_file(file):
    return file.read()

def write_file(filename, data):
    with open(filename, 'wb') as file:
        file.write(data)

def hide_message(carrier_img, message_img):
    img = np.asarray(carrier_img)
    shape = img.shape

    message_data = read_file(message_img)
    message_data += b'END'
    message_bits = ''.join([format(i,'08b') for i in message_data])

    img = img.flatten()

    for idx, bit in enumerate(message_bits):
        if idx >= len(img):
            break
        val = img[idx]
        val = bin(val)
        val = val[:-1] + bit
        img[idx] = int(val,2)

    img = img.reshape(shape)
    img = Image.fromarray(img)

    return img

def extract_message(img):
    img = np.asarray(img)
    img = img.flatten()
    msg = ""
    idx = 0
    while msg[-3:] != 'END':
        bits = [bin(i)[-1] for i in img[idx:idx+8]]
        bits = ''.join(bits)
        msg += chr(int(bits, 2))
        idx+=8
        if idx > img.shape[0]:
            return None

    b = bytearray()
    b.extend(map(ord, msg))

    return Image.open(io.BytesIO(b))

@app.route('/hide', methods=['POST'])
def hide():
    carrier_img = Image.open(request.files['carrier']).convert('RGB')
    message_img = request.files['message']
    img = hide_message(carrier_img, message_img)
    
    output = io.BytesIO()
    img.save(output, format='PNG')
    output.seek(0)

    return send_file(output, mimetype='image/png')

@app.route('/extract', methods=['POST'])
def extract():
    img = Image.open(request.files['image']).convert('RGB')
    message_img = extract_message(img)

    if message_img is None:
        return {"error": "No hidden message found"}, 400

    output = io.BytesIO()
    message_img.save(output, format='JPEG')
    output.seek(0)

    return send_file(output, mimetype='image/jpeg')

@app.route('/', methods = ['GET'])
def hello():
    return 'hhello'

if __name__ == '__main__':
    app.run(host='0.0.0.0')
