import os, json, logging, sys
import urllib2, base64, json

from iCimsModel import IcimsJobPosting

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Load Settings
settings_file = open('settings.json', 'r')
settings = json.loads(settings_file.read())
settings_file.close()

# API Settings
api_url = 'https://api.icims.com/customers/' + settings['icims_customer_number'] + '/search/jobs?searchJson='
api_filter = urllib2.quote('{"filters":[{"name":"job.folder","value":["C14567"],"operator":"="},{"name":"job.jobpost.isposted","value":["Yes"],"operator":"="},{"name":"job.jobpost.type","value":["3"],"operator":"="},{"name":"job.jobpost.status","value":["1"],"operator":"="}],"operator":"&"}')

basic_auth_string = base64.encodestring('%s:%s' % (settings['icims_username'],settings['icims_password'])).replace('\n', '')

request_url = api_url + api_filter

engine = create_engine(settings['db_connection_string'])
DBSession = sessionmaker(bind=engine)
session = DBSession()

'''------- Pull Data From iCims ---------'''

def apiQuery():

    request = urllib2.Request(request_url)
    request.add_header("Authorization", "Basic %s" % basic_auth_string)

    try:
        result = urllib2.urlopen(request)
    except urllib2.HTTPError, err:
        if err.code == 404:
            print "Page not found!"
        elif err.code == 403:
            print "Access denied!"
        else:
            print "Something happened! Error code", err.code
    except urllib2.URLError, err:
        print "Something happened! Error code", err.reason, response.geturl()

    # load JSON jobPostings
    data = json.load(result)
    jobPostings = data['searchResults']

    for jobObject in jobPostings:

        # load specific job
        requestJob = urllib2.Request(jobObject['self'] + "?fields=overview,responsibilities,qualifications,jobtitle,id,joblocation,joblocation")
        requestJob.add_header("Authorization", "Basic %s" % basic_auth_string)
        print requestJob.get_full_url()

        resultJob = urllib2.urlopen(requestJob)
        jobData = json.load(resultJob)

        requestAddress = urllib2.Request(jobData['joblocation']['address'])
        requestAddress.add_header("Authorization", "Basic %s" % basic_auth_string)
        print requestAddress.get_full_url()

        resultAddress = urllib2.urlopen(requestAddress)
        addressData = json.load(resultAddress)

        city = addressData['addresscity'] + ', ' + addressData['addressstate']['value']

        dbAdd(jobData, city)

    dbComplete()

'''#################### Place Data ######################'''


def dbClear():

    session.execute('truncate table icims_JobPostings;')


def dbAdd(jobData, city):

    print "dbAdd"

    newJob = IcimsJobPosting()
    newJob.jobid = jobData['id']
    newJob.jobtitle = jobData['jobtitle']
    newJob.qualifications = jobData['qualifications']
    newJob.overview = jobData['overview']
    newJob.responsibilities = jobData['responsibilities']
    newJob.location = city

    session.add(newJob)


def dbComplete():

    try:
        print "session.commit()"
        dbClear()
        session.commit()
    except:
        print "rollback"
        session.rollback()
        e = sys.exc_info()[0]
        print e

apiQuery()
