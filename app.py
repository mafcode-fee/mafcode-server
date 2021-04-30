import jwt
from flask import Flask, request, jsonify
import pymongo
import urllib
import os
import face_recognition
from flask import Flask, json, request, Response, send_from_directory, jsonify, g
from flask_mongoengine import MongoEngine
from glob import glob
import uuid
from flask_expects_json import expects_json
import schemas
from werkzeug.security import generate_password_hash, check_password_hash
from jsonschema.exceptions import ValidationError
from jsonschema import validate
import json
import models
server = Flask(__name__)


def get_from_env_or(key, deafult):
  return os.environ.get(key) if key in os.environ else deafult


FILES_DIR = get_from_env_or(key="FILES_DIR", deafult="./data/files")
DB_HOST = get_from_env_or(key="DB_HOST", deafult="localhost")

os.makedirs(FILES_DIR, exist_ok=True)

server.config['MONGODB_SETTINGS'] = {
    "db": "mafcode",
    "host": DB_HOST
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

def getFormData():
  out = {}
  for keyValue in request.form:
    out[keyValue] = request.form[keyValue]
  return out

def validateWithExHandling(data, schema):
  try:
    validate(data, schema)
  except ValidationError as e:
    return e
  
  return "valid"


@server.route('/ping')
def test():
  return "pong"

@server.route('/img/<image_id>', methods=["GET"])
def img(image_id):
  return send_from_directory(FILES_DIR, image_id)

def add_report(type: models.ReportTypes):
  data = validate_json(request.form.get('payload'), schemas.REPORT)
  image_file = request.files.get('image')
  image_ext = image_file.filename.split(".")[-1]
  image_id = str(uuid.uuid4()) + '.' + image_ext
  image_file.save(os.path.join(FILES_DIR, image_id))
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

@server.route('/reports', methods=["GET"])
def get_all_reports():
  reports = models.Report.objects.all()
  return Response(reports.to_json(), mimetype='application/json')

@server.route('/reports/<report_id>', methods=["GET"])
def get_report(report_id):
  report = models.Report.objects.get(id=report_id)
  return Response(report.to_json(), mimetype='application/json')

@server.route('/reports/<report_id>/matchings', methods=["GET"])
def get_matching_reports(report_id):
  report = models.Report.objects.get(id=report_id)
  report_image_enc = load_and_encode(os.path.join(FILES_DIR, report.photo_id))

  target_report_type = models.ReportTypes.FOUND
  if report.report_type == models.ReportTypes.FOUND:
    target_report_type = models.ReportTypes.MISSING

  target_reports = models.Report.objects(report_type=target_report_type).all()
  image_encodings_w_reports = [{
      "report": r,
      "enc": load_and_encode(os.path.join(FILES_DIR, r.photo_id))
  } for r in target_reports]
  matches = [json.loads(enc_r["report"].to_json())
             for enc_r in image_encodings_w_reports
             if compare_faces(enc_r['enc'], report_image_enc)]
  return Response(json.dumps(matches), mimetype='application/json')


@server.route("/register", methods=["POST"])
def register():
  
  data = getFormData()
  status = str(validateWithExHandling(data, schemas.REGISTER))
  if status != "valid":
    return status

  email = data['email']
  user = models.User.objects(email=email)
  
  if user:
    return jsonify(message="This email already exists"), 409
  
  else:
    hashedPassword = generate_password_hash(data["password"], method='pbkdf2:sha1', salt_length=8)
    user = models.User(
          email=email,
          password = hashedPassword,
          first_name = data["first_name"],
          last_name = data["last_name"]
      )
    user.save()
    return jsonify(message="User added sucessfully"), 201


key = "key"
@server.route("/login", methods=["POST"])
def login():
  data = getFormData()
  email = data["email"]
  password = data["password"]

  user = models.User.objects(email=email).first()
  #return user.password
  if user:
    if ( check_password_hash(user.password,password)):
      token = jwt.encode({"email": user.email}, key ,algorithm="HS256")
      print(token)
      return jsonify(message="Login Succeeded!", access_token=token), 201
    else:
      return jsonify(message="Incorrect password"), 401
  else:
    return jsonify(message="This email isn't registered!! :)"), 401


@server.route("/checkDB", methods=["GET"])
def showDB():
  dbCheck = []
  for user in models.User.objects:
    dbCheck.append(user)

  return jsonify(dbCheck)



@server.route("/validate", methods=['POST'])
def validateFormData():
  data = getFormData()
  try:
    validate(data, schemas.REGISTER)
  except ValidationError as e:
    return str(e)
  
  return "valid"



if __name__ == "__main__":
  server.run(host="0.0.0.0", port=4000 , debug = True)
