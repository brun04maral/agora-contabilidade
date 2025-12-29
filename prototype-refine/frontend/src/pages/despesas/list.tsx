import { List, useTable, EditButton, DeleteButton } from "@refinedev/antd";
import { Table, Space, Tag } from "antd";

export const DespesaList: React.FC = () => {
  const { tableProps } = useTable({
    resource: "despesas",
    syncWithLocation: true,
  });

  return (
    <List>
      <Table {...tableProps} rowKey="id">
        <Table.Column dataIndex="numero" title="Número" />
        <Table.Column dataIndex="descricao" title="Descrição" />
        <Table.Column
          dataIndex="tipo"
          title="Tipo"
          render={(value) => <Tag>{value}</Tag>}
        />
        <Table.Column
          dataIndex="valor"
          title="Valor"
          render={(value) => `€${parseFloat(value).toFixed(2)}`}
        />
        <Table.Column
          dataIndex="estado"
          title="Estado"
          render={(value) => {
            const colors: Record<string, string> = {
              PENDENTE: "warning",
              PAGO: "success",
              CANCELADO: "error",
            };
            return <Tag color={colors[value] || "default"}>{value}</Tag>;
          }}
        />
        <Table.Column dataIndex="data_despesa" title="Data" />
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
