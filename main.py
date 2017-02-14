import os
import webapp2
import jinja2

from google.appengine.ext import db

# TODO redirect to '/blog' from '/'

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

class FrontPage(Handler):
    def get(self):
        self.redirect('/newpost')

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

        if title and body:
            p = Post(title=title, body=body)
            p.put()
            p_id = p.key().id()
            perma = '/blog/' + str(p_id)
            self.redirect(perma)
        else:
            error = 'Please include a title and body!'
            self.render_form(title, body, error)

class ViewPostHandler(Handler):

    def get(self, id, post='', error=''):
        post = Post.get_by_id(int(id))
        if not post:
            error = 'This post does not exist!'
        self.render('view-post.html', post=post, error=error)


app = webapp2.WSGIApplication([
    ('/', FrontPage),
    ('/blog', MainBlog),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
], debug=True)
