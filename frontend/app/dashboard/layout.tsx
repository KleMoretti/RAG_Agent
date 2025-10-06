import { AppSidebar } from "@/components/layout/Sidebar";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { AuthGuard } from "@/components/auth/AuthGuard";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard requireAuth={true}>
      <SidebarProvider>
        <AppSidebar />
        <SidebarInset className="bg-sidebar h-svh overflow-hidden">
          <main className="flex flex-col flex-1 h-full bg-background m-2 ml-0 rounded-xl border border-border overflow-hidden min-h-0">
            {children}
          </main>
        </SidebarInset>
      </SidebarProvider>
    </AuthGuard>
  );
}
