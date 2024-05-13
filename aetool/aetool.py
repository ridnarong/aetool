"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import String, Integer, Scope
try:
    from xblock.utils.resources import ResourceLoader
except ModuleNotFoundError:
    from xblockutils.resources import ResourceLoader

@XBlock.wants('settings')
@XBlock.wants('user')
@XBlock.needs("i18n")
class AEToolXBlock(XBlock):
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
        choices=[
            ('simulator', 'Simulator'),
            ('chatbot', 'Chatbot'),
            ('bookroll', 'Bookroll'),
            ('iframe', 'External URL')
        ],
        default='iframe',
        help="Select AE Tool",
        scope=Scope.settings
    )
    btn_text = String(
        display_name="Button text",
        default='Button',
        help="Button text",
        scope=Scope.settings
    )
    iframe_url = String(
        display_name="IFrame URL",
        default='',
        help="IFrame URL display in modal",
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
        default='modal',
        help="Element display option",
        scope=Scope.settings
    )

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
        return 
        
    def _get_context_for_template(self):
        return {
            'lms_role': self.lms_role,
            'user_name': self.lms_user_name,
            'definition_id': self.scope_ids.def_id,
            'usage_id': self.scope_ids.usage_id,
            'display': self.display,
            'btn_text': self.btn_text,
            'iframe_url': self.iframe_url,
            'width': self.width,
            'height': self.height,
            'display_name': self.display_name
        }


    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the AEToolXBlock, shown to students
        when viewing courses.
        """
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
