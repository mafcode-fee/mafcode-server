import os
import face_recognition
from flask import Flask, json, request, Response, send_from_directory, jsonify, g
from flask_mongoengine import MongoEngine
from glob import glob
import uuid
from flask_expects_json import expects_json
import schemas
from jsonschema import validate
import json
import models
server = Flask(__name__)

os.makedirs("./data/files", exist_ok=True)

server.config['MONGODB_SETTINGS'] = {
    "db": "mafcode",
}
db = MongoEngine(server)

def validate_json(json_string, schema):
  data = json.loads(json_string)
  validate(data, schema)
  return data

def load_and_encode(file):
  return face_recognition.face_encodings(face_recognition.load_image_file(file))[0]

def compare_faces(f1, f2):
  return face_recognition.compare_faces([f1], f2)[0]

@server.route('/ping')
def test():
  return "pong"

@server.route('/img/<image_id>', methods=["GET"])
def img(image_id):
  return send_from_directory('data/files', image_id)

def add_report(type: models.ReportTypes):
  data = validate_json(request.form.get('payload'), schemas.REPORT)
  image_file = request.files.get('image')
  image_ext = image_file.filename.split(".")[-1]
  image_id = str(uuid.uuid4()) + '.' + image_ext
  image_file.save(f'./data/files/{image_id}')
  report = models.Report(
      report_type=type,
      name=data.get("name"),
      age=data.get("age"),
      clothing=data.get("clothing"),
      notes=data.get("notes"),
      photo_id=image_id
  )
  report.save()
  return Response(report.to_json(), mimetype='application/json')

@server.route('/reports/missing', methods=["POST"])
def add_missing_report():
  return add_report(models.ReportTypes.MISSING)

@server.route('/reports/found', methods=["POST"])
def add_found_report():
  return add_report(models.ReportTypes.FOUND)

@server.route('/reports/<report_id>/matchings', methods=["GET"])
def get_matching_reports(report_id):
  report = models.Report.objects.get(id=report_id)
  report_image_enc = load_and_encode(f'./data/files/{report.photo_id}')

  target_report_type = models.ReportTypes.FOUND
  if report.report_type == models.ReportTypes.FOUND:
    target_report_type = models.ReportTypes.MISSING

  target_reports = models.Report.objects(report_type=target_report_type).all()
  image_encodings_w_reports = [{
      "report": r,
      "enc": load_and_encode(f'./data/files/{r.photo_id}')
  } for r in target_reports]
  matches = [json.loads(enc_r["report"].to_json())
             for enc_r in image_encodings_w_reports
             if compare_faces(enc_r['enc'], report_image_enc)]
  return Response(json.dumps(matches), mimetype='application/json')


# @server.route('/add', methods=["POST"])
# def add():
#   image_file = request.files.get('image')
#   name = request.form.get('name')
#   file_name = f'{name}$${uuid.uuid1()}$${image_file.filename}'
#   file_name = file_name
#   image_file.save(f'./data/{file_name}')
#   return {
#       "name": name,
#       "img_url": f"/img/{file_name}",
#   }

# @server.route('/search', methods=["POST"])
# def search():
#   image_file = request.files.get('image')
#   persons = [{
#       "image_enc": load_and_encode(p_img),
#       "name": p_img.split("$$")[0].split("/")[-1],
#       "img_url": f"/img/" + p_img.split("/")[-1]
#   } for p_img in glob('data/*')]
#   image_file_enc = load_and_encode(image_file)
#   matches = [{"name": person['name'], "img_url": person['img_url']}
#              for person in persons
#              if compare_faces(person['image_enc'], image_file_enc)]
#   return jsonify(matches)
if __name__ == "__main__":
  server.run(host="0.0.0.0", port=4000)
