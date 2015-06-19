"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
import urllib
import urllib2
import sys
import time
import json

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, Boolean
from xblock.fragment import Fragment


class LoginXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    # TO-DO: delete count, and define your own fields.
    create_result = Integer(default="", scope=Scope.user_state,
                            help="the response code of creating account", )
    autoLogin_result = Integer(default="", scope=Scope.user_state,
                               help="the response code of autologin", )
    mailExist_result = Integer(default="", scope=Scope.user_state,
                               help="the response code of mail exist", )
    autoLogin_url = String(default="", scope=Scope.user_state,
                           help="the url for going ProctorU", )

    authorization = String(help="Authorization Token", default="",
                           scope=Scope.content)

    autoLogChecked = Boolean(default=False, scope=Scope.user_state, )
    createStudentChecked = Boolean(default=False, scope=Scope.user_state, )

    time_send = String(default="", scope=Scope.user_state, help="the time of sending", )
    student_id = String(default="", scope=Scope.user_state, help="the student's id, usually is E-mail", )
    last_name = String(default="", scope=Scope.user_state, help="student's last name", )
    first_name = String(default="", scope=Scope.user_state, help="student's first name", )
    adress1 = String(default="", scope=Scope.user_state, help="student's address", )
    adress2 = String(default="", scope=Scope.user_state, help="student's supplement address", )
    city = String(default="", scope=Scope.user_state, help="student's city", )
    state = String(default="", scope=Scope.user_state, help="student's state", )
    country = String(default="", scope=Scope.user_state, help="student's country", )
    zipcode = String(default="", scope=Scope.user_state, help="student's zipcode", )
    phone1 = String(default="", scope=Scope.user_state, help="student's phone number", )
    email = String(default="", scope=Scope.user_state, help="student's e-mail", )
    time_zone_id = String(default="Central Standard Time", scope=Scope.user_state, help="student's time zone", )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the LoginXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/login.html")
        if self.runtime.get_real_user is not None:
            try:
                self.student_id = self.runtime.get_real_user(self.runtime.anonymous_student_id).email
                self.first_name = self.runtime.get_real_user(self.runtime.anonymous_student_id).username
                self.last_name = self.runtime.get_real_user(self.runtime.anonymous_student_id).username
                frag = Fragment(unicode(html).format(self=self, student_id=self.student_id,
                                                     first_name=self.first_name,
                                                     last_name=self.last_name))
            except Exception:  # pylint: disable=broad-except
                msg = 'Some Errors Occurred for getting information from FUN'
        else:
            frag = Fragment(unicode(html).format(self=self, student_id="",
                                                 first_name="",
                                                 last_name=""))
        frag.add_css(self.resource_string("static/css/login.css"))
        frag.add_javascript(self.resource_string("static/js/src/login.js"))
        frag.initialize_js('LoginXBlock')
        return frag


    def studio_view(self, context):
        """
        Create a fragment used to display the edit view in the Studio.
        """
        html_str = pkg_resources.resource_string(__name__, "static/html/login_edit.html")
        if self.authorization != "":
            frag = Fragment(unicode(html_str).format(self=self, authorization=self.authorization))
        else:
            frag = Fragment(unicode(html_str).format(self=self, authorization=""))

        js_str = pkg_resources.resource_string(__name__, "static/js/src/login_edit.js")
        frag.add_javascript(unicode(js_str))
        frag.initialize_js('LoginEditBlock')

        return frag

        # TO-DO: change this handler to perform your own actions.  You may need more
        # than one handler, or you may not need any handlers at all.

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
        Called when submitting the form in Studio.
        """
        self.authorization = data.get('authorization')

        return {'result': 'success'}

    @XBlock.json_handler
    def autoLogIn(self, data, suffix=''):
        # based url and required header
        self.student_id = data.get('student_id')
        self.last_name = data.get('lastname')
        self.first_name = data.get('firstname')
        self.adress1 = ''
        self.adress2 = ''
        self.city = ''
        self.state = ''
        self.country = ''
        self.zipcode = ''
        self.phone1 = ''
        self.autoLogChecked = data.get('autoLogin')
        self.createStudentChecked = data.get('createStudent')

        if (self.student_id == '' or
                    self.last_name == '' or
                    self.first_name == ''):
            return {'create_result': 'Please fill the form',
                    'autoLogin_result': '',
                    'autoLogin_url': ''}

        if (self.autoLogChecked and self.createStudentChecked) \
                or ((not self.autoLogChecked) and (not self.createStudentChecked)):
            return {'create_result': 'Please choose one option',
                    'autoLogin_result': '',
                    'autoLogin_url': ''}
        # check the student existed
        # based url and required header
        else:
            url = "https://apitest.proctoru.com/getEmailExist"
            headersSending = {"Content-type": "application/x-www-form-urlencoded",
                              "Authorization-Token": self.authorization, }
            gmt_time = time.gmtime()
            formatGmtTime = time.strftime("%Y-%m-%dT%H:%M:%SZ", gmt_time)
            # user login information
            dataSending = urllib.urlencode(
                {
                    "time_sent": formatGmtTime,
                    "email": self.student_id
                })

            # create request object
            request = urllib2.Request(url, dataSending, headersSending)
            # do request
            try:
                result = urllib2.urlopen(request)
            except urllib2.URLError as e:
                if hasattr(e, 'code'):
                    print ("Error code:", e.code)
                elif hasattr(e, 'reason'):
                    print ("Reason:", e.reason)
            finally:
                if result:
                    the_page = result.read()
                    receive_header = result.info()
                    # avoid the messy code
                    the_page = the_page.decode('utf-8', 'replace').encode(sys.getfilesystemencoding())
                    mailExist = json.loads(the_page)
                    self.mailExist_result = mailExist['data']
                    result.close()

                    if self.mailExist_result != None and self.createStudentChecked:
                        return {'create_result':
                                    'Sorry, you have already had the account in ProctorU with '
                                    + self.student_id + ' from school '
                                    + self.mailExist_result['schoolname'],
                                'autoLogin_result': mailExist,
                                'autoLogin_url': ''}

                    elif self.mailExist_result == None and self.autoLogChecked:
                        return {'create_result': mailExist,
                                'autoLogin_result':
                                    'Sorry, you don\'t have an account with ProctorU',
                                'autoLogin_url': ''}

                    # create the account
                    elif self.mailExist_result == None and self.createStudentChecked:
                        # create the account
                        gmt_time = time.gmtime()
                        formatGmtTime = time.strftime("%Y-%m-%dT%H:%M:%SZ", gmt_time)
                        print (formatGmtTime)

                        url = "https://apitest.proctoru.com/editStudent"
                        headersSending = {"Content-type": "application/x-www-form-urlencoded",
                                          "Authorization-Token": self.authorization, }

                        # user initial login information
                        dataSending = urllib.urlencode(
                            {
                                "time_sent": formatGmtTime,
                                "student_id": self.student_id,
                                "last_name": self.last_name,
                                "first_name": self.first_name,
                                "address1": self.adress1,
                                "address2": self.adress2,
                                "city": self.city,
                                "state": self.state,
                                "country": self.country,
                                "zipcode": self.zipcode,
                                "phone1": self.phone1,
                                "email": self.student_id,
                                "time_zone_id": "Central Standard Time"
                            })

                        # create request object
                        request = urllib2.Request(url, dataSending, headersSending)
                        # do request
                        try:
                            result = urllib2.urlopen(request)
                        except urllib2.URLError as e:
                            if hasattr(e, 'code'):
                                print ("Error code:", e.code)
                            elif hasattr(e, 'reason'):
                                print ("Reason:", e.reason)
                        finally:
                            if result:
                                the_page = result.read()
                                receive_header = result.info()
                                # avoid the messy code
                                the_page = the_page.decode('utf-8', 'replace').encode(sys.getfilesystemencoding())
                                createResult = json.loads(the_page)
                                self.create_result = createResult['response_code']
                                result.close()
                                if self.create_result == 1:
                                    # auto-login
                                    # based url and required header
                                    gmt_time = time.gmtime()
                                    formatGmtTime = time.strftime("%Y-%m-%dT%H:%M:%SZ", gmt_time)
                                    url = "https://apitest.proctoru.com/autoLogin"
                                    headersSending = {"Content-type": "application/x-www-form-urlencoded",
                                                      "Authorization-Token": self.authorization, }
                                    # user login information
                                    dataSending = urllib.urlencode(
                                        {
                                            "time_sent": formatGmtTime,
                                            "student_id": self.student_id,
                                            "last_name": self.last_name,
                                            "first_name": self.first_name,
                                            "email": self.student_id
                                        })

                                    # create request object
                                    request = urllib2.Request(url, dataSending, headersSending)
                                    # do request
                                    try:
                                        result = urllib2.urlopen(request)
                                    except urllib2.URLError as e:
                                        if hasattr(e, 'code'):
                                            print ("Error code:", e.code)
                                        elif hasattr(e, 'reason'):
                                            print ("Reason:", e.reason)
                                    finally:
                                        if result:
                                            the_page = result.read()
                                            receive_header = result.info()
                                            # avoid the messy code
                                            the_page = the_page.decode('utf-8', 'replace').encode(
                                                sys.getfilesystemencoding())
                                            autoLoginResult = json.loads(the_page)
                                            self.autoLogin_result = autoLoginResult['response_code']
                                            self.autoLogin_url = autoLoginResult['data']['url']
                                            # print ("create account successful")
                                            result.close()
                                            if self.autoLogin_result == 1:
                                                return {'create_result':
                                                            'Success to create the account and Success to log in ProctorU'
                                                            + ' You can visit ProctorU by clicking:',
                                                        'autoLogin_result': '',
                                                        'autoLogin_url': self.autoLogin_url}
                                            else:
                                                return {'create_result': 'Success to create the account',
                                                        'autoLogin_result': autoLoginResult['message'],
                                                        'autoLogin_url': '', }
                                else:
                                    return {'create_result': createResult['message'],
                                            'autoLogin_result': '',
                                            'autoLogin_url': ''}
                                    # print ("create account successful")
                    elif self.mailExist_result != None and self.autoLogChecked:
                        gmt_time = time.gmtime()
                        formatGmtTime = time.strftime("%Y-%m-%dT%H:%M:%SZ", gmt_time)
                        url = "https://apitest.proctoru.com/autoLogin"
                        headersSending = {"Content-type": "application/x-www-form-urlencoded",
                                          "Authorization-Token": self.authorization, }
                        # user login information
                        dataSending = urllib.urlencode(
                            {
                                "time_sent": formatGmtTime,
                                "student_id": self.student_id,
                                "last_name": self.last_name,
                                "first_name": self.first_name,
                                "email": self.student_id
                            })

                        # create request object
                        request = urllib2.Request(url, dataSending, headersSending)
                        # do request
                        try:
                            result = urllib2.urlopen(request)
                        except urllib2.URLError as e:
                            if hasattr(e, 'code'):
                                print ("Error code:", e.code)
                            elif hasattr(e, 'reason'):
                                print ("Reason:", e.reason)
                        finally:
                            if result:
                                the_page = result.read()
                                receive_header = result.info()
                                # avoid the messy code
                                the_page = the_page.decode('utf-8', 'replace').encode(
                                    sys.getfilesystemencoding())
                                autoLoginResult = json.loads(the_page)
                                self.autoLogin_result = autoLoginResult['response_code']
                                self.autoLogin_url = autoLoginResult['data']['url']
                                # print ("create account successful")
                                result.close()
                                if self.autoLogin_result == 1:
                                    return {
                                        'create_result': 'Success to log in ProctorU, you can visit the ProctorU by clicking the link below',
                                        'autoLogin_result': '',
                                        'autoLogin_url': self.autoLogin_url}
                                else:
                                    return {'autoLogin_result': autoLoginResult['message'],
                                            'create_result': '',
                                            'autoLogin_url': ''}


# TO-DO: change this to create the scenarios you'd like to see in the
# workbench while developing your XBlock.
@staticmethod
def workbench_scenarios():
    """A canned scenario for display in the workbench."""
    return [
        ("LoginXBlock",
         """<vertical_demo>
            <login/>
            </vertical_demo>
         """),
    ]
