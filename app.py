import face_recognition
from face_recognition.api import face_encodings
from flask import Flask, request, send_from_directory, jsonify
from glob import glob
import uuid
import json

server = Flask(__name__)


def load_and_encode(file):
  return face_recognition.face_encodings(face_recognition.load_image_file(file))[0]

def compare_faces(f1, f2):
  return face_recognition.compare_faces([f1], f2)[0]

@server.route('/ping')
def test():
  return "pong"


@server.route('/img/<filename>', methods=["GET"])
def img(filename):
  return send_from_directory('data', filename)

@server.route('/add', methods=["POST"])
def add():
  image_file = request.files.get('image')
  name = request.form.get('name')
  file_name = f'{name}$${uuid.uuid1()}$${image_file.filename}'
  image_file.save(f'./data/{file_name}')
  return {
      "name": name,
      "img_url": f"/img/{file_name}",
  }


@server.route('/search', methods=["POST"])
def search():
  image_file = request.files.get('image')
  persons = [{
      "image_enc": load_and_encode(p_img),
      "name": p_img.split("$$")[0].split("/")[-1],
      "img_url": f"/img/{p_img}"
  } for p_img in glob('data/*')]
  image_file_enc = load_and_encode(image_file)
  matches = [{"name": person['name'], "img_url": person['img_url']}
             for person in persons if compare_faces(person['image_enc'], image_file_enc)]
  return jsonify(matches)
