from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from decimal import Decimal
from ehr.models import Admission, AdmissionCharge, Paypoint
from django.db import transaction

class Command(BaseCommand):
    help = 'Generate daily admission charges for patients'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            help='Generate charges for a specific date (YYYY-MM-DD)',
            required=False
        )

    def handle(self, *args, **options):
        if options['date']:
            try:
                charge_date = date.fromisoformat(options['date'])
            except ValueError:
                self.stderr.write(self.style.ERROR('Invalid date format. Use YYYY-MM-DD'))
                return
        else:
            charge_date = date.today()

        self.stdout.write(f'Generating charges for {charge_date}')

        active_admissions = Admission.objects.filter(
            status='RECEIVED'
        ).select_related('ward', 'patient')

        for admission in active_admissions:
            try:
                charge_exists = AdmissionCharge.objects.filter(
                    admission=admission,
                    charge_date=charge_date
                ).exists()

                if not charge_exists:
                    paypoint = Paypoint.objects.create(
                        patient=admission.patient,
                        service=f"Ward Stay - {admission.ward.name}",
                        unit='admission',
                        price=admission.ward.daily_rate,
                        status=False,
                        payment_method='WALLET'
                    )

                    AdmissionCharge.objects.create(
                        admission=admission,
                        paypoint=paypoint,
                        charge_date=charge_date,
                        amount=admission.ward.daily_rate,
                        is_processed=False
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created charge for patient {admission.patient}'
                        )
                    )

            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f'Error processing admission {admission.id}: {str(e)}'
                    )
                )