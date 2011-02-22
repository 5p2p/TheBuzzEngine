#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Alexandru Nedelcu"
__email__     = "contact@alexn.org"


import json, hashlib

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from buzzengine.api.forms import NewCommentForm
from buzzengine.api import models


def comments(request):
    url = request.REQUEST.get('article_url') or request.META.get('HTTP_REFERER')

    if not url:        
        resp = HttpResponse(json.dumps({'article_url': ['This field is required.']}, indent=4), mimetype='text/plain')
        resp.status_code = 400
        return resp

    if request.method == 'POST':
        return _comment_create(request, url)
    else:
        return _comment_list(request, url)


def _comment_create(request, article_url):
    data = request.POST
    data = dict([ (k,data[k]) for k in data.keys() ])
    data['article_url'] = article_url

    is_json = not request.META['HTTP_ACCEPT'].find("html")

    form = NewCommentForm(data)
    if not form.is_valid():
        if is_json:
            resp = HttpResponse(json.dumps(form.errors, indent=4), mimetype='text/plain')
            resp.status_code = 400
            return resp
        else:
            return _comment_list(request, article_url, form=form)

    form.save()
    if is_json:
        return HttpResponse("OK", mimetype='text/plain')
    return HttpResponseRedirect("/api/comments/")


def _comment_list(request, article_url, form=None):
    article = models.Article.get_by_key_name(article_url)
    if article:
        comments = models.Comment.gql("WHERE article = :1", article)
    else:
        comments = []    

    is_json = not request.META['HTTP_ACCEPT'].find("html")
    if is_json:
        comments = [ {'comment': c.comment, "author": { "name": c.author.name, 'url': c.author.url }} for c in comments ]
        return HttpResponse(json.dumps(comments, indent=4), mimetype="text/plain")

    form = form or NewCommentForm()
    return render_to_response("api/comments.html", {'comments': comments, 'form': form})


def test_page(request):
    return render_to_response("api/test_page.html")