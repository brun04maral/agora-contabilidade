import { List, useTable, EditButton, DeleteButton } from "@refinedev/antd";
import { Table, Space, Tag } from "antd";

export const ProjetoList: React.FC = () => {
  const { tableProps } = useTable({
    resource: "projetos",
    syncWithLocation: true,
  });

  return (
    <List>
      <Table {...tableProps} rowKey="id">
        <Table.Column dataIndex="numero" title="Número" />
        <Table.Column dataIndex="nome" title="Nome" />
        <Table.Column
          dataIndex="tipo"
          title="Tipo"
          render={(value) => (
            <Tag color={value === "EMPRESA" ? "blue" : "green"}>{value}</Tag>
          )}
        />
        <Table.Column
          dataIndex="estado"
          title="Estado"
          render={(value) => {
            const colors: Record<string, string> = {
              ORCAMENTO: "default",
              EM_CURSO: "processing",
              CONCLUIDO: "success",
              FATURADO: "warning",
              RECEBIDO: "green",
              ANULADO: "error",
            };
            return <Tag color={colors[value] || "default"}>{value}</Tag>;
          }}
        />
        <Table.Column
          dataIndex="valor_total"
          title="Valor"
          render={(value) => `€${parseFloat(value).toFixed(2)}`}
        />
        <Table.Column
          dataIndex="data_inicio"
          title="Data Início"
        />
        <Table.Column
          title="Ações"
          dataIndex="actions"
          render={(_, record: any) => (
            <Space>
              <EditButton hideText size="small" recordItemId={record.id} />
              <DeleteButton hideText size="small" recordItemId={record.id} />
            </Space>
          )}
        />
      </Table>
    </List>
  );
};
