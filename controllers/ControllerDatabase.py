from typing import List

from models.ModelTag import ModelTag
from models.ModelPost import ModelPost
import sqlite3

from utils.UtilDatabaseCursor import UtilDatabaseCursor


class ControllerDatabase:

    @staticmethod
    def __connection():
        return sqlite3.connect("./blog.sqlite")

    @staticmethod
    def insert_post(post: ModelPost) -> int:
        post_id = 0
        try:
            with ControllerDatabase.__connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO posts (body, title, url_slug, parent_post_id) "
                    "VALUES (:title, :body, :url_slug, :parent_post_id);",
                    post.__dict__
                )
                post_id = cursor.execute("SELECT last_insert_rowid()").fetchone()[0]
                cursor.close()
        except Exception as exc:
            print(exc)
        return post_id

    @staticmethod
    def update_post(post: ModelPost):
        try:
            with ControllerDatabase.__connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE posts SET (title, body, url_slug, parent_post_id) = "
                    "(:title, :body, :url_slug, :parent_post_id) WHERE post_id = :post_id",
                    post.__dict__

                )
                cursor.close()

        except Exception as exc:
            print(exc)

    @staticmethod
    def get_post(post_id: int = None, url_slug: str = None) -> ModelPost:
        post = None
        try:
            with ControllerDatabase.__connection() as conn:
                cursor = conn.cursor()
                if post_id:
                    query = cursor.execute(
                        "SELECT * FROM posts WHERE post_id = :post_id LIMIT 1;",
                        {'post_id': post_id}
                    )
                else:
                    query = cursor.execute(
                        "SELECT * FROM posts WHERE url_slug = :url_slug LIMIT 1;",
                        {'url_slug': url_slug}
                    )
                if query.rowcount:
                    col = query.fetchone() # tuple of all * col values
                    post = ModelPost() # instance of object

                    (
                        post.post_id,
                        post.title,
                        post.body,
                        post.created,
                        post.modified,
                        post.url_slug,
                        post.thumbnail_uuid,
                        post.status,
                        post.parent_post_id
                    ) = col # pythonic wat to copy one by one variable from one tuple to another tuple
                cursor.close()

                # if post.parent_post_id is not None:
                #     post.parent_post = ControllerDatabase.get_post(post_id=post.parent_post_id)

                post.children_posts = ControllerDatabase.get_all_posts(parent_post_id=post.post_id)


        except Exception as exc:
            print(exc)
        return post

    @staticmethod
    def delete_post(post_id: int) -> bool:
        is_success = False
        try:
            with ControllerDatabase.__connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM posts WHERE post_id = ?;",
                    [post_id]
                )
                is_success = True
        except Exception as exc:
            print(exc)
        return is_success

    @staticmethod
    def get_all_posts(parent_post_id=None):
        posts = []
        try:
            with UtilDatabaseCursor() as cursor:
                cursor.execute(
                    f"SELECT post_id FROM posts WHERE parent_post_id {'=' if parent_post_id else 'IS'} ?",
                    [parent_post_id]
                )

                for post_id, in cursor.fetchall():
                    post = ControllerDatabase.get_post(post_id)
                    posts.append(post)
        except Exception as exc:
            print(exc)
        return posts

    @staticmethod
    def get_all_posts_flattened(parent_post_id=None, exclude_branch_post_id=None):
        posts_flattened = []
        try:
            post_hierarchy = ControllerDatabase.get_all_posts(parent_post_id)
            depth_by_post_id = {}
            while len(post_hierarchy) > 0:
                cur_post = post_hierarchy.pop(0)
                depth_by_post_id[cur_post.post_id] = 1

                if cur_post.post_id == exclude_branch_post_id:  # do not allow to create loops of parents
                    continue

                if cur_post.parent_post_id:
                    depth_by_post_id[cur_post.post_id] += depth_by_post_id[cur_post.parent_post_id]
                    cur_post.depth = depth_by_post_id[cur_post.post_id] - 1;

                post_hierarchy = cur_post.children_posts + post_hierarchy
                posts_flattened.append(cur_post)
        except Exception as exc:
            print(exc)
        return posts_flattened

    @staticmethod
    def get_all_tags() -> List[ModelTag]:
        tags = []
        try:
            with UtilDatabaseCursor() as cursor:
                cursor.execute(
                    f"SELECT * FROM tags"
                )
                for (
                    tag_id,
                    label,
                    is_deleted,
                    created,
                    modified
                ) in cursor.fetchall():
                    tag = ModelTag()
                    tag.tag_id = tag_id
                    tag.label = label
                    tag.is_deleted = is_deleted
                    tag.created = created
                    tag.modified = modified
                    tags.append(tag)

        except Exception as exc:
            print(exc)

        return tags