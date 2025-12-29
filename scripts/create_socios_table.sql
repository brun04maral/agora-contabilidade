-- Create core_socio table manually
-- This is needed because migration 0004 was faked but socios table is new

CREATE TABLE IF NOT EXISTS core_socio (
    codigo VARCHAR(2) PRIMARY KEY,
    nome_completo VARCHAR(100) NOT NULL,
    nome_curto VARCHAR(50) NOT NULL,
    email VARCHAR(254) NOT NULL,
    telefone VARCHAR(50) DEFAULT '' NOT NULL,
    percentagem_participacao NUMERIC(5,2) DEFAULT 50.00 NOT NULL,
    ativo BOOLEAN DEFAULT true NOT NULL,
    cor_tema VARCHAR(7) DEFAULT '#1976d2',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create index on email (typically created by Django)
CREATE INDEX IF NOT EXISTS core_socio_email_idx ON core_socio(email);

SELECT 'Tabela core_socio criada com sucesso!' AS status;
