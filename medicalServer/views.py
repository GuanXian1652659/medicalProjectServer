from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import json
from .tasks import add
# Create your views here.

#test my settings...
'''def getIP(request):
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip =  request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    return ip
'''

def index(request):
    #api in json format
    add.delay(4,5)
    data={
        'hello':12,
        'world':13,
        'summer':14,
        'databasecoursedesign':'fuck',
        #'ans':ans
    }
    return JsonResponse(data)



