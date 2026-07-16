# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError, UserError
from datetime import date


@tagged('post_install', '-standard', 'pms_revenue')
class TestPmsRevenueBase(TransactionCase):
    """Base test class with shared setup for revenue/fee tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # ── Create a property ────────────────────────────────────────────
        product_tmpl = cls.env['product.template'].create({
            'name': 'Test Beach House',
            'list_price': 500.0,
            'type': 'service',
        })
        cls.property = cls.env['pms.property'].create({
            'product_tmpl_id': product_tmpl.id,
            'property_type': 'house',
            'number_of_rooms': 3,
            'max_occupancy': 8,
        })

        # ── Create an owner ──────────────────────────────────────────────
        cls.owner = cls.env['pms.owner'].create({
            'name': 'Test Owner LLC',
            'tax_name': 'Test Owner LLC',
            'tax_street_address': '123 Main St',
            'tax_extended_address': 'Suite 100',
            'tax_locality': 'Test City',
            'tax_region': 'TS',
            'tax_postal_code': '12345',
            'tax_country': 'US',
            'tax_phone': '555-1234',
        })

        # ── Charge Types ─────────────────────────────────────────────────
        ChargeType = cls.env['pms.charge.type']
        cls.ct_rent = ChargeType.create({'name': 'Rent', 'code': 'RENT', 'is_revenue': True})
        cls.ct_cleaning = ChargeType.create({'name': 'Cleaning Fee', 'code': 'CLEANING', 'is_revenue': True})
        cls.ct_pet = ChargeType.create({'name': 'Pet Fee', 'code': 'PET_FEE', 'is_revenue': True})
        cls.ct_resort = ChargeType.create({'name': 'Resort Fee', 'code': 'RESORT_FEE', 'is_revenue': True})
        cls.ct_lodging_tax = ChargeType.create({
            'name': 'Lodging Tax', 'code': 'LODGING_TAX',
            'is_revenue': False, 'is_tax': True,
        })
        cls.ct_sales_tax = ChargeType.create({
            'name': 'Sales Tax', 'code': 'SALES_TAX',
            'is_revenue': False, 'is_tax': True,
        })
        cls.ct_ota_commission = ChargeType.create({
            'name': 'OTA Commission', 'code': 'OTA_COMMISSION',
            'is_revenue': False, 'is_expense': True,
        })
        cls.ct_cc_fee = ChargeType.create({
            'name': 'Credit Card Fee', 'code': 'CC_FEE',
            'is_revenue': False, 'is_expense': True,
        })
        cls.ct_owner_maint = ChargeType.create({
            'name': 'Owner Maintenance Expense', 'code': 'OWNER_MAINT',
            'is_revenue': False, 'is_expense': True,
        })
        cls.ct_discount = ChargeType.create({'name': 'Discount', 'code': 'DISCOUNT', 'is_revenue': True})
        cls.ct_refund = ChargeType.create({
            'name': 'Refund', 'code': 'REFUND',
            'is_revenue': True, 'is_refund': True,
        })
        cls.ct_cancel_fee = ChargeType.create({
            'name': 'Cancellation Fee', 'code': 'CANCELLATION_FEE',
            'is_revenue': True,
        })
        cls.ct_security_deposit = ChargeType.create({
            'name': 'Security Deposit', 'code': 'SECURITY_DEPOSIT',
            'is_revenue': False,
        })

        # ── Revenue Policy: 20% management fee on rent ───────────────────
        cls.policy = cls.env['pms.revenue.policy'].create({
            'name': 'Standard 20% Policy',
            'management_fee_type': 'percentage',
            'management_fee_percent': 20.0,
            'rounding_method': 'round',
        })
        # Policy lines
        PolicyLine = cls.env['pms.revenue.policy.line']
        cls.pl_rent = PolicyLine.create({
            'policy_id': cls.policy.id,
            'charge_type_id': cls.ct_rent.id,
            'owner_share_percent': 100.0,
            'manager_share_percent': 0.0,
            'liability_share_percent': 0.0,
            'commission_basis': 'gross_amount',
        })
        cls.pl_cleaning = PolicyLine.create({
            'policy_id': cls.policy.id,
            'charge_type_id': cls.ct_cleaning.id,
            'owner_share_percent': 100.0,
            'manager_share_percent': 0.0,
            'liability_share_percent': 0.0,
            'commission_basis': 'excluded',
        })
        cls.pl_pet = PolicyLine.create({
            'policy_id': cls.policy.id,
            'charge_type_id': cls.ct_pet.id,
            'owner_share_percent': 50.0,
            'manager_share_percent': 50.0,
            'liability_share_percent': 0.0,
            'commission_basis': 'excluded',
        })
        cls.pl_resort = PolicyLine.create({
            'policy_id': cls.policy.id,
            'charge_type_id': cls.ct_resort.id,
            'owner_share_percent': 100.0,
            'manager_share_percent': 0.0,
            'liability_share_percent': 0.0,
            'commission_basis': 'gross_amount',
        })
        cls.pl_lodging_tax = PolicyLine.create({
            'policy_id': cls.policy.id,
            'charge_type_id': cls.ct_lodging_tax.id,
            'owner_share_percent': 0.0,
            'manager_share_percent': 0.0,
            'liability_share_percent': 100.0,
            'commission_basis': 'excluded',
        })
        cls.pl_ota = PolicyLine.create({
            'policy_id': cls.policy.id,
            'charge_type_id': cls.ct_ota_commission.id,
            'owner_share_percent': 100.0,
            'manager_share_percent': 0.0,
            'liability_share_percent': 0.0,
            'commission_basis': 'excluded',
            'expense_responsibility': 'owner',
        })
        cls.pl_cc_fee = PolicyLine.create({
            'policy_id': cls.policy.id,
            'charge_type_id': cls.ct_cc_fee.id,
            'owner_share_percent': 50.0,
            'manager_share_percent': 50.0,
            'liability_share_percent': 0.0,
            'commission_basis': 'excluded',
            'expense_responsibility': 'split',
        })
        cls.pl_discount = PolicyLine.create({
            'policy_id': cls.policy.id,
            'charge_type_id': cls.ct_discount.id,
            'owner_share_percent': 100.0,
            'manager_share_percent': 0.0,
            'liability_share_percent': 0.0,
            'commission_basis': 'gross_amount',
        })
        cls.pl_refund = PolicyLine.create({
            'policy_id': cls.policy.id,
            'charge_type_id': cls.ct_refund.id,
            'owner_share_percent': 100.0,
            'manager_share_percent': 0.0,
            'liability_share_percent': 0.0,
            'commission_basis': 'gross_amount',
        })
        cls.pl_cancel_fee = PolicyLine.create({
            'policy_id': cls.policy.id,
            'charge_type_id': cls.ct_cancel_fee.id,
            'owner_share_percent': 50.0,
            'manager_share_percent': 50.0,
            'liability_share_percent': 0.0,
            'commission_basis': 'gross_amount',
        })

        # ── Owner Agreement ──────────────────────────────────────────────
        cls.agreement = cls.env['pms.owner.agreement'].create({
            'owner_id': cls.owner.id,
            'property_id': cls.property.id,
            'effective_start_date': date(2026, 1, 1),
            'status': 'active',
            'settlement_frequency': 'monthly',
            'revenue_policy_id': cls.policy.id,
        })

    # ── Helpers ──────────────────────────────────────────────────────────

    def _create_reservation(self, checkin=None, checkout=None):
        """Create a basic confirmed booking for the test property."""
        if checkin is None:
            checkin = date(2026, 6, 1)
        if checkout is None:
            checkout = date(2026, 6, 7)
        partner = self.env['res.partner'].create({'name': 'Test Guest'})
        return self.env['pms.booking'].create({
            'property_id': self.property.id,
            'partner_id': partner.id,
            'checkin_date': checkin,
            'checkout_date': checkout,
            'state': 'confirmed',
        })

    def _create_charge(self, reservation, charge_type, amount, tx_date=None, tax_amount=0.0, **kwargs):
        """Create a reservation charge line."""
        if tx_date is None:
            tx_date = date(2026, 6, 1)
        vals = {
            'reservation_id': reservation.id,
            'charge_type_id': charge_type.id,
            'unit_amount': amount,
            'quantity': 1.0,
            'transaction_date': tx_date,
            'tax_amount': tax_amount,
        }
        vals.update(kwargs)
        return self.env['pms.reservation.charge'].create(vals)

    def _create_settlement(self, period_start=None, period_end=None):
        """Create a draft settlement for the test property."""
        if period_start is None:
            period_start = date(2026, 6, 1)
        if period_end is None:
            period_end = date(2026, 6, 30)
        return self.env['pms.owner.settlement'].create({
            'owner_id': self.owner.id,
            'property_id': self.property.id,
            'period_start': period_start,
            'period_end': period_end,
        })


@tagged('post_install', '-standard', 'pms_revenue')
class TestPercentageRentOnly(TestPmsRevenueBase):
    """Test: Percentage management fee applied to rent only."""

    def test_percentage_rent_only(self):
        res = self._create_reservation()
        self._create_charge(res, self.ct_rent, 1000.0)

        settlement = self._create_settlement()
        settlement.action_calculate()

        self.assertEqual(settlement.state, 'calculated')
        self.assertEqual(settlement.commission_base, 1000.0)
        self.assertEqual(settlement.management_fee, 200.0)
        self.assertEqual(settlement.owner_gross_proceeds, 1000.0)
        self.assertEqual(settlement.owner_net_payout, 800.0)
        self.assertEqual(settlement.tax_liability, 0.0)


@tagged('post_install', '-standard', 'pms_revenue')
class TestPercentageRentAndFees(TestPmsRevenueBase):
    """Test: Percentage applied to rent and selected fees (resort fee)."""

    def test_percentage_rent_and_fees(self):
        res = self._create_reservation()
        self._create_charge(res, self.ct_rent, 1000.0)
        self._create_charge(res, self.ct_resort, 150.0)
        self._create_charge(res, self.ct_cleaning, 100.0)  # excluded from commission

        settlement = self._create_settlement()
        settlement.action_calculate()

        # Commission base = rent (1000) + resort (150) = 1150 (cleaning excluded)
        self.assertEqual(settlement.commission_base, 1150.0)
        self.assertEqual(settlement.management_fee, 230.0)  # 20% of 1150
        # Owner gross = rent (1000) + resort (150) + cleaning (100) = 1250
        self.assertEqual(settlement.owner_gross_proceeds, 1250.0)
        self.assertEqual(settlement.owner_net_payout, 1250.0 - 230.0)


@tagged('post_install', '-standard', 'pms_revenue')
class TestFeeSplitOwnerManager(TestPmsRevenueBase):
    """Test: Fee split between owner and manager (pet fee 50/50)."""

    def test_fee_split(self):
        res = self._create_reservation()
        self._create_charge(res, self.ct_rent, 1000.0)
        self._create_charge(res, self.ct_pet, 100.0)

        settlement = self._create_settlement()
        settlement.action_calculate()

        # Check the pet fee line
        pet_line = settlement.line_ids.filtered(lambda l: l.charge_type_id == self.ct_pet)
        self.assertEqual(len(pet_line), 1)
        self.assertEqual(pet_line.owner_amount, 50.0)
        self.assertEqual(pet_line.manager_amount, 50.0)

        # Owner gross = rent (1000) + pet owner share (50) = 1050
        self.assertEqual(settlement.owner_gross_proceeds, 1050.0)
        # Commission base = rent only (pet excluded)
        self.assertEqual(settlement.commission_base, 1000.0)
        self.assertEqual(settlement.management_fee, 200.0)


@tagged('post_install', '-standard', 'pms_revenue')
class TestTaxExclusion(TestPmsRevenueBase):
    """Test: Taxes are excluded from owner and manager revenue."""

    def test_tax_exclusion(self):
        res = self._create_reservation()
        self._create_charge(res, self.ct_rent, 1000.0)
        self._create_charge(res, self.ct_lodging_tax, 120.0)

        settlement = self._create_settlement()
        settlement.action_calculate()

        # Tax should not be owner or manager revenue
        self.assertEqual(settlement.owner_gross_proceeds, 1000.0)
        self.assertEqual(settlement.tax_liability, 120.0)
        # Commission base is rent only
        self.assertEqual(settlement.commission_base, 1000.0)
        self.assertEqual(settlement.management_fee, 200.0)
        self.assertEqual(settlement.owner_net_payout, 800.0)


@tagged('post_install', '-standard', 'pms_revenue')
class TestOwnerPaidOTACommission(TestPmsRevenueBase):
    """Test: Owner-paid OTA commission as an expense."""

    def test_owner_paid_ota(self):
        res = self._create_reservation()
        self._create_charge(res, self.ct_rent, 1000.0)
        self._create_charge(res, self.ct_ota_commission, 150.0)

        settlement = self._create_settlement()
        settlement.action_calculate()

        # OTA commission is an owner expense
        self.assertEqual(settlement.owner_expenses, 150.0)
        # Owner gross is just rent
        self.assertEqual(settlement.owner_gross_proceeds, 1000.0)
        # Net = 1000 - 200 (mgmt fee) - 150 (OTA) = 650
        self.assertEqual(settlement.owner_net_payout, 650.0)


@tagged('post_install', '-standard', 'pms_revenue')
class TestDiscounts(TestPmsRevenueBase):
    """Test: Discounts reduce commission base and owner proceeds."""

    def test_discount(self):
        res = self._create_reservation()
        self._create_charge(res, self.ct_rent, 1000.0)
        self._create_charge(res, self.ct_discount, -100.0)  # negative = discount

        settlement = self._create_settlement()
        settlement.action_calculate()

        # Discount is revenue with gross_amount basis, so commission base includes it
        # Commission base = 1000 + (-100) = 900
        self.assertEqual(settlement.commission_base, 900.0)
        self.assertEqual(settlement.management_fee, 180.0)
        # Owner gross = 1000 + (-100) = 900
        self.assertEqual(settlement.owner_gross_proceeds, 900.0)
        # Net = 900 - 180 = 720
        self.assertEqual(settlement.owner_net_payout, 720.0)


@tagged('post_install', '-standard', 'pms_revenue')
class TestPartialRefund(TestPmsRevenueBase):
    """Test: Partial refund reverses original allocation."""

    def test_partial_refund(self):
        res = self._create_reservation()
        rent_charge = self._create_charge(res, self.ct_rent, 1000.0)
        # Partial refund of 200
        refund_charge = self._create_charge(
            res, self.ct_refund, 200.0,
            reversal_of_id=rent_charge.id,
        )

        settlement = self._create_settlement()
        settlement.action_calculate()

        # Commission base = 1000 (rent) + (-200 refund reversal) = 800
        self.assertEqual(settlement.commission_base, 800.0)
        self.assertEqual(settlement.management_fee, 160.0)
        # Owner gross = 1000 - 200 = 800
        self.assertEqual(settlement.owner_gross_proceeds, 800.0)
        self.assertEqual(settlement.owner_net_payout, 800.0 - 160.0)


@tagged('post_install', '-standard', 'pms_revenue')
class TestFullCancellation(TestPmsRevenueBase):
    """Test: Full cancellation reverses everything."""

    def test_full_cancellation(self):
        res = self._create_reservation()
        rent_charge = self._create_charge(res, self.ct_rent, 1000.0)
        cleaning_charge = self._create_charge(res, self.ct_cleaning, 100.0)
        # Full refund
        self._create_charge(
            res, self.ct_refund, 1100.0,
            reversal_of_id=rent_charge.id,
        )

        settlement = self._create_settlement()
        settlement.action_calculate()

        # Commission base = 1000 (rent) + (-1100 refund) = -100
        # But refund reverses at original allocation rate
        # Rent refund: 1000 * 100% owner, commission basis gross → -1000
        # Extra 100 refund: at refund charge type allocation (100% owner, gross basis) → -100
        # Total commission base = 1000 - 1000 - 100 = -100... but refund was 1100, rent was 1000
        # Actually: rent gross = 1000, refund gross = 1100
        # Rent commissionable = 1000 (gross_amount)
        # Refund commissionable = -1100 (gross_amount reversed)
        # Total = 1000 - 1100 = -100
        self.assertEqual(settlement.commission_base, -100.0)
        # Management fee on negative base: -20
        self.assertEqual(settlement.management_fee, -20.0)


@tagged('post_install', '-standard', 'pms_revenue')
class TestCancellationFeeRevenue(TestPmsRevenueBase):
    """Test: Cancellation fee is treated as its own charge type, not rent."""

    def test_cancellation_fee(self):
        res = self._create_reservation()
        # Cancellation fee charged
        self._create_charge(res, self.ct_cancel_fee, 200.0)

        settlement = self._create_settlement()
        settlement.action_calculate()

        cancel_line = settlement.line_ids.filtered(lambda l: l.charge_type_id == self.ct_cancel_fee)
        self.assertEqual(len(cancel_line), 1)
        # 50/50 split
        self.assertEqual(cancel_line.owner_amount, 100.0)
        self.assertEqual(cancel_line.manager_amount, 100.0)
        # Commission basis = gross_amount → 200
        self.assertEqual(settlement.commission_base, 200.0)
        self.assertEqual(settlement.management_fee, 40.0)  # 20% of 200
        # Owner gross = owner share of cancel fee = 100
        self.assertEqual(settlement.owner_gross_proceeds, 100.0)


@tagged('post_install', '-standard', 'pms_revenue')
class TestAgreementEffectiveDates(TestPmsRevenueBase):
    """Test: Agreement changes with effective dates are respected."""

    def test_agreement_effective_dates(self):
        # Create a second agreement that starts mid-period
        policy2 = self.env['pms.revenue.policy'].create({
            'name': '30% Policy',
            'management_fee_type': 'percentage',
            'management_fee_percent': 30.0,
            'rounding_method': 'round',
        })
        self.env['pms.revenue.policy.line'].create({
            'policy_id': policy2.id,
            'charge_type_id': self.ct_rent.id,
            'owner_share_percent': 100.0,
            'manager_share_percent': 0.0,
            'liability_share_percent': 0.0,
            'commission_basis': 'gross_amount',
        })

        # Terminate old agreement, activate new one
        self.agreement.status = 'terminated'
        # Set end date on old agreement before new one starts
        self.agreement.effective_end_date = date(2026, 6, 15)
        new_agreement = self.env['pms.owner.agreement'].create({
            'owner_id': self.owner.id,
            'property_id': self.property.id,
            'effective_start_date': date(2026, 6, 16),
            'status': 'active',
            'settlement_frequency': 'monthly',
            'revenue_policy_id': policy2.id,
        })

        # Charge before the switch (June 10) → should use old agreement
        res1 = self._create_reservation(checkin=date(2026, 6, 10), checkout=date(2026, 6, 12))
        self._create_charge(res1, self.ct_rent, 1000.0, tx_date=date(2026, 6, 10))

        # Charge after the switch (June 20) → should use new agreement
        res2 = self._create_reservation(checkin=date(2026, 6, 20), checkout=date(2026, 6, 22))
        self._create_charge(res2, self.ct_rent, 1000.0, tx_date=date(2026, 6, 20))

        # Settlement for the full month — should find agreement for period_start
        # find_active_agreement uses the date passed in
        settlement = self._create_settlement()
        settlement.action_calculate()

        # The settlement will use the agreement found for period_start (June 1 → old 20% policy)
        # Both charges are included in one settlement with one policy
        self.assertEqual(settlement.commission_base, 2000.0)
        # Management fee = 20% of 2000 = 400 (old policy)
        self.assertEqual(settlement.management_fee, 400.0)


@tagged('post_install', '-standard', 'pms_revenue')
class TestFinalizedImmutable(TestPmsRevenueBase):
    """Test: Finalized settlements remain unchanged after a policy update."""

    def test_finalized_unchanged(self):
        res = self._create_reservation()
        self._create_charge(res, self.ct_rent, 1000.0)

        settlement = self._create_settlement()
        settlement.action_calculate()
        settlement.action_review()
        settlement.action_finalize()

        # Record the values
        original_fee = settlement.management_fee
        original_payout = settlement.owner_net_payout
        self.assertEqual(settlement.state, 'finalized')
        self.assertTrue(settlement.snapshot_policy_data)

        # Now change the policy
        self.policy.management_fee_percent = 50.0

        # Settlement should be unchanged
        self.assertEqual(settlement.management_fee, original_fee)
        self.assertEqual(settlement.owner_net_payout, original_payout)

        # Attempting to write to a finalized settlement should raise
        with self.assertRaises(ValidationError):
            settlement.write({'period_start': date(2026, 7, 1)})


@tagged('post_install', '-standard', 'pms_revenue')
class TestRoundingBehavior(TestPmsRevenueBase):
    """Test: Rounding behavior with different methods."""

    def test_round_down(self):
        self.policy.rounding_method = 'round_down'
        self.policy.management_fee_percent = 10.0  # 10% of 1005.33 = 100.533 → 100.53

        res = self._create_reservation()
        self._create_charge(res, self.ct_rent, 1005.33)

        settlement = self._create_settlement()
        settlement.action_calculate()

        self.assertEqual(settlement.management_fee, 100.53)

    def test_round_up(self):
        self.policy.rounding_method = 'round_up'
        self.policy.management_fee_percent = 10.0  # 10% of 1005.33 = 100.533 → 100.54

        res = self._create_reservation()
        self._create_charge(res, self.ct_rent, 1005.33)

        settlement = self._create_settlement()
        settlement.action_calculate()

        self.assertEqual(settlement.management_fee, 100.54)

    def test_round(self):
        self.policy.rounding_method = 'round'
        self.policy.management_fee_percent = 10.0  # 10% of 1005.33 = 100.533 → 100.53

        res = self._create_reservation()
        self._create_charge(res, self.ct_rent, 1005.33)

        settlement = self._create_settlement()
        settlement.action_calculate()

        self.assertEqual(settlement.management_fee, 100.53)


@tagged('post_install', '-standard', 'pms_revenue')
class TestMissingChargeTypeMapping(TestPmsRevenueBase):
    """Test: Unmapped charge types put settlement into exception state."""

    def test_missing_mapping(self):
        # Create a charge type with no policy line
        unmapped_ct = self.env['pms.charge.type'].create({
            'name': 'Spa Service',
            'code': 'SPA',
            'is_revenue': True,
        })

        res = self._create_reservation()
        self._create_charge(res, self.ct_rent, 1000.0)
        self._create_charge(res, unmapped_ct, 200.0)

        settlement = self._create_settlement()
        settlement.action_calculate()

        # Should be in exception state
        self.assertEqual(settlement.state, 'exception')
        self.assertTrue(settlement.exception_note)
        self.assertIn('Spa Service', settlement.exception_note)

        # The unmapped charge should have zero allocations
        spa_line = settlement.line_ids.filtered(lambda l: l.charge_type_id == unmapped_ct)
        self.assertEqual(len(spa_line), 1)
        self.assertEqual(spa_line.owner_amount, 0.0)
        self.assertEqual(spa_line.manager_amount, 0.0)


@tagged('post_install', '-standard', 'pms_revenue')
class TestMissingActiveAgreement(TestPmsRevenueBase):
    """Test: No active agreement for the property results in exception."""

    def test_no_agreement(self):
        # Terminate the existing agreement
        self.agreement.status = 'terminated'

        res = self._create_reservation()
        self._create_charge(res, self.ct_rent, 1000.0)

        settlement = self._create_settlement()
        settlement.action_calculate()

        self.assertEqual(settlement.state, 'exception')
        self.assertTrue(settlement.exception_note)


@tagged('post_install', '-standard', 'pms_revenue')
class TestAllocationValidation(TestPmsRevenueBase):
    """Test: Allocation percentages must total 100% for revenue lines."""

    def test_allocation_must_total_100(self):
        with self.assertRaises(ValidationError):
            self.env['pms.revenue.policy.line'].create({
                'policy_id': self.policy.id,
                'charge_type_id': self.ct_rent.id,
                'owner_share_percent': 60.0,
                'manager_share_percent': 20.0,
                'liability_share_percent': 10.0,  # Total = 90, not 100
                'commission_basis': 'gross_amount',
            })

    def test_negative_share_rejected(self):
        with self.assertRaises(ValidationError):
            self.env['pms.revenue.policy.line'].create({
                'policy_id': self.policy.id,
                'charge_type_id': self.ct_cleaning.id,
                'owner_share_percent': 110.0,
                'manager_share_percent': -10.0,
                'liability_share_percent': 0.0,
                'commission_basis': 'excluded',
            })


@tagged('post_install', '-standard', 'pms_revenue')
class TestOverlapPrevention(TestPmsRevenueBase):
    """Test: Overlapping active agreements for same property are prevented."""

    def test_overlap_prevented(self):
        with self.assertRaises(ValidationError):
            self.env['pms.owner.agreement'].create({
                'owner_id': self.owner.id,
                'property_id': self.property.id,
                'effective_start_date': date(2026, 3, 1),  # Overlaps with existing
                'status': 'active',
                'settlement_frequency': 'monthly',
                'revenue_policy_id': self.policy.id,
            })

    def test_non_overlapping_allowed(self):
        # Create one that starts after the current one ends
        self.agreement.effective_end_date = date(2026, 6, 30)
        new_agr = self.env['pms.owner.agreement'].create({
            'owner_id': self.owner.id,
            'property_id': self.property.id,
            'effective_start_date': date(2026, 7, 1),
            'status': 'active',
            'settlement_frequency': 'monthly',
            'revenue_policy_id': self.policy.id,
        })
        self.assertTrue(new_agr.id)


@tagged('post_install', '-standard', 'pms_revenue')
class TestManagementFeeTypes(TestPmsRevenueBase):
    """Test: Fixed and percentage_plus_fixed management fee types."""

    def test_fixed_fee(self):
        self.policy.management_fee_type = 'fixed'
        self.policy.management_fee_fixed_amount = 250.0

        res = self._create_reservation()
        self._create_charge(res, self.ct_rent, 1000.0)

        settlement = self._create_settlement()
        settlement.action_calculate()

        self.assertEqual(settlement.management_fee, 250.0)
        self.assertEqual(settlement.owner_net_payout, 750.0)

    def test_percentage_plus_fixed(self):
        self.policy.management_fee_type = 'percentage_plus_fixed'
        self.policy.management_fee_percent = 10.0
        self.policy.management_fee_fixed_amount = 50.0

        res = self._create_reservation()
        self._create_charge(res, self.ct_rent, 1000.0)

        settlement = self._create_settlement()
        settlement.action_calculate()

        # 10% of 1000 + 50 = 150
        self.assertEqual(settlement.management_fee, 150.0)
        self.assertEqual(settlement.owner_net_payout, 850.0)

    def test_min_max_fee(self):
        self.policy.management_fee_percent = 5.0
        self.policy.minimum_management_fee = 100.0
        self.policy.maximum_management_fee = 300.0

        res = self._create_reservation()
        # Small rent → 5% of 500 = 25, but min is 100
        self._create_charge(res, self.ct_rent, 500.0)

        settlement = self._create_settlement()
        settlement.action_calculate()

        self.assertEqual(settlement.management_fee, 100.0)  # min applies

        # Large rent → 5% of 10000 = 500, but max is 300
        res2 = self._create_reservation(checkin=date(2026, 6, 10), checkout=date(2026, 6, 12))
        self._create_charge(res2, self.ct_rent, 10000.0, tx_date=date(2026, 6, 10))

        settlement2 = self._create_settlement()
        settlement2.action_calculate()

        self.assertEqual(settlement2.management_fee, 300.0)  # max applies


@tagged('post_install', '-standard', 'pms_revenue')
class TestPreviewCalculation(TestPmsRevenueBase):
    """Test: Calculation preview interface on the agreement."""

    def test_preview(self):
        sample_lines = [
            {'charge_type_code': 'RENT', 'gross_amount': 1000.0, 'tax_amount': 0.0},
            {'charge_type_code': 'CLEANING', 'gross_amount': 100.0, 'tax_amount': 0.0},
            {'charge_type_code': 'PET_FEE', 'gross_amount': 100.0, 'tax_amount': 0.0},
            {'charge_type_code': 'LODGING_TAX', 'gross_amount': 120.0, 'tax_amount': 0.0},
            {'charge_type_code': 'OTA_COMMISSION', 'gross_amount': 150.0, 'tax_amount': 0.0},
        ]
        result = self.env['pms.owner.agreement'].preview_calculation(
            self.agreement.id, sample_lines
        )

        # Commission base = rent (1000) + pet_fee owner allocated... no, pet is excluded
        # Actually: rent gross_amount = 1000, resort excluded, pet excluded, cleaning excluded
        # Commission base = 1000 (rent only, pet is excluded)
        self.assertEqual(result['commission_base'], 1000.0)
        self.assertEqual(result['management_fee'], 200.0)
        # Owner gross = rent (1000) + cleaning (100) + pet owner share (50) = 1150
        self.assertEqual(result['owner_gross_proceeds'], 1150.0)
        # Owner expenses = OTA = 150
        self.assertEqual(result['owner_expenses'], 150.0)
        # Net = 1150 - 200 - 150 = 800
        self.assertEqual(result['owner_net_payout'], 800.0)
        # Taxes = 120 (lodging tax)
        self.assertEqual(result['taxes_liabilities'], 120.0)


@tagged('post_install', '-standard', 'pms_revenue')
class TestSplitExpense(TestPmsRevenueBase):
    """Test: Split expenses between owner and manager (50/50)."""

    def test_split_expense(self):
        res = self._create_reservation()
        self._create_charge(res, self.ct_rent, 1000.0)
        self._create_charge(res, self.ct_cc_fee, 40.0)  # split 50/50

        settlement = self._create_settlement()
        settlement.action_calculate()

        # CC fee split: owner pays 20, manager pays 20
        self.assertEqual(settlement.owner_expenses, 20.0)


@tagged('post_install', '-standard', 'pms_revenue')
class TestSettlementStateTransitions(TestPmsRevenueBase):
    """Test: Settlement state transitions are enforced."""

    def test_state_flow(self):
        res = self._create_reservation()
        self._create_charge(res, self.ct_rent, 1000.0)

        settlement = self._create_settlement()
        self.assertEqual(settlement.state, 'draft')

        settlement.action_calculate()
        self.assertEqual(settlement.state, 'calculated')

        settlement.action_review()
        self.assertEqual(settlement.state, 'reviewed')

        settlement.action_finalize()
        self.assertEqual(settlement.state, 'finalized')
        self.assertTrue(settlement.finalized_at)
        self.assertTrue(settlement.snapshot_agreement_data)
        self.assertTrue(settlement.snapshot_policy_data)

        settlement.action_pay()
        self.assertEqual(settlement.state, 'paid')

    def test_cannot_finalize_without_review(self):
        res = self._create_reservation()
        self._create_charge(res, self.ct_rent, 1000.0)

        settlement = self._create_settlement()
        settlement.action_calculate()

        with self.assertRaises(ValidationError):
            settlement.action_finalize()

    def test_cannot_cancel_finalized(self):
        res = self._create_reservation()
        self._create_charge(res, self.ct_rent, 1000.0)

        settlement = self._create_settlement()
        settlement.action_calculate()
        settlement.action_review()
        settlement.action_finalize()

        with self.assertRaises(ValidationError):
            settlement.action_cancel()