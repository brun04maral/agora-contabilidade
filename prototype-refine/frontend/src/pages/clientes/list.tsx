import { List, useTable, EditButton, DeleteButton } from "@refinedev/antd";
import { Table, Space } from "antd";

export const ClienteList: React.FC = () => {
  const { tableProps } = useTable({
    resource: "clientes",
    syncWithLocation: true,
  });

  return (
    <List>
      <Table {...tableProps} rowKey="id">
        <Table.Column dataIndex="nome" title="Nome" />
        <Table.Column dataIndex="nif" title="NIF" />
        <Table.Column dataIndex="email" title="Email" />
        <Table.Column dataIndex="telefone" title="Telefone" />
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
