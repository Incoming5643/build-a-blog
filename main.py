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
import os, cgi, re, webapp2, jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

class Handler(webapp2.RequestHandler):

    def write(self, *a, **kwargs):
        self.response.write(*a, **kwargs)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs))


class Art(db.Model):
    title = db.StringProperty(required=True)
    art = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class BlogPage(Handler):
	def render_blog(self, title="", art="", error=""):
		arts = db.GqlQuery("""SELECT * FROM Art ORDER BY created DESC LIMIT 5""")
		self.render("blog.html", title=title, art=art, error=error, arts=arts)
	
	def get(self):
		self.render_blog()

class FrontPage(Handler):
	def get(self):
		self.render("front.html")

class NewPostPage(Handler):
	def render_newpost(self, title="", art="", error=""):
		self.render("newpost.html", title=title, art=art, error=error)
		
	def get(self):
		self.render_newpost()

	def post(self):
		title = self.request.get("title")
		art = self.request.get("art")

		if title and art:
			a = Art(title=title, art=art)
			a.put()
			self.redirect("/blog/"+str(a.key().id()))

		else:
			self.render_newpost(title, art, "Both fields are required!")


class ViewPost(Handler):
	def get(self, id):
		entry = Art.get_by_id(int(id))
		if(not entry):
			self.render("404.html", error="That entry does not exist")
		else:
			self.render("singleblog.html", title=entry.title, art=entry.art)

app = webapp2.WSGIApplication([
    ('/', FrontPage),
	('/blog', BlogPage),
	('/newpost', NewPostPage),
	webapp2.Route('/blog/<id:\d+>', ViewPost)
], debug=True)
