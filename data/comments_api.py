import flask
from flask import jsonify, request, redirect
from . import db_session
from .comments import News
from flask_login import current_user

blueprint = flask.Blueprint(
    'comments_api',
    __name__,
    template_folder='templates'
)


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
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['content']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    news = News(
        content=request.json['content'],
        usid=current_user.id
    )
    db_sess.add(news)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/comments/<int:news_id>', methods=['DELETE'])
@blueprint.route('/api/commentsdel/<int:news_id>')
def delete_news(news_id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).get(news_id)
    if news.usid == current_user.id:
        if not news:
            return jsonify({'error': 'Not found'})
        db_sess.delete(news)
        db_sess.commit()
        return redirect("/")
    else:
        return jsonify({'error': 'It is not your comment'})


