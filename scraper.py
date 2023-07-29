from bs4 import BeautifulSoup
from re import search, escape, IGNORECASE
from datetime import datetime
from database import init_db, db_session
from models import IndeedJob
from scrapercofig import driver
from time import sleep
from random import random

init_db()


def get_job_urls(url: str) -> list:
    # Get the search results page
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    # Extract job urls from the search results
    job_urls = [a['href'] for a in soup.find_all('a', {'id': lambda x: x and x.startswith('job_')})]

    return job_urls


def get_job_info(job_url: str) -> tuple:
    # Extract job info from each job url
    driver.get('https://au.indeed.com' + job_url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    job_title = soup.find('h1').text

    job_search = soup.find('div', {"class": lambda x: x and x.startswith('jobsearch')})
    job_search_info = job_search.find(
        'div', {"class": lambda x: x and x.startswith('jobsearch-CompanyInfoWithoutHeaderImage')})

    job_company = job_search_info.find('div', {"class": lambda x: x and x.startswith('css-1cjkto6')}).text

    try:
        job_description_list = job_search.find('div', {'id': 'jobDescriptionText'}).find_all(['p', 'div'])
        job_description = ' '.join([item.text.lstrip() for item in job_description_list])
    except AttributeError:
        job_description = 'N/A'

    return job_title, job_company, job_description


def search_jobs(job_title: str, location='Sydney', page_num=1):
    job_title = job_title.replace(' ', '+')
    for i in range(page_num):
        url = f'https://au.indeed.com/jobs?q={job_title}&l={location}&start={i * 10}&sort=date'
        job_urls = get_job_urls(url)
        cached_job_urls = [job.job_link for job in IndeedJob.query.all()]
        for job_url in job_urls:
            if job_url not in cached_job_urls:
                job_info = get_job_info(job_url)
                job = IndeedJob(job_link=job_url, search_date=datetime.now().strftime("%d/%m/%Y"),
                                title=job_info[0], company=job_info[1], description=job_info[2],
                                location=location)
                db_session.add(job)
                db_session.commit()
                sleep(random() * 2 + 1)


def sum_programming_skills(programming_skills: list) -> dict:
    programming_skills_dict = {}
    for programming_skill in programming_skills:
        programming_skills_dict[programming_skill] = 0
        if programming_skill == 'go' or programming_skill == 'java' or programming_skill == 'sql':
            pattern = r'\b' + escape(programming_skill) + r'\b'
        else:
            pattern = escape(programming_skill)
        for job in IndeedJob.query.all():
            if search(pattern, job.description, IGNORECASE):
                programming_skills_dict[programming_skill] += 1

    programming_skills_dict = dict(sorted(programming_skills_dict.items(), key=lambda item: item[1], reverse=True))

    return programming_skills_dict


programming_languages = ['python', 'java', 'c++', 'c#', 'javascript', 'typescript', 'php', 'sql', 'ruby',
                         'swift', 'go', 'kotlin', 'scala']
frameworks = ['django', 'flask', 'spring', 'react', 'angular', 'vue', 'node', 'express', 'jquery', '.net',
              'asp.net']
databases = ['mysql', 'postgresql', 'mongodb', 'redis', 'rdbms', 'oracle', 'sql server', 'sqlite']


def main():
    search_jobs('software engineer', 'Sydney', 2)
    programming_languages_dict = sum_programming_skills(programming_languages)
    frameworks_dict = sum_programming_skills(frameworks)
    databases_dict = sum_programming_skills(databases)
    print("Total number of jobs scraped: ", len(IndeedJob.query.all()))
    print('Programming Languages')
    print(programming_languages_dict)
    print('Frameworks')
    print(frameworks_dict)
    print('Databases')
    print(databases_dict)


if __name__ == '__main__':
    main()
