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

    template = schema.Choice(
        title=_(u"Which template to use"),
        required=True,
        vocabulary="collective.chimpfeed.vocabularies.Templates",
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

    def action(self):
        # Needed in case of default_page and/or named view
        return self.request.get('ACTUAL_URL')

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
                   "template_id": data['template'],
                     }

        try:
            content = self.context.getText()
        except:
            content = self.context[self.context.default_page].getText()

        content = {'html_MAIN': content,
                   'generate_text': True}

        campaign_id = api.campaignCreate(type="regular",
                                         options=options,
                                         content=content)

        if data['send_scheduled']:
            # TODO: Get values from form
            # api in: YYYY-MM-DD HH:II:SS format in GMT
            results = api.campaignSchedule(cid=campaign_id,
                                           schedule_time=data['schedule_time'])

        if data['send_now']:
            results = api.campaignSendNow(cid=campaign_id)

        self.status = _(u"Newsletter send (%s)" % (results))


