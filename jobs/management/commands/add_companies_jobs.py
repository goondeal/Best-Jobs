import json
import logging
import random
from django.core.management.base import BaseCommand
from accounts.models import *
from jobs.models import *


class Command(BaseCommand):
    help = 'Adds jobs data to the db'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='path to <file>.json')

    def handle(self, *args, **kwargs):
        fpath = kwargs['file_path']
        data = None
        with open(file=fpath, mode='r', encoding='utf-8') as f:
            data = json.loads(f.read())

        logger = logging.getLogger('django')                    
        
        industries = [
            i for i in Industry.objects.all()
            # Industry.objects.create(name=industry_data['name'])
            # for industry_data in data['industries']
        ]
        logger.info(f'{len(industries)} industries were created')
        skills = [
            s for s in Skill.objects.all()
            # Skill.objects.create(name=skill_data['name'])
            # for skill_data in data['skills']
        ]
        logger.info(f'{len(skills)} skills were created')

        from pathlib import Path
        p = Path(__file__).resolve().parent.parent.parent.parent / 'media/company-logo'
        companies_names = [f.name for f in p.iterdir() if f.is_file()]
        logger.info(f'Got {len(companies_names)} comanies names')
        cities = City.objects.all()
        cities = City.objects.filter(state__country__code='eg')
        for company_data in data['companies']:
            name, ext = random.choice(companies_names).split('.')
            company = Company.objects.create(
                email=f'user{random.randint(0, 99)}@{name.lower().replace(" ", "")}.com',
            )
            company.set_password('123456')
            info = CompanyInfo.objects.create(
                company=company,
                name=name,
                description=company_data['description'],
                foundation_year=random.randint(1900, 2020),
                logo=f'{name}.{ext}',
                city=random.choice(cities),
                size=random.randint(2, 2000),
                industry=random.choice(industries)
            )
            logger.info(f'Company {info.name} were created.')
            questions = random.sample(data['questions'], k=random.choice([3, 4]))
            for q in questions:
                question = JobQuestion.objects.create(
                    company=company,
                    question=q['question'],
                    optional=random.choice([False, True, False])
                )
                if q.get('answers'):
                    for a in q.get('answers'):
                        JobQuestionAnswer.objects.create(
                            question=question,
                            value=a
                        )

            # logger.info(f'{len(questions)} questions were added')
            jobs_count = random.randint(0, 5)
            for i in range(jobs_count):
                roles = list(filter(lambda x: x['name'] == info.industry.name, data['industries']))[0]['roles']
                role = random.choice(roles)
                _cities = [info.city, random.choice(City.objects.filter(state__country=info.city.state.country))]
                min_salary=random.choice(range(3, 51))*1000
                job = Job.objects.create(
                    company=company,
                    title=role['title'],
                    type=random.choice(Job._JOB_TYPES)[0],
                    # category=,
                    industry=random.choice(industries),
                    city=random.choice(_cities),
                    career_level=random.choice(Job._CAREER_LEVELS)[0],
                    min_years_of_experience=role['years'][0],
                    max_years_of_experience=role['years'][-1],
                    salary_min=min_salary,
                    salary_max=min_salary+10_000,
                    show_salary=random.choice([True, False]),
                    salary_additional_details=random.choice(['401 package.\nHealth insurance.\nand more.', '401 package.', '']),
                    num_of_vacancies=random.randint(1, 5),
                    description='Provide an efficient Customer Chanel for Customer feedback through assisting customers in a friendly and professional manner with all calls coming into IKEA Hotline, whether inquiries, suggestions or Complaints. Log all feedback onto CRM system and send necessary feedback to relevant Departments.',
                    requirements="""Bachelor’s degree in computer science or a similar field.
                                Proven work experience as a WordPress developer.
                                Knowledge of front-end technologies including CSS3, JavaScript, HTML5, and jQuery.
                                Knowledge of code versioning tools including Git, Mercurial, and SVN.
                                Experience working with debugging tools such as Chrome Inspector and Firebug.
                                Good understanding of website architecture and aesthetics.
                                Ability to manage projects.
                                Good communication skills.""",
                    what_we_offer=random.choice(['', """Great Environment.\n401 Package.\nWork-life balance."""]),
                    keep_company_confidential=random.choice([True, False])
                )
                c_skills=random.sample(skills, k=random.randint(3, 15))
                for s in c_skills:
                    job.skills.add(s)
                q_list = list(company.questions.all())
                qs = random.sample(q_list, k=random.randint(1, len(q_list)-1))
                for q in qs:
                    job.questions.add(q)
                job.save()      

            logger.info(f'{jobs_count} jobs were added')
