import json

from flask import request, Response, url_for
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from posts import app
from .database import session, and_

@app.route("/api/posts", methods=["GET"])
@decorators.accept("application/json")
def posts_get(): 
    """Get a list of posts """
    #Check query string: 
    title_like = request.args.get("title_like")
    body_like = request.args.get("body_like")
    
    #get the posts from the database
    posts = session.query(models.Post)
    if title_like and body_like: 
        posts=posts.filter(and_(models.Post.title.contains(title_like), models.Post.body.contains(body_like)))
    elif title_like: 
        posts=posts.filter(models.Post.title.contains(title_like))
    elif body_like: 
        posts=posts.filter(models.Post.body.contains(body_like))    
    posts = posts.order_by(models.Post.id)    
    
    #convert the posts to JSON and return response
    data = json.dumps([post.as_dictionary() for post in posts])
    return Response(data, 200, mimetype="application/json")
    
@app.route("/api/posts/<int:id>", methods=["GET"])    
@decorators.accept("application/json")
def post_get(id):
    """Single post endpoint"""
    #Get the post from the database
    
    post=session.query(models.Post).get(id)
    
    #Check whether post exists, if not return a 404 with a helpful message
    
    if not post: 
        message="Could not find post with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")
        
    data = json.dumps(post.as_dictionary())
    return Response(data, 200, mimetype="application/json")
    
@app.route("/api/posts/<int:id>", methods=["DELETE"])    
@decorators.accept("application/json")
def post_delete(id): 
    post = session.query(models.Post).get(id)
    
    if not post: 
        message="Could not find post with id {}".format(id)
        data=json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")
        
    session.delete(post)
    session.commit()
    message="Post with id {} deleted".format(id)
    data=json.dumps({"message": message})
    return Response(data, 200, mimetype="application/json")