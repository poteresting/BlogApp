import functools

import flask
from flask import request, redirect, url_for

from controllers.ControllerDatabase import ControllerDatabase
from models.ModelPost import ModelPost
from models.ModelTag import ModelTag

class ControllerPosts:
    blueprint = flask.Blueprint("posts", __name__, url_prefix="/posts")

    @staticmethod
    @blueprint.route("/new", methods=["POST", "GET"])
    @blueprint.route("/edit/<post_id>", methods=["POST", "GET"])
    def post_edit(post_id=None):

        post = ModelPost()
        if post_id:
            post_id = int(post_id)
            if post_id > 0:
                post = ControllerDatabase.get_post(post_id)

        posts_flattened = ControllerDatabase.get_all_posts_flattened(exclude_branch_post_id=post_id)
        post_parent_id_and_title = [
            (None, "No parent")
        ]
        for post_hierarchy in posts_flattened:
            str_indent = ''
            if post_hierarchy.parent_post_id:
                str_indent = ''.join(['-'] * post_hierarchy.depth) + ' '
            str_title = f'{str_indent}{post_hierarchy.title}'
            post_parent_id_and_title.append(
                (post_hierarchy.post_id, str_title)
            )

        if request.method == "POST":
            button_type = request.form.get("button_type")
            if button_type == "delete":
                ControllerDatabase.delete_post(post_id)
                return redirect('/?deleted=1')

            post.title = request.form.get('post_title').strip()
            post.body = request.form.get('post_body').strip()
            post.url_slug = request.form.get('url_slug').strip()


            try:
                post.parent_post_id = int(request.form.get('parent_post_id'))
            except:
                post.parent_post_id = None

            if post.post_id > 0:
                ControllerDatabase.update_post(post)
                return redirect(f"/?edited={post.url_slug}")
            else:
                post_id = ControllerDatabase.insert_post(post)

            return redirect(url_for('posts.post_view', url_slug=post.url_slug))

        post_tags_ids = []
        tags = ControllerDatabase.get_all_tags()

        return flask.render_template(
            'posts/edit.html',
            post=post,
            post_tags_ids=post_tags_ids,
            tags=tags,
            post_parent_id_and_title=post_parent_id_and_title
        )

    @staticmethod
    @blueprint.route("/view/<url_slug>", methods=["GET"])
    def post_view(url_slug):
        post = ControllerDatabase.get_post(url_slug=url_slug)
        return flask.render_template(
            'posts/view.html',
            post=post
        )