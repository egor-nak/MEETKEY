from flask import Flask, request, jsonify, render_template, send_from_directory, send_file, redirect
import os
from flask_restful import reqparse, abort, Api, Resource
from flask import make_response
from flask_login import LoginManager, login_user, login_required, logout_user
from data.users import User
from data.comments import News
from data import db_session
from data.add_comment import AddJobForm
from data.register import RegisterForm
from data.login_form import LoginForm
from data import comments_api
from flask_ngrok import run_with_ngrok
from flask_login import current_user

app = Flask(__name__)
api = Api(app)
app.config['UPLOAD_FOLDER'] = '/README.txt'
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
namecur = ''


# Обработка ошибки
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# коннект с базой данных
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# главная страница
@app.route("/")
def root():
    db_sess = db_session.create_session()
    jobs = db_sess.query(News).all()
    users = db_sess.query(User).all()
    names = {name.id: name.name for name in users}
    flag = True
    try:
        print(current_user.id)
    except Exception:
        flag = False
    if flag:
        return render_template("addcomettomainpage.html", coments=jobs, names=names, cr=current_user)
    else:
        return render_template("addcomettomainpage.html", coments=jobs, names=names, cr='hi')


# кнопка скачать
@app.route("/download", methods=['GET', 'POST'])
def hi():
    return send_file('text.txt', as_attachment=True)


# страница регестрации
@app.route("/reg", methods=['GET', 'POST'])
def reg():
    global namecur

    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('reg.html', title='Register', form=form,
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('reg.html', title='Register', form=form,
                                   message="This user already exists")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        namecur = form.name.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        print(form.name.data)
        return redirect(f"/addjob/{user.id}")
    return render_template('reg.html', title='Регистрация', form=form)


# страница входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    global namecur
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            namecur = user.name
            return redirect(f"/addjob/{user.id}")
        return render_template('log.html', message="Wrong login or password", form=form)
    return render_template('log.html', title='Authorization', form=form)


# добавление комментариев
@app.route('/addjob/<int:id>', methods=['GET', 'POST'])
def addjob(id):
    global namecur
    try:
        print(current_user.id)
        add_form = AddJobForm()
        if add_form.validate_on_submit():
            db_sess = db_session.create_session()
            users = db_sess.query(User).all()
            names = {name.id: name.name for name in users}
            jobs = News(
                content=add_form.content.data,
                usid=id
            )
            db_sess.add(jobs)
            db_sess.commit()
            return redirect('/')
        return render_template('addcomment.html', title='Adding a job', form=add_form)
    except:
        return "log in please"


# разлогиниться
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# редактирование комментария
@app.route('/commentsedit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = AddJobForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.usid == current_user.id
                                          ).first()
        if news:
            form.content.data = news.content
            us = news.usid
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.usid == current_user.id
                                          ).first()
        us = news.usid
        if news:
            news.content = form.content.data
            news.usid = us
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('addcomment.html',
                           title='Редактирование новости',
                           form=form
                           )


def main():
    db_session.global_init("db/main_data.db")
    app.register_blueprint(comments_api.blueprint)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    logout_user()


if __name__ == "__main__":
    main()
