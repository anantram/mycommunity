#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2
import time
import datetime

from google.appengine.ext import db
template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

# Databases

class communitydb(db.Model):
	community_name = db.StringProperty()
	community_pass = db.StringProperty()

class housedb(db.Model):
	house_comm_id = db.StringProperty()
	house_number = db.StringProperty()
	house_pass = db.StringProperty()

class houseownerdb(db.Model):
	house_comm_id = db.StringProperty()
	house_id = db.StringProperty()
	house_owner = db.StringProperty()
	house_contact = db.StringProperty()
	house_status = db.BooleanProperty()
	house_number = db.StringProperty()

class duesdb(db.Model):
	community_id = db.StringProperty()
	house_id = db.StringProperty()
	due_detail = db.StringProperty()
	due_amount = db.IntegerProperty()
	due_month = db.StringProperty()
	due_year = db.StringProperty()
	due_type = db.StringProperty()
	due_created = db.DateTimeProperty()

class paymentsdb(db.Model):
	community_id = db.StringProperty()
	house_id = db.StringProperty()
	payment_detail = db.StringProperty()
	payment_amount = db.IntegerProperty()
	payment_month = db.StringProperty()
	payment_year = db.StringProperty()
	payment_type = db.StringProperty()
	payment_created = db.DateTimeProperty()

class expensesdb(db.Model):
	community_id = db.StringProperty()
	expense_month = db.StringProperty()
	expense_year = db.StringProperty()
	expense_detail = db.StringProperty()
	expense_amount = db.IntegerProperty()

class membersdb(db.Model):
	house_id = db.StringProperty()
	member_name = db.StringProperty()
	member_DOB = db.StringProperty()
	member_gender = db.StringProperty()



# Fuctions

class MainHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
    	self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
    	t = jinja_env.get_template(template)
    	return t.render(params)

    def render(self, template, **kw):
    	self.write(self.render_str(template, **kw))

    def get(self):
        self.render("welcome.html")

    def post(self):
	comm_name = self.request.get("comm_name")
	comm_pass1 = self.request.get("comm_pass1")
	comm_pass2 = self.request.get("comm_pass2")
	community_exists = False
	communitylist = communitydb.all()
	if comm_pass1 == comm_pass2:
		for community in communitylist:
			if community.community_name == comm_name:
				community_exists = True
		if community_exists:
			self.render("Welcome.html", error = "Community exits")
		else:
			dbIn = communitydb(community_name = comm_name,community_pass = comm_pass1)
			dbIn.put()
			self.redirect("/")
	else:
		self.render("welcome.html", error = "password missmatched")

class commlogin(MainHandler):
	def post(self):
		comm_name = self.request.get("comm_name")
		communitylist = communitydb.all()
		community_exists = False;
		for community in communitylist:
			if community.community_name == comm_name:
				community_exists = True
				self.response.headers.add_header('Set-Cookie', 'logged_community_id = %s' % (str)(community.key()))
				self.response.headers.add_header('Set-Cookie', 'logged_community_name = %s' % (str)(community.community_name))
				break
		if community_exists:
			self.redirect("/community")
		else:
			self.redirect("/")

class community(MainHandler):
	def get(self):
		comm_id = self.request.cookies.get('logged_community_name')
		self.render("commhome.html", name = comm_id)

class commadmin(MainHandler):
	def post(self):
		comm_pass = self.request.get("comm_pass")
		comm_id = self.request.cookies.get('logged_community_id')
		communitylist = communitydb.all()
		community_exists = False;
		for community in communitylist:
			if (str)(community.key()) == comm_id:
				if community.community_pass == comm_pass:
					community_exists = True
					break
		if community_exists:
			self.redirect("/loggedadmin")
		else:
			self.redirect("/community")

class commuser(MainHandler):
	def post(self):
		comm_house_number = self.request.get("comm_house_number")
		comm_house_pass = self.request.get("comm_house_password")
		comm_id = self.request.cookies.get('logged_community_id')
		house_id = ""
		houselist = housedb.all()
		house_exists = False;
		for house in houselist:
			if house.house_comm_id == comm_id:
				if house.house_number == comm_house_number:
					if house.house_pass == comm_house_pass:
						house_exists = True
						house_id = house.key()
						self.response.headers.add_header('Set-Cookie', 'logged_house_id = %s' % (str)(house.key()))
						self.response.headers.add_header('Set-Cookie', 'logged_house_name = %s' % (str)(house.house_number))
						break
		ownerlist = houseownerdb.all()
		if house_exists:
			for owner in ownerlist:
				if owner.house_comm_id == comm_id:
					if owner.house_number == comm_house_number:
						self.response.headers.add_header('Set-Cookie', 'logged_house_owner = %s' % (str)(owner.house_owner))
						self.response.headers.add_header('Set-Cookie', 'logged_house_contact = %s' % (str)(owner.house_contact))
						break
			self.redirect("/loggeduser")
		else:
			self.redirect("/community")

class newhome(MainHandler):
	def get(self):
		self.render("newhome.html")

	def post(self):
		comm_id = self.request.cookies.get('logged_community_id')
		comm_house_number = self.request.get("house_number")
		comm_house_pass = self.request.get("house_pass")
		comm_house_owner = self.request.get("house_owner_name")
		comm_house_contact = self.request.get("house_owner_contact")

		dbIn = housedb(house_number = comm_house_number, house_pass = comm_house_pass, house_comm_id = comm_id)  
		dbIn.put()

		dbIn = houseownerdb(house_number = comm_house_number, house_owner = comm_house_owner,
			house_comm_id = comm_id, house_contact = comm_house_contact, house_status = True )  
		dbIn.put()
		self.redirect("/loggedadmin")

class loggedadmin(MainHandler):
	def get(self):
		comm_id = self.request.cookies.get('logged_community_id')
		comm_name = self.request.cookies.get('logged_community_name')
		house_list = db.GqlQuery("select * from houseownerdb where house_comm_id = '%(kwarg)s'" % {'kwarg':comm_id})
		houses = house_list.fetch(100)
		house_list1 = db.GqlQuery("select * from housedb where house_comm_id = '%(kwarg)s'" % {'kwarg':comm_id})
		houses1 = house_list1.fetch(100)
		payment_list = db.GqlQuery("select * from paymentsdb where community_id = '%(kwarg)s'" % {'kwarg':comm_id})
		payments = payment_list.fetch(100)
		expense_list = db.GqlQuery("select * from expensesdb where community_id = '%(kwarg)s'" % {'kwarg':comm_id})
		expenses = expense_list.fetch(100)
		collection = 0
		totalexpense = 0
		for payment in payments:
			collection = collection + payment.payment_amount
		for expense in expenses:
			totalexpense = totalexpense + expense.expense_amount
		accountstatus = False

		if collection >= totalexpense:
			amountleft = collection - totalexpense
			accountstatus = True
		else:
			amountleft = totalexpense - collection


		self.render("admindash.html", houses = houses, comm_name = comm_name, houses1 = houses1, amountleft = amountleft, accountstatus = accountstatus)

class loggeduser(MainHandler):
	def get(self):
		
		house_owner = self.request.cookies.get('logged_house_owner')
		house_contact = self.request.cookies.get('logged_house_contact')
		house_id = self.request.cookies.get('logged_house_id')
		community_id = self.request.cookies.get('logged_community_id')
		house_name = self.request.cookies.get('logged_house_name')
		due_list = db.GqlQuery("select * from duesdb where house_id = '%(kwarg)s'" % {'kwarg':house_id})
		dues = due_list.fetch(100)
		payment_list = db.GqlQuery("select * from paymentsdb where house_id = '%(kwarg)s'" % {'kwarg':house_id})
		payments = payment_list.fetch(100)
		member_list = db.GqlQuery("select * from membersdb where house_id = '%(kwarg)s'" % {'kwarg':house_id})
		members = member_list.fetch(100)
		neighbour_list = db.GqlQuery("select * from houseownerdb where house_comm_id = '%(kwarg)s' and house_number != '%(housename)s'" % {'kwarg':community_id,'housename':house_name})
		neighbours = neighbour_list.fetch(100)
		totaldue = 0
		for due in dues:
			totaldue = totaldue + due.due_amount
		self.render("userdash.html", dues = dues, payments = payments, totaldue = totaldue, houseowner = house_owner,
			housecontact = house_contact, members = members, neighbours = neighbours)

class newMonth(MainHandler):
	def post(self):
		month = self.request.get("month")
		year = self.request.get("year")
		amount = self.request.get("amount")
		paymentType = self.request.get("type")
		detail = self.request.get("detail")
		comm_id = self.request.cookies.get('logged_community_id')
		dues = duesdb.all()
		due_exists = False
		for due in dues:
			if due.due_month == month:
				if due.due_year == year:
					if due.due_type == paymentType:
						if paymentType == "monthly":
							due_exists = True
							break
						else:
							if detail == due.due_detail:
								due_exists = True
								break

		if not due_exists:
			current_time = datetime.datetime.now()
			houses = housedb.all()
			comm_id = self.request.cookies.get('logged_community_id')
			for house in houses:
				if house.house_comm_id == comm_id:
					dbIn = duesdb(due_month = month, due_year = year, due_amount =(int)(amount), due_type = paymentType, due_detail = detail,
						house_id = (str)(house.key()), due_created = current_time, community_id = comm_id)
					dbIn.put()
					self.redirect("/loggedadmin")
		else:
			self.redirect("/loggedadmin")

class logout(MainHandler):
	def get(self):
		self.response.headers.add_header('Set-Cookie', 'logged_house_id = ""')
		self.response.headers.add_header('Set-Cookie', 'logged_house_name = ""')
		self.redirect('/community')

class dues(MainHandler):
	def post(self):
		house_id = self.request.get("house_id")
		house_name = self.request.get("house_name")
		dbIn = db.GqlQuery("select * from duesdb where house_id = '%(name)s' order by due_created" % {'name':house_id})
		dues = dbIn.fetch(100)
		self.render("dues.html", dues = dues, house_id = house_id, house_name = house_name)

class newexpense(MainHandler):
	def post(self):
		expense_detail = self.request.get("expense_detail")
		expense_month = self.request.get("expense_month")
		expense_year = self.request.get("expense_year")
		expense_amount = (int)(self.request.get("expense_amount"))
		comm_id = self.request.cookies.get('logged_community_id')
		dbIn = expensesdb(expense_year = expense_year, expense_amount = expense_amount, expense_month = expense_month,
			community_id = comm_id, expense_detail = expense_detail)
		dbIn.put()
		self.redirect("/loggedadmin")

class viewexpense(MainHandler):
	def post(self):
		expense_month = self.request.get("expense_month")
		expense_year = self.request.get("expense_year")
		comm_id = self.request.cookies.get('logged_community_id')
		expense_list = db.GqlQuery("select * from expensesdb where community_id = '%(kwarg)s' and expense_month = '%(month)s'" % {'kwarg':comm_id,'month':expense_month})
		expenses = expense_list.fetch(100)
		self.render("expenses.html", expenses = expenses)

class newmember(MainHandler):
	def post(self):
		member_name = self.request.get("member_name")
		member_gender = self.request.get("member_gender")
		member_DOB = self.request.get("member_DOB")
		house_id = self.request.cookies.get('logged_house_id')
		dbIn = membersdb(member_name = member_name, member_gender = member_gender, member_DOB = member_DOB,
			house_id = house_id)
		dbIn.put()
		self.redirect("/loggeduser")


class paydue(MainHandler):
	def post(self):
		house_id = self.request.get("house_id")
		due_month = self.request.get("due_month")
		due_year = self.request.get("due_year")
		due_amount = self.request.get("due_amount")
		due_detail = self.request.get("due_detail")
		due_type = self.request.get("due_type")
		comm_id = self.request.cookies.get('logged_community_id')
		current_time = datetime.datetime.now()
		dues = duesdb.all()
		due_found = False
		for due in dues:
			if due.house_id == house_id:
				if due.due_year == due_year:
					if due.due_month == due_month:
						if due.due_type == "monthly":
							due.delete()
							due_found = True
							break
						else:
							if due.due_detail == due_detail:
								due.delete()
								due_found = True
								break
		if due_found:
			dbIn = paymentsdb(payment_month = due_month, payment_year = due_year, payment_amount =(int)(due_amount), 
				payment_type = due_type, payment_detail = due_detail, house_id = house_id, payment_created = current_time,
				community_id = comm_id)
			dbIn.put()
	
		self.redirect('/loggedadmin')

class editpassword(MainHandler):
	def post (self):
		community_id = self.request.cookies.get('logged_community_id')
		current_password = self.request.get("current_password")
		new_password = self.request.get("new_password")
		reenter_password = self.request.get("reenter_password")
		if new_password == reenter_password:
			communities = communitydb.all()
			for community in communities:
				if (str)(community.key()) == community_id:
					community.community_pass = new_password
					community.put()
					break
		self.redirect("/loggedadmin")

class editpassworduser(MainHandler):
	def post (self):
		house_id = self.request.cookies.get('logged_house_id')
		current_password = self.request.get("current_password")
		new_password = self.request.get("new_password")
		reenter_password = self.request.get("reenter_password")
		if new_password == reenter_password:
			houses = housedb.all()
			for house in houses:
				if (str)(house.key()) == house_id:
					house.house_pass = new_password
					house.put()
					break
		self.redirect("/loggedadmin")

class changestatus(MainHandler):
	def post(self):
		community_id = self.request.cookies.get('logged_community_id')
		house_number = self.request.get("house_number")
		house_id = ""
		houses = housedb.all()
		for house in houses:
			if house.house_number == house_number:
				if house.house_comm_id == community_id:
					house_id = (str)(house.key())
					house.house_pass = "0000"
					house.put()
					break

		owners = houseownerdb.all()
		for owner in owners:
			if owner.house_comm_id == community_id:
				if owner.house_number == house_number:
					if owner.house_status:
						owner.house_status = False
						dbIn = db.GqlQuery("select * from membersdb where house_id = '%(name)s'" % {'name':house_id})
						members = dbIn.fetch(100) 
						for member in members:
							member.delete()
					else:
						owner.house_status = True
					owner.put()
					break
		self.redirect("/loggedadmin")


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/commlogin', commlogin),
    ('/commadmin', commadmin),
    ('/commuser', commuser),
    ('/community', community),
    ('/loggedadmin', loggedadmin),
    ('/loggeduser', loggeduser),
    ('/newhome', newhome),
    ('/newmonth', newMonth),
    ('/logout', logout),
    ('/due',dues),
    ('/paydue',paydue),
    ('/newexpense', newexpense),
    ('/viewexpense', viewexpense),
    ('/newmember', newmember),
    ('/editpassword', editpassword),
    ('/editpassworduser', editpassworduser),
    ('/changestatus', changestatus)
], debug=True)
