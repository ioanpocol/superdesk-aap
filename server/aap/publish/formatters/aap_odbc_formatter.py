# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from superdesk.io.iptc import subject_codes
from apps.packages import TakesPackageService
from .aap_formatter_common import set_subject
from apps.archive.common import get_utc_schedule
from .field_mappers.locator_mapper import LocatorMapper
from .field_mappers.slugline_mapper import SluglineMapper
from superdesk.metadata.item import EMBARGO
from eve.utils import config
import superdesk
from .unicodetoascii import to_ascii
from bs4 import BeautifulSoup


class AAPODBCFormatter():
    def get_odbc_item(self, article, subscriber, category, codes, pass_through=False):
        """
        Construct an odbc_item with the common key value pairs populated, if pass_through is true then the headline
        original headline is maintained.
        :param article:
        :param subscriber:
        :param category:
        :param codes:
        :param pass_through:
        :return:
        """
        article['headline'] = BeautifulSoup(article.get('headline', ''), 'html.parser').text
        pub_seq_num = superdesk.get_resource_service('subscribers').generate_sequence_number(subscriber)
        odbc_item = dict(originator=article.get('source', None), sequence=pub_seq_num,
                         category=category.get('qcode').lower(),
                         author=BeautifulSoup(article.get('byline', '') or '', 'html.parser').text.replace
                         ('\'', '\'\''),
                         keyword=SluglineMapper().map(article=article,
                                                      category=category.get('qcode').upper(),
                                                      truncate=True).replace('\'', '\'\'') if not pass_through else
                         (article.get('slugline', '') or '').replace('\'', '\'\''),
                         subject_reference=set_subject(category, article),
                         take_key=(article.get('anpa_take_key', '') or '').replace('\'', '\'\''))
        if 'genre' in article and len(article['genre']) >= 1:
            odbc_item['genre'] = article['genre'][0].get('name', None)
        else:
            odbc_item['genre'] = 'Current'  # @genre
        odbc_item['news_item_type'] = 'News'
        odbc_item['fullStory'] = 1
        odbc_item['ident'] = '0'  # @ident
        odbc_item['selector_codes'] = ' '.join(codes) if codes else ' '

        headline = to_ascii(LocatorMapper().get_formatted_headline(article, category.get('qcode').upper()))
        odbc_item['headline'] = headline.replace('\'', '\'\'').replace('\xA0', ' ')

        self.expand_subject_codes(odbc_item)
        self.set_usn(odbc_item, article)

        return pub_seq_num, odbc_item

    def add_embargo(self, odbc_item, article):
        """
        Add the embargo text to the article if required
        :param odbc_item:
        :param article:
        :return:
        """
        if article.get(EMBARGO):
            embargo = '{}{}\r\n'.format('Embargo Content. Timestamp: ', get_utc_schedule(article, EMBARGO).isoformat())
            odbc_item['article_text'] = embargo + odbc_item['article_text']

    def add_ednote(self, odbc_item, article):
        """
        Add the editorial note if required
        :param odbc_item:
        :param article:
        :return:
        """
        if article.get('ednote'):
            ednote = 'EDS:{}\r\n'.format(article.get('ednote').replace('\'', '\'\''))
            odbc_item['article_text'] = ednote + odbc_item['article_text']

    def add_byline(self, odbc_item, article):
        """
        Add the byline to the article text
        :param odbc_item:
        :param article:
        :return:
        """
        if article.get('byline') and article.get('byline') != '':
            byline = BeautifulSoup(article.get('byline', ''), 'html.parser').text
            if len(byline) >= 3 and byline[:2].upper() != 'BY':
                byline = 'By ' + byline
            byline = '\x19   {}\x19\r\n'.format(byline).replace('\'', '\'\'')
            odbc_item['article_text'] = byline + odbc_item['article_text']

    def expand_subject_codes(self, odbc_item):
        """
        Expands the subject reference to the subject matter and subject detail
        :param odbc_item:
        :return:
        """
        if 'subject_reference' in odbc_item and odbc_item['subject_reference'] is not None \
                and odbc_item['subject_reference'] != '00000000':
            odbc_item['subject'] = subject_codes[odbc_item['subject_reference'][:2] + '000000']
            if odbc_item['subject_reference'][2:5] != '000':
                odbc_item['subject_matter'] = subject_codes[odbc_item['subject_reference'][:5] + '000']
            else:
                odbc_item['subject_matter'] = ''
            if not odbc_item['subject_reference'].endswith('000'):
                odbc_item['subject_detail'] = subject_codes[odbc_item['subject_reference']]
            else:
                odbc_item['subject_detail'] = ''
        else:
            odbc_item['subject_reference'] = '00000000'

    def set_usn(self, odbc_item, article):
        """
        Set the usn (unique story number) in the odbc item
        :param odbc_item:
        :param article:
        :return:
        """
        takes_package_service = TakesPackageService()
        pkg = takes_package_service.get_take_package(article)
        if pkg is not None:
            odbc_item['usn'] = pkg.get('unique_id', None)  # @usn
        else:
            odbc_item['usn'] = article.get('unique_id', None)  # @usn

    def is_last_take(self, article):
        article[config.ID_FIELD] = article.get('item_id', article.get(config.ID_FIELD))
        return TakesPackageService().is_last_takes_package_item(article)

    def is_first_part(self, article):
        return article.get('sequence', 1) == 1
