"""Login xblock speeding up proctoru registration process using EDX information"""
"""Copyright Yuhao Zhao, Yuqing Wei, Olivier Paul, Telecom SudParis"""

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

    authorization = String(help="Authorization Token", default="",
                           scope=Scope.content)

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the LoginXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/login.html")
        if self.runtime.get_real_user is not None:
            try:
                student_id = self.runtime.get_real_user(self.runtime.anonymous_student_id).email
                first_name = self.runtime.get_real_user(self.runtime.anonymous_student_id).username
                last_name = self.runtime.get_real_user(self.runtime.anonymous_student_id).username
                frag = Fragment(unicode(html).format(self=self, student_id=student_id,
                                                     first_name=first_name,
                                                     last_name=last_name))
            except Exception:  # pylint: disable=broad-except
                msg = 'Some errors occurred while getting information from FUN'
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
        student_id = data.get('student_id')
        last_name = data.get('lastname')
        first_name = data.get('firstname')
        adress1 = ''
        adress2 = ''
        city = ''
        state = ''
        country = ''
        zipcode = ''
        phone1 = ''
        autoLogChecked = data.get('autoLogin')
        createStudentChecked = not(autoLogChecked)

        if (student_id == '' or
                    last_name == '' or
                    first_name == ''):
            return {'create_result': 'Please fill the form before submitting',
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
                    "email": student_id
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
                    mailExist_result = mailExist['data']
                    result.close()

                    if mailExist_result != None and createStudentChecked:
                        return {'create_result':
                                    'Sorry, you already have an account with ProctorU using '
                                    + student_id + ' from school '
                                    + mailExist_result['schoolname'],
                                'autoLogin_result': '',
                                'autoLogin_url': ''}

                    elif mailExist_result == None and autoLogChecked:
                        return {'create_result': '',
                                'autoLogin_result':
                                    'Sorry, you don\'t have an account with ProctorU',
                                'autoLogin_url': ''}

                    # create the account
                    elif mailExist_result == None and createStudentChecked:

                        gmt_time = time.gmtime()
                        formatGmtTime = time.strftime("%Y-%m-%dT%H:%M:%SZ", gmt_time)
                        print (formatGmtTime)

                        url = "https://apitest.proctoru.com/editStudent"

                        # user initial login information
                        dataSending = urllib.urlencode(
                            {
                                "time_sent": formatGmtTime,
                                "student_id": student_id,
                                "last_name": last_name,
                                "first_name": first_name,
                                "address1": adress1,
                                "address2": adress2,
                                "city": city,
                                "state": state,
                                "country": country,
                                "zipcode": zipcode,
                                "phone1": phone1,
                                "email": student_id,
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
                                create_result = createResult['response_code']
                                result.close()
                                if create_result != 1:
                                    return {'create_result': createResult['message'],
                                            'autoLogin_result': '',
                                            'autoLogin_url': ''}

		    elif (mailExist_result != None and autoLogChecked):
				create_result = 0

                    if (mailExist_result != None and autoLogChecked) or \
		       (mailExist_result == None and createStudentChecked and create_result == 1):

                        gmt_time = time.gmtime()
                        formatGmtTime = time.strftime("%Y-%m-%dT%H:%M:%SZ", gmt_time)
                        url = "https://apitest.proctoru.com/autoLogin"

                        # user login information
                        dataSending = urllib.urlencode(
                            {
                                "time_sent": formatGmtTime,
                                "student_id": student_id,
                                "last_name": last_name,
                                "first_name": first_name,
                                "email": student_id
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
                                autoLogin_result = autoLoginResult['response_code']
                                autoLogin_url = autoLoginResult['data']['url']
                                # print ("create account successful")
                                result.close()

                                if autoLogin_result == 1:
				    if (create_result == 1):
                                      return {
                                            'create_result': 'Account was successfully created',
                                            'autoLogin_result': 'To visit ProctorU please click the link below',
                                            'autoLogin_url': autoLogin_url}
				    else:
                                        return {
                                            'create_result': '',
                                            'autoLogin_result': 'To visit ProctorU please click the link below',
                                            'autoLogin_url': autoLogin_url}
                                else:
				    if (create_result == 1):
                                        return {'create_result': 'Account was successfully created, however autologin was unsuccessful',
                                                'autoLogin_result': autoLoginResult['message'],
                                                'autoLogin_url': '', }
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
