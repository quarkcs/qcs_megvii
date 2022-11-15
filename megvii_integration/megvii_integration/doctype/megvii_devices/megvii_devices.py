# Copyright (c) 2022, QCS and contributors
# For license information, please see license.txt

import frappe
import requests
import json, hashlib
from frappe.model.document import Document
from hashlib import sha256
from frappe.utils import today
from datetime import datetime

class MegviiDevices(Document):
	def validate(self):
		

		url = self.device_url + "/api/auth/login/challenge?username=" + self.device_username

		payload={}
		files={}
		headers = {}

		response = requests.request("GET", url, headers=headers, data=payload, files=files)

		
		data_dump = json.loads(response.text)
		#frappe.errprint(data_dump['salt'])
		#frappe.errprint(data_dump['challenge'])
		h_string = str(self.device_password) + str(data_dump['salt']) + str(data_dump['challenge'])
		
		h_pass = sha256((h_string.encode('utf-8')))
		h_pass = hashlib.sha256(h_string.encode("utf-8")).hexdigest()
		#frappe.errprint(str(h_pass))
		

		url = self.device_url + "/api/auth/login"

		payload = json.dumps({
		"session_id": data_dump['session_id'],
		"username": "admin",
		"password": str(h_pass)
		})
		headers = {
		'Content-Type': 'application/json'
		}

		response = requests.request("POST", url, headers=headers, data=payload)

		#frappe.errprint(response.text)
		data_dump = json.loads(response.text)
		if data_dump['status'] == 200:
			if self.server_actions == "Read":
				url = self.device_url + "/api/passes/query"
				payload = json.dumps({
				"limit": "1000"
				})
				headers = {
				'Content-Type': 'application/json',
				'Cookie': 'sessionID=' + data_dump['session_id']
				}
				#frappe.errprint(headers)
				response = requests.request("POST", url, headers=headers, data=payload)
				frappe.errprint(response.text)

			if self.server_actions == "Write":
				url = self.device_url + "/api/subscribe/push"
				payload = json.dumps({
				"server_uri": self.api_url,
				"enabled": 1,
				"method": "POST"
				})
				headers = {
				'Content-Type': 'application/json',
				'Cookie': 'sessionID=' + data_dump['session_id']
				}
				#frappe.errprint(headers)
				response = requests.request("PUT", url, headers=headers, data=payload)
				frappe.errprint(response.text)


@frappe.whitelist(allow_guest=True)
def mgv_add_event(**kwargs):
	ec = frappe.new_doc("Employee Checkin")
	ec.employee = kwargs["person_id"]
	ec.rt = kwargs["recognition_type"]
	ec.custom_time = kwargs["timestamp"]
	ec.save()


def megvi_action(employee, method=None):
	if employee.megvi_actions == "Create":
		create_mgv_data(employee)
	if employee.megvi_actions == "Delete":
		delete_mgv_data(employee)

	
def create_mgv_data(employee):
	if employee.device:
		mgv = frappe.get_doc("Megvii Devices", employee.device)
		url = mgv.device_url + "/api/auth/login/challenge?username=" + mgv.device_username

		payload={}
		files={}
		headers = {}

		response = requests.request("GET", url, headers=headers, data=payload, files=files)

			
		data_dump = json.loads(response.text)
		#frappe.errprint(data_dump['salt'])
		#frappe.errprint(data_dump['challenge'])
		h_string = str(mgv.device_password) + str(data_dump['salt']) + str(data_dump['challenge'])
			
		h_pass = sha256((h_string.encode('utf-8')))
		h_pass = hashlib.sha256(h_string.encode("utf-8")).hexdigest()
		#frappe.errprint(str(h_pass))
			

		url = mgv.device_url + "/api/auth/login"

		payload = json.dumps({
		"session_id": data_dump['session_id'],
		"username": "admin",
		"password": str(h_pass)
		})
		headers = {
		'Content-Type': 'application/json'
		}

		response = requests.request("POST", url, headers=headers, data=payload)

		#frappe.errprint(response.text)
		data_dump = json.loads(response.text)
			
		if data_dump['status'] == 200:
			if employee.image:
				img_details = frappe.db.get_value("File", {"file_url": employee.image}, ["file_name", "content_hash"])
				if img_details and img_details[0] and img_details[1]:
					is_private = employee.image.startswith("/private/files/")
					frappe.errprint(get_files_path(img_details[0]))
					with open(get_files_path(img_details[0], is_private=is_private), "rb") as image_file:
						b64_string = base64.b64encode(image_file.read())
			#with open(content.file_url, "rb") as img_file:
			#	b64_string = base64.b64encode(img_file.read())
			#frappe.errprint(b64_string)
			url = mgv.device_url + "/api/persons/item"
			img_api = "data:image/jpg;base64," + str(b64_string)[2:]
			#frappe.errprint(img_api)
			payload = json.dumps({
			"recognition_type": "staff",
			"is_admin": 0,
			"id": employee.name,
			"person_name": employee.first_name,
			"group_list": ["1"],
			"face_list": [{"idx":"0", "data": img_api}]
			})
			headers = {
			'Content-Type': 'application/json',
			'Cookie': 'sessionID=' + data_dump['session_id']
			}
			#frappe.errprint(headers)

			response = requests.request("POST", url, headers=headers, data=payload)

			#frappe.errprint(response.text)


def delete_mgv_data(employee):
	#frappe.errprint("inside delete")
	if employee.device:
		mgv = frappe.get_doc("Megvii Devices", employee.device)
		url = mgv.device_url + "/api/auth/login/challenge?username=" + mgv.device_username

		payload={}
		files={}
		headers = {}

		response = requests.request("GET", url, headers=headers, data=payload, files=files)

			
		data_dump = json.loads(response.text)
		#frappe.errprint(data_dump['salt'])
		#frappe.errprint(data_dump['challenge'])
		h_string = str(mgv.device_password) + str(data_dump['salt']) + str(data_dump['challenge'])
			
		h_pass = sha256((h_string.encode('utf-8')))
		h_pass = hashlib.sha256(h_string.encode("utf-8")).hexdigest()
		#frappe.errprint(str(h_pass))
			

		url = mgv.device_url + "/api/auth/login"

		payload = json.dumps({
		"session_id": data_dump['session_id'],
		"username": "admin",
		"password": str(h_pass)
		})
		headers = {
		'Content-Type': 'application/json'
		}

		response = requests.request("POST", url, headers=headers, data=payload)

		#frappe.errprint(response.text)
		data_dump = json.loads(response.text)
			
		if data_dump['status'] == 200:

			url = mgv.device_url + "/api/persons/item/"
				
			payload = json.dumps({
			"recognition_type": "staff",
			"person_list": [{"id":employee.name}],
			#"person_name": self.first_name,
			#"group_list": ["1"],
			#"face_list": [{"idx":"0", "data": img_api}]
			})
			headers = {
			'Content-Type': 'application/json',
			'Cookie': 'sessionID=' + data_dump['session_id']
			}
			#frappe.errprint(headers)

			response = requests.request("DELETE", url, headers=headers, data=payload)
			#response = requests.request("DELETE", url, headers=headers)

			#frappe.errprint(response.text)

