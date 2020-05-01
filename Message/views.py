from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout, views
from django.contrib.auth.decorators import *
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import json, re
from django.utils.html import format_html, escape, strip_tags
from datetime import datetime
#from babel.dates import format_date, format_datetime, format_time
from django.utils.text import unescape_entities
from django.utils.datastructures import MultiValueDictKeyError
# Create your views here.
from Message.models import *

def chat_myself(self_user, mesaj):
    myself = """<li class='self mb-10'>
        <div class='self-msg-wrap'>
        <div class='msg block pull-right'>{}
        <div class='msg-per-detail text-right'>
        <span class='msg-time txt-grey'>{}</span>
        </div>
        </div>
        <div class='clearfix'></div>
        </div>
        </li>
        """.format(mesaj.text.encode('utf8'), mesaj.tr_date())
    return myself
def chat_friend(target, mesaj):
    friend = """<li class='friend'>
        <div class='friend-msg-wrap'>
        <img class='user-img img-circle block pull-left'  src='{}' alt='user'/>
        <div class='msg pull-left'>
        <p>{}</p>
        <div class='msg-per-detail text-right'>
        <span class='msg-time txt-grey'>{}</span>
        </div>
        </div>
        <div class='clearfix'></div>
        </div></li>""".format(None #target.photo_url(),
        	,mesaj.text.encode('utf8'), mesaj.tr_date())
    return friend
def text_to_html(target=None, self_user=None, first=None): #BUTUN MESAJLARI GETIREN FONKSIYON
    if target and self_user:
        header = """<div id="xx" value="{}" class='chat-content'><ul class='chatapp-chat-nicescroll-bar pt-20'>""".format(target.user.username)
        footer = """</ul></div>"""
        body = """"""
        try:
        	if first:
        		message_room = first
        	else:
        		message_room = Message_room.objects.filter(users__id__iexact=target.id).filter(users__id__iexact=self_user.id)[0]
	        message_room.root_date = None #datetime.utcnow()
	        message_room.save()
        except ObjectDoesNotExist:
        	message_room = Message_room.objects.create()
        	message_room.users.add(target)
        	message_room.users.add(self_user)
        	message_room.root_date = None #datetime.utcnow()
        	message_room.save()
        	#room = Message_room.objects.get(user=self_user)
        chat_room = Message_room.objects.all_messages(message_room) # get all messages from message_room
        if len(chat_room) != 0:
            for mesaj in chat_room:
            	if mesaj.sender.user == self_user.user:
            		body += chat_myself(self_user, mesaj)
            	else:
            		body += chat_friend(target, mesaj)

            html_output = header+body+footer
            return format_html(html_output)
        else:
            html_output = header+body+footer
            return format_html(html_output)
    # HACK:  $(".recent-chat-box-wrap .panel-body .chat-content").html("") chat_box siliyor



#@user_passes_test(check_admin)
def message(request):
    if request.method == "POST":
        if request.is_ajax():
            user=request.user
            try:
                msj = request.POST["message"]
                target = request.POST["target"]
                msj = escape(msj).replace('{', 'x').replace('}', 'x')
                try:
                    target = User.objects.get(username=target)
                    target = Persons.objects.get(user=target)
                    self_user = Persons.objects.get(user=user)
                    try:
                    	message_room = Message_room.objects.filter(users__id__iexact=target.id).filter(users__id__iexact=self_user.id)[0]
                    except ObjectDoesNotExist:
                        message_room = Message_room.objects.create()
                        message_room.users.add(target)
                        message_room.users.add(self_user)
                        message_room.root_date = None #datetime.utcnow()
                        message_room.save()
                    message = Messages.objects.create(room=message_room, target_user=target, sender=self_user, text=msj)
                except ObjectDoesNotExist:
                    return None
                print(message.text, message.tr_date())
                return HttpResponse(json.dumps({"message":message.text, "m_date":message.tr_date()}))
                #return HttpResponse({"message":str(message.text), "m_date":message.tr_date()})
                #return HttpResponse(json.dumps({"message":str(message.text), "m_date":message.tr_date()}), content_type="application/json")
            except MultiValueDictKeyError: #eger kullanicilar yok ise
                msj = None
            try:
                usr = request.POST["user"]
                usr = strip_tags(usr)
                try:
                    user = User.objects.get(username=usr)
                    kursiyer = Kursiyer.objects.get(user=user)
                except ObjectDoesNotExist:
                    return None
                chat_box = text_to_html(kursiyer=kursiyer, instructor=user)
                return HttpResponse(json.dumps({"chat_box":chat_box}))
            except MultiValueDictKeyError:
                usr = None
            return None
    elif request.method == "GET":
        if request.user:
            person = Persons.objects.get(user=request.user)
            context_dict={}
            chat_rooms = Message_room.objects.filter(users__id=person.id).distinct().order_by('updated_at')
            #chat_rooms = Message_room.objects.filter(user=person).order_by('updated_at')
            target = chat_rooms.first().users.all().exclude(user=person.user)[0]
            friend_list = []
            for x in chat_rooms:
            	friend_list += [x.users.all().exclude(user=person.user)[0].user]
            #friend listten kullanicilari cek kursiyerler = donem.kursiyerler.all()
            first_message = text_to_html(target=target, self_user=person, first=chat_rooms.first())
            if first_message:
                context_dict.update({"chat_box":first_message})
            focused = {"username":target.user.username, "isim":target.user.username}
            context_dict.update({"focused":focused, "friends":friend_list}) #kurisyerler yerine friendlisti sec
            return render (request, 'message.html', context_dict)




#Message_room objects cerate
#message_room = Message_room.objects.create()
#message_room.users.add(user1)
#message_room.users.add(user2)

#filter
#x = Message_room.objects.filter(users__in=[1,2]).distinct() #user ids or person objects
#x[0].users.all().values('user_id')

###### filtering bug solved ###
#https://code.djangoproject.com/ticket/16172
