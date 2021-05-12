from django.http import HttpResponse,HttpResponseNotFound
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages

from datetime import datetime

from . import models

def messages_view(request):
    """Private Page Only an Authorized User Can View, renders messages page
       Displays all posts and friends, also allows user to make new posts and like posts
    Parameters
    ---------
      request: (HttpRequest) - should contain an authorized user
    Returns
    --------
      out: (HttpResponse) - if user is authenticated, will render private.djhtml
    """
    if request.user.is_authenticated:
        user_info = models.UserInfo.objects.get(user=request.user)


        # TODO Objective 9: query for posts (HINT only return posts needed to be displayed)
        posts = []
        posts1 = models.Post.objects.all().order_by('-timestamp')
        for post in posts1:
            posts += [post]
        request.session['limit'] = request.session.get('limit',1)
        # TODO Objective 10: check if user has like post, attach as a new attribute to each post 
        context = { 'user_info' : user_info
                  , 'posts' : posts }
        return render(request,'messages.djhtml',context)

    request.session['failed'] = True
    return redirect('login:login_view')

def account_view(request):
    """Private Page Only an Authorized User Can View, allows user to update
       their account information (i.e UserInfo fields), including changing
       their password
    Parameters
    ---------
      request: (HttpRequest) should be either a GET or POST
    Returns
    --------
      out: (HttpResponse)
                 GET - if user is authenticated, will render account.djhtml
                 POST - handle form submissions for changing password, or User Info
                        (if handled in this view)
    """
    if request.user.is_authenticated:
        if request.method == 'POST':
            if 'change_password' in request.POST:
                form1 = PasswordChangeForm(request.user, request.POST)
                if form1.is_valid():
                    user = form1.save()
                    update_session_auth_hash(request, user) 
                    return redirect('login:login_view')
            elif 'update_info' in request.POST:
                user1 = models.UserInfo.objects.get(user=request.user)
                employment = request.POST.get('employment', 'Unspecified')
                location = request.POST.get('location', 'Unspecified')
                birthday = request.POST.get('birthday', 'None')
                user_int = request.POST.get('interest')
                if models.Interest.objects.filter(label__iexact=user_int):
                    int1 = models.Interest.objects.filter(label__iexact=user_int)   
                else:
                    int1 = models.Interest.objects.create(label=user_int)
                user1.employment = employment
                user1.location = location
                user1.birthday = birthday
                user1.interests.add(int1)
                user1.save()
                return redirect('social:messages_view')
        else:
            form1 = PasswordChangeForm(request.user)

        # TODO Objective 3: Create Forms and Handle POST to Update UserInfo / Password

        user_info = models.UserInfo.objects.get(user=request.user)
        if user_info.birthday is not None:
           birth = datetime.strftime(user_info.birthday, '%Y-%m-%d')
        else:
           birth = ""
        context = { 'user_info' : user_info,
                    'form1' : form1,
                    'birth' : birth,}
        return render(request,'account.djhtml',context)

    request.session['failed'] = True
    return redirect('login:login_view')

def people_view(request):
    """Private Page Only an Authorized User Can View, renders people page
       Displays all users who are not friends of the current user and friend requests
    Parameters
    ---------
      request: (HttpRequest) - should contain an authorized user
    Returns
    --------
      out: (HttpResponse) - if user is authenticated, will render people.djhtml
    """
    if request.user.is_authenticated:
        user_info = models.UserInfo.objects.get(user=request.user)
        # TODO Objective 4: create a list of all users who aren't friends to the current user (and limit size)
        friends1 = user_info.friends.all()
        all_people = []
        people = models.UserInfo.objects.exclude(user=request.user)
        for person in people:
            if person not in friends1:
                all_people += [person]

        request.session['limit'] = request.session.get('limit',1)     
        # TODO Objective 5: create a list of all friend requests to current user
        
        friend_requests = []
        fr = models.FriendRequest.objects.filter(to_user=user_info).all()
        for r in fr:
            friend_requests += [r]
        
        ls1 = []
        l1 = list(models.FriendRequest.objects.filter(from_user=user_info).all())
        for i in l1:
            ls1+=[i.to_user]
        
        ls2 = []
        fr1 = list(models.FriendRequest.objects.filter(to_user=user_info).all())
        for f in fr1:
            ls2+=[f.from_user]
        context = { 'user_info' : user_info
                    ,'all_people' : all_people
                    ,'friend_requests' : friend_requests
                    ,'list1':ls1
                    ,'list2':ls2 }

        return render(request,'people.djhtml',context)

    request.session['failed'] = True
    return redirect('login:login_view')

def like_view(request):
    '''Handles POST Request recieved from clicking Like button in messages.djhtml,
       sent by messages.js, by updating the corrresponding entry in the Post Model
       by adding user to its likes field
    Parameters
	----------
	  request : (HttpRequest) - should contain json data with attribute postID,
                                a string of format post-n where n is an id in the
                                Post model

	Returns
	-------
   	  out : (HttpResponse) - queries the Post model for the corresponding postID, and
                             adds the current user to the likes attribute, then returns
                             an empty HttpResponse, 404 if any error occurs
    '''
    postIDReq = request.POST.get('postID')
    if postIDReq is not None:
        # remove 'post-' from postID and convert to int
        # TODO Objective 10: parse post id from postIDReq
        
        if request.user.is_authenticated:
            # TODO Objective 10: update Post model entry to add user to likes field
            l = postIDReq.split("|")
            pID = int(l[2])
            postID = int(l[1])
            user = models.UserInfo.objects.get(user=request.user)
            t = models.UserInfo.objects.get(user_id=postID)
            models.Post.objects.filter(owner=t).get(id=pID).likes.add(user)
        
            # return status='success'
            return HttpResponse()
        else:
            return redirect('login:login_view')

    return HttpResponseNotFound('like_view called without postID in POST')

def post_submit_view(request):
    '''Handles POST Request recieved from submitting a post in messages.djhtml by adding an entry
       to the Post Model
    Parameters
	----------
	  request : (HttpRequest) - should contain json data with attribute postContent, a string of content

	Returns
	-------
   	  out : (HttpResponse) - after adding a new entry to the POST model, returns an empty HttpResponse,
                             or 404 if any error occurs
    '''
    postContent = request.POST.get('postContent')
    if postContent is not None:
        if request.user.is_authenticated:
            user1 = models.UserInfo.objects.get(user=request.user)
            # TODO Objective 8: Add a new entry to the Post model
            ts = datetime.now().timestamp()
            models.Post.objects.create(owner=user1, content=postContent, timestamp=ts)
            # return status='success'
            return HttpResponse()
        else:
            return redirect('login:login_view')

    return HttpResponseNotFound('post_submit_view called without postContent in POST')

def more_post_view(request):
    '''Handles POST Request requesting to increase the amount of Post's displayed in messages.djhtml
    Parameters
	----------
	  request : (HttpRequest) - should be an empty POST

	Returns
	-------
   	  out : (HttpResponse) - should return an empty HttpResponse after updating hte num_posts sessions variable
    '''
    if request.user.is_authenticated:
        # update the # of posts dispalyed

        # TODO Objective 9: update how many posts are displayed/returned by messages_view
        request.session['limit'] = request.session['limit'] + 1
        # return status='success'
        return HttpResponse()

    return redirect('login:login_view')

def more_ppl_view(request):
    '''Handles POST Request requesting to increase the amount of People displayed in people.djhtml
    Parameters
	----------
	  request : (HttpRequest) - should be an empty POST

	Returns
	-------
   	  out : (HttpResponse) - should return an empty HttpResponse after updating the num ppl sessions variable
    '''
    if request.user.is_authenticated:
        # update the # of people dispalyed
        request.session['limit'] = request.session['limit'] + 1
        # TODO Objective 4: increment session variable for keeping track of num ppl displayed
        
        # return status='success'
        return HttpResponse()

    return redirect('login:login_view')

def friend_request_view(request):
    '''Handles POST Request recieved from clicking Friend Request button in people.djhtml,
       sent by people.js, by adding an entry to the FriendRequest Model
    Parameters
	----------
	  request : (HttpRequest) - should contain json data with attribute frID,
                                a string of format fr-name where name is a valid username

	Returns
	-------
   	  out : (HttpResponse) - adds an etnry to the FriendRequest Model, then returns
                             an empty HttpResponse, 404 if POST data doesn't contain frID
    '''
    frID = request.POST.get('frID')

    if frID is not None:
        # remove 'fr-' from frID
        username = frID[3:]
        #fr = models.UserInfo.objects.filter(user=username)
        if request.user.is_authenticated:
            # TODO Objective 5: add new entry to FriendRequest
            fuser = models.UserInfo.objects.get(user=request.user)
            tuser = models.UserInfo.objects.get(user_id = username)
            # fr1 = models.FriendRequest.objects.get(to_user=tuser, from_user=fuser)
            models.FriendRequest.objects.create(to_user=tuser, from_user=fuser)
            # return status='success'
            return HttpResponse()
        else:
            return redirect('login:login_view')

    return HttpResponseNotFound('friend_request_view called without frID in POST')

def accept_decline_view(request):
    '''Handles POST Request recieved from accepting or declining a friend request in people.djhtml,
       sent by people.js, deletes corresponding FriendRequest entry and adds to users friends relation
       if accepted
    Parameters
	----------
	  request : (HttpRequest) - should contain json data with attribute decision,
                                a string of format A-name or D-name where name is
                                a valid username (the user who sent the request)

	Returns
	-------
   	  out : (HttpResponse) - deletes entry to FriendRequest table, appends friends in UserInfo Models,
                             then returns an empty HttpResponse, 404 if POST data doesn't contain decision
    '''
    data = request.POST.get('decision')
    username = data[2:]
    user = models.UserInfo.objects.get(user = request.user)
    fuser = models.UserInfo.objects.get(user_id=username)
    if data is not None:
        # TODO Objective 6: parse decision from data

        if request.user.is_authenticated:
            req = models.FriendRequest.objects.get(to_user= user, from_user= fuser)
            req.delete()
            if data[0] == 'A':
                user.friends.add(fuser)
                fuser.friends.add(user)
            # TODO Objective 6: delete FriendRequest entry and update friends in both Users

            # return status='success'
            return HttpResponse()
        else:
            return redirect('login:login_view')

    return HttpResponseNotFound('accept-decline-view called without decision in POST')
