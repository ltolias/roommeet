#render shortcut
from django.shortcuts import render, redirect
import time
import json
import math

#responses, httpresponse not necessary with render shortcut
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
#templates and contexts, not necessary with render shortcut
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.utils.html import strip_tags

import datetime
from roommeet.forms import ProfileForm

from django.views.decorators.csrf import csrf_exempt
from people.models import Person
from django.contrib.auth.decorators import login_required

from django.forms.models import model_to_dict


#function to generate html and return

@login_required
def meet(request):
	p = Person.objects.filter(netid=request.user.username)
	if (not p):
		p1 = Person(netid=request.user.username)
		p1.save()

	currentNetid = request.user.username
	me = Person.objects.get(netid=currentNetid)
	if request.method == 'POST':
		pf = ProfileForm(request.POST)

		if pf.is_valid():
			cd = pf.cleaned_data
			p = Person.objects.filter(netid=currentNetid)
			if (p):
				p1 = p[0];
				p1.netid = currentNetid
				p1.first_name = cd['first_name']
				p1.last_name = cd['last_name']
				p1.lat = cd['lat_s']
				p1.lon = cd['lon_s']
				p1.start = cd['start']
				p1.end = cd['end']
				p1.company = cd['company']
				p1.year = (int)(cd['year'])
				p1.desired = cd['desired']
				p1.gender = cd['gender']
				p1.save()
			else:
				p1 = Person(netid=currentNetid, first_name=['first_name'], 
				last_name=cd['last_name'], lat=cd['lat_s'], 
				lon=cd['lon_s'], company=cd['company'], year=cd['year'])
				p1.save()

			t = get_template('profile.html')
			html = t.render(RequestContext(request, {'form': pf}))
			data = {'success':'true', 'html':html}
			return HttpResponse(json.dumps(data), content_type = "application/json")

		else:
			pf.errors['lat_s'] = pf.error_class()

		t = get_template('profile.html')
		html = t.render(RequestContext(request, {'form': pf}))
		
		data = {'success':'false', 'html':html}
		return HttpResponse(json.dumps(data), content_type = "application/json")

	else:
		pf = ProfileForm(initial=model_to_dict(me))
	friends = me.friends.all()
	return render(request, 'meet.html', {'form': pf, 'friend_list':friends})


@login_required
def talk(request):
	currentNetid = request.user.username
	me = Person.objects.get(netid=currentNetid)
	friends = me.friends.all()
	return render(request, 'talk.html', {'friend_list':friends})


@login_required
def get_marks(request):
	currentNetid = request.user.username
	radius = 100000000000;
	gender = 'either'
	olap = -10000

	year = 0
	if request.POST:
		if 'radius' in request.POST:
			radius = int(request.POST['radius'])
		if 'gender' in request.POST:
			gender = str(request.POST['gender'])
		if 'year' in request.POST:
			year = int(request.POST['year'])
		if 'olap' in request.POST:
			olap = int(request.POST['olap'])

		if radius == 0:
			radius = 100000000000;
	me = Person.objects.get(netid=currentNetid)
	lrad = math.cos(math.radians(float(me.lat))) * 111.325 * 0.621371;
	lonrad = radius / lrad;
	radius = radius / 69.172;
	olap = olap
	if gender == 'either' and year == 0:
		p = Person.objects.filter(lat__gt=float(me.lat)-radius).filter(lat__lt=float(me.lat)+radius).filter(lon__gt=float(me.lon)-lonrad).filter(lon__lt=float(me.lon)+lonrad)
	elif gender == 'either' and year != 0:
		p = Person.objects.filter(lat__gt=float(me.lat)-radius).filter(lat__lt=float(me.lat)+radius).filter(lon__gt=float(me.lon)-lonrad).filter(lon__lt=float(me.lon)+lonrad).filter(year=year)
	elif gender != 'either' and year == 0:
		p = Person.objects.filter(lat__gt=float(me.lat)-radius).filter(lat__lt=float(me.lat)+radius).filter(lon__gt=float(me.lon)-lonrad).filter(lon__lt=float(me.lon)+lonrad).filter(gender=gender)
	else :
		p = Person.objects.filter(lat__gt=float(me.lat)-radius).filter(lat__lt=float(me.lat)+radius).filter(lon__gt=float(me.lon)-lonrad).filter(lon__lt=float(me.lon)+lonrad).filter(gender=gender).filter(year=year)
	print radius
	locs = []
	people = []
	for person in p:
		mylength = me.end - me.start
		personlength = person.end - person.start
			
		if me.start < person.start:
			startdiff = person.start - me.start
			overlapTime = min(mylength-startdiff, personlength)
			print "length days: ", overlapTime.days
		else : 
			startdiff = me.start - person.start
			overlapTime = min(personlength-startdiff, mylength)
			print "length days: ", overlapTime.days
		if overlapTime.days > olap:
			people.append(person)
	if not people or me not in people:
		people.append(me)
	for p1 in people:
		print p1.first_name,
		print p1.gender
		friend = "no"
		f = True
                isSelf = False
                if (p1.netid == currentNetid):
                        isSelf = True
		if (me.friends.filter(netid=p1.netid)):
			friend = "yes"
			f = False
		t = get_template('buttonfill.html')
		html = t.render(Context({'person':p1, 'add':f, 'isSelf':isSelf}))
		locs.append({'lat':str(p1.lat), 'lon':str(p1.lon), 'netid':p1.netid, 'html':html})
	locs.append({'lat':str(me.lat), 'lon':str(me.lon),})
	return HttpResponse(json.dumps(locs), mimetype='application/json; charset=UTF-8')

@login_required
def meet_person(request):
	currentNetid = request.user.username
	addNetid = ''
	if request.POST:
		if 'netid' in request.POST:
			addNetid = request.POST['netid']
	me = Person.objects.get(netid=currentNetid)
	r = {'result':'success'}
	html = ''
	if (me.friends.filter(netid=addNetid)):
		r['result'] = 'already there'
        elif (currentNetid == addNetid):
                p1 = Person.objects.get(netid=addNetid)
                t = get_template('buttonfill.html')
                html = t.render(Context({'person':p1, 'add':True, 'isSelf':True}))
	else:
		p1 = Person.objects.get(netid=addNetid)
		me.friends.add(p1)
		t = get_template('buttonfill.html')
		html = t.render(Context({'person':p1, 'add':False, 'isSelf':False}))

	r['html'] = html
	t = get_template('tablefill.html')
	friends = me.friends.all()
	table = t.render(Context({'friend_list':friends}))
	r['table'] = table
	return HttpResponse(json.dumps(r), mimetype='application/json; charset=UTF-8')

@login_required
def remove_person(request):
	currentNetid = request.user.username
	remNetid = ''
	rtype = 'meet'
	if request.POST:
		if 'netid' in request.POST:
			remNetid = request.POST['netid']
	me = Person.objects.get(netid=currentNetid)
	p1 = Person.objects.get(netid=remNetid)
	me.friends.remove(p1)
	friends = me.friends.all()
	t = get_template('tablefill.html')
	table = t.render(Context({'friend_list':friends}))
	r = {'table':table}

	t = get_template('buttonfill.html')
	html = t.render(Context({'person':p1, 'add':True}))
	r['html'] = html

	return HttpResponse(json.dumps(r), mimetype='application/json; charset=UTF-8')


