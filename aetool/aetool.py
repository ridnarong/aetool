"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import String, Integer, Scope, JSONField
from webob import Response
import urllib.parse
import json
import requests
import time
from datetime import datetime

try:
    from xblock.utils.resources import ResourceLoader
    from xblock.utils.studio_editable import StudioEditableXBlockMixin
except ModuleNotFoundError:  # For backward compatibility with releases older than Quince.
    from xblockutils.resources import ResourceLoader
    from xblockutils.studio_editable import StudioEditableXBlockMixin

@XBlock.wants('settings')
@XBlock.wants('user')
@XBlock.needs("i18n")
class AEToolXBlock(StudioEditableXBlockMixin, XBlock):
    """
    Provide embeded iframe to each of AE Tool available on platform or custom url.
    This plugin provides course / block infomation along with url to locate the usage.
    Also has display option embeded iframe or open iframe in modal. 
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.
    display_name = String(
        display_name="Display name",
        default='AE Tool',
        help="Display name show on block header",
        scope=Scope.settings
    )
    aetool = String(
        display_name="AE Tool",
        values=[
            {"value": 'simulator', "display_name": 'Simulator'},
            {"value": 'chatbot', "display_name": 'Chatbot'},
            {"value": 'bookroll', "display_name": 'BookRoll'},
            {"value": 'video', "display_name": 'Video Player'},
            {"value": 'iframe', "display_name": 'External URL'},
        ],
        default='iframe',
        help="Select AE Tool",
        scope=Scope.settings
    )
    aetool_config = JSONField(
        display_name ="AE Tool Additional Configuration",
        default={},
        values=[
            {
                'display_name': 'simulator',
                'value': None
            },
            {
                'display_name': 'chatbot',
                'value': {
                    'sheet_id': {
                        'type': 'string',
                        'label': 'Google sheet - ID/URL',
                        'help': 'Enter Google sheet URL'
                    },
                    'sheet_name': {
                        'type': 'string',
                        'label': 'Google sheet - Sheet name',
                        'help': 'Enter Google sheet - Sheet name used for this block'
                    },
                    'type': {
                        'type': 'string',
                        'label': 'Type',
                        'help': 'Abdul chatbot type',
                        'choices': [
                            ['', '--- Select Type ---'],
                            ['quiz', 'Quiz'],
                            ['faq', 'FAQ'],
                            ['qa', 'QA']
                        ]
                    },
                    'train': {
                        'type': 'button',
                        'label': 'Train',
                        'help': 'Train Chatbot each time for making change of questions'
                    },
                }
            },
            {
                'display_name': 'bookroll',
                'value': {
                    'pdf_file': {
                        'type': 'file',
                        'label': 'Upload file',
                        'help': 'Upload PDF file',
                        'accept': 'application/pdf',
                        'multiple': False,
                    }
                }
            },
            {
                'display_name': 'iframe',
                'value': {
                    'iframe_url': {
                        'type': 'string',
                        'label': 'IFrame URL',
                        'help': 'URL of external resources'
                    }
                }
            },
            {
                'display_name': 'video',
                'value': {
                    'video_url': {
                        'type': 'string',
                        'label': 'Video URL',
                        'help': 'YouTube Video URL'
                    }
                }
            },
        ]
    )
    iframe_url = String(
        display_name="IFrame URL",
        default='',
        help="IFrame URL display in modal",
        scope=Scope.settings
    )
    btn_text = String(
        display_name="Button text",
        default='Button',
        help="Button text",
        scope=Scope.settings
    )
    width = String(
        display_name="Width",
        default='80%',
        help="Element Width",
        scope=Scope.settings
    )
    height = String(
        display_name="Height",
        default='600',
        help="Element Height",
        scope=Scope.settings
    )
    display = String(
        display_name="Display mode",
        values=[
            {"value": 'inline', "display_name": 'Embedded inline'},
            {"value": 'modal', "display_name": 'Open modal by button'},
            {"value": 'modalWithInline', "display_name": 'Embedded inline with modal'},
            {"value": 'newWindow', "display_name": 'Open new window by button'}
        ],
        default='inline',
        help="Element display option",
        scope=Scope.settings
    )
    editable_fields = ('display_name', 'aetool', 'aetool_config', 'iframe_url', 'btn_text', 'width', 'height', 'display')
    token = None

    @property
    def icon_class(self):
        return 'problem'

    @property
    def lms_role(self):
        """
        Get system user role.
        """
        user = self.runtime.service(self, 'user').get_current_user()
        return user.opt_attrs.get('edx-platform.user_role', 'student')

    @property
    def lms_user_name(self):
        """
        Returns the edx-platform database user id for the current user.
        """
        username = self.runtime.service(self, 'user').get_current_user().opt_attrs.get(
            'edx-platform.username', '')
        return username
        
    def _get_context_for_template(self):
        return {
            'lms_role': self.lms_role,
            'user_name': self.lms_user_name,
            'definition_id': self.scope_ids.def_id,
            'usage_id': self.scope_ids.usage_id,
            'display': self.display,
            'btn_text': self.btn_text,
            'iframe_url': self.iframe_url,
            'aetool': self.aetool,
            'aetool_config': self.aetool_config,
            'width': self.width,
            'height': self.height,
            'display_name': self.display_name
        }
    
    def _uid(self):
        return str(self.scope_ids.usage_id)


    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def studio_view(self, context):
        """
        Render a form for editing this XBlock
        """
        fragment = Fragment()
        context = {
            'fields': [],
            'lms_role': self.lms_role,
            'user_name': self.lms_user_name,
            'definition_id': self.scope_ids.def_id,
            'usage_id': self.scope_ids.usage_id
        }
        # Build a list of all the fields that can be edited:
        for field_name in self.editable_fields:
            field = self.fields[field_name]
            assert field.scope in (Scope.content, Scope.settings), (
                "Only Scope.content or Scope.settings fields can be used with "
                "StudioEditableXBlockMixin. Other scopes are for user-specific data and are "
                "not generally created/configured by content authors in Studio."
            )
            field_info = self._make_field_info(field_name, field)
            if field_info is not None:
                if field_info["type"] == 'generic' and field_info["name"] == 'aetool_config' and field_info["has_values"]:
                    field_info["value"] = json.loads(field_info["value"])
                context["fields"].append(field_info)
        frag = Fragment()
        frag.add_content(ResourceLoader(__name__).render_django_template(
            "/templates/studio_edit.html",
            context=context,
            i18n_service=self.runtime.service(self, "i18n"),
        ))
        frag.add_css(self.resource_string("static/css/aetool.css"))
        frag.add_javascript(self.resource_string("static/js/src/aetool.js"))
        frag.initialize_js('AEToolXBlockStudio')
        return frag

    def student_view(self, context=None):
        """
        The primary view of the AEToolXBlock, shown to students
        when viewing courses.
        """
        # return self.studio_view(context)
        frag = Fragment()
        frag.add_content(ResourceLoader(__name__).render_django_template(
            "/templates/student.html",
            context={
                **self._get_context_for_template(),
                **{'view': 'student'}
            },
            i18n_service=self.runtime.service(self, "i18n"),
        ))
        frag.add_css(self.resource_string("static/css/aetool.css"))
        frag.add_javascript(self.resource_string("static/js/src/aetool.js"))
        frag.initialize_js('AEToolXBlock')
        return frag

    def author_view(self, context=None):
        frag = Fragment()
        frag.add_content(ResourceLoader(__name__).render_django_template(
            "/templates/student.html",
            context={
                **self._get_context_for_template(),
                **{'view': 'studio'}
            },
            i18n_service=self.runtime.service(self, "i18n"),
        ))
        frag.add_css(self.resource_string("static/css/aetool.css"))
        frag.add_javascript(self.resource_string("static/js/src/aetool.js"))
        frag.initialize_js('AEToolXBlock')
        return frag
    
    def get_token(self):
        if self.token and self.token.get('expired_at', 0) > time.time() - 30:
            return self.token
        else:
            try:
                r = requests.post("https://id.meca.in.th/auth/realms/kidbright/protocol/openid-connect/token", data={
                    'grant_type': 'client_credentials',
                    'client_id': 'openedx',
                    'client_secret': '1d3f1bdd-6c49-4c7c-bf40-d40b3739ab27'
                })
                if r.status_code == 200:
                    t = r.json()
                    self.token = {**t, **{
                        'expired_at': time.time() + t.get('expires_in')
                    }}
                    return self.token
            except:
                pass
        return None

    @XBlock.json_handler
    def aetool_log_activity(self, data, suffix=''): # pylint: disable=unused-argument
        try:
            keys = [
                '@timestamp',
                'timestamp',
                'logLevel',
                'appID',
                'userID',
                'courseID',
                'sessionID',
                'flowID',
                'eventCategory',
                'event',
                'note',
                'customFields',
                'tags',
            ]
            cleanData = {}
            for k in keys:
                cleanData[k] = data.get(k)
            print(json.dumps(cleanData))
            r = requests.post('http://elasticsearch:9200/ae-activity-data-stream/_doc', json=cleanData)
            if r.status_code == 200:
                return r.json()
            else:
                print(r.status_code)
                print(r.text)
        except:
            pass
        return None

    @XBlock.json_handler
    def chatbot_init(self, data, suffix=''):  # pylint: disable=unused-argument
        courseId = self._uid().split('@')[0].split(':')[1].replace('+type', '') if len(self._uid().split('@')[0].split(':')) > 1  else self._uid().split('@')[0]
        blockId = self._uid().split('@')[2] if len(self._uid().split('@')) > 2  else self._uid().split('@')[0]
        try:
            r = requests.get('https://abdul.in.th/lite/core/api/v1/edubot-knowledge', params={
                'courseid': courseId,
                'sectionid': blockId
            })
            if r.status_code == 200:
                return r.json()
            else:
                print(r.status_code)
                print(r.text)
        except:
            pass
        return None

    @XBlock.json_handler
    def chatbot_train(self, data, suffix=''):  # pylint: disable=unused-argument
        courseId = self._uid().split('@')[0].split(':')[1].replace('+type', '') if len(self._uid().split('@')[0].split(':')) > 1  else self._uid().split('@')[0]
        blockId = self._uid().split('@')[2] if len(self._uid().split('@')) > 2  else self._uid().split('@')[0]
        courseName = ""
        sectionName = ""
        info = requests.get("http://ae-backend.learning/lms/%s/%s" % (
            urllib.parse.quote_plus(courseId), urllib.parse.quote_plus(blockId)
        ))
        if info.status_code == 200:
            courseInfo = {}
            try:
                courseInfo = info.json()
                courseName = courseInfo.get('courseTitle')
                sectionName = courseInfo.get('sequentialTitle')
            except:
                print(info.text)
            r = requests.post("https://abdul.in.th/lite/core/api/v1/edubot-knowledge", params={
                'courseid': courseId,
                'sectionid': blockId,
                'coursename': courseName,
                'sectionname': sectionName,
                'sheetid': data['sheetId'],
                'name': data['sheetName'],
                'type': data['type']
            })
            if r.status_code == 200:
                print(r.json())
                return r.json()
            else:
                print("train")
                print(r.status_code)
                print(r.text)
        return None

    @XBlock.json_handler
    def bookroll_init(self, data, suffix=''):  # pylint: disable=unused-argument
        courseId = self._uid().split('@')[0].split(':')[1].replace('+type', '') if len(self._uid().split('@')[0].split(':')) > 1  else self._uid().split('@')[0]
        blockId = self._uid().split('@')[2] if len(self._uid().split('@')) > 2  else self._uid().split('@')[0]
        token = self.get_token()
        if token:
            try:
                r = requests.get("https://bookroll.learning.app.meca.in.th/bookroll/v2/books/%s/%s" % (
                    courseId, blockId
                ), headers={
                    'Authorization': "Bearer %s" % (token.get('access_token'),)
                })
                if r.status_code == 200:
                    return r.json()
                else:
                    print(r.status_code)
                    print(r.text)
            except:
                pass
        return None

    @XBlock.json_handler
    def bookroll_delete(self, data, suffix=''):  # pylint: disable=unused-argument
        courseId = self._uid().split('@')[0].split(':')[1].replace('+type', '') if len(self._uid().split('@')[0].split(':')) > 1  else self._uid().split('@')[0]
        blockId = self._uid().split('@')[2] if len(self._uid().split('@')) > 2  else self._uid().split('@')[0]
        if 'contentId' in data:
            token = self.get_token()
            if token:
                try:
                    r = requests.delete("https://bookroll.learning.app.meca.in.th/bookroll/v2/books/%s" % (
                        data['contentId']
                    ), headers={
                        'Authorization': "Bearer %s" % (token.get('access_token'),)
                    })
                    if r.status_code == 200:
                        return r.json()
                    else:
                        print(r.status_code)
                        print(r.text)
                except:
                    pass
        return None
    
    @XBlock.handler
    def bookroll_handler(self, request, suffix=''):  # pylint: disable=unused-argument
        courseId = self._uid().split('@')[0].split(':')[1].replace('+type', '') if len(self._uid().split('@')[0].split(':')) > 1  else self._uid().split('@')[0]
        blockId = self._uid().split('@')[2] if len(self._uid().split('@')) > 2  else self._uid().split('@')[0]
        token = self.get_token()
        if token:
            try:
                r = requests.post("https://bookroll.learning.app.meca.in.th/bookroll/v2/books/%s/%s" % (
                    courseId, blockId
                ),
                files=request.body_file.FILES,
                headers={
                    'Authorization': "Bearer %s" % (token.get('access_token'),)
                })
                return Response(r.text, content_type='application/json', charset='utf8')
            except:
                pass
        return Response('null', content_type='application/json', charset='utf8')
    
    @XBlock.json_handler
    def iframe_init(self, data, suffix=''):  # pylint: disable=unused-argument
        courseId = self._uid().split('@')[0].split(':')[1].replace('+type', '') if len(self._uid().split('@')[0].split(':')) > 1  else self._uid().split('@')[0]
        blockId = self._uid().split('@')[2] if len(self._uid().split('@')) > 2  else self._uid().split('@')[0]
        return None
    
    @XBlock.json_handler
    def simulator_init(self, data, suffix=''):  # pylint: disable=unused-argument
        courseId = self._uid().split('@')[0].split(':')[1].replace('+type', '') if len(self._uid().split('@')[0].split(':')) > 1  else self._uid().split('@')[0]
        blockId = self._uid().split('@')[2] if len(self._uid().split('@')) > 2  else self._uid().split('@')[0]
        return None
    
    @XBlock.json_handler
    def video_init(self, data, suffix=''):  # pylint: disable=unused-argument
        courseId = self._uid().split('@')[0].split(':')[1].replace('+type', '') if len(self._uid().split('@')[0].split(':')) > 1  else self._uid().split('@')[0]
        blockId = self._uid().split('@')[2] if len(self._uid().split('@')) > 2  else self._uid().split('@')[0]
        return None
    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("AEToolXBlock",
             """<aetool/>
             """),
            ("Multiple AEToolXBlock",
             """<vertical_demo>
                <aetool/>
                <aetool/>
                <aetool/>
                </vertical_demo>
             """),
        ]
