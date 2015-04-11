#!/usr/bin/env python3

import json
import requests
import logging


class loan(dict):
	'A simple class to represent a LendingClub loan. This is a wrapper implementing comparison methods to allow sorting'

	def __init__(self, *args, **kw):
		super(loan,self).__init__(*args, **kw)
		self.quality = 100

	def __setitem__(self, key, value):
		if key == 'quality':
			self.quality = value
		else:
			super(loan,self).__setitem__(key, value)
		return
	def __getitem__(self, key):
		if key == 'quality':
			return self.quality
		return super(loan,self).__getitem__(key)

	def __lt__(self, other):
		return self.quality < other.quality
	def __le__(self, other):
		return self.quality <= other.quality
	def __eq__(self, other):
		return self.quality == other.quality
	def __nq__(self, other):
		return self.quality != other.quality
	def __gt__(self, other):
		return self.quality > other.quality
	def __ge__(self, other):
		return self.quality >= other.quality

	def set_quality(self, quality):
		self.quality = quality


class investor:
	'A simple class to interact with your LendingClub account'

	def __init__(self, iid, authKey, investAmt=25):
		self.iid = iid
		self.headers = { 'Authorization' : authKey, 'Accept' : 'application/json', 'Content-type' : 'application/json' }
		self.investAmt = investAmt
		self.logger = logging.getLogger(__name__)

	def __execute_get(self, url):
		response = requests.get(url, headers=self.headers)
		if not response:
			self.logger.error('Error occurred during GET: %s\n  HTTP response: %s' % (url, response.status_code))
		return response.text

	def __execute_post(self, url, payload=None):
		response = requests.post(url, data=payload, headers=self.headers)
		if not response:
			self.logger.error('Error occurred during POST: %s\n  HTTP response: %s' % (url, response.status_code))
		return response.text

	def get_cash(self):
		cash = self.__execute_get('https://api.lendingclub.com/api/investor/v1/accounts/%s/availablecash' % (self.iid))
		if not cash:
			return 0
		return json.loads(cash)['availableCash']

	def get_new_loans(self, showAll=False):
		listings_json = self.__execute_get('https://api.lendingclub.com/api/investor/v1/loans/listing?showAll=%s' % (showAll))
		raw_loans = json.loads(listings_json)['loans']
		return [ loan(raw_loan) for raw_loan in raw_loans ]

	def get_my_note_ids(self):
		mynotes_json = self.__execute_get('https://api.lendingclub.com/api/investor/v1/accounts/%s/notes' % (self.iid))
		return [ x['loanId'] for x in json.loads(mynotes_json)['myNotes'] ]

	def submit_order(self, loans):
		loan_dict = [ { 'loanId' : loan['id'], 'requestedAmount' : self.investAmt } for loan in loans ]
		order = json.dumps({ "aid" : self.iid, "orders" : loan_dict })
		self.__execute_post('https://api.lendingclub.com/api/investor/v1/accounts/%s/orders' % (self.iid), payload=order)

	def add_funds(self, amount):
		payload = json.dumps({ 'amount' : amount, 'transferFrequency' : 'LOAD_NOW' })
		self.__execute_post('https://api.lendingclub.com/api/investor/v1/accounts/%s/funds/add' % (self.iid), payload=payload)

