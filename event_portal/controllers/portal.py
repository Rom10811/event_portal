# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict
from operator import itemgetter
from markupsafe import Markup

from odoo import conf, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem

from odoo.osv.expression import OR, AND

from odoo.addons.web.controllers.main import HomeStaticTemplateHelpers


class EventCustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'event_count' in counters:
            values['event_count'] = request.env['event.event'].search_count([]) \
                if request.env['event.event'].check_access_rights('read', raise_exception=False) else 0
        return values

    # ------------------------------------------------------------
    # My Event
    # ------------------------------------------------------------
    def _event_get_page_view_values(self, event, access_token, page=1, date_begin=None, date_end=None, sortby=None,
                                    search=None, search_in='content', groupby=None, **kwargs):
        # TODO: refactor this because most of this code is duplicated from portal_my_events method
        values = self._prepare_portal_layout_values()

        # default sort by value
        if not sortby:
            sortby = 'date'

        # default filter by value
        domain = [('id', '=', event.id)]

        # default group by value
        if not groupby:
            groupby = 'event'

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        Event = request.env['event.event']
        if access_token:
            Event = Event.sudo()
        elif not request.env.user._is_public():
            domain = AND([domain, request.env['ir.rule']._compute_domain(Event._name, 'read')])
            Event = Event.sudo()

        # event count
        event_count = Event.search_count(domain)
        # pager
        url = "/my/events/%s" % event.id
        pager = portal_pager(
            url=url,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'groupby': groupby,
                      'search_in': search_in, 'search': search},
            total=event_count,
            page=page,
            step=self._items_per_page
        )

        events = Event.search(domain, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_event_events_history'] = events.ids[:100]

        values.update(
            date=date_begin,
            date_end=date_end,
            page_name='event',
            default_url=url,
            pager=pager,
            search_in=search_in,
            search=search,
            sortby=sortby,
            groupby=groupby,
            event=event,
        )
        return self._get_page_view_values(event, access_token, values, 'my_events_history', False, **kwargs)

    @http.route(['/my/events', '/my/events/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_events(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Event = request.env['event.event']
        domain = []

        domain += [('message_is_follower', '=', True), ('is_done', "!=", True), ('is_finished', '!=', True)]

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # events count
        event_count = Event.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/events",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=event_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        events = Event.search(domain, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_events_history'] = events.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'events': events,
            'page_name': 'event',
            'default_url': '/my/events',
            'pager': pager,
            'sortby': sortby
        })
        return request.render("event_portal.portal_my_events", values)

    @http.route(['/my/events/<int:event_id>'], type='http', auth="public", website=True)
    def portal_my_event(self, event_id=None, access_token=None, page=1, date_begin=None, date_end=None, sortby=None,
                        search=None, search_in='content', groupby=None, **kw):
        try:
            event_sudo = self._document_check_access('event.event', event_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        event_sudo = event_sudo if access_token else event_sudo.with_user(request.env.user)
        values = self._event_get_page_view_values(event_sudo, access_token, page, date_begin, date_end, sortby, search,
                                                  search_in, groupby, **kw)
        return request.render("event_portal.portal_my_event", values)
