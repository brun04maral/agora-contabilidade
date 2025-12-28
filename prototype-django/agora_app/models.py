"""
Models para Agora Contabilidade
Baseado nos models SQLAlchemy existentes
"""
from django.db import models
from decimal import Decimal


class Socio(models.Model):
    """Sócio da empresa (BA ou RR)"""
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    email = models.EmailField(verbose_name="Email")
    telefone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    nif = models.CharField(max_length=9, blank=True, verbose_name="NIF")
    iban = models.CharField(max_length=34, blank=True, verbose_name="IBAN")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sócio"
        verbose_name_plural = "Sócios"
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def calcular_saldo(self):
        """Calcula saldo do sócio (IN - OUT)"""
        # INs: Projetos pessoais + Prémios
        ins = Decimal('0.00')
        outs = Decimal('0.00')

        # Projetos pessoais RECEBIDOS
        projetos_pessoais = self.projetos_owner.filter(
            estado='RECEBIDO'
        )
        ins += sum([p.valor_total for p in projetos_pessoais], Decimal('0.00'))

        # Prémios de projetos da empresa
        premios_bruno = Projeto.objects.filter(estado='RECEBIDO').aggregate(
            total=models.Sum('premio_bruno')
        )['total'] or Decimal('0.00')

        premios_rafael = Projeto.objects.filter(estado='RECEBIDO').aggregate(
            total=models.Sum('premio_rafael')
        )['total'] or Decimal('0.00')

        if self.nome == 'BA':
            ins += premios_bruno
        elif self.nome == 'RR':
            ins += premios_rafael

        # OUTs: Despesas fixas (÷2) + Despesas pessoais
        despesas_fixas = Despesa.objects.filter(
            tipo='FIXA_MENSAL',
            estado='PAGO'
        ).aggregate(total=models.Sum('valor'))['total'] or Decimal('0.00')
        outs += despesas_fixas / 2

        despesas_pessoais = self.despesas_socio.filter(
            estado='PAGO'
        ).exclude(tipo='FIXA_MENSAL').aggregate(
            total=models.Sum('valor')
        )['total'] or Decimal('0.00')
        outs += despesas_pessoais

        return ins - outs


class Cliente(models.Model):
    """Cliente da empresa"""
    nome = models.CharField(max_length=200, verbose_name="Nome")
    nif = models.CharField(max_length=9, blank=True, verbose_name="NIF")
    email = models.EmailField(blank=True, verbose_name="Email")
    telefone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    morada = models.TextField(blank=True, verbose_name="Morada")
    notas = models.TextField(blank=True, verbose_name="Notas")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Fornecedor(models.Model):
    """Fornecedor da empresa"""
    nome = models.CharField(max_length=200, verbose_name="Nome")
    nif = models.CharField(max_length=9, blank=True, verbose_name="NIF")
    email = models.EmailField(blank=True, verbose_name="Email")
    telefone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    morada = models.TextField(blank=True, verbose_name="Morada")
    iban = models.CharField(max_length=34, blank=True, verbose_name="IBAN")
    notas = models.TextField(blank=True, verbose_name="Notas")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Projeto(models.Model):
    """Projeto da empresa"""
    TIPO_CHOICES = [
        ('EMPRESA', 'Empresa'),
        ('PESSOAL_BRUNO', 'Pessoal Bruno'),
        ('PESSOAL_RAFAEL', 'Pessoal Rafael'),
    ]

    ESTADO_CHOICES = [
        ('ORCAMENTO', 'Orçamento'),
        ('EM_CURSO', 'Em Curso'),
        ('CONCLUIDO', 'Concluído'),
        ('FATURADO', 'Faturado'),
        ('RECEBIDO', 'Recebido'),
        ('ANULADO', 'Anulado'),
    ]

    numero = models.CharField(max_length=20, unique=True, verbose_name="Número")
    nome = models.CharField(max_length=200, verbose_name="Nome")
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='projetos',
        verbose_name="Cliente"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ORCAMENTO', verbose_name="Estado")

    valor_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Total")
    premio_bruno = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prémio Bruno")
    premio_rafael = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prémio Rafael")

    data_inicio = models.DateField(verbose_name="Data Início")
    data_entrega = models.DateField(null=True, blank=True, verbose_name="Data Entrega")
    data_pagamento = models.DateField(null=True, blank=True, verbose_name="Data Pagamento")

    descricao = models.TextField(blank=True, verbose_name="Descrição")
    notas = models.TextField(blank=True, verbose_name="Notas")

    owner = models.ForeignKey(
        Socio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projetos_owner',
        verbose_name="Responsável"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Projeto"
        verbose_name_plural = "Projetos"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.numero} - {self.nome}"


class Despesa(models.Model):
    """Despesa da empresa"""
    TIPO_CHOICES = [
        ('FIXA_MENSAL', 'Fixa Mensal'),
        ('PESSOAL_BRUNO', 'Pessoal Bruno'),
        ('PESSOAL_RAFAEL', 'Pessoal Rafael'),
        ('EQUIPAMENTO', 'Equipamento'),
        ('PROJETO', 'Projeto'),
    ]

    ESTADO_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('CANCELADO', 'Cancelado'),
    ]

    numero = models.CharField(max_length=20, unique=True, verbose_name="Número")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo")
    descricao = models.CharField(max_length=200, verbose_name="Descrição")

    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='despesas',
        verbose_name="Fornecedor"
    )

    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="IVA")

    data_despesa = models.DateField(verbose_name="Data Despesa")
    data_pagamento = models.DateField(null=True, blank=True, verbose_name="Data Pagamento")

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDENTE', verbose_name="Estado")

    socio = models.ForeignKey(
        Socio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='despesas_socio',
        verbose_name="Sócio"
    )

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='despesas',
        verbose_name="Projeto"
    )

    notas = models.TextField(blank=True, verbose_name="Notas")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Despesa"
        verbose_name_plural = "Despesas"
        ordering = ['-data_despesa']

    def __str__(self):
        return f"{self.numero} - {self.descricao}"
