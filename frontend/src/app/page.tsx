"use client"
import React, { useEffect, useState } from "react";
import axios from "axios";
import { 
  Activity, Users, ShieldAlert, Lock, 
  Terminal, Server, Globe, Search, ArrowRight,
  Shield, Cpu, AlertTriangle
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const API_BASE = "http://localhost:8000/api";

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [riskyUsers, setRiskyUsers] = useState<any[]>([]);
  const [network, setNetwork] = useState<any>({ services: [], connections: [] });
  const [loading, setLoading] = useState(true);

  // Mock Authentication token for development
  const fetchDashboard = async () => {
    try {
      // In a real app, you would login first, but we temporarily bypassed auth 
      // by not verifying token for the stats and risky_users if we adjust backend
      // But let's actually just login to get a token:
      const authRes = await axios.post(`${API_BASE}/auth/login`, new URLSearchParams({
        username: "admin",
        password: "password"
      }));
      const token = authRes.data.access_token;
      
      const config = { headers: { Authorization: `Bearer ${token}` } };
      
      const [statsRes, usersRes, netRes] = await Promise.all([
        axios.get(`${API_BASE}/dashboard/stats`, config),
        axios.get(`${API_BASE}/dashboard/risky_users`, config),
        axios.get(`${API_BASE}/live/network`, config)
      ]);
      
      setStats(statsRes.data);
      setRiskyUsers(usersRes.data);
      setNetwork(netRes.data);
    } catch (error) {
      console.error("Failed to load data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(fetchDashboard, 15000); // 15s refresh
    return () => clearInterval(interval);
  }, []);

  if (loading && !stats) {
    return (
      <div className="flex h-screen items-center justify-center bg-zinc-950 text-zinc-50">
        <div className="flex flex-col items-center gap-4">
          <ShieldAlert className="h-12 w-12 animate-pulse text-blue-500" />
          <h2 className="text-xl font-bold tracking-tight">Initializing ThreatSentinel Enterprise...</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-zinc-950 text-zinc-50">
      <header className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur supports-[backdrop-filter]:bg-zinc-900/50">
        <div className="container flex h-16 items-center gap-4 px-4 max-w-7xl mx-auto">
          <Shield className="h-6 w-6 text-blue-500" />
          <h1 className="text-xl font-bold tracking-tight">ThreatSentinel <span className="text-blue-500">Enterprise</span></h1>
          <div className="ml-auto flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
              </span>
              <span className="text-sm text-zinc-400">System Online</span>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 container max-w-7xl mx-auto p-4 space-y-6 mt-6">
        {/* STATS GRID */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card className="bg-zinc-900/50 border-zinc-800">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-zinc-400">Total Logs Analyzed</CardTitle>
              <Activity className="h-4 w-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.totalLogs.toLocaleString() || 0}</div>
              <p className="text-xs text-zinc-500">+20.1% from last hour</p>
            </CardContent>
          </Card>
          <Card className="bg-zinc-900/50 border-zinc-800">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-zinc-400">Credential Leaks</CardTitle>
              <ShieldAlert className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-500">{stats?.credentialLeaks || 0}</div>
              <p className="text-xs text-zinc-500">Critical Priority</p>
            </CardContent>
          </Card>
          <Card className="bg-zinc-900/50 border-zinc-800">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-zinc-400">Gov. Violations</CardTitle>
              <AlertTriangle className="h-4 w-4 text-orange-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-500">{stats?.govViolations || 0}</div>
              <p className="text-xs text-zinc-500">High Priority</p>
            </CardContent>
          </Card>
          <Card className="bg-zinc-900/50 border-zinc-800">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-zinc-400">Locked Accounts</CardTitle>
              <Lock className="h-4 w-4 text-zinc-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.lockedAccounts || 0}</div>
              <p className="text-xs text-zinc-500">Automatically mitigated</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 md:grid-cols-7">
          {/* ML RISK TABLE */}
          <Card className="md:col-span-4 bg-zinc-900/50 border-zinc-800">
            <CardHeader>
              <CardTitle>Active Hybrid Risk Assessment</CardTitle>
              <CardDescription>Top High-Risk Users via Isolation Forest & LLM Routing</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border border-zinc-800">
                <Table>
                  <TableHeader className="bg-zinc-900">
                    <TableRow className="border-zinc-800 hover:bg-zinc-800/50">
                      <TableHead>User ID</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Threat Type</TableHead>
                      <TableHead className="text-right">Risk Score</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {riskyUsers.map((user, i) => (
                      <TableRow key={i} className="border-zinc-800 hover:bg-zinc-800/50">
                        <TableCell className="font-medium flex items-center gap-2">
                          <Users className="h-4 w-4 text-zinc-400" />
                          {user.user}
                        </TableCell>
                        <TableCell>
                          <Badge variant={user.status_raw === "ex" ? "destructive" : "default"} className={user.status_raw !== "ex" ? "bg-green-500/10 text-green-500 hover:bg-green-500/20" : ""}>
                            {user.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <span className={user.threat !== "No Threat" ? "text-red-400 font-medium" : "text-zinc-400"}>
                            {user.threat}
                          </span>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end gap-2">
                            <div className="w-16 h-1.5 rounded-full bg-zinc-800 overflow-hidden">
                              <div 
                                className={`h-full ${user.ml_risk > 75 ? "bg-red-500" : user.ml_risk > 50 ? "bg-orange-500" : "bg-blue-500"}`} 
                                style={{ width: `${user.ml_risk}%` }}
                              />
                            </div>
                            <span className="font-mono text-xs">{user.ml_risk.toFixed(1)}</span>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                    {riskyUsers.length === 0 && (
                      <TableRow className="border-zinc-800 hover:bg-zinc-800/50">
                        <TableCell colSpan={4} className="h-24 text-center text-zinc-500">
                          No high-risk anomalous users detected.
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>

          {/* LIVE SYSTEM MONITOR */}
          <Card className="md:col-span-3 bg-zinc-900/50 border-zinc-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5 text-blue-500" />
                Live Network Monitor
              </CardTitle>
              <CardDescription>Real-time OS and network telemetry</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-semibold text-zinc-400 mb-2 uppercase flex items-center gap-2">
                    <Terminal className="h-3 w-3" /> Active Connections
                  </h4>
                  <div className="space-y-2">
                    {network.connections.slice(0, 5).map((conn: any, i: number) => (
                      <div key={i} className="flex items-center justify-between text-xs bg-zinc-950 p-2 rounded border border-zinc-800">
                        <span className="text-blue-400 font-mono">{conn.local_address}</span>
                        <ArrowRight className="h-3 w-3 text-zinc-600" />
                        <span className="text-orange-400 font-mono">{conn.remote_address}</span>
                        <Badge variant="outline" className="text-[10px] h-4 border-zinc-700 bg-zinc-900">
                          {conn.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-zinc-400 mb-2 uppercase flex items-center gap-2">
                    <Server className="h-3 w-3" /> Suspicious Services
                  </h4>
                  <div className="space-y-2">
                    {network.services.slice(0, 5).map((svc: any, i: number) => (
                      <div key={i} className="flex items-center justify-between text-xs bg-zinc-950 p-2 rounded border border-zinc-800">
                        <span className="text-zinc-300 font-mono">{svc.name}</span>
                        <span className="text-zinc-500 truncate max-w-[150px]">{svc.display_name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
