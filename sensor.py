import bluetooth
import datetime
import json
from peewee import *
import requests
import sched
import sys
import time

from datetime import timedelta
from sqlite3 import Error


db = SqliteDatabase("./scanner-status.db", pragmas={'foreign_keys': 1})
s = sched.scheduler(time.time, time.sleep)


class BaseModel(Model):
    class Meta:
        database = db


class Hubitat(BaseModel):
    id = AutoField()
    hubitat_ip = CharField()
    cloud_auth = CharField(null=True)
    maker_api = CharField()
    access_token = CharField()


class Device(BaseModel):
    device_id = CharField(primary_key=True)
    mac_address = CharField()
    name = CharField()


class Status(BaseModel):
    id = AutoField()
    device = ForeignKeyField(Device, backref='statuses', unique=True)
    last_update = DateTimeField(default=datetime.datetime.now)


def main():
    db.connect()
    db.create_tables([Hubitat, Device, Status])

    hubitat = Hubitat.create(
        hubitat_ip="",  # hubitat IP
        cloud_auth="",  # hubitat cloud auth string. Leave blank if using local connection
        maker_api="",  # hubitat maker api
        access_token=""  # hubitat access token. found after ?access_token
    )

    if hubitat.cloud_auth is None and hubitat.cloud_auth.strip() != "":
        url = hubitat.hubitat_ip + "/apps/api/" + hubitat.maker_api + \
              "/devices/all?access_token=" + hubitat.access_token
    else:
        url = hubitat.hubitat_ip + "/api/" + hubitat.cloud_auth + "/apps/" + \
              hubitat.maker_api + "/devices/all?access_token=" + hubitat.access_token

    data = send_request(url)
    now = datetime.datetime.now()

    for device in data:
        id = device.get("id")
        device_query = Device.select().where(Device.device_id == id)
        if "type" in device:
            if device.get("type") == "Virtual Phone Presence Plus" and not device_query.exists():
                Device.create(
                    device_id=id,
                    mac_address=device.get("attributes", {}).get("BluetoothMacAddress"),
                    name=device.get("name")
                )
                Status.create(
                    device_id=device.get("id"),
                    last_update=now
                )
                print (device.get("name"), "was inserted into db")

    nearby_devices = bluetooth.discover_devices()
    for device in Device.select(Device, Status).join(Status, attr='status'):
        if device.mac_address.upper().strip() in nearby_devices:
            is_nearby = True
        else:
            is_nearby = False
        cloud_status = get_cloud_status(device.device_id, hubitat)
        if is_nearby:
            device.status.last_update = str(now)
            device.save()
            print (device.status.last_update)
        if is_nearby != cloud_status:
            if is_nearby:
                print("turning " + device.name + " on.")
                if hubitat.cloud_auth is None or hubitat.cloud_auth.strip() == "":
                    new_url = hubitat.hubitat_ip + "/apps/api/" + hubitat.maker_api + "/devices/" + \
                        device.device_id + "/on?access_token=" + hubitat.access_token
                else:
                    new_url = hubitat.hubitat_ip + "/api/" + hubitat.cloud_auth + "/apps/" + \
                        hubitat.maker_api + "/devices/" + device.device_id + "/on/?access_token=" + hubitat.access_token
                print ("sending request: " + new_url)
                send_request(new_url)
            elif is_five_min_ago_plus(device.device_id):
                print("turning " + device.name + " off.")
                if hubitat.cloud_auth is None or hubitat.cloud_auth.strip() == "":
                    new_url = hubitat.hubitat_ip + "/api/" + hubitat.cloud_auth + "/apps/" + hubitat.maker_api + \
                        "/devices/" + device.device_id + "/off/?access_token=" + hubitat.access_token
                else:
                    new_url = hubitat.hubitat_ip + "/api/" + hubitat.cloud_auth + "/apps/" + \
                        hubitat.maker_api + "/devices/" + device.device_id + \
                        "/off/?access_token=" + hubitat.access_token
                print ("sending request: " + new_url)
                send_request(new_url)
    db.close()
    print ("connection to db closed")
    s.enter(30, 1, main())


# Sends request to Hubitat and returns response
def send_request(url):
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:
        print(e)
        print ("Hubitat update failed. Trying again")
        send_request(url)
    if not r.status_code == requests.codes.ok:
        now = datetime.datetime.now()
        print(now), "Hubitat update failed with status code ", r.status_code
        if int(r.status_code) == '500':
            print(now), "Is this really a Virutal Switch?"
    else:
        return r.json()


# Gets the current status of device from Hubitat
def get_cloud_status(device_id, hubitat):
    if hubitat.cloud_auth is None or hubitat.cloud_auth.strip() == "":
        url = hubitat.hubitat_ip + "/apps/api/" + hubitat.maker_api + "/devices/" + \
              device_id + "?access_token=" + hubitat.access_token
    else:
        url = hubitat.hubitat_ip + "/api/" + hubitat.cloud_auth + "/apps/" + \
              hubitat.maker_api + "/devices/" + device_id + "?access_token=" + hubitat.access_token

    data = send_request(url)
    value = data.get('attributes', {})[2].get('currentValue')
    return value


# Checks if timestamp is less than 5 minutes ago
def is_five_min_ago_plus(device_id):
    timestamp = Status.get(Status.device_id == device_id).last_update
    five_min_ago = datetime.datetime.now() - datetime.timedelta(minutes=-5)
    return timestamp >= five_min_ago


if __name__ == '__main__':
    main()
