import flask
from flask import jsonify, request, redirect, render_template
from . import db_session
from .comments import News
from flask_login import current_user
from flask_login import LoginManager, login_user, login_required, logout_user
from .login_form import LoginForm
from .users import User
from flask_login import current_user

blueprint = flask.Blueprint(
    'comments_api',
    __name__,
    template_folder='templates'
)

namecur = ''


@blueprint.route('/api/login', methods=['GET', 'POST'])
def login():
    global namecur
    # print(current_user.id)
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['email', 'password']):
        return jsonify({'error': 'Bad request'})
    d = request.json
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == d['email']).first()
    if user and user.check_password(d['password']):
        login_user(user)
        namecur = user.id
        # print(namecur)
        try:
            print(current_user)
        except Exception:
            print('no')
        return jsonify({'success': 'OK'})
    else:
        return jsonify({'error': 'Wrong password'})


@blueprint.route('/api/comments')
def get_news():
    db_sess = db_session.create_session()
    news = db_sess.query(News).all()
    return jsonify(
        {
            'news':
                [item.to_dict(only=('content', 'name'))
                 for item in news]
        }
    )


@blueprint.route('/api/comments/<int:news_id>', methods=['GET'])
def get_one_news(news_id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).get(news_id)
    if not news:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'news': news.to_dict(only=('content', 'usid'))
        }
    )


@blueprint.route('/api/comments', methods=['POST'])
def create_news():
    global namecur
    try:
        if not request.json:
            return jsonify({'error': 'Empty request'})
        elif not all(key in request.json for key in
                     ['content']):
            return jsonify({'error': 'Bad request'})
        db_sess = db_session.create_session()
        news = News(
            content=request.json['content'],
            usid=namecur
        )
        db_sess.add(news)
        db_sess.commit()
        return jsonify({'success': 'OK'})
    except Exception:
        return jsonify({'error': 'please log in'})


@blueprint.route('/api/comments/<int:news_id>', methods=['DELETE'])
@blueprint.route('/api/commentsdel/<int:news_id>')
def delete_news(news_id):
    global namecur
    try:
        db_sess = db_session.create_session()
        news = db_sess.query(News).all()
        flag = False
        nw = ''
        for i in news:
            print(i.id, news_id)
            if int(i.id) == news_id:
                flag = True
                nw = i
                break
        if not flag:
            return jsonify({'error': 'Not found'})
        if nw.usid == namecur:
            db_sess.delete(nw)
            db_sess.commit()
            return redirect("/")
        else:
            return jsonify({'error': 'It is not your comment'})
    except Exception:
        return jsonify({'error': 'Please log in'})
