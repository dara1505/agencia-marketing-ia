import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Tipos
interface Client {
  id: string;
  nombre: string;
  email: string;
  tipo_negocio: string;
  objetivo: string;
  presupuesto: number;
  created_at: string;
}

interface Campaign {
  id: string;
  client_id: string;
  nombre: string;
  objetivo_especifico: string;
  estado: 'draft' | 'approved' | 'active' | 'completed';
  presupuesto: number;
  created_at: string;
  output_agentes?: any;
}

interface Agent {
  name: string;
  status: 'idle' | 'working' | 'complete';
  confidence: number;
  icon: string;
}

// Componente Principal
export default function DashboardAdmin() {
  const [tab, setTab] = useState<'dashboard' | 'clientes' | 'campanas' | 'integraciones'>('dashboard');
  const [clients, setClients] = useState<Client[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [selectedClient, setSelectedClient] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  
  // Formularios
  const [showNewClient, setShowNewClient] = useState(false);
  const [newClient, setNewClient] = useState({
    nombre: '',
    email: '',
    tipo_negocio: 'Salud',
    objetivo: 'Generar Leads',
    publico_objetivo: '',
    presupuesto: 500,
    descripcion: ''
  });
  
  const [showNewCampaign, setShowNewCampaign] = useState(false);
  const [newCampaign, setNewCampaign] = useState({
    nombre_campaña: '',
    objetivo_especifico: '',
    canal_principal: 'Instagram',
    duracion_semanas: 12,
    presupuesto: 500,
    additional_context: ''
  });

  const API_URL = 'http://localhost:8000';

  // Cargar datos
  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async () => {
    try {
      const response = await fetch(`${API_URL}/api/clients`);
      const data = await response.json();
      setClients(data.clientes);
    } catch (error) {
      console.error('Error cargando clientes:', error);
    }
  };

  const loadCampaigns = async (clientId: string) => {
    try {
      const response = await fetch(`${API_URL}/api/clients/${clientId}/campaigns`);
      const data = await response.json();
      setCampaigns(data.campanas);
      setSelectedClient(clientId);
    } catch (error) {
      console.error('Error cargando campañas:', error);
    }
  };

  // Crear cliente
  const handleCreateClient = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch(`${API_URL}/api/clients`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newClient)
      });
      
      if (response.ok) {
        setShowNewClient(false);
        setNewClient({
          nombre: '',
          email: '',
          tipo_negocio: 'Salud',
          objetivo: 'Generar Leads',
          publico_objetivo: '',
          presupuesto: 500,
          descripcion: ''
        });
        loadClients();
      }
    } catch (error) {
      console.error('Error creando cliente:', error);
    } finally {
      setLoading(false);
    }
  };

  // Generar campaña
  const handleCreateCampaign = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedClient) return;
    
    setLoading(true);
    
    try {
      const response = await fetch(`${API_URL}/api/campaigns`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_id: selectedClient,
          ...newCampaign
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setShowNewCampaign(false);
        setNewCampaign({
          nombre_campaña: '',
          objetivo_especifico: '',
          canal_principal: 'Instagram',
          duracion_semanas: 12,
          presupuesto: 500,
          additional_context: ''
        });
        loadCampaigns(selectedClient);
      }
    } catch (error) {
      console.error('Error creando campaña:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        
        {/* HEADER */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-cyan-400 to-green-400 bg-clip-text text-transparent">
            Agencia Marketing IA
          </h1>
          <p className="text-slate-400">Panel de administración - Gestiona clientes, campañas e integraciones</p>
        </div>

        {/* TABS */}
        <div className="flex gap-4 mb-8 border-b border-slate-700">
          {[
            { id: 'dashboard', label: '📊 Dashboard', icon: '📊' },
            { id: 'clientes', label: '👥 Clientes', icon: '👥' },
            { id: 'campanas', label: '🎯 Campañas', icon: '🎯' },
            { id: 'integraciones', label: '🔗 Integraciones', icon: '🔗' }
          ].map(t => (
            <button
              key={t.id}
              onClick={() => setTab(t.id as any)}
              className={`pb-3 px-4 font-medium transition ${
                tab === t.id
                  ? 'border-b-2 border-cyan-400 text-cyan-400'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* CONTENIDO POR TAB */}

        {/* DASHBOARD */}
        {tab === 'dashboard' && (
          <div className="space-y-8">
            {/* CARDS PRINCIPALES */}
            <div className="grid grid-cols-4 gap-4">
              <StatCard icon="👥" title="Clientes" value={clients.length} />
              <StatCard icon="🎯" title="Campañas" value={campaigns.length} />
              <StatCard icon="💰" title="Presupuesto Total" value={`$${clients.reduce((sum, c) => sum + c.presupuesto, 0)}`} />
              <StatCard icon="📈" title="ROI Promedio" value="2.8:1" />
            </div>

            {/* AGENTES EN ACCIÓN */}
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-xl font-bold mb-6">Agentes IA Disponibles</h2>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { name: 'Strategy', icon: '🎯', status: 'complete', confidence: 0.95 },
                  { name: 'Content', icon: '📝', status: 'complete', confidence: 0.88 },
                  { name: 'Design', icon: '🖼️', status: 'complete', confidence: 0.90 },
                  { name: 'Video', icon: '🎬', status: 'complete', confidence: 0.87 },
                  { name: 'Ads', icon: '📢', status: 'complete', confidence: 0.92 },
                  { name: 'Automation', icon: '⚙️', status: 'complete', confidence: 0.89 }
                ].map(agent => (
                  <div key={agent.name} className="bg-slate-700 p-4 rounded-lg border border-slate-600 hover:border-cyan-400 transition">
                    <div className="text-2xl mb-2">{agent.icon}</div>
                    <h3 className="font-semibold">{agent.name}</h3>
                    <div className="flex items-center gap-2 mt-2">
                      <div className="w-full bg-slate-600 rounded h-2">
                        <div className="bg-green-500 h-2 rounded" style={{width: `${agent.confidence * 100}%`}}></div>
                      </div>
                      <span className="text-xs text-green-400">{(agent.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* GRÁFICOS */}
            <div className="grid grid-cols-2 gap-6">
              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <h3 className="text-lg font-bold mb-4">Leads Generados (Últimos 30 días)</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={[
                    { dia: '1', leads: 5 },
                    { dia: '5', leads: 12 },
                    { dia: '10', leads: 28 },
                    { dia: '15', leads: 35 },
                    { dia: '20', leads: 48 },
                    { dia: '25', leads: 52 }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="dia" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{backgroundColor: '#1e293b', border: '1px solid #475569'}} />
                    <Line type="monotone" dataKey="leads" stroke="#06b6d4" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <h3 className="text-lg font-bold mb-4">ROI por Canal</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={[
                    { canal: 'Google', roi: 3.2 },
                    { canal: 'Meta', roi: 2.8 },
                    { canal: 'Email', roi: 2.1 },
                    { canal: 'Organic', roi: 1.9 }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="canal" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{backgroundColor: '#1e293b', border: '1px solid #475569'}} />
                    <Bar dataKey="roi" fill="#06b6d4" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* CLIENTES */}
        {tab === 'clientes' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Gestión de Clientes</h2>
              <button
                onClick={() => setShowNewClient(!showNewClient)}
                className="bg-cyan-500 hover:bg-cyan-600 text-black font-bold py-2 px-4 rounded transition"
              >
                + Nuevo Cliente
              </button>
            </div>

            {/* Formulario Nuevo Cliente */}
            {showNewClient && (
              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <h3 className="text-lg font-bold mb-4">Crear Nuevo Cliente</h3>
                <form onSubmit={handleCreateClient} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <input
                      type="text"
                      placeholder="Nombre"
                      className="bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500"
                      value={newClient.nombre}
                      onChange={(e) => setNewClient({...newClient, nombre: e.target.value})}
                      required
                    />
                    <input
                      type="email"
                      placeholder="Email"
                      className="bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500"
                      value={newClient.email}
                      onChange={(e) => setNewClient({...newClient, email: e.target.value})}
                      required
                    />
                    <select
                      className="bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
                      value={newClient.tipo_negocio}
                      onChange={(e) => setNewClient({...newClient, tipo_negocio: e.target.value})}
                    >
                      <option>Salud</option>
                      <option>E-commerce</option>
                      <option>SaaS</option>
                      <option>Servicios</option>
                    </select>
                    <input
                      type="number"
                      placeholder="Presupuesto"
                      className="bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500"
                      value={newClient.presupuesto}
                      onChange={(e) => setNewClient({...newClient, presupuesto: parseInt(e.target.value)})}
                    />
                  </div>
                  <input
                    type="text"
                    placeholder="Público Objetivo"
                    className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500"
                    value={newClient.publico_objetivo}
                    onChange={(e) => setNewClient({...newClient, publico_objetivo: e.target.value})}
                  />
                  <textarea
                    placeholder="Descripción"
                    className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500 h-24"
                    value={newClient.descripcion}
                    onChange={(e) => setNewClient({...newClient, descripcion: e.target.value})}
                  />
                  <div className="flex gap-2">
                    <button
                      type="submit"
                      disabled={loading}
                      className="bg-green-500 hover:bg-green-600 text-black font-bold py-2 px-4 rounded transition disabled:opacity-50"
                    >
                      {loading ? 'Creando...' : 'Crear Cliente'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowNewClient(false)}
                      className="bg-slate-700 hover:bg-slate-600 text-white font-bold py-2 px-4 rounded transition"
                    >
                      Cancelar
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Lista de Clientes */}
            <div className="space-y-4">
              {clients.map(client => (
                <div key={client.id} className="bg-slate-800 rounded-lg p-4 border border-slate-700 hover:border-cyan-400 transition cursor-pointer"
                  onClick={() => loadCampaigns(client.id)}>
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-bold text-lg">{client.nombre}</h3>
                      <p className="text-slate-400 text-sm">{client.email}</p>
                      <div className="flex gap-4 mt-2 text-sm">
                        <span className="text-cyan-400">{client.tipo_negocio}</span>
                        <span className="text-green-400">${client.presupuesto}</span>
                      </div>
                    </div>
                    <button className="bg-cyan-500 hover:bg-cyan-600 text-black font-bold py-1 px-3 rounded text-sm transition">
                      Ver Campañas
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CAMPAÑAS */}
        {tab === 'campanas' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">
                {selectedClient ? 'Campañas' : 'Selecciona un cliente'}
              </h2>
              {selectedClient && (
                <button
                  onClick={() => setShowNewCampaign(!showNewCampaign)}
                  className="bg-cyan-500 hover:bg-cyan-600 text-black font-bold py-2 px-4 rounded transition"
                >
                  + Nueva Campaña
                </button>
              )}
            </div>

            {selectedClient && (
              <>
                {/* Formulario Nueva Campaña */}
                {showNewCampaign && (
                  <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                    <h3 className="text-lg font-bold mb-4">Crear Nueva Campaña (Agentes Generarán Todo)</h3>
                    <form onSubmit={handleCreateCampaign} className="space-y-4">
                      <input
                        type="text"
                        placeholder="Nombre campaña"
                        className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500"
                        value={newCampaign.nombre_campaña}
                        onChange={(e) => setNewCampaign({...newCampaign, nombre_campaña: e.target.value})}
                        required
                      />
                      <input
                        type="text"
                        placeholder="Objetivo específico"
                        className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500"
                        value={newCampaign.objetivo_especifico}
                        onChange={(e) => setNewCampaign({...newCampaign, objetivo_especifico: e.target.value})}
                        required
                      />
                      <div className="grid grid-cols-2 gap-4">
                        <select
                          className="bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
                          value={newCampaign.canal_principal}
                          onChange={(e) => setNewCampaign({...newCampaign, canal_principal: e.target.value})}
                        >
                          <option>Instagram</option>
                          <option>Google</option>
                          <option>Facebook</option>
                          <option>Email</option>
                          <option>TikTok</option>
                        </select>
                        <input
                          type="number"
                          placeholder="Duración (semanas)"
                          className="bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500"
                          value={newCampaign.duracion_semanas}
                          onChange={(e) => setNewCampaign({...newCampaign, duracion_semanas: parseInt(e.target.value)})}
                        />
                        <input
                          type="number"
                          placeholder="Presupuesto"
                          className="bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500"
                          value={newCampaign.presupuesto}
                          onChange={(e) => setNewCampaign({...newCampaign, presupuesto: parseInt(e.target.value)})}
                        />
                      </div>
                      <textarea
                        placeholder="Contexto adicional (opcional)"
                        className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500 h-20"
                        value={newCampaign.additional_context}
                        onChange={(e) => setNewCampaign({...newCampaign, additional_context: e.target.value})}
                      />
                      <div className="flex gap-2">
                        <button
                          type="submit"
                          disabled={loading}
                          className="bg-green-500 hover:bg-green-600 text-black font-bold py-2 px-6 rounded transition disabled:opacity-50"
                        >
                          {loading ? '⏳ Generando Campaña...' : '🚀 Generar Campaña (6 Agentes)'}
                        </button>
                        <button
                          type="button"
                          onClick={() => setShowNewCampaign(false)}
                          className="bg-slate-700 hover:bg-slate-600 text-white font-bold py-2 px-4 rounded transition"
                        >
                          Cancelar
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                {/* Lista de Campañas */}
                <div className="space-y-4">
                  {campaigns.map(campaign => (
                    <CampaignCard key={campaign.id} campaign={campaign} />
                  ))}
                </div>
              </>
            )}

            {!selectedClient && (
              <div className="text-center py-12 text-slate-400">
                Selecciona un cliente en la pestaña de Clientes
              </div>
            )}
          </div>
        )}

        {/* INTEGRACIONES */}
        {tab === 'integraciones' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold">Integraciones</h2>
            <div className="grid grid-cols-2 gap-4">
              {[
                { name: 'Meta (Facebook/Instagram)', icon: '📱', connected: false },
                { name: 'Google Ads', icon: '🔍', connected: false },
                { name: 'Email (SMTP)', icon: '✉️', connected: false },
                { name: 'n8n Automation', icon: '⚙️', connected: false }
              ].map(integration => (
                <div key={integration.name} className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                  <div className="text-3xl mb-2">{integration.icon}</div>
                  <h3 className="font-bold mb-4">{integration.name}</h3>
                  <div className="mb-4">
                    <span className={`text-sm ${integration.connected ? 'text-green-400' : 'text-yellow-400'}`}>
                      {integration.connected ? '✅ Conectado' : '⏳ Pendiente'}
                    </span>
                  </div>
                  <button className="w-full bg-cyan-500 hover:bg-cyan-600 text-black font-bold py-2 px-4 rounded transition">
                    {integration.connected ? 'Reconectar' : 'Conectar'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Componentes Auxiliares
function StatCard({ icon, title, value }: { icon: string; title: string; value: any }) {
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div className="text-3xl mb-2">{icon}</div>
      <p className="text-slate-400 text-sm mb-1">{title}</p>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
}

function CampaignCard({ campaign }: { campaign: Campaign }) {
  const statusColor = {
    draft: 'bg-yellow-500',
    approved: 'bg-blue-500',
    active: 'bg-green-500',
    completed: 'bg-slate-500'
  };

  return (
    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 hover:border-cyan-400 transition">
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="font-bold text-lg">{campaign.nombre}</h3>
          <p className="text-slate-400 text-sm">{campaign.objetivo_especifico}</p>
        </div>
        <span className={`${statusColor[campaign.estado]} text-black text-xs font-bold px-3 py-1 rounded`}>
          {campaign.estado.toUpperCase()}
        </span>
      </div>
      <div className="flex justify-between items-center text-sm text-slate-400 mb-3">
        <span>💰 ${campaign.presupuesto}</span>
        <span>📅 {new Date(campaign.created_at).toLocaleDateString()}</span>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <button className="bg-slate-700 hover:bg-slate-600 text-white py-1 px-2 rounded text-sm transition">
          Ver Outputs
        </button>
        {campaign.estado === 'approved' && (
          <button className="bg-green-500 hover:bg-green-600 text-black py-1 px-2 rounded text-sm font-bold transition">
            🚀 Activar
          </button>
        )}
        {campaign.estado === 'draft' && (
          <button className="bg-blue-500 hover:bg-blue-600 text-black py-1 px-2 rounded text-sm font-bold transition">
            ✓ Aprobar
          </button>
        )}
      </div>
    </div>
  );
}
