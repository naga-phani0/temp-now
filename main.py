"""Importing all the required libraries."""
from concurrent.futures import ThreadPoolExecutor
import os
import bs4
from threading import Lock
import requests
from unidecode import unidecode
import logging
from job_meta_upload_script_v2 import JobsMeta
# from configparser import ConfigParser
from datetime import date
import time

# config_rdr=ConfigParser()
# config_rdr.read('root/job_scheduling/db_config.ini')
DEV_MAIL = 'aliashhar3@gmail.com'  # config_rdr.get('dev_mails','devmail') #('dev_mails','rutwik')
POST_AUTHOR = 17  # config_rdr.get('post_author_no','Pratik')


class TCS:
    '''Creating TCS class containing all the methods.'''

    def __init__(self, company):
        logging.basicConfig(filename=f'{company}_logs_{date.today().strftime("%d_%m_%Y")}.log',
                            format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                            level=logging.INFO)
        self.company = company
        self.logger_ob = logging.getLogger()
        self.threadlock = Lock()
        self.objct = JobsMeta(self.company, self.logger_ob)
        self.session = requests.Session()
        self.cookies = {
            'JSESSIONID': '"RS2NfZ9O6jbLiyDinEtf1ym8pEzlhUFxMSp3LZv5.slave1:server-four"',
            'ROUTEID': '.12',
            'TS013b808c': '0199acb0de4df80dfc2fbb9300dd7f95d0a46f91be7a618febecd863d1ec75593ccfb33d65c128360877ceb2247008448ae1b47b64167af5ef2c472498833d78cf37d7c26b0da707282ed22f11d6c7f90318abbfbc',
            's_ecid': 'MCMID%7C84493998703042525302073980631843266982',
            'AMCV_35DC284C55D1CEAD7F000101%40AdobeOrg': '1176715910%7CMCMID%7C84493998703042525302073980631843266982%7CMCAAMLH-1668689049%7C12%7CMCAAMB-1668689049%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1668091450s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.4.0',
            'TS01ab71c3': '0199acb0de67316280de48134afe0ef648e28a82f87a618febecd863d1ec75593ccfb33d657684f81a0c6395e8341759b23c735612',
        }

        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://ibegin.tcs.com',
            'Pragma': 'no-cache',
            'Referer': 'https://ibegin.tcs.com/iBegin/jobs/search',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        self.params = {
            'at': '1673403339172',
        }

        self.json_data = {
            'jobCity': None,
            'jobSkill': None,
            'pageNumber': '1',
            'userText': '',
            'jobTitleOrder': None,
            'jobCityOrder': None,
            'jobFunctionOrder': None,
            'jobExperienceOrder': None,
            'applyByOrder': None,
            'regular': True,
            'walkin': True,
        }
        url = "https://ibegin.tcs.com/iBegin/jobs/search"
        try:

            response = self.session.post(
                'https://ibegin.tcs.com/iBegin/api/v1/jobs/searchJ',
                params=self.params,
                cookies=self.cookies,
                headers=self.headers,
                json=self.json_data,
            )
            jdata = response.json()
        except Exception as resp_err:
            self.logger_ob.critical(f'Error while requesting and getting json data from {url} : {resp_err}')
            self.objct.exit_fun()
        self.count = int(jdata['data']['totalJobs'])

    def link_page(self, i):
        try:
            self.json_data['pageNumber'] = str(i)
            page_url = str(i)
            response = self.session.post(
                'https://ibegin.tcs.com/iBegin/api/v1/jobs/searchJ',
                params=self.params,
                cookies=self.cookies,
                headers=self.headers,
                json=self.json_data,
            )
            jdata = response.json()['data']['jobs']
            for jobs in jdata:
                j_url = 'https://ibegin.tcs.com/iBegin/jobs/' + jobs['id']
                self.threadlock.acquire()
                self.objct.link_insertion(page_url, j_url)
                self.threadlock.release()
                print(j_url + " Inserted into scat table")
        except Exception as ins_err:
            self.logger_ob.error(f'Error while getting and inserting job url {j_url} from page {page_url} : {ins_err}')

    def new_scraper(self, pj_url):
        try:
            p_url = pj_url[0]
            j_url = pj_url[1]
            jID = str(j_url).split('/jobs/')[1][:-1]
            if j_url[-1] != 'W':
                requrl = 'https://ibegin.tcs.com/iBegin/api/v1/job/desc'
                job_type = "Regular"
                params = {
                    'at': '1673407886129',
                }
            else:
                requrl = 'https://ibegin.tcs.com/iBegin/api/v1/job/desc/walkin'
                job_type = "WALK - IN - DRIVE"
                params = {
                    'at': '1673413501514',
                }
            json_data = {
                'jobId': jID,
            }
            try:
                response = self.session.post(
                    requrl,
                    params=params,
                    cookies=self.cookies,
                    headers=self.headers,
                    json=json_data,
                )
                j_data = response.json()['data']
            except Exception as scr_err:
                self.logger_ob.error(f'Error while scraping data from {j_url} : {scr_err}')
            else:
                print('Started Scraping')
                ex_stat = 'Not Existing'
                url = 'https://ibegin.tcs.com/iBegin/jobs/' + str(j_data['jobId'])
                if url == j_url[:-1]:
                    try:
                        job_desc = str(bs4.BeautifulSoup(j_data['description'], "lxml").text) \
                                   + "\nWalk in interview details:\nVenue: " + str(j_data['walkInVenue']) \
                                   + "\nTime:" + str(j_data['walkInRegTime'])
                    except:
                        job_desc = ""
                    try:
                        job_qual = j_data['qualifications']
                    except:
                        job_qual = ""
                    try:
                        job_loc = j_data['location'] + ", " + j_data['country']
                    except:
                        job_loc = ""
                    try:
                        job_exp = j_data['experience']
                    except:
                        job_exp = ""
                    try:
                        job_skills = j_data['skilldetail']
                    except:
                        job_skills = ""
                    try:
                        job_title = j_data['title']
                    except:
                        job_title = ""
                    try:
                        impinfo = "Job Expires By : " + j_data['applyby'] + "\nAdditional info : " + str(
                            j_data['additionalInfo'])
                    except:
                        impinfo = ""
                    try:
                        self.threadlock.acquire()
                    except Exception as th_lock_acq_err:
                        self.logger_ob.error(f'Error while acquiring thread lock : {th_lock_acq_err}')
                    else:
                        self.objct.upload_job_meta_upd(postauth=POST_AUTHOR, postcontent=job_desc, posttitle=job_title,
                                                       companyname='TCS',
                                                       location=job_loc, jobtype=job_type, search_page_no=p_url,
                                                       job_url=j_url,
                                                       qualification=job_qual, skills=job_skills, experience=job_exp,
                                                       imp_info=impinfo, company_website="https://www.tcs.com/",
                                                       company_tagline="We're Building On Belief",
                                                       company_video="Not Available", company_twitter="@TCS",
                                                       job_logo=True,
                                                       localFilePath="./logo/TCS_logo.png")
                        print(f'{j_url} Scraped')
                        self.objct.change_status(j_url)
                        self.threadlock.release()
                        ex_stat = 'Existing'
                if ex_stat == 'Not Existing':
                    self.objct.del_not_existing(j_url)
        except Exception as scr_err:
            self.logger_ob.error(f'Error in scraping for {j_url} : {scr_err}')

    def multi_thread_updated(self):
        '''multithreading.'''
        pager = list(range(1, int((self.count + 20) / 10)))

        '''Add Links to company_job_st_tb table with '''
        try:
            print(f'Total jobs on portal : {self.count}')
            with ThreadPoolExecutor() as link_adder:
                link_adder.map(self.link_page, pager)
        except Exception as st_tb_mul_thd_err:
            self.logger_ob.critical(
                f'Error while inserting links in status table using multithreading : {st_tb_mul_thd_err}')
            print(f'Error while inserting links in status table using multithreading : {st_tb_mul_thd_err}')
            self.objct.exit_fun(DEV_MAIL)
        else:
            try:
                ns_j_links = self.objct.not_scraped_urls()
                # print(ns_j_links)
                print(f'Links remaining to be scraped : {len(ns_j_links)}')
                with ThreadPoolExecutor() as executor:
                    executor.map(self.new_scraper, ns_j_links)
                self.objct.check_different('TCS')
                print(f'Links remaining to be scraped : {len(self.objct.delete_temp_table())}')

            except Exception as job_scp_mt_err:
                self.logger_ob.critical(
                    f'Error while inserting links in trial_job_meta using multithreading : {job_scp_mt_err}')
                self.objct.exit_fun()


if __name__ == '__main__':
    t1 = time.time()
    obj = TCS('TCS')
    obj.objct.create_sc_stat_tb()
    obj.multi_thread_updated()
    print(f'Time taken to complete scraping all {obj.count} is : {time.time() - t1}s')
    if os.stat(f'{obj.company}_logs_{date.today().strftime("%d_%m_%Y")}.log').st_size != 0:
        # obj.objct.mail_log_file()
        print('Log file mailed')
    else:
        print('Log file is empty')
        logging.shutdown()
        os.remove(f'{obj.company}_logs_{date.today().strftime("%d_%m_%Y")}.log')
        if not os.path.exists(f'{obj.company}_logs_{date.today().strftime("%d_%m_%Y")}.log'):
            print('Log File deleted')