import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **kw):
        t = jinja_env.get_template(template)
        return t.render(kw)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainBlog(Handler):
    def render_main(self, title='', body=''):
        posts = db.GqlQuery('SELECT * FROM Post ORDER BY created DESC LIMIT 5')

        self.render('main-blog.html', posts=posts)

    def get(self):
        self.render_main()

class NewPost(Handler):
    def render_form(self, title='', body='', error=''):
        self.render('new-post.html', title=title, body=body, error=error)

    def get(self):
        self.render_form()

    def post(self):
        title = (self.request.get('title')).strip()
        body = (self.request.get('body')).strip()
        # TODO Print error if empty field(spaces) is submitted
        if title and body:
            p = Post(title=title, body=body)
            p.put()
            self.redirect('/blog')
        else:
            error = 'Please include a title and body!'
            self.render_form(title, body, error)



app = webapp2.WSGIApplication([
    ('/blog', MainBlog),
    ('/newpost', NewPost),
], debug=True)
