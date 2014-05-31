from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
import jinja2
from jinja2.ext import loopcontrols
from webhub.checker import check
from webhub.models import *

jinja_environ = jinja2.Environment(loader=jinja2.FileSystemLoader(['ui']), extensions=[loopcontrols])

#Calls index page
def index(request):
    return HttpResponse(jinja_environ.get_template('index.html').render({"pcuser":None}))
    
#Calls dashboard wish is shown after a user is logged in
def dashboard(request):
    
    retval = check(request)
    if retval <> None:
        return retval
    
    template_values = {'pcuser' : request.user.pcuser,
                    }
    return HttpResponse(jinja_environ.get_template('dashboard.html').render(template_values)) 


#Called when a user clicks login button. 
@csrf_exempt
def login_do(request):
    username = request.REQUEST['username']
    password = request.REQUEST['password']
    user = authenticate(username=username, password=password)
    
    if user is not None:
        if user.is_active:
            login(request, user)
            if 'redirect' in request.REQUEST.keys():
                return HttpResponse(jinja_environ.get_template('redirect.html').render({"rider":None,"redirect_url":request.REQUEST['redirect'].replace("!!__!!","&")}))
            return HttpResponse(jinja_environ.get_template('redirect.html').render({"pcuser":None,"redirect_url":"/"}))
            
    else:
        # Return an 'invalid login' error message.
        if "js" in request.REQUEST.keys():
            if len(User.objects.filter(username=request.REQUEST['username'])) == 0:
                return HttpResponse("inv_user")
            return HttpResponse("inv_pass")
        return HttpResponse(jinja_environ.get_template('notice.html').render({"pcuser":None,
                                                                              "text":'Invalid Login. Please go back or click OK to go to the homepage',"link":'/'}))
    
    
#Called when a user clicks logout button.
def logout_do(request):
    logout(request)
    redirect_url = "/"
    if 'redirect_url' in request.REQUEST.keys():
        redirect_url = request.REQUEST['redirect_url']
    return HttpResponse(jinja_environ.get_template('redirect.html').render({"pcuser":None,"redirect_url":redirect_url}))


def malaria(request):
    all_posts = Post.objects.all()
    return HttpResponse(jinja_environ.get_template('malaria.html').render({"all_posts":all_posts}))

def view_post(request):
    retval = check(request)
    if retval <> None:
        return retval

    try:
        pcuser=request.user.pcuser
        key=request.REQUEST['key']
        postobj=Post.objects.get(id=key)
        return HttpResponse(jinja_environ.get_template('viewpost.html').render({"pcuser":request.user.pcuser, 'post':postobj}))
    except Exception as e:
        return HttpResponse(e)
    

#The call function for new post form.    
def post_form(request):
    retval = check(request)
    if retval <> None:
        return retval
    return HttpResponse(jinja_environ.get_template('newpost.html').render({"pcuser":request.user.pcuser, 'owner':request.user.pcuser}))

#Called when a user clicks submit on new post form.                                                                          
@csrf_exempt
def post_new(request):
    #check for user login
    retval = check(request)
    if retval <> None:
        return retval
    owner = request.user.pcuser
    title_post = request.REQUEST['title']
    description_post = request.REQUEST['description']
    
    entry = Post(owner=owner, 
                 title_post=title_post,
                 description_post=description_post,
                 )
    entry.save()
    return HttpResponse(jinja_environ.get_template('notice.html').render({"pcuser":request.user.pcuser,
                                                                          "text":'<p>Post successful. </p>Please go back or click OK to go to the homepage',
                                                                          "link": '/'}))

#Calls the edit post page. Also, sends the autofill form data.    
def edit_post_page(request):
    retval = check(request)
    if retval <> None:
        return retval

    try:
        pcuser=request.user.pcuser
        key=request.REQUEST['key']
        postobj=Post.objects.get(id=key)
        return HttpResponse(jinja_environ.get_template('editpost.html').render({"pcuser":request.user.pcuser, 'post':postobj}))
    except Exception as e:
        return HttpResponse(e)
    
#Called when a user edits his/her post. If there already are reservers, the user gets a negative flag.
@csrf_exempt
def edit_post(request):
    retval = check(request)
    if retval <> None:
        return retval
    
    owner = request.user.pcuser
    postid = request.REQUEST['postid']
    postobj = None
    try:
        postobj = Post.objects.get(pk=postid)
    except Exception as e:
        return HttpResponse(e)
    
    title_post = request.REQUEST['title']
    description_post = request.REQUEST['description']
    
    
    postobj.title_post = title_post
    postobj.description_post = description_post
    
    postobj.save()
    
    postobj.owner.save()
    return HttpResponse(jinja_environ.get_template('notice.html').render({"pcuser":request.user.pcuser,
                                                                          "text":'Post edited successfully. Click OK to view the post.', "link": '/post_page/?key=' + str(postobj.id)}))

#Called when a user cancels his post. Here all the reserved users are sent a notification and the owner gets a negative flag if there are confirmed users on that post.
@csrf_exempt
def delete_post(request):
    retval = check(request)
    if retval <> None:
        return retval
    user = request.user

    postid = request.REQUEST['postid']
        
    postobj = None
    try:
        postobj = Post.objects.get(pk=postid)
    except Exception as e:
        return HttpResponse(e)
    
    postobj.delete()

    return HttpResponse(jinja_environ.get_template('notice.html').render({"pcuser":request.user.pcuser,
                                                                          "text":'Post Deleted successfully. Please go back or click OK to go to the homepage',"link":'/'}))

#Call to open user's profile page.Sends data to be displayed.        
def profile(request):
    
    try:
        pcuserid = request.REQUEST['id']
        if pcuserid == request.user.pcuser.pk:
            return HttpResponse(jinja_environ.get_template('profile.html').render({"pcuser":request.user.pcuser, "profiler":request.user.pcuser}))
        else:
            return HttpResponse(jinja_environ.get_template('profile.html').render({"pcuser":request.user.pcuser, "profiler":Pcuser.objects.get(pk=pcuserid)}))
    except:
        return HttpResponse(jinja_environ.get_template('profile.html').render({"pcuser":request.user.pcuser, "profiler":request.user.pcuser}))


#Calls the edit profile page. The autofill data is sent too.
def edit_profile_page(request):
    if not request.user.is_authenticated():
        return HttpResponse(jinja_environ.get_template('index.html').render({"pcuser":None}))
    pcuserid = request.REQUEST['id']
    return HttpResponse(jinja_environ.get_template('edit_profile.html').render({"pcuser":Pcuser.objects.get(pk=pcuserid)}))

#Edit profile function. Called after a user presses done in edit profile. New data is requested from frontend and stored.
@csrf_exempt
def edit_profile(request):
    if not request.user.is_authenticated():
        return HttpResponse(jinja_environ.get_template('index.html').render({"pcuser":None}))

    #Check if user has an associated rider
    #(This will be false if the admin logs in)
    
    try:
        request.user.pcuser
    except:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"pcuser":None,
                                                                              "text":'<p>No Rider associated!.</p><p>Please go back or click OK to go to the homepage</p>', "link":'/'}))
    
    
    
def peacetrack(request):
    return HttpResponse(jinja_environ.get_template('peacetrack.html').render({"pcuser":None}))