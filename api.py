from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)

# 数据表
class PostModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"Post(title = {self.title}, content = {self.content})"

# ?# 数据序列化
post_args = reqparse.RequestParser()
post_args.add_argument("title", type=str, help="Title of the post", required=True)
post_args.add_argument("content", type=str, help="Content of the post", required=True)


# ?# 数据反序列化
postFields = {
    'id': fields.Integer,
    'title': fields.String,
    'content': fields.String
}

# ?# 资源类
class Posts(Resource):
    @marshal_with(postFields)
    def get(self):
        posts = PostModel.query.all()
        return posts

    @marshal_with(postFields)
    def post(self):
        args = post_args.parse_args()
        post = PostModel(title=args['title'], content=args['content'])
        db.session.add(post)
        db.session.commit()
        return post, 201
    
# ?# 资源类
class Post(Resource):
    @marshal_with(postFields)
    def get(self, post_id):
        post = PostModel.query.filter_by(id=post_id).first()
        if not post:
            abort(404, message="Post not found")
        return post

    @marshal_with(postFields)
    def put(self, post_id):
        args = post_args.parse_args()
        post = PostModel.query.filter_by(id=post_id).first()
        if not post:
            abort(404, message="Post not found")
        post.title = args['title']
        post.content = args['content']
        db.session.commit()
        return post

    def delete(self, post_id):
        post = PostModel.query.filter_by(id=post_id).first()
        if not post:
            abort(404, message="Post not found")
        db.session.delete(post)
        db.session.commit()
        return '', 204

api.add_resource(Posts, "/posts")
api.add_resource(Post, "/posts/<int:post_id>")

@app.route('/')
def home():
    return '<h1>Flask REST API</h1>'

if __name__ == "__main__":
    # 初始化数据库
    with app.app_context():
        db.create_all()
    app.run(debug=True)