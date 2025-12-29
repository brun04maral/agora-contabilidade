import { Create, useForm, useSelect } from "@refinedev/antd";
import { Form, Input, Select, InputNumber, DatePicker } from "antd";

export const ProjetoCreate: React.FC = () => {
  const { formProps, saveButtonProps } = useForm();

  const { selectProps: clienteSelectProps } = useSelect({
    resource: "clientes",
    optionLabel: "nome",
    optionValue: "id",
  });

  return (
    <Create saveButtonProps={saveButtonProps}>
      <Form {...formProps} layout="vertical">
        <Form.Item
          label="Número"
          name="numero"
          rules={[{ required: true }]}
        >
          <Input />
        </Form.Item>

        <Form.Item
          label="Nome"
          name="nome"
          rules={[{ required: true }]}
        >
          <Input />
        </Form.Item>

        <Form.Item
          label="Cliente"
          name="cliente_id"
          rules={[{ required: true }]}
        >
          <Select {...clienteSelectProps} />
        </Form.Item>

        <Form.Item
          label="Tipo"
          name="tipo"
          rules={[{ required: true }]}
        >
          <Select>
            <Select.Option value="EMPRESA">Empresa</Select.Option>
            <Select.Option value="PESSOAL_BRUNO">Pessoal Bruno</Select.Option>
            <Select.Option value="PESSOAL_RAFAEL">Pessoal Rafael</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item
          label="Estado"
          name="estado"
          initialValue="ORCAMENTO"
        >
          <Select>
            <Select.Option value="ORCAMENTO">Orçamento</Select.Option>
            <Select.Option value="EM_CURSO">Em Curso</Select.Option>
            <Select.Option value="CONCLUIDO">Concluído</Select.Option>
            <Select.Option value="FATURADO">Faturado</Select.Option>
            <Select.Option value="RECEBIDO">Recebido</Select.Option>
            <Select.Option value="ANULADO">Anulado</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item
          label="Valor Total (€)"
          name="valor_total"
          rules={[{ required: true }]}
        >
          <InputNumber style={{ width: "100%" }} min={0} precision={2} />
        </Form.Item>

        <Form.Item
          label="Prémio Bruno (€)"
          name="premio_bruno"
          initialValue={0}
        >
          <InputNumber style={{ width: "100%" }} min={0} precision={2} />
        </Form.Item>

        <Form.Item
          label="Prémio Rafael (€)"
          name="premio_rafael"
          initialValue={0}
        >
          <InputNumber style={{ width: "100%" }} min={0} precision={2} />
        </Form.Item>

        <Form.Item
          label="Data Início"
          name="data_inicio"
          rules={[{ required: true }]}
          getValueProps={(value) => ({ value: value ? dayjs(value) : undefined })}
        >
          <DatePicker style={{ width: "100%" }} format="YYYY-MM-DD" />
        </Form.Item>

        <Form.Item label="Descrição" name="descricao">
          <Input.TextArea rows={4} />
        </Form.Item>
      </Form>
    </Create>
  );
};

// Helper import (add dayjs)
import dayjs from "dayjs";
