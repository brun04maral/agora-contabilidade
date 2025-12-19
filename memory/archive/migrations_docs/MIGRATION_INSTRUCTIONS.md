# Instruções de Migração - Estado ATIVO → PENDENTE

## Problema
Após o último pull, a aplicação apresenta o erro:
```
LookupError: 'ATIVO' is not among the defined enum values. Enum name: estadodespesa. Possible values: PENDENTE, VENCIDO, PAGO
```

## Causa
O código foi atualizado para usar o estado `PENDENTE` em vez de `ATIVO`, mas a base de dados ainda contém registos antigos com o valor `ATIVO`.

## Solução
Execute o script de migração **antes** de iniciar a aplicação:

```bash
python3 database/migrations/005_rename_ativo_to_pendente.py
```

## O que o script faz
- Atualiza todos os registos de despesas com estado `ATIVO` para `PENDENTE`
- Mostra quantas despesas foram atualizadas
- Não afeta despesas com outros estados (VENCIDO, PAGO)

## Após a migração
Pode iniciar a aplicação normalmente:
```bash
python3 main.py
```

## Notas
- A migração é segura e pode ser executada múltiplas vezes
- Apenas despesas com estado `ATIVO` são afetadas
- A cor amarelo pastel mantém-se para o novo estado `PENDENTE`
