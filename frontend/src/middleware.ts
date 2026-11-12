import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const token = request.cookies.get("autotutor_token")?.value;
  const { pathname } = request.nextUrl;

  // Rotas que dispensam qualquer tratamento de sessão
  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api") ||
    pathname === "/favicon.ico"
  ) {
    return NextResponse.next();
  }

  // Se já estiver autenticado (não convidado) e tentar acessar /login, envia para a home
  if (token && token !== "guest_anonymous" && pathname === "/login") {
    return NextResponse.redirect(new URL("/", request.url));
  }

  // Se não houver token, provisiona automaticamente uma sessão de convidado
  // para permitir navegação SPA imediata e sem atrito em todas as rotas
  if (!token && !pathname.startsWith("/login")) {
    const response = NextResponse.next();
    response.cookies.set("autotutor_token", "guest_anonymous", {
      path: "/",
      maxAge: 86400 * 30, // 30 dias
      sameSite: "lax",
    });
    return response;
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
