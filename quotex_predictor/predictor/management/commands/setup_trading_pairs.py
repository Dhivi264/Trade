from django.core.management.base import BaseCommand
from predictor.models import TradingPair


class Command(BaseCommand):
    help = 'Setup initial trading pairs'

    def handle(self, *args, **options):
        trading_pairs = [
            # Currency Pairs from Quotex OTC (as shown in image)
            {'symbol': 'NZDJPY_OTC', 'name': 'NZD/JPY (OTC)'},
            {'symbol': 'AUDCAD_OTC', 'name': 'AUD/CAD (OTC)'},
            {'symbol': 'AUDUSD_OTC', 'name': 'AUD/USD (OTC)'},
            {'symbol': 'EURCAD_OTC', 'name': 'EUR/CAD (OTC)'},
            {'symbol': 'USDBRL_OTC', 'name': 'USD/BRL (OTC)'},
            {'symbol': 'NZDCAD_OTC', 'name': 'NZD/CAD (OTC)'},
            {'symbol': 'USDPHP_OTC', 'name': 'USD/PHP (OTC)'},
            {'symbol': 'USDCOP_OTC', 'name': 'USD/COP (OTC)'},
            {'symbol': 'USDIDR_OTC', 'name': 'USD/IDR (OTC)'},
            {'symbol': 'EURGBP_OTC', 'name': 'EUR/GBP (OTC)'},
            {'symbol': 'GBPCHF_OTC', 'name': 'GBP/CHF (OTC)'},
            {'symbol': 'GBPNZD_OTC', 'name': 'GBP/NZD (OTC)'},
            
            # Additional popular OTC pairs for broader coverage
            {'symbol': 'EURUSD_OTC', 'name': 'EUR/USD (OTC)'},
            {'symbol': 'GBPUSD_OTC', 'name': 'GBP/USD (OTC)'},
            {'symbol': 'USDJPY_OTC', 'name': 'USD/JPY (OTC)'},
            {'symbol': 'USDCAD_OTC', 'name': 'USD/CAD (OTC)'},
            {'symbol': 'USDCHF_OTC', 'name': 'USD/CHF (OTC)'},
            {'symbol': 'EURJPY_OTC', 'name': 'EUR/JPY (OTC)'},
            {'symbol': 'GBPJPY_OTC', 'name': 'GBP/JPY (OTC)'},
            {'symbol': 'AUDNZD_OTC', 'name': 'AUD/NZD (OTC)'},
        ]

        for pair_data in trading_pairs:
            pair, created = TradingPair.objects.get_or_create(
                symbol=pair_data['symbol'],
                defaults={'name': pair_data['name'], 'is_active': True}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created trading pair: {pair.symbol}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Trading pair already exists: {pair.symbol}')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully setup trading pairs!')
        )