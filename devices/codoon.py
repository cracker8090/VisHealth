#!/usr/bin/env python
# _*_ coding: utf-8 _*_
__author__ = 'iascchen@gmail.com'

import requests
from requests.auth import HTTPBasicAuth
import json
import codoonurl
import logging
from lxml import etree

class DeviceCodoon:
    auth_info = None
    codoonHeaders = None
    codoonCookies = None

    httpClientKey = "dc039f07e003da02938a5bc4605b5acc"
    httpClientSecret = "5eabee082afac17ff97e0f33b6aaf66d"

    # devUserAgent = "Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9308 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"
    devUserAgent = "Dalvik/1.6.0 (Linux; U; Android 4.2.2; sdk Build/JB_MR1.1)"

    def __init__(self):
        logging.basicConfig(filename = '../logs/log.txt', level = logging.DEBUG)
        self.codoonHeaders = {"User-Agent" : self.devUserAgent }

    def logCommand(self , command , ret , headers ):
        # tmp = { "cmd" : command , "ret" : json.dumps(retJson) , "hed" : headers }
        # logging.debug( tmp )

        logging.debug( ret , headers )

    def saveJsonData(self , filename, data):
        f = open("../data/codoon/%s" % filename, "w")
        f.write(json.dumps( data , indent = 4 ))
        f.close()

    def saveXmlData(self , filename, data):
        f = open("../data/codoon/%s" % filename, "w")
        doc = etree.fromstring(data)
        f.write( etree.tostring( doc, pretty_print=True ) )
        f.close()

    def excuteGetRequstWithCookies(self , command , params = None, cookies = None):
        print "Get : " , command
        response = requests.get(command , params = params ,  headers = self.codoonHeaders , cookies = cookies)
        content = response.json
        self.logCommand( command , content , response.headers )

        if( 200 != response.status_code):
            print "StatusCode : " , response.status_code

        return content

    def excuteGetRequst(self , command , params = None):
        print "Get : " , command
        response = requests.get(command , params = params ,  headers = self.codoonHeaders)
        content = response.json
        self.logCommand( command , content , response.headers )

        if( 200 != response.status_code):
            print "StatusCode : " , response.status_code

        return content

    def excutePostRequst(self , command , data = None):
        print "Post : " , command
        response = requests.post(command , data = json.dumps(data),  headers = self.codoonHeaders )
        content = response.json
        self.logCommand( command , content , response.headers )

        if( 200 != response.status_code):
            print "StatusCode : " , response.status_code

        return content

    def get_users_login(self , email , password ):
        command = codoonurl.getTokenUrl()
        print "Post : " , command
        request_data = { "grant_type" : "password" ,
                         "client_id" : self.httpClientKey ,
                         "scope" : "user" ,
                         "email": email, "password" : password  }

        auth = HTTPBasicAuth(self.httpClientKey, self.httpClientSecret)
        response = requests.post( command , data = request_data , headers = self.codoonHeaders , auth = auth )
        content = response.json
        self.logCommand( command , content , response.headers )

        if( 200 != response.status_code):
            print response.status_code
            return

        self.auth_info = content
        self.codoonHeaders.update( { "Authorization" : "Bearer  %s" % content["access_token"] ,
                               "Charset" : "UTF-8"} )
        return content

    def verify_credentials(self):
        command = codoonurl.getVerifyCredentialsUrl()
        return self.excuteGetRequst(command , params = None)

    def version_run_xml(self):
        command = codoonurl.getVersionRunUrl()
        response = requests.get(command)
        content = response.content
        self.logCommand( command , content , response.headers )

        if( 200 != response.status_code):
            print "StatusCode : " , response.status_code
        return content

    # This method used to SSO with sso.codoon.com, so if you want to access www.codoon.com, you can use it.
    def get_misc_mobile( self ):
        command = codoonurl.getMiscMobileUrl()
        request_data = { "access_token" : self.auth_info["access_token"] }

        response = requests.get(command , params = request_data ,  headers = self.codoonHeaders)
        self.logCommand( command , "" , response.headers )

        if( 200 != response.status_code):
            print "StatusCode : " , response.status_code

        self.codoonCookies = response.cookies

    # This method will access www.codoon.com , so it must called after get_misc_mobile
    def get_user_statistic(self):
        command = codoonurl.getUserStatisticUrl()
        return self.excuteGetRequstWithCookies(command , params = None ,
            cookies = self.codoonCookies  )

    def get_user_medal(self):
        command = codoonurl.getUserMedalUrl()
        return self.excuteGetRequst(command , params = None )

    def get_user_growing_point_related(self):
        command = codoonurl.getUserGrowingPointUrl()
        return self.excuteGetRequst(command , params = None )

    def gps_highest_record(self):
        command = codoonurl.getGpsHighestRecordUrl()
        return self.excuteGetRequst(command , params = None )

    def get_mobile_portraits(self):
        command = codoonurl.getMobilePortraitsUrl()
        return self.excuteGetRequst(command , params = None )

    def gps_statistic(self , fromDate , toDate):
        command = codoonurl.getGpsStatisticUrl()
        request_data = {"from_date" : fromDate , "to_date" : toDate}
        return self.excutePostRequst(command , data = request_data)

    def get_air_quality(self, cityName = None):
        command = codoonurl.getAirQualityUrl()
        request_data = {"city_name" : cityName }
        return self.excutePostRequst(command , data = request_data)

    def get_route_log(self , productId , count = 100 , excluded = "" , page = 1 , isPart = 1 ):
        command = codoonurl.getRouteLogUrl()
        request_data = {"product_id" : productId , "count" : count , "excluded" : excluded ,
                        "page" : page , "is_part" : isPart }
        return self.excutePostRequst(command , data = request_data)

    def get_single_log(self , routeId):
        command = codoonurl.getSingleLogUrl()
        request_data = {"route_id" : routeId }
        return self.excutePostRequst(command , data = request_data)

    def sports_program_manifest_for_codoon(self, programIds):
        command = codoonurl.getSportsProgramManifestUrl()
        request_data = {"ids" : programIds }
        return self.excutePostRequst(command , data = request_data)

    def sports_program_detail(self , programId):
        command = codoonurl.getSportsProgramDetailUrl()
        request_data = {"id" : programId }
        return self.excutePostRequst(command , data = request_data)

    def get_tracker_summary(self, endDate, daysBack ):
        command = codoonurl.getTrackerSummaryUrl()
        request_data = {"date_end" : endDate, "days_back" : daysBack }
        return self.excutePostRequst(command , data = request_data)

    def get_tracker_data(self , datestr):
        command = codoonurl.getTrackerDataUrl()
        request_data = {"the_day" : datestr }
        return self.excutePostRequst(command , data = request_data )

    def get_tracker_goal(self):
        command = codoonurl.getTrackerGoalUrl()
        return self.excuteGetRequst(command , params = None)

    def get_sleep_data(self, datestr):
        command = codoonurl.getSleepDataUrl()
        request_data = {"the_day" : datestr }
        return self.excutePostRequst(command , data = request_data)

    # gender : 1 Male, 0 Female. Gender is not 0 or 1, will return all
    # Bug : if hobby is Chinese , will return 500 error, :(
    def people_surrounding(self , point , gender = 2 , hobby = None , page = 1):
        command = codoonurl.getPeopleSurroundingUrl()
        request_data = {"point" : point , "gender" : gender , "hobby" : hobby , "page" : page }
        return self.excutePostRequst(command , data = request_data)

if __name__ == "__main__":
    account = { "email" : "your@email" , "passwd" : "yourpassword" }

    startDate = "2013-06-01"
    endDate =  "2013-06-30"
    checkDate = "2013-06-17"

    point = "36.5,112.32"
    imei = "000000000000000"

    device = DeviceCodoon ()

    # login
    ret = device.get_users_login(account["email"], account["passwd"])
    device.saveJsonData( filename = "/users_token.json" , data = ret)

    ret = device.verify_credentials()
    device.saveJsonData( filename = "/verify_credentials.json" , data = ret)

    ret = device.version_run_xml()
    device.saveXmlData( filename = "/version_run.xml" , data = ret)

    device.get_misc_mobile( )
    ret = device.get_user_statistic(  )
    device.saveJsonData( filename = "/user_statistic.json" , data = ret)

    ret = device.get_user_medal( )
    device.saveJsonData( filename = "/user_medal.json" , data = ret)

    ret = device.get_user_growing_point_related( )
    device.saveJsonData( filename = "/user_growing_point_related.json" , data = ret)

    ret = device.get_tracker_goal(  )
    device.saveJsonData( filename = "/tracker_goal.json" , data = ret)

    ret = device.gps_highest_record( )
    device.saveJsonData( filename = "/gps_highest_record.json" , data = ret)

    ret = device.get_mobile_portraits( )
    device.saveJsonData( filename = "/mobile_portraits.json" , data = ret)

    ret = device.get_route_log( productId = imei )
    device.saveJsonData( filename = "/route_log.json" , data = ret)
    routeId = ret["data"][0]["route_id"]
    ret = device.get_single_log( routeId = routeId )
    device.saveJsonData( filename = "/single_log.json" , data = ret)

    ret = device.gps_statistic( startDate , endDate )
    device.saveJsonData( filename = "/gps_statistic.json" , data = ret)

    ret = device.sports_program_manifest_for_codoon( programIds = "" )
    device.saveJsonData( filename = "/sports_program_manifest_for_codoon.json" , data = ret)
    programId = ret["data"][0]["id"]
    ret = device.sports_program_detail( programId = programId )
    device.saveJsonData( filename = "/sports_program_detail.json" , data = ret)

    ret = device.gps_statistic( startDate , endDate )
    device.saveJsonData( filename = "/gps_statistic.json" , data = ret)

    ret = device.get_sleep_data( checkDate )
    device.saveJsonData( filename = "/sleep_data.json" , data = ret)

    ret = device.get_tracker_data( checkDate )
    device.saveJsonData( filename = "/tracker_data.json" , data = ret)

    ret = device.get_tracker_summary( endDate = endDate, daysBack = 30)
    device.saveJsonData( filename = "/tracker_summary.json" , data = ret)

    ret = device.get_air_quality( cityName = "北京" )
    device.saveJsonData( filename = "/air_quality.json" , data = ret)

    # Bug : if hobby is Chinese , will return 500 error, :(
    # ret = device.people_surrounding( point = point , gender = "1" , hobby = "跑步" , page = 1) will return 500
    ret = device.people_surrounding( point = point , gender = 2 , hobby = "" , page = 1)
    device.saveJsonData( filename = "/people_surrounding.json" , data = ret)