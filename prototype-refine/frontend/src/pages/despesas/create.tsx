import { Create, useForm } from "@refinedev/antd";
import { Form, Input, Select, InputNumber, DatePicker } from "antd";

export const DespesaCreate: React.FC = () => {
  const { formProps, saveButtonProps } = useForm();

  return (
    <Create saveButtonProps={saveButtonProps}>
      <Form {...formProps} layout="vertical">
        <Form.Item label="Número" name="numero" rules={[{ required: true }]}>
          <Input />
        </Form.Item>

        <Form.Item label="Descrição" name="descricao" rules={[{ required: true }]}>
          <Input />
        </Form.Item>

        <Form.Item label="Tipo" name="tipo" rules={[{ required: true }]}>
          <Select>
            <Select.Option value="FIXA_MENSAL">Fixa Mensal</Select.Option>
            <Select.Option value="PESSOAL_BRUNO">Pessoal Bruno</Select.Option>
            <Select.Option value="PESSOAL_RAFAEL">Pessoal Rafael</Select.Option>
            <Select.Option value="EQUIPAMENTO">Equipamento</Select.Option>
            <Select.Option value="PROJETO">Projeto</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item label="Valor (€)" name="valor" rules={[{ required: true }]}>
          <InputNumber style={{ width: "100%" }} min={0} precision={2} />
        </Form.Item>

        <Form.Item label="IVA (€)" name="iva" initialValue={0}>
          <InputNumber style={{ width: "100%" }} min={0} precision={2} />
        </Form.Item>

        <Form.Item label="Estado" name="estado" initialValue="PENDENTE">
          <Select>
            <Select.Option value="PENDENTE">Pendente</Select.Option>
            <Select.Option value="PAGO">Pago</Select.Option>
            <Select.Option value="CANCELADO">Cancelado</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item label="Data Despesa" name="data_despesa" rules={[{ required: true }]}>
          <DatePicker style={{ width: "100%" }} format="YYYY-MM-DD" />
        </Form.Item>

        <Form.Item label="Notas" name="notas">
          <Input.TextArea rows={3} />
        </Form.Item>
      </Form>
    </Create>
  );
};
