import greatape
import lxml.html

from zope import schema
from zope.interface import Interface

from z3c.form import field
from z3c.form import button

from collective.chimpfeed.interfaces import IFeedSettings
from collective.chimpfeed.form import BaseForm
from collective.chimpfeed import MessageFactory as _

# from plone.formwidget.datetime.z3cform.widget import DatetimeFieldWidget
from collective.z3cform.datetimewidget import DatetimeFieldWidget


class ISendAsNewsletter(Interface):
    list = schema.Choice(
        title=_(u"Send through list"),
        required=True,
        vocabulary="collective.chimpfeed.vocabularies.Lists",
        )

    send_scheduled = schema.Datetime(
        title=_(u"Send scheduled"),
        required=False,
        )

    send_now = schema.Bool(
        title=_(u"Send now"),
        required=False,
        )


class SendAsNewsletter(BaseForm):

    fields = field.Fields(ISendAsNewsletter)
    fields['send_scheduled'].widgetFactory = DatetimeFieldWidget

    @button.buttonAndHandler(_(u'Send'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        settings = IFeedSettings(self.context)
        api_key = settings.mailchimp_api_key
        api = greatape.MailChimp(api_key, debug=True)

        options = {"list_id": data['list'],
                   "subject": self.context.title,
                   "from_email": "franklin@fourdigits.nl",
                   "from_name": "Franklin Kingma",
                   "auto_footer": "True",
                   "template_id": "147237",
                     }

        # import pdb; pdb.set_trace( )

        # bla = self.context()
        # bla = bla.encode('utf-8')
        # document = lxml.html.fromstring(bla)
        # content = document.cssselect("div#content")

        # content = {'html': lxml.html.tostring(content[0])}

        content = {'html_MAIN': self.context.getText(),
                   'generate_text': True}

        campaign_id = api.campaignCreate(type="regular",
                                         options=options,
                                         content=content)

        if data['send_scheduled']:
            # schedule_time   the time to schedule the campaign.
            # For A/B Split "schedule" campaigns, the time for Group A -
            # in YYYY-MM-DD HH:II:SS format in GMT
            results = api.campaignSchedule(cid=campaign_id,
                                           schedule_time=data['schedule_time'])

        if data['send_now']:
            results = api.campaignSendNow(cid=campaign_id)

