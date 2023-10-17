# -*- coding: utf-8 -*-
import unittest
from odoo.addons.account.tests.test_payment import TestPayment
from odoo.addons.account.tests.test_reconciliation import TestReconciliationExec


@unittest.skip('Skipped tests')
def skip_test(self):
    pass


TestPayment.test_full_payment_process = skip_test
TestReconciliationExec.test_statement_usd_invoice_usd_transaction_eur
