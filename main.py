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

class communitydb(db.Model):
	community_id = db.IntegerProperty()
	community_name = db.StringProperty()
	community_pass = db.StringProperty()

class housedb(db.Model):
	house_comm_id = db.IntegerProperty()
	house_id = db.IntegerProperty()
	house_number = db.StringProperty()
	house_pass = db.StringProperty()


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
	if comm_pass1 == comm_pass2:
		communitylist = communitydb.all()
		if communitylist:
			comm_list_length = communitylist.count()
		else:
			comm_list_length = 0

		for community in communitylist:
			if community.community_name == comm_name:
				community_exists = True
		if community_exists:
			self.render("Welcome.html", error = "Community exits")
		else:
			comm_list_length = comm_list_length + 1
			dbIn = communitydb(community_name = comm_name, community_id = comm_list_length, community_pass = comm_pass1)
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
				self.response.headers.add_header('Set-Cookie', 'logged_community_id = %s' % (str)(community.community_id))
				break
		if community_exists:
			self.redirect("/community")
		else:
			self.redirect("/")

class community(MainHandler):
	def get(self):
		comm_id = self.request.cookies.get('logged_community_id')
		self.render("commhome.html", name = comm_id)

class commadmin(MainHandler):
	def post(self):
		comm_pass = self.request.get("comm_pass")
		comm_id = (int)(self.request.cookies.get('logged_community_id'))
		communitylist = communitydb.all()
		community_exists = False;
		for community in communitylist:
			if community.community_id == comm_id:
				if community.community_pass == comm_pass:
					community_exists = True
					break
		if community_exists:
			self.redirect("/loggedadmin")
		else:
			self.redirect("/commlogin")

class commuser(MainHandler):
	def post(self):
		comm_house_number = self.request.get("comm_house_number")
		comm_house_pass = self.request.get("comm_house_password")
		comm_id = self.request.cookies.get('logged_community_id')
		houselist = housedb.all()
		house_exists = False;
		for house in houselist:
			if house.house_name == comm_house_number:
				if house.house_pass == comm_house_pass:
					house_exists = True
					self.response.headers.add_header('Set-Cookie', 'logged_house_id = %s' % (str)(house.house_id))
					break
		if house_exists:
			self.redirect("/loggeduser")
		else:
			self.redirect("/commlogin")

class newhome(MainHandler):
	def post(self):
		comm_id = (int)(self.request.cookies.get('logged_community_id'))
		comm_house_number = self.request.get("house_number")
		comm_house_pass = self.request.get("house_number")
		houselist = housedb.all()
		listlength = houselist.count() + 1
		dbIn = housedb(house_id = listlength, house_number = comm_house_number, house_pass = comm_house_pass,house_comm_id = comm_id)  
		dbIn.put()
		self.redirect("/loggedadmin")
class loggedadmin(MainHandler):
	def get(self):
		self.render("admindash.html")

class loggeduser(MainHandler):
	def get(self):
		self.render("userdash.html")



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/commlogin', commlogin),
    ('/commadmin', commadmin),
    ('/community', community),
    ('/loggedadmin', loggedadmin),
    ('/loggeduser', loggeduser),
    ('/newhome', newhome)
], debug=True)
