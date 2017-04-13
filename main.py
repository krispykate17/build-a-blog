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

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Blog(db.Model):
    title = db.StringProperty(required = True)
    blog_content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class NewPost(webapp2.RequestHandler):
    def render_NewPost(self, title="", blog_content="", error=""):
        t = jinja_env.get_template("new_posts.html")
        content = t.render(title=title, blog_content=blog_content, error=error)
        self.response.write(content)

    def get(self):
        self.render_NewPost()

    def post(self):
        title = self.request.get("title")
        blog_content = self.request.get("blog_content")

        if title and blog_content:
            b = Blog(title=title, blog_content=blog_content)
            b.put()
            blog_id = str(b.key().id())

            self.redirect("/blog/" + blog_id)
        else:
            error = "We need both a title and some content"
            self.render_NewPost(title, blog_content, error)

class TopFive(webapp2.RequestHandler):
    def render_TopFive(self, title="", blog_content="", error=""):
        top_five = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")

        t = jinja_env.get_template("main_blog.html")
        content = t.render(title=title, blog_content=blog_content, error=error,
                            top_five=top_five)
        self.response.write(content)

    def get(self):
        self.render_TopFive()

class ViewPostHandler(webapp2.RequestHandler):
    def render_IndivBlog(self, int_id):
        indivBlog = Blog.get_by_id(int_id)

        t = jinja_env.get_template("indivblog.html")
        content = t.render(blog= indivBlog)
        self.response.write(content)

    def get(self, id):
        int_id = int(id)
        blog_verification = Blog.get_by_id(int_id)

        if not blog_verification:
            self.response.write("Error: 404 That blog does not exist :(")

        else:
            self.render_IndivBlog(int_id)

app = webapp2.WSGIApplication([
    ('/', NewPost),
    ('/blog', TopFive),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
