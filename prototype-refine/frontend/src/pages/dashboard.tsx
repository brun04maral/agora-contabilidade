import { Card, Col, Row, Statistic } from "antd";
import { useApiUrl, useCustom } from "@refinedev/core";

export const Dashboard: React.FC = () => {
  const API_URL = useApiUrl();

  // Fetch saldos
  const { data: saldosData } = useCustom({
    url: `${API_URL}/saldos`,
    method: "get",
  });

  const saldos = saldosData?.data?.saldos || {};

  return (
    <div style={{ padding: 24 }}>
      <h1>💰 Dashboard - Agora Contabilidade</h1>

      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={12}>
          <Card>
            <Statistic
              title="Saldo Bruno (BA)"
              value={saldos.BA?.saldo || 0}
              precision={2}
              prefix="€"
              valueStyle={{ color: (saldos.BA?.saldo || 0) >= 0 ? "#3f8600" : "#cf1322" }}
            />
            <p style={{ marginTop: 16, color: "#666" }}>
              {saldos.BA?.nome_completo || "Sócio Bruno"}
            </p>
          </Card>
        </Col>

        <Col span={12}>
          <Card>
            <Statistic
              title="Saldo Rafael (RR)"
              value={saldos.RR?.saldo || 0}
              precision={2}
              prefix="€"
              valueStyle={{ color: (saldos.RR?.saldo || 0) >= 0 ? "#3f8600" : "#cf1322" }}
            />
            <p style={{ marginTop: 16, color: "#666" }}>
              {saldos.RR?.nome_completo || "Sócio Rafael"}
            </p>
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="Projetos Ativos"
              value={0}
              suffix="projetos"
            />
          </Card>
        </Col>

        <Col span={8}>
          <Card>
            <Statistic
              title="Despesas Pendentes"
              value={0}
              suffix="despesas"
              valueStyle={{ color: "#faad14" }}
            />
          </Card>
        </Col>

        <Col span={8}>
          <Card>
            <Statistic
              title="Total Clientes"
              value={0}
              suffix="clientes"
            />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 24 }}>
        <h3>📊 Visão Geral</h3>
        <p>Dashboard com estatísticas e resumos financeiros.</p>
        <p><em>Features completas serão implementadas na versão final.</em></p>
      </Card>
    </div>
  );
};
