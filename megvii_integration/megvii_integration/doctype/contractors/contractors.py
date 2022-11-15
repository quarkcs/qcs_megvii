# Copyright (c) 2022, QCS and contributors
# For license information, please see license.txt

import frappe
import requests
import json, hashlib
from frappe.model.document import Document
from hashlib import sha256
from frappe.utils import today
from datetime import datetime

class Contractors(Document):
	def validate(self):
		device = frappe.get_doc("Megvii Devices", self.device)

		url = device.device_url + "/api/auth/login/challenge?username=" + device.device_username

		payload={}
		files={}
		headers = {}

		response = requests.request("GET", url, headers=headers, data=payload, files=files)

		
		data_dump = json.loads(response.text)
		#frappe.errprint(data_dump['salt'])
		#frappe.errprint(data_dump['challenge'])
		h_string = str(device.device_password) + str(data_dump['salt']) + str(data_dump['challenge'])
		
		h_pass = sha256((h_string.encode('utf-8')))
		h_pass = hashlib.sha256(h_string.encode("utf-8")).hexdigest()
		#frappe.errprint(str(h_pass))
		

		url = device.device_url + "/api/auth/login"

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
			
			url = device.device_url + "/api/groups/item"

			payload = json.dumps({
			"group_name": self.company_name,
			"schedule_id": "1"
			})
			headers = {
			'Content-Type': 'application/json',
			'Cookie': 'sessionID=' + data_dump['session_id']
			}
			frappe.errprint(headers)

			response = requests.request("POST", url, headers=headers, data=payload)
			data_dump = json.loads(response.text)
			frappe.errprint(response.text)
			self.device_group_id = data_dump['id']