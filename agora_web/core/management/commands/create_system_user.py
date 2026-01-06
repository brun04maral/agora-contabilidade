# -*- coding: utf-8 -*-
"""
Comando para criar user "Sistema" para importações automáticas
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Cria ou atualiza o user "Sistema" para importações automáticas de Excel'

    def handle(self, *args, **options):
        username = 'sistema'
        email = 'sistema@agoramediaproduction.pt'
        first_name = 'Sistema'
        last_name = 'Importação'

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_staff': False,
                'is_active': True,
                'is_superuser': False,
            }
        )

        if created:
            # Define password impossível de usar (user não pode fazer login)
            user.set_unusable_password()
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'✅ User "{username}" criado com sucesso!')
            )
        else:
            # Atualiza dados caso já exista
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.set_unusable_password()
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'✅ User "{username}" atualizado!')
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nUser ID: {user.id}\n'
                f'Username: {user.username}\n'
                f'Nome completo: {user.get_full_name()}\n'
                f'Email: {user.email}\n'
                f'\nEste user será usado para marcar objetos criados via importação de Excel.'
            )
        )
