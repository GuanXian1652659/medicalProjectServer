from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import json
import tasks
# Create your views here.

#test my settings...

def index(request):
    #api in json format
    ans=tasks.add(1,100)
    data={
        'hello':12,
        'world':13,
        'summer':14,
        'databasecoursedesign':'fuck',
        'ans':ans
    }
    return JsonResponse(data)



