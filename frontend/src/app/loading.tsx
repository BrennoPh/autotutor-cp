export default function RootLoading() {
  // Retorna null para evitar desmontagem e layout shift da página atual durante navegações SPA.
  // O TopProgressBar exibe o feedback visual contínuo e imediato no topo da tela.
  return null;
}
