from sqlalchemy import Column, String
from database import Base


class IndeedJob(Base):
    __tablename__ = 'indeed_jobs'
    job_link = Column(String, primary_key=True)
    search_date = Column(String)
    location = Column(String)
    title = Column(String)
    company = Column(String)
    description = Column(String)

    def __repr__(self):
        return f'<IndeedJob(job_link={self.job_link}, search_date={self.search_date}, location={self.location}, ' \
               f'title={self.title}, company={self.company}, description={self.description})>'
