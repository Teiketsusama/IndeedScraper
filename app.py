from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from scraper import search_jobs, sum_programming_skills, programming_languages, frameworks, databases
from os import path

app = Flask(__name__)

app.config['SECRET_KEY'] = 'So-Seckrekt'
basedir = path.abspath(path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + path.join(basedir, 'indeed_jobs.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

with app.app_context():
    db.Model.metadata.reflect(db.engine)


class Job(db.Model):
    __table__ = db.Model.metadata.tables['indeed_jobs']

    def __repr__(self):
        return f'<Job(job_link={self.job_link}, search_date={self.search_date}, title={self.title}, ' \
               f'company={self.company}, description={self.description})>'


@app.route('/')
def index():
    programming_language_dict = sum_programming_skills(programming_languages)
    framework_dict = sum_programming_skills(frameworks)
    database_dict = sum_programming_skills(databases)
    latest_date = Job.query.order_by(Job.search_date.desc()).first().search_date
    num_jobs = len(Job.query.all())
    locations = Job.query.with_entities(Job.location).distinct().all()

    return render_template('index.html',
                           programming_languages=programming_language_dict,
                           frameworks=framework_dict,
                           databases=database_dict,
                           latest_date=latest_date,
                           num_jobs=num_jobs,
                           locations=locations)


@app.route('/search', methods=['POST'])
def search():
    num_jobs = len(Job.query.all())
    if request.method == 'POST':
        job_title = request.form['job_title']
        job_location = request.form['job_location']
        num_pages = int(request.form['num_pages'])
        search_jobs(job_title, job_location, num_pages)
        flash(f'Scraped {num_pages} pages of {job_title} jobs in {job_location}!')
        flash('{} new jobs found!'.format(len(Job.query.all()) - num_jobs))
        return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
