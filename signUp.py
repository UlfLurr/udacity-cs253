import webapp2
import cgi
import re
import user
from head import fold
from head import adr


title = "Sign Up "

form = """
 <label><h1>Sign Up</h1></label>
 <form method="post">
   <label>Name</label>
   <input type=input name="username" value="%(name)s">
   <label class="error">%(nameerr)s</label>
 
   <label>Password</label>
   <input type=password name="password" >
   <label class="error">%(pswerr)s</label>
 
   <label>Verify password</label>
   <input type=password name="verify" >
   <label class="error">%(vererr)s</label>
 
   <label>E mail (now optional)</label>
   <input type=input name="email" value="%(mail)s">
   <label class="error">%(mailerr)s</label>

   <input type=submit value="Sign Up">
</form>
"""

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PSW_RE = re.compile(r"^.{3,20}$")
MAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

class SignUpPage(webapp2.RequestHandler):
    def validUsername(self, username):
        return USER_RE.match(username)
    def validPsw(self, psw):
        return PSW_RE.match(psw)
    def validMail(self, mail):
        if(mail):
            return MAIL_RE.match(mail)
        else:
            return True
    def write_form(self,name = "", mail="", nameerr="", pswerr="", vererr="", mailerr="",):
        self.response.headers['Content-Type'] = 'text/html'
        name = cgi.escape(name, quote = True)
        mail = cgi.escape(mail, quote = True)
        self.response.write(fold(form%{"name":name, "mail":mail, "nameerr":nameerr, "pswerr":pswerr, "vererr":vererr, "mailerr":mailerr},title))
    def get(self):
        self.write_form()
    def post(self):
        username = self.request.get("username")
        email = self.request.get("email")
        psw =  self.request.get("password")   
        psw2 =  self.request.get("verify")
        if(self.validUsername(username)):
            if user.exists(username):
                nameerr = "Username already exists."
            else:
                nameerr = ""
        else:
            nameerr = "Invalid username."

        if(self.validPsw(psw)):
            pswerr = ""
            if(psw==psw2):
                vererr = ""
            else:
                vererr = "Passwords do not match."
        else:
            vererr = ""
            pswerr = "Invalid password."
        if(self.validMail(email)):
            mailerr = ""
        else:
            mailerr = "Invalid mail."
        
        if(nameerr == "" and pswerr=="" and vererr=="" and mailerr==""):

            userCookie = user.bake(username, psw)
            #self.redirect(adr['welcome'] + "?username=" + username) weird old vith  GET userneme    
            self.redirect(adr['welcome']);      
            self.response.headers.add_header('Set-Cookie', str('user=%s; Path=/'%userCookie)) 
        else:
            self.write_form(username,email,nameerr,pswerr,vererr,mailerr)

class ClearPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(fold('<form method="post"><input type=submit value="Clear"></form>',title))
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        user.cleanUsers()    
        self.response.write(fold("Clean!",title))


from welcome import WelcomePage
app = webapp2.WSGIApplication([    
    (adr['signup'], SignUpPage),
    (adr['welcome'], WelcomePage),
    (adr['signup']+'/clean', ClearPage),
], debug=True)
