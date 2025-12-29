-- Add socio_id FK columns to existing tables
-- This is needed because migration 0004 was faked

-- Add socio_id to projetos table
ALTER TABLE projetos
ADD COLUMN IF NOT EXISTS socio_id VARCHAR(2) REFERENCES core_socio(codigo) ON DELETE RESTRICT;

-- Add socio_codigo to boletins table (if not exists)
ALTER TABLE boletins
ADD COLUMN IF NOT EXISTS socio_codigo VARCHAR(2) DEFAULT 'BA' NOT NULL;

-- Add socio_id to boletins table
ALTER TABLE boletins
ADD COLUMN IF NOT EXISTS socio_id VARCHAR(2) REFERENCES core_socio(codigo) ON DELETE RESTRICT;

-- Add socio_id to orcamentos table
ALTER TABLE orcamentos
ADD COLUMN IF NOT EXISTS socio_id VARCHAR(2) REFERENCES core_socio(codigo) ON DELETE RESTRICT;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS projetos_socio_id_idx ON projetos(socio_id);
CREATE INDEX IF NOT EXISTS boletins_socio_id_idx ON boletins(socio_id);
CREATE INDEX IF NOT EXISTS orcamentos_socio_id_idx ON orcamentos(socio_id);

SELECT 'Colunas FK adicionadas com sucesso!' AS status;
