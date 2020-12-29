from flask import render_template
from app import app

from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.models import User, Post
from .forms import LoginForm, RegisterForm, EditProfileForm, CreatePostForm
from flask_login import login_required, login_user, logout_user, current_user
import datetime
import time
import pytz
import feedparser

CARDS_PER_PAGE = 5


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.datetime.utcnow()
        db.session.commit()


# Главный адрес
# Перенаправляет на /login, /admin, /counter
@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        if current_user.username == 'admin':
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('blog'))

    return redirect(url_for('login'))


# Авторизация
# Вход в аккаунт или переход к регистрации
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.username == 'admin':
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('blog'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        if user.username == 'admin':
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('blog'))

    return render_template('login.html',
                           title='Вход',
                           form=form)


# Выход из аккаунта
# Выходит и пересылает на логин
@app.route('/logout/')
def logout():
    logout_user()
    flash("Вы успешно вышли из аккаунта.")
    return redirect(url_for('login'))


# Регистрация
# Форма регистрации с редиректом на логин
# Можно зарегаться только как юзер
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()

    if form.validate_on_submit():
        user = User(username=form.username.data)

        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Вы зарегистрировались! Теперь можно входить.')
        return redirect(url_for('login'))

    return render_template('register.html',
                           title='Регистрация',
                           form=form)


# Информация о любом пользователе
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    utc = pytz.timezone('UTC')
    msk = pytz.timezone('Europe/Moscow')
    user.last_seen = utc.localize(user.last_seen).astimezone(msk).strftime("%d-%m-%Y %H:%M")

    return render_template('user.html', user=user)


# Редактирование профиля (для владельца или админа)
@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    profile_id = request.args.get("id", current_user.id, type=int)
    u = User.query.filter(User.id == profile_id).first()

    form = EditProfileForm()
    if form.validate_on_submit():
        u.username = form.username.data
        u.about_me = form.about_me.data

        if form.password.data != '':
            u.set_password(form.password.data)

        db.session.commit()

        flash('Ваши изменения сохранены!')
        return redirect(url_for('edit_profile', id=profile_id))
    elif request.method == 'GET':
        form.username.data = u.username
        form.password.data = ''
        form.about_me.data = u.about_me

    return render_template("edit-profile.html",
                           title='Редактировать профиль',
                           user=u,
                           form=form)


# Админка (только для админов)
# Позволяет просматривать инфу о пользователях и удалять профили
@login_required
@app.route('/admin')
def admin():
    if current_user.username != 'admin':
        return redirect(url_for('blog'))

    delete_id = request.args.get('delete', -1, type=int)
    if delete_id > -1:
        u = User.query.filter(User.id == delete_id).first()

        for t in u.transactions.all():
            db.session.delete(t)

        db.session.delete(u)
        db.session.commit()

        flash('Пользователь удален!')
        return redirect(url_for('admin'))

    users_list = User.query.all()

    return render_template('admin.html',
                           title='Админка',
                           user=current_user,
                           users_list=users_list)


# Список постов с кнопкой удаления для админа
@login_required
@app.route('/manage')
def manage():
    if current_user.username != 'admin':
        return redirect(url_for('blog'))

    delete_id = request.args.get('delete', -1, type=int)
    if delete_id > -1:
        p = Post.query.filter(Post.id == delete_id).first()

        db.session.delete(p)
        db.session.commit()

        flash('Пост удален!')
        return redirect(url_for('manage'))

    posts = Post.query.all()

    return render_template('manage.html',
                           title='Админка',
                           user=current_user,
                           posts=posts)


# Написать новый пост
@login_required
@app.route('/create', methods=['GET', 'POST'])
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        post = Post(headline=form.headline.data,
                    text=form.text.data,
                    author=current_user
                    )

        db.session.add(post)
        db.session.commit()

        flash('Новость добавлена на главную страницу!')
        return redirect(url_for('blog'))

    return render_template("create.html",
                           title='Добавить новость',
                           user=current_user,
                           form=form)


# Страничка с постами пользователей и пагинацией
@login_required
@app.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, CARDS_PER_PAGE, False)

    next_url = url_for('blog', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('blog', page=posts.prev_num) \
        if posts.has_prev else None

    for p in posts.items:
        utc = pytz.timezone('UTC')
        msk = pytz.timezone('Europe/Moscow')
        p.timestamp = utc.localize(p.timestamp).astimezone(msk)
        p.timestamp = p.timestamp.strftime("%d-%m-%Y %H:%M")

    return render_template('blog.html',
                           title='Блог',
                           user=current_user,
                           posts=posts.items,
                           next_url = next_url,
                           prev_url = prev_url
                           )


# Страничка с новостями
@login_required
@app.route('/news')
def news():
    page = request.args.get('page', 1, type=int)
    d = feedparser.parse('https://republic.ru/export/all.xml')

    next_url = url_for('news', page=page + 1)
    prev_url = url_for('news', page=page - 1) \
        if page > 1 else None

    news_items = d.entries[((page - 1) * CARDS_PER_PAGE):(page * CARDS_PER_PAGE)]
    for n in news_items:
        t = datetime.datetime.fromtimestamp(time.mktime(n.published_parsed))
        utc = pytz.timezone('UTC')
        msk = pytz.timezone('Europe/Moscow')
        t = utc.localize(t).astimezone(msk)

        n.time = t.strftime("%d-%m-%Y %H:%M (MSK)")

    return render_template('news.html',
                           title='Новости',
                           user=current_user,
                           news = news_items,
                           next_url=next_url,
                           prev_url=prev_url
                           )
