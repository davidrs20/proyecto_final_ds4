import os
import json
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from app import app, db
from models import User, SavedJournal
from forms import LoginForm, RegistrationForm, SearchForm, JournalSearchForm, SaveJournalForm
from scraper import get_journal_data, search_journals, get_all_journals

@app.route('/')
@app.route('/index')
def index():
    search_form = SearchForm()
    issn_form = JournalSearchForm()
    
    # Get some sample journals for the homepage
    journals = get_all_journals()
    sample_journals = journals[:5] if len(journals) > 5 else journals
    
    return render_template('index.html', title='SciJournal Explorer', 
                          sample_journals=sample_journals,
                          search_form=search_form,
                          issn_form=issn_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard')
        
        flash('Login successful!', 'success')
        return redirect(next_page)
    
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's saved journals
    saved_journals = SavedJournal.query.filter_by(user_id=current_user.id).all()
    
    # Get the full journal data for each saved journal
    journals = []
    for saved in saved_journals:
        journal_data = get_journal_data(saved.journal_issn)
        if journal_data:
            # Add the notes and saved date to the journal data
            journal_data['notes'] = saved.notes
            journal_data['saved_at'] = saved.saved_at
            journals.append(journal_data)
    
    return render_template('dashboard.html', title='Your Dashboard', journals=journals)

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    
    results = []
    if form.validate_on_submit() or request.args.get('query'):
        query = form.query.data if form.validate_on_submit() else request.args.get('query')
        field = form.field.data if form.validate_on_submit() else request.args.get('field', 'title')
        
        results = search_journals(query, field)
        
        # Pre-populate the form with the search parameters
        form.query.data = query
        form.field.data = field
    
    return render_template('search.html', title='Search Journals', form=form, results=results)

@app.route('/journal/<issn>')
def journal_details(issn):
    journal = get_journal_data(issn)
    
    if not journal:
        flash('Journal not found', 'danger')
        return redirect(url_for('index'))
    
    # Check if the journal is saved by the current user
    is_saved = False
    saved_journal = None
    if current_user.is_authenticated:
        saved_journal = SavedJournal.query.filter_by(
            user_id=current_user.id, journal_issn=issn
        ).first()
        is_saved = saved_journal is not None
    
    save_form = SaveJournalForm()
    if saved_journal:
        save_form.notes.data = saved_journal.notes
    
    return render_template('journal_details.html', title=journal.get('title', 'Journal Details'),
                          journal=journal, is_saved=is_saved, save_form=save_form)

@app.route('/journal/<issn>/save', methods=['POST'])
@login_required
def save_journal(issn):
    # Check if journal exists
    journal = get_journal_data(issn)
    if not journal:
        flash('Journal not found', 'danger')
        return redirect(url_for('index'))
    
    form = SaveJournalForm()
    if form.validate_on_submit():
        # Check if already saved
        saved_journal = SavedJournal.query.filter_by(
            user_id=current_user.id, journal_issn=issn
        ).first()
        
        if saved_journal:
            # Update existing
            saved_journal.notes = form.notes.data
            flash('Journal updated in your saved list', 'success')
        else:
            # Create new
            saved_journal = SavedJournal()
            saved_journal.journal_issn = issn
            saved_journal.user_id = current_user.id
            saved_journal.notes = form.notes.data
            db.session.add(saved_journal)
            flash('Journal added to your saved list', 'success')
        
        db.session.commit()
    
    return redirect(url_for('journal_details', issn=issn))

@app.route('/journal/<issn>/unsave', methods=['POST'])
@login_required
def unsave_journal(issn):
    saved_journal = SavedJournal.query.filter_by(
        user_id=current_user.id, journal_issn=issn
    ).first()
    
    if saved_journal:
        db.session.delete(saved_journal)
        db.session.commit()
        flash('Journal removed from your saved list', 'success')
    
    return redirect(url_for('journal_details', issn=issn))

@app.route('/issn_lookup', methods=['POST'])
def issn_lookup():
    form = JournalSearchForm()
    if form.validate_on_submit():
        issn = form.issn.data
        if issn:
            issn = issn.strip()
            return redirect(url_for('journal_details', issn=issn))
        return redirect(url_for('index'))
    
    # If form has errors, go back to the index page
    return redirect(url_for('index'))

@app.template_filter('format_date')
def format_date(value, format='%Y-%m-%d'):
    if value:
        return value.strftime(format)
    return ""