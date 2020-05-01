from django.db import models
from django.conf import settings
from django.utils.html import format_html
import datetime
from django.contrib.auth.models import User
from babel.dates import format_date, format_datetime, format_time
# Create your models here.

class Persons(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
    #def son_mesaj(self):
	#	try:
	#		room = Message_room.objects.get(kursiyer=self)
	#		son_mesaj = Message_room.objects.all_messages(room)
	#		if len(son_mesaj) != 0:
	#			son_mesaj = son_mesaj.last().text
	#			return son_mesaj
	#		else:
	##			return "Henuz mesaj yok."
	#	except ObjectDoesNotExist:
	#		return "Henuz mesaj yok."

	def __str__(self):
		return self.user.username

class room_manager(models.Manager):
    def all_messages(self, room):  # aktif olan odevleri dondurur.  aktif_odevler.objects.is_active()
        return Messages.objects.filter(room=room).order_by('created_at')

    def last_message(self, room): #odani nson mesajini dondurur
        return Messages.objects.all_messages(room=room).last()

class Message_room(models.Model):
    #user  = models.ForeignKey('Persons',null=True, blank=True, on_delete=models.CASCADE)
    users = models.ManyToManyField(Persons)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = room_manager()
    kursiyer_date = models.DateTimeField(null=True, blank=True)
    root_date = models.DateTimeField(null=True, blank=True)

    def unread(self, target=None): #kisiyi pasla ve ona gore okunmayan mesajalri goruntule
	    all_messages= Message_room.objects.all_messages(self)
	    if len(all_messages) <= 0:
	    	return "0"
	    son_mesaj = all_messages.last()
	    if self.root_date:
	    	if self.root_date < son_mesaj.created_at:
	    		unread = all_messages.filter(created_at__range=(self.root_date, datetime.datetime.now()), sender=self.Persons.user)
	    		return str(len(unread)) #okunmayan mesajalrin sayisi
	    	else:
	    		return "0"
	    else:
	    	return str(len(all_messages.filter(sender=self.user.user)))
        #elif Person: #eger kursiyer ise
        #    instructor = User.objects.get(username='root')
        #    all_messages= Message_room.objects.all_messages(self)
        #    if len(all_messages) <= 0:
         #       return "0"
         #   son_mesaj = all_messages.last()
        #    if self.kursiyer_date < son_mesaj.created_at:
        #        unread = all_messages.filter(created_at__range=(self.kursiyer_date, datetime.datetime.now()), sender=instructor)
        #        return str(len(unread)) #okunmayan mesajalrin sayisi
        #    else:
        #        return "0"
            #return self.filter(donem=donem,end_time__gt=now, start_time__lt=now)

    def __str__(self):
    	return "{} - {}".format(self.users.all()[0].user.username, self.users.all()[1].user.username)
    	#return self.user.user.username+"'s CHAT ROOM"

class Messages(models.Model):
    sender = models.ForeignKey(Persons, on_delete=models.CASCADE, related_name='sender')
    text = models.TextField(max_length=600, default=None, blank=True)
    target_user = models.ForeignKey(Persons, on_delete=models.CASCADE, related_name='target')
    room = models.ForeignKey(Message_room, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def tr_date(self):
        hour = self.created_at.strftime("%H:%M")
        date = format_date(self.created_at, locale="tr")
        date = hour + " "+ date
        return date
		#return date.encode('utf8')

    def __str__(self):
        return self.sender.user.username + "->" + self.target_user.user.username + " | "  + self.text
