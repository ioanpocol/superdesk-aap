# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import unittest
from .currency_usd_to_aud import usd_to_aud
from decimal import Decimal


class CurrencyTestCase(unittest.TestCase):

    def test_usd_to_aud(self):
        text = 'This is a $ 40 note. ' \
               'This is a $ 1000 note. ' \
               'This is a $41 note. ' \
               'This is a $(42) note. ' \
               'This is a $46,483 note. ' \
               'This is a $4,648,382 note. ' \
               'This is a $4,648,382.20 ' \
               '$4,648,382.2 only ' \
               'This is ($4,648,382.2) only ' \
               'This is $4,648,820.20 only ' \
               '$46,483 only ' \
               'This is $(46.00) only ' \
               'This is a  USD 52 note. ' \
               'This is a  USD53 note. ' \
               'This is a  USD(54,000) note. ' \
               'This is a  USD (55,233.00) note. ' \
               'This is a  $US 52 note. ' \
               'This is a  $US53 note. ' \
               'This is a  $US58m note. ' \
               'This is a  $US(54,000) note. ' \
               'This is a  $US (55,233.00) note. ' \
               'This is a  $US 52-million note. ' \
               'This is a  $US 52 mln note. ' \
               'This is a  $US53 b note. ' \
               'This is a  $US(540,000) million note. ' \
               'This is a  $US (55,233.00) million note. ' \
               'This is a  $US (55,233.00 billion) note. ' \

        item = {'body_html': text}
        res, diff = usd_to_aud(item, rate=Decimal(2))
        self.assertEqual(diff['$ 40'], '$US 40 ($A80)')
        self.assertEqual(diff['$ 1000'], '$US 1000 ($A2,000)')
        self.assertEqual(diff['$41'], '$US41 ($A82)')
        self.assertEqual(diff['$(42)'], '$US(42) ($A84)')
        self.assertEqual(diff['$46,483'], '$US46,483 ($A92,966)')
        self.assertEqual(diff['$4,648,382'], '$US4,648,382 ($A9.3 million)')
        self.assertEqual(diff['$4,648,382.20'], '$US4,648,382.20 ($A9.30 million)')
        self.assertEqual(diff['USD(54,000)'], 'USD(54,000) ($A108,000)')
        self.assertEqual(diff['USD 52'], 'USD 52 ($A104)')
        self.assertEqual(diff['USD53'], 'USD53 ($A106)')
        self.assertEqual(diff['USD (55,233.00)'], 'USD (55,233.00) ($A110,466.00)')
        self.assertEqual(diff['$US(54,000)'], '$US(54,000) ($A108,000)')
        self.assertEqual(diff['$US 52'], '$US 52 ($A104)')
        self.assertEqual(diff['$US53'], '$US53 ($A106)')
        self.assertEqual(diff['$US58m'], '$US58m ($A116 m)')
        self.assertEqual(diff['$US (55,233.00)'], '$US (55,233.00) ($A110,466.00)')
        self.assertEqual(diff['$US 52-million'], '$US 52-million ($A104 million)')
        self.assertEqual(diff['$US 52 mln'], '$US 52 mln ($A104 mln)')
        self.assertEqual(diff['$US53 b'], '$US53 b ($A106 b)')
        self.assertEqual(diff['$US(540,000) million'], '$US(540,000) million ($A1,080 billion)')
        self.assertEqual(diff['$US (55,233.00) million'], '$US (55,233.00) million ($A110.47 billion)')
        self.assertEqual(diff['$US (55,233.00 billion)'], '$US (55,233.00 billion) ($A110.47 trillion)')
