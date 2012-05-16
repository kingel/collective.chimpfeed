import greatape

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from collective.chimpfeed.interfaces import IFeedSettings

import lxml.html


class SendAsNewsletter(BrowserView):
    """The recent portlet
    """

    def index(self):
        settings = IFeedSettings(self.context)
        api_key = settings.mailchimp_api_key
        api = greatape.MailChimp(api_key, debug=True)

        options = {"list_id": "3e34449235",
                   "subject": "test",
                   "from_email": "franklin@fourdigits.nl",
                   "from_name": "Franklin Kingma",
                   "auto_footer": "True",
                     }

        bla = self.context()
        bla = bla.encode('utf-8')

        document = lxml.html.fromstring(bla)
        content = document.cssselect("div#content")

        content = {'html': lxml.html.tostring(content[0])}

        campaign_id = api.campaignCreate(type="regular",
                                         options=options,
                                         content=content)

        results = api.campaignSendNow(cid=campaign_id)

    def results(self):
        """Get the search results
        """
        context = aq_inner(self.context)
        putils = getToolByName(context, 'plone_utils')
        portal_catalog = getToolByName(context, 'portal_catalog')
        typesToShow = putils.getUserFriendlyTypes()
        return self.request.get(
            'items',
            portal_catalog.searchResults(sort_on='modified',
                                         portal_type=typesToShow,
                                         sort_order='reverse',
                                         sort_limit=5)[:5])