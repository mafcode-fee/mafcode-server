import mongoengine_goodjson as good_mongo
import mongoengine as mongo
from mongoengine.fields import StringField
from enum import Enum, unique

class User(good_mongo.Document):
  email = mongo.EmailField(unique=True)
  password = mongo.StringField()
  first_name = mongo.StringField()
  last_name = mongo.StringField()

class Person(good_mongo.Document):
  encodeing_hash = mongo.StringField()
  is_found = mongo.BooleanField(default=False)
  photos_ids = mongo.ListField(mongo.StringField)


class ReportTypes(Enum):
  FOUND = "FOUND"
  MISSING = "MISSING"

class Report(good_mongo.Document):
  report_type = mongo.EnumField(ReportTypes, required=True)
  photo_id = mongo.StringField()
  matched_person = mongo.ObjectIdField()
  name = mongo.StringField()
  last_seen_location = mongo.GeoPointField()
  age = mongo.IntField()
  clothing = mongo.StringField()
  notes = mongo.StringField()
