import webapp2
import jinja2
import re
import head
import user
import datetime
from jinja2 import Template

page = """
 <h1>{{title}}</h1>
 <form method="post">
   <label>Name</label>
   <input type="text" name="username" {% if name %}value="{{name|e}}"{% endif %}>
   <label class="error">{{nameerr}}</label>
 
   <label>Password</label>
   <input type="password" name="password" >
   <label class="error">{{pswerr}}</label>
 
   {% if isSignup %}

   <label>Verify password</label>
   <input type="password" name="verify" >
   <label class="error">{{vererr}}</label>
 
   <label>E mail (now optional)</label>
   <input type="text" name="email" {% if mail %}value="{{mail|e}}"{% endif %}>
   <label class="error">{{mailerr}}</label>

   {% endif %}

   <input type=submit value="{{submitText}}">
</form>
"""
template = Template(page);

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PSW_RE = re.compile(r"^.{3,20}$")
MAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

class SignPage(webapp2.RequestHandler):
    title = "Sign"
    submitText = "Submit"
    def write(self,**params):
        self.response.headers['Content-Type'] = 'text/html'
        params['title'] = self.title
        params['submitText'] = self.submitText
        c = template.render(params)
        self.response.write(head.fold(c,self.title))
    def validUsername(self, username):
        return USER_RE.match(username)
    def validPsw(self, psw):
        return PSW_RE.match(psw)
    def validMail(self, mail):
        if(mail):
            return MAIL_RE.match(mail)
        else:
            return True
    def get(self):
        self.write()
    def setUserCookie(self,userCookie):
        self.response.set_cookie('user', userCookie, expires= datetime.datetime.now() + datetime.timedelta(days = 7), path='/')

class SignUpPage(SignPage):
    title = "Sign Up"
    submitText = "Sign Up"
    def write(self,**kw):
        super(SignUpPage,self).write(isSignup = True,**kw)
    def post(self):
        username = self.request.get("username")
        email = self.request.get("email")
        psw =  self.request.get("password")   
        psw2 =  self.request.get("verify")

        args = {"name":username, "mail": email }
        err = False

        if self.validUsername(username):
            if user.exists(username):
                args["nameerr"] = "Username already exists."
                err = True
        else:
            args["nameerr"] = "Invalid username."
            err = True

        if not self.validPsw(psw):        
            args["pswerr"] = "Invalid password."
            err = True

        if psw != psw2:
            args["vererr"] = "Passwords do not match."
            err = True

        if not (self.validMail(email)):
            args["mailerr"] = "Invalid mail."
            err = True
        
        if err:
            self.write(**args)
            return

        userCookie = user.bake(username, psw)
        self.setUserCookie(userCookie)
        self.redirect(head.adr['welcome']);   


class SignInPage(SignPage):
    title = "Log In"
    submitText = "Log In"
    def write(self,**kw):
        super(SignInPage,self).write(isSignup = False,**kw)
    def post(self):
        username = self.request.get("username")
        password =  self.request.get("password")
        args = {"name":username}
        err = False

        if not self.validUsername(username):
            args["nameerr"] = "Invalid username."
            err = True

        if not self.validPsw(password):
            args["pswerr"] = "Invalid password."
            err = True

        if err:
            self.write(**args)
            return

        u =  user.getUser(username)
        if (u):
            if u.check(password):
                userCookie = u.bake()                
                self.setUserCookie(userCookie)
                self.redirect(head.adr['welcome']); 
                return
            self.write(pswerr = "Incorrect password.",**args)
            return
        self.write(nameerr = "User not found.",**args)


class SignOutPage(webapp2.RequestHandler):
    def get(self):
        self.response.set_cookie('user', "", expires= datetime.datetime.now() - datetime.timedelta(days = 7), path='/')
        self.redirect(head.adr['signup']);

class ClearPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(head.fold('<form method="post"><input type=submit value="Clear"></form>',"Clean Users"))
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        user.cleanUsers()    
        self.response.write(head.fold("Clean!","Cleaned"))


from welcome import WelcomePage
app = webapp2.WSGIApplication([    
    (head.adr['signup'], SignUpPage),
    (head.adr['signin'], SignInPage),
    (head.adr['signout'], SignOutPage),
    (head.adr['welcome'], WelcomePage),
    (head.adr['signup']+'/cleaneveryuser', ClearPage),
], debug = head.debug)
