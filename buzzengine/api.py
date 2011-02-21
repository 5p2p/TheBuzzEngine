#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Alexandru Nedelcu"
__email__     = "contact@alexn.org"


import json

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from buzzengine.forms import NewCommentForm
from buzzengine import models

def hello(request):
    return HttpResponse("Hello World")
        

def comment_create(request):
    if request.method != 'GET':
        resp = HttpResponse("Method Not Allowed", mimetype="text/plain")
        resp.status_code = 405
        return resp

    form = NewCommentForm(request.REQUEST)
    if not form.is_valid():
        resp = HttpResponse(json.dumps(form.errors, indent=4), mimetype='text/plain')
        resp.status_code = 400
        return resp

    form.save()
    return HttpResponse(json.dumps(form.output, indent=4), mimetype='text/plain')


def comment_list(request):
    url = request.REQUEST.get('article_url')    
    
    if not url:
        resp = HttpResponse(json.dumps({'article_url': ['This field is required.']}, indent=4), mimetype='text/plain')
        resp.status_code = 400
        return resp
    
    article = models.Article.get_by_key_name(url)
    if not article:
        raise Http404

    comments = models.Comment.gql("WHERE article = :1", article)    
    comments = [ {'comment': c.comment, "author": { "name": c.author.name, 'url': c.author.url }} for c in comments ]

    return HttpResponse(json.dumps(comments, indent=4), mimetype="text/plain")
