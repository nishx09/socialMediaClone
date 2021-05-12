# CS 1XA3 Project03 - gargn4

## Usage
Install Conda environment with `conda create -n djangoenv python=3.7` and then install django in that environment using `conda install -c anaconda django`.

Once Installation is properly done, you have two choices to run your project, either on the `local machine` or the `mac1xa3.ca` server:

* __Run locally with:__
  `python manage.py runserver localhost:8000`
* __Run on mac1xa3.ca with:__
  `python manage.py runserver localhost:10033`

(**NOTE:** You should be on the root of your project (where manage.py exists) to run this command)


After opening the required address, you'll see two options saying `login` and `signup`:
 

* Initially, **Log in** with **Username:** TestUser , **Password:** 1234
* You can also log in with any of the user info defined in the database (info available in **Objective 11**). 
* You can also **create a new account** using the signup option.
## Objective 01
### Description:
* This feature is displayed in `signup.djhtml` which is rendered by `def signup_view` in **Project03/login/views.py** . 
* Inbuilt form for **User Creation** was used from `django.contrib.auth.forms` library.
* The form makes a POST request which is handled by `create_view` creating a new UserInfo object.
* Once the User is created, gets redirected to the `social:messages_view`.

### Exception:
* If the user fills in the _invalid_ user info, it shows an error saying **"Invalid username or password"** and gets redirected to `login:signup_view` again.

## Objective 02
### Description:
* This feature is displayed in `social_base.djhtml` which is inherited by many templates rendered in **Project03/social/views.py** . 
* The **user_info** object passed in the context dictionary is used to turn the static profile into a real one.
* As interest is a many-to-many field, `for loop` is used to show all the interests in the user profile.
    ```django
    {% for interest in user_info.interests.all %}
         <span class="w3-tag w3-small w3-theme-d5">{{ interest.label }}</span>
    {% endfor %}
    ```
### Exception:
* As initially, no information on Employment, Location, Birthday and Interests is provided, it simply says **Unspecified or none** in some, but in the case of interests it shows literally nothing.

## Objective 03
### Description:
* This feature is displayed in `account.djhtml` which is rendered by `def account_view` in **Project03/social/views.py** .
* Inbuilt form for **Password Change** was used from `django.contrib.auth.forms` library and an HTML based form is built for **updating userinfo**. 
* In the Update Info form, on the click of the Update button, the data gets **posted** to the server.
* Further, the data posted is added to the instance of UserInfo object using `Queries` and after that, it redirects to `'social:messages_view'` showing the updated information about the user.

### Exception:
* The **input field** in the Update Info form holds the values for those instances, all works fine, but in the case of storing the value of the birthday, `strftime` is used to be able to re-use that value of birthday in that input field.

    ```python
    birth = datetime.strftime(user_info.birthday, '%Y-%m-%d')
    ```
* For the **very first time**, while updating the user info, it is **necessary** to add the `birthday`, but later on the birthday will **automatically** be loaded as the value of the input field **(so no need to provide that again)**.

## Objective 04
### Description:
* This feature is displayed in `people.djhtml` which is rendered by `def people_view` in **Project03/social/views.py** .
* The `Queries`, `conditional statements` and `for loops` are used to get the list of the people who are not friends. Later, this list **(namely 'all_people')** is sent along with the request to render `people.djhtml`.
    ```python
    friends1 = user_info.friends.all()
    all_people = []
    people = models.UserInfo.objects.exclude(user=request.user)
    for person in people:
        if person not in friends1:
            all_people += [person]
    ``` 
* The **all_people** object passed in the context dictionary is used to turn the static profile of a person into a real one.
* Used `session` variables to get the list of people displayed in the one-by-one incrementation pattern on click of More button.
    ```python
    request.session['limit'] = request.session['limit'] + 1
    ```
### Exception:
* Click of the more button increases the number of profiles every time, but when the user logs out and opens again the number of profiles should start again from one. For that, reset the `session` variable to one in the `logout_view` in **Project03/login/views.py** .
    ```python
    request.session['limit'] = request.session.get('limit',1)
    ```

## Objective 05
### Description: 
* This feature is displayed in `people.djhtml` which is rendered by `def people_view` in **Project03/social/views.py** .
* Additionally, **Friend Request buttons** are linked to a JQuery event in `people.js`, which uses its `id` to send a **AJAX POST request** to the function `def friend_request_view`.
     ```html5
     id="fr-{{ people.user_id }}"
     ```
* This `id` is then used to create a new FriendRequest object specifying the **from_user** to be the person who clicked the button and **to_user**, the person who's profile's friend request button was clicked.
     ```python
     models.FriendRequest.objects.create(to_user=tuser, from_user=fuser)
     ```
* Now, in the right column, where the friend requests are shown, using the list of friend requests that the current user has received **(namely 'friend_requests')**, transform the current static version of FR to the real one.
### Exceptions:
* When a user sends a friend request to another person, he can't send the request to the same user again. For that, disabling the button once pressed works out pretty neatly.
* When the request is sent from A to another user B, then B can't send a request to A, before taking any decision on the existing FR. For that, disable the FR button for the B user until he takes any decision on the existing FR.

```django
{% if people in list1 or people in list2%}disabled{% endif %}
```

## Objective 06
### Description:
* This feature is displayed in `people.djhtml`, when the user pushes the accept/decline button, an **AJAX POST** is sent to `accept_decline_view`
with the appropriate button `id`.
* Where `accept_decline_view` handles the request and checks from the `id` provided that if the accept or decline button is pressed, and accordingly updates the list of user's friends and removes its instance from the FriendRequest model.
    ```python
    req = models.FriendRequest.objects.get(to_user= user, from_user= fuser)
            req.delete()
            if data[0] == 'A':
                user.friends.add(fuser)
                fuser.friends.add(user)
    ```

### Exceptions:
* While clicking on the accept/decline button, if the user clicks on the icon portion of the button, it will throw an error. For that, nullifying the `pointer-events` for that icon will work very well.
      
   ```html
   <i class="fa fa-check" style="pointer-events: none;"></i>
   ```

## Objective 07
### Description:
* This feature is displayed in `messages.djhtml` which is rendered by `def messages_view` in **Project03/social/views.py** .
* Used the `user_info` object passed in the context dictionary to show all the friends in the right column of `messages.djhtml`.
     ```html
     {% for friend in user_info.friends.all %}{% endfor %}
     ```

### Exceptions:
* If the user has no friends, then the right column of the `messages.djhtml` will be empty.

## Objective 08
### Description:
* This feature is displayed in `messages.djhtml`, when the user clicks the Post button, an **AJAX POST** is sent to `post_submit_view` along with the post content 
    ```JQuery
    let content = $('#post-text').text();
    ```
* In `post_submit_view`, a new instance of Post model, with the **content** from the AJAX POST, along with the **current timestamp** is created.
    ```python
    models.Post.objects.create(owner=user1, content=postContent, timestamp=ts)
    ```
* The page is reloaded on success response.
### Exception:
* If response of the AJAX Post was not success it will give an alert saying "failed to post".

## Objective 09
### Description:
* This feature is displayed in `messages.djhtml` which is rendered by `def messages_view` in **Project03/social/views.py** .
* The posts list passed in the context dictionary is used to turn the static post into a real one.
    ```html5
    {% for post in posts %} {% endfor %}
    ```
* The middle column shows the posts made by all the users, listed in order from being newest to oldest.
    ```python
    models.Post.objects.all().order_by('-timestamp')
    ```
* Used `session` variables to get the list of posts displayed in the one-by-one incrementation pattern on click of More button.
    ```python
    request.session['limit'] = request.session['limit'] + 1
    ```
### Exception:
* Click of the more button increases the number of posts every time, but when the user logs out and opens again the number of posts should start again from one. For that, reset the `session` variable to one in the `logout_view` in **Project03/login/views.py** .
    ```python
    request.session['limit'] = request.session.get('limit',1)
    ```
## Objective 10
### Description:
* This feature is displayed in `messages.djhtml`, when the user pushes the like button, an **AJAX POST** is sent to `like_view` with the appropriate button `id` containing information about the post `owner` and the post `id`.
* Where `like_view` handles the request and adds the current user to the `likes` Queryset of the **Post owner's particular post**, corresponding to that post `id`.
    ```python
    models.Post.objects.filter(owner=t).get(id=pID).likes.add(user)
    ```
* To show the count of the number of likes on that post,  `posts` list is used.
    ```html
    {{ post.likes.all.count }}
    ```
### Exception:
* A user can like a post only **one** time, otherwise, it will be a biased system. So, to deal with this situation, **disable** the `like` button once the user has liked the post.
    ```html
    {% if user_info in post.likes.all %} disabled {% endif %}
    ```
## Objective 11
### Description:
* Created a variety of test users, posts and likes and different friend requests to showcase the functionality I’ve implemented.
* **Log in** information for the Users which have been created:
   * **username:** TestUser_1 , **password:** 1234567@
   * **username:** TestUser_2 , **password:** 1234567@
   * **username:** TestUser_3 , **password:** 1234567@ 
   * **username:** TestUser_4 , **password:** 1234567@
   * **username:** TestUser_5 , **password:** 1234567@
* Various Posts, Likes and friend requests has already been made. But to test the program more precisely and generally, you can always create new user using signup form on the main page.


// THE END
