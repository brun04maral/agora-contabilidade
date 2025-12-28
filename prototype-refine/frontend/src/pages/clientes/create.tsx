import { Create, useForm } from "@refinedev/antd";
import { Form, Input } from "antd";

export const ClienteCreate: React.FC = () => {
  const { formProps, saveButtonProps } = useForm();

  return (
    <Create saveButtonProps={saveButtonProps}>
      <Form {...formProps} layout="vertical">
        <Form.Item label="Nome" name="nome" rules={[{ required: true }]}>
          <Input />
        </Form.Item>

        <Form.Item label="NIF" name="nif">
          <Input maxLength={9} />
        </Form.Item>

        <Form.Item label="Email" name="email" rules={[{ type: "email" }]}>
          <Input />
        </Form.Item>

        <Form.Item label="Telefone" name="telefone">
          <Input />
        </Form.Item>

        <Form.Item label="Morada" name="morada">
          <Input.TextArea rows={3} />
        </Form.Item>

        <Form.Item label="Notas" name="notas">
          <Input.TextArea rows={3} />
        </Form.Item>
      </Form>
    </Create>
  );
};
