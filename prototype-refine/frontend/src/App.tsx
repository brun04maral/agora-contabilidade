import { Refine } from "@refinedev/core";
import { RefineKbar, RefineKbarProvider } from "@refinedev/kbar";
import {
  ErrorComponent,
  ThemedLayoutV2,
  ThemedSiderV2,
  useNotificationProvider,
} from "@refinedev/antd";
import routerBindings, {
  DocumentTitleHandler,
  NavigateToResource,
  UnsavedChangesNotifier,
} from "@refinedev/react-router-v6";
import dataProvider from "@refinedev/simple-rest";
import { BrowserRouter, Outlet, Route, Routes } from "react-router-dom";
import { App as AntdApp, ConfigProvider } from "antd";
import pt_PT from "antd/locale/pt_PT";

// Pages
import { ProjetoList, ProjetoCreate, ProjetoEdit } from "./pages/projetos";
import { DespesaList, DespesaCreate, DespesaEdit } from "./pages/despesas";
import { ClienteList, ClienteCreate, ClienteEdit } from "./pages/clientes";
import { Dashboard } from "./pages/dashboard";

// Styles
import "@refinedev/antd/dist/reset.css";

function App() {
  return (
    <BrowserRouter>
      <ConfigProvider locale={pt_PT}>
        <AntdApp>
          <RefineKbarProvider>
            <Refine
              dataProvider={dataProvider("http://localhost:8000/api")}
              notificationProvider={useNotificationProvider}
              routerProvider={routerBindings}
              resources={[
                {
                  name: "projetos",
                  list: "/projetos",
                  create: "/projetos/create",
                  edit: "/projetos/edit/:id",
                  meta: {
                    label: "Projetos",
                    icon: "🎬",
                  },
                },
                {
                  name: "despesas",
                  list: "/despesas",
                  create: "/despesas/create",
                  edit: "/despesas/edit/:id",
                  meta: {
                    label: "Despesas",
                    icon: "💳",
                  },
                },
                {
                  name: "clientes",
                  list: "/clientes",
                  create: "/clientes/create",
                  edit: "/clientes/edit/:id",
                  meta: {
                    label: "Clientes",
                    icon: "👥",
                  },
                },
              ]}
              options={{
                syncWithLocation: true,
                warnWhenUnsavedChanges: true,
                projectId: "agora-contabilidade",
              }}
            >
              <Routes>
                <Route
                  element={
                    <ThemedLayoutV2
                      Sider={() => <ThemedSiderV2 Title={() => <h2>💰 Agora</h2>} />}
                    >
                      <Outlet />
                    </ThemedLayoutV2>
                  }
                >
                  <Route index element={<Dashboard />} />
                  <Route path="/projetos">
                    <Route index element={<ProjetoList />} />
                    <Route path="create" element={<ProjetoCreate />} />
                    <Route path="edit/:id" element={<ProjetoEdit />} />
                  </Route>
                  <Route path="/despesas">
                    <Route index element={<DespesaList />} />
                    <Route path="create" element={<DespesaCreate />} />
                    <Route path="edit/:id" element={<DespesaEdit />} />
                  </Route>
                  <Route path="/clientes">
                    <Route index element={<ClienteList />} />
                    <Route path="create" element={<ClienteCreate />} />
                    <Route path="edit/:id" element={<ClienteEdit />} />
                  </Route>
                  <Route path="*" element={<ErrorComponent />} />
                </Route>
              </Routes>

              <RefineKbar />
              <UnsavedChangesNotifier />
              <DocumentTitleHandler />
            </Refine>
          </RefineKbarProvider>
        </AntdApp>
      </ConfigProvider>
    </BrowserRouter>
  );
}

export default App;
