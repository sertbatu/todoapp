from todoapp import db
from todoapp.forms import EditItemForm
from flask import render_template, redirect, url_for, flash, request, Blueprint, jsonify, session
from flask_login import current_user, login_user, logout_user, login_required
from todoapp.forms import LoginForm, RegistrationForm, ListForm, ItemForm
from todoapp.models import User, List, Item, FavoriteList
from werkzeug.urls import url_parse

# Blueprint-Konfiguration
web = Blueprint(
    'web', __name__,
    template_folder='templates',
)

# Route zur Startseite
@web.route('/')
@web.route('/index')
@login_required
def index():
    lists = List.query.all()
    return render_template('index.html', lists=lists)

# Route zur Benutzerregistrierung
@web.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('web.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('web.login'))
    return render_template('register.html', title='Register', form=form)

# Route zur Benutzeranmeldung
@web.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('web.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('web.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('web.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

# Route zur Benutzerabmeldung
@web.route('/logout')
def logout():
    logout_user()
    session.pop('_flashes', None)
    return redirect(url_for('web.login'))

# Route zu den Listen des Benutzers
@web.route('/lists')
@login_required
def lists():
    lists = current_user.lists
    return render_template('list.html', lists=lists)

# Route zur Erstellung einer neuen Liste
@web.route('/new_list', methods=['GET', 'POST'])
@login_required
def new_list():
    form = ListForm()
    if form.validate_on_submit():
        list = List(title=form.title.data, owner=current_user)
        db.session.add(list)
        db.session.commit()
        db.session.flush()
        list_id = list.id
        print(list_id)
        flash('Your list has been created!')
        return redirect(url_for('web.list', list_id=list_id))
    return render_template('create_list.html', title='New List', form=form)

# Route zu den Listendetails
@web.route('/list/<int:list_id>', methods=['GET', 'POST'])
@login_required
def list(list_id):
    list = List.query.get_or_404(list_id)
    form = ItemForm()
    if form.validate_on_submit():
        item = Item(description=form.name.data, deadline=form.deadline.data, status=form.status.data, list=list)
        db.session.add(item)
        db.session.commit()
        flash('Your item has been added to the list!')
        return redirect(url_for('web.list', list_id=list.id))
    return render_template('list_detail.html', title=list.title, list=list, form=form)



# Route zum Löschen einer Liste
@web.route('/list/<int:list_id>/delete', methods=['POST'])
@login_required
def delete_list(list_id):
    list = List.query.get_or_404(list_id)
    for item in list.items:
        db.session.delete(item)
    db.session.delete(list)
    db.session.commit()
    flash('Your list has been deleted!')
    return redirect(url_for('web.user', username=current_user.username))


# Route zum Kopieren einer Liste
@web.route('/list/<int:list_id>/copy', methods=['GET', 'POST'])
@login_required
def copy_list(list_id):
    list = List.query.get_or_404(list_id)
    new_list = List(title=list.title, owner=current_user)
    db.session.add(new_list)
    db.session.commit()
    for item in list.items:
        new_item = Item(description=item.description, deadline=item.deadline, status=item.status, list=new_list)
        db.session.add(new_item)
        db.session.commit()
    flash(f'The Shared list from User {list.owner.username} has been copied to your private To-Do List!')
    return redirect(url_for('web.user', username=current_user.username))


# Route zum Umschalten des Completed-Status eines Items
@web.route('/item/<int:item_id>/toggle', methods=['POST'])
@login_required
def toggle_item(item_id):
    status = request.json.get('status')
    item = Item.query.get_or_404(item_id)
    item.completed = status
    db.session.commit()
    return jsonify({'success': True})


# Route zum Umschalten zwischen public/private List
@web.route('/list/<int:list_id>/toggle_public', methods=['POST'])
@login_required
def toggle_public(list_id):
    list = List.query.get_or_404(list_id)
    
    # Prüfen, ob der aktuelle Benutzer der owner der Liste ist
    if list.owner != current_user:
        flash("You don't have permission to change the visibility of this list.")
        return redirect(url_for('web.list', list_id=list_id))

    if list.public:
        list.public = False
    else:
        list.public = True
    db.session.commit()
    return redirect(url_for('web.list', list_id=list_id))



# Route zum Umschalten der Favoritenliste
@web.route('/list/<int:list_id>/toggle_favorite', methods=['POST'])
@login_required
def toggle_favorite(list_id):
    referrer = request.referrer
    favorite = FavoriteList.query.filter_by(user_id=current_user.id, list_id=list_id).first()
    if favorite:
        db.session.delete(favorite)
    else:
        favorite = FavoriteList(user_id=current_user.id, list_id=list_id)
        db.session.add(favorite)
    db.session.commit()
    return redirect(referrer)


# Route zu den Favoritenlisten
@web.route('/favorites')
@login_required
def favorites():
    favorite_lists = current_user.favorite_lists
    return render_template('favorites.html', favorite_lists=favorite_lists)
    


# Route zum Benutzerprofil
@web.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    lists = user.lists
    return render_template('profile.html', user=user, lists=lists)


# Route zur Bearbeitung eines Items
@web.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.list.user_id != current_user.id:
        abort(403)
    form = EditItemForm()
    if form.validate_on_submit():
        item.description = form.description.data
        item.deadline = form.deadline.data
        item.status = form.status.data
        db.session.commit()
        flash('Your item has been updated!', 'success')
        return redirect(url_for('web.list', list_id=item.list_id))
    elif request.method == 'GET':
        form.description.data = item.description
        form.deadline.data = item.deadline
        form.status.data = item.status
    return render_template('edit_item.html', form=form, item=item)


# Fehlerbehandlung für 404 (Seite nicht gefunden)
@web.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Fehlerbehandlung für 500 (Interner Fehler)
@web.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500