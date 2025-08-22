import React, { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import AdminPrivateRoute from '../auth/AdminPrivateRoute';
import {
  setAdminToken,
  adminOverview,
  listUsers,
  listVendors,
  promoteToVendor,
  promoteToAdmin
} from '../../services/adminService';
import {
  setCrmToken,
  listSegments,
  listCampaigns,
  listNotifications,
  createSegment,
  previewSegmentUsers,
  createCampaign,
  previewCampaignUsers,
  dispatchCampaign
} from '../../services/crmService';
import { CheckCircle, Loader2, ShieldCheck } from 'lucide-react';

const AdminDashboard: React.FC = () => {
  // Helper function to safely render arrays
  const safeArrayMap = (arr: any, renderFn: (item: any, index: number) => React.ReactNode) => {
    return Array.isArray(arr) ? arr.map(renderFn) : [];
  };
  const { token } = useAuth();
  const [overview, setOverview] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [vendors, setVendors] = useState<any[]>([]);
  const [segments, setSegments] = useState<any[]>([]);
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loadingOverview, setLoadingOverview] = useState<boolean>(true);
  const [promoteLoadingByUserId, setPromoteLoadingByUserId] = useState<Record<string, 'vendor' | 'admin' | null>>({});
  const [toasts, setToasts] = useState<Array<{ id: string; type: 'success' | 'error'; message: string }>>([]);
  const [segmentForm, setSegmentForm] = useState({
    name: '',
    description: '',
    lastDays: '',
    minTotalSpent: '',
    minNumPurchases: '',
    prompt: ''
  });
  const [campaignForm, setCampaignForm] = useState({
    name: '',
    description: '',
    message: '',
    segmentIds: [] as string[]
  });
  const [segmentPreview, setSegmentPreview] = useState<Record<string, string[]>>({});
  const [campaignPreview, setCampaignPreview] = useState<Record<string, string[]>>({});

  useEffect(() => {
    setAdminToken(token);
    setCrmToken(token);
    (async () => {
      try {
        setLoadingOverview(true);
        const ov = await adminOverview();
        setOverview(ov);
      } finally {
        setLoadingOverview(false);
      }
      const us = await listUsers(20, 0);
      console.log('Users data:', us, 'Type:', typeof us, 'Is Array:', Array.isArray(us));
      setUsers(us);
      const vs = await listVendors(20, 0);
      console.log('Vendors data:', vs, 'Type:', typeof vs, 'Is Array:', Array.isArray(vs));
      setVendors(vs);
      setSegments(await listSegments());
      setCampaigns(await listCampaigns());
      setNotifications(await listNotifications('queued'));
    })();
  }, [token]);

  const addToast = (type: 'success' | 'error', message: string) => {
    const id = Math.random().toString(36).slice(2);
    setToasts(prev => [...prev, { id, type, message }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 3000);
  };

  const handlePromoteVendor = async (id: string) => {
    setPromoteLoadingByUserId(prev => ({ ...prev, [id]: 'vendor' }));
    // Optimisme: canviar rol a la llista d'usuaris i afegir a venedors visualment
    const targetUser = (users || []).find(u => u.id === id);
    if (targetUser) {
      setUsers(prev => prev?.map(u => (u.id === id ? { ...u, role: 'vendor' } : u)) || []);
      setVendors(prev => (prev?.some(v => v.id === id) ? prev : [...(prev || []), { ...targetUser, role: 'vendor' }]));
    }
    try {
      await promoteToVendor(id);
      // Refrescar llistes per coherència
      const [us, vs] = await Promise.all([listUsers(20, 0), listVendors(20, 0)]);
      setUsers(us);
      setVendors(vs);
      addToast('success', 'Usuari promogut a venedor');
    } catch (e: any) {
      addToast('error', e?.message || 'Error en promoure a venedor');
    } finally {
      setPromoteLoadingByUserId(prev => ({ ...prev, [id]: null }));
    }
  };

  const handlePromoteAdmin = async (id: string) => {
    setPromoteLoadingByUserId(prev => ({ ...prev, [id]: 'admin' }));
    // Optimisme: canviar rol a la llista d'usuaris
    setUsers(prev => prev?.map(u => (u.id === id ? { ...u, role: 'admin' } : u)) || []);
    try {
      await promoteToAdmin(id);
      // Refrescar llistes
      const us = await listUsers(20, 0);
      setUsers(us);
      addToast('success', 'Usuari promogut a admin');
    } catch (e: any) {
      addToast('error', e?.message || 'Error en promoure a admin');
    } finally {
      setPromoteLoadingByUserId(prev => ({ ...prev, [id]: null }));
    }
  };

  const submitCreateSegment = async (e: React.FormEvent) => {
    e.preventDefault();
    const filters: any = {};
    if (segmentForm.lastDays) filters.last_days = Number(segmentForm.lastDays);
    if (segmentForm.minTotalSpent) filters.min_total_spent = Number(segmentForm.minTotalSpent);
    if (segmentForm.minNumPurchases) filters.min_num_purchases = Number(segmentForm.minNumPurchases);
    const payload: any = { name: segmentForm.name, description: segmentForm.description, filters };
    if (segmentForm.prompt) payload.prompt = segmentForm.prompt;
    await createSegment(payload);
    setSegments(await listSegments());
    setSegmentForm({ name: '', description: '', lastDays: '', minTotalSpent: '', minNumPurchases: '', prompt: '' });
    addToast('success', 'Segment creat correctament');
  };

  const toggleSegmentPreview = async (segmentId: string) => {
    if (segmentPreview[segmentId]) {
      const copy = { ...segmentPreview }; delete copy[segmentId]; setSegmentPreview(copy);
    } else {
      const users = await previewSegmentUsers(segmentId, 50);
      setSegmentPreview(prev => ({ ...prev, [segmentId]: users }));
    }
  };

  const submitCreateCampaign = async (e: React.FormEvent) => {
    e.preventDefault();
    await createCampaign({ name: campaignForm.name, description: campaignForm.description, message: campaignForm.message, segment_ids: campaignForm.segmentIds });
    setCampaigns(await listCampaigns());
    setCampaignForm({ name: '', description: '', message: '', segmentIds: [] });
    addToast('success', 'Campanya creada correctament');
  };

  const toggleCampaignPreview = async (campaignId: string) => {
    if (campaignPreview[campaignId]) {
      const copy = { ...campaignPreview }; delete copy[campaignId]; setCampaignPreview(copy);
    } else {
      const users = await previewCampaignUsers(campaignId, 50);
      setCampaignPreview(prev => ({ ...prev, [campaignId]: users }));
    }
  };

  const handleDispatchCampaign = async (campaignId: string) => {
    await dispatchCampaign(campaignId);
    setNotifications(await listNotifications('queued'));
    addToast('success', 'Campanya enviada a la cua');
  };

  return (
    <AdminPrivateRoute>
      <div className="p-6 space-y-6">
        {/* Toasts */}
        <div className="fixed top-4 right-4 z-50 space-y-2">
          {toasts.map(t => (
            <div
              key={t.id}
              className={`flex items-center gap-2 px-4 py-2 rounded shadow text-white ${
                t.type === 'success' ? 'bg-green-600' : 'bg-red-600'
              }`}
            >
              <CheckCircle className="h-4 w-4" />
              <span>{t.message}</span>
            </div>
          ))}
        </div>

        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Panell d'administració</h1>
          <CurrentRolePill />
        </div>

        {overview && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <StatCard label="Usuaris" value={overview.total_users} />
            <StatCard label="Venedors" value={overview.total_vendors} />
            <StatCard label="Admins" value={overview.total_admins} />
            <StatCard label="Compres" value={overview.total_purchases} />
            <StatCard label="€ gastat" value={overview.total_spent ? overview.total_spent.toFixed(2) : '0.00'} />
          </div>
        )}
        {loadingOverview && (
          <div className="flex items-center gap-2 text-gray-600"><Loader2 className="h-4 w-4 animate-spin" /> Carregant resum...</div>
        )}
        <Section title="Usuaris (no venedors ni admins)">
          <div className="space-y-2">
            {safeArrayMap(Array.isArray(users) ? users.filter(u => u.role === 'user') : [], u => (
              <div key={u.id} className="flex items-center justify-between bg-white p-3 rounded border">
                <div>
                  <div className="font-medium">{u.email}</div>
                  <div className="text-sm text-gray-500">{u.role}</div>
                </div>
                <div className="space-x-2">
                  <button
                    className="px-3 py-1 bg-blue-600 text-white rounded disabled:opacity-60 disabled:cursor-not-allowed inline-flex items-center gap-2"
                    onClick={() => handlePromoteVendor(u.id)}
                    disabled={promoteLoadingByUserId[u.id] !== undefined && promoteLoadingByUserId[u.id] !== null}
                  >
                    {promoteLoadingByUserId[u.id] === 'vendor' ? (
                      <><Loader2 className="h-4 w-4 animate-spin" /> Fent venedor...</>
                    ) : (
                      'Fer venedor'
                    )}
                  </button>
                  <button
                    className="px-3 py-1 bg-purple-600 text-white rounded disabled:opacity-60 disabled:cursor-not-allowed inline-flex items-center gap-2"
                    onClick={() => handlePromoteAdmin(u.id)}
                    disabled={promoteLoadingByUserId[u.id] !== undefined && promoteLoadingByUserId[u.id] !== null}
                  >
                    {promoteLoadingByUserId[u.id] === 'admin' ? (
                      <><Loader2 className="h-4 w-4 animate-spin" /> Fent admin...</>
                    ) : (
                      'Fer admin'
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </Section>

        <Section title="Venedors">
          <div className="space-y-2">
            {Array.isArray(vendors) ? vendors.filter(v => v.role === 'vendor').map(v => (
              <div key={v.id} className="flex items-center justify-between bg-white p-3 rounded border">
                <div>
                  <div className="font-medium">{v.email}</div>
                  <div className="text-sm text-gray-500">{v.role}</div>
                </div>
              </div>
            )) : null}
          </div>
        </Section>

        <Section title="Tots els usuaris (amb rols)">
          <div className="space-y-2">
            {(users || []).map(u => (
              <div key={u.id} className="flex items-center justify-between bg-white p-3 rounded border">
                <div>
                  <div className="font-medium">{u.email}</div>
                  <div className={`text-sm px-2 py-1 rounded inline-block ${
                    u.role === 'admin' ? 'bg-purple-100 text-purple-800' :
                    u.role === 'vendor' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {u.role}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Section>

        <Section title="CRM: Crear segment">
          <form onSubmit={submitCreateSegment} className="bg-white p-4 rounded border grid grid-cols-1 md:grid-cols-3 gap-3">
            <input className="border p-2 rounded" placeholder="Nom" value={segmentForm.name} onChange={e => setSegmentForm({ ...segmentForm, name: e.target.value })} required />
            <input className="border p-2 rounded md:col-span-2" placeholder="Descripció" value={segmentForm.description} onChange={e => setSegmentForm({ ...segmentForm, description: e.target.value })} />
            <input className="border p-2 rounded" placeholder="Darrers dies" type="number" value={segmentForm.lastDays} onChange={e => setSegmentForm({ ...segmentForm, lastDays: e.target.value })} />
            <input className="border p-2 rounded" placeholder="Despesa mínima (€)" type="number" value={segmentForm.minTotalSpent} onChange={e => setSegmentForm({ ...segmentForm, minTotalSpent: e.target.value })} />
            <input className="border p-2 rounded" placeholder="Mín nº compres" type="number" value={segmentForm.minNumPurchases} onChange={e => setSegmentForm({ ...segmentForm, minNumPurchases: e.target.value })} />
            <textarea className="border p-2 rounded md:col-span-3" placeholder="Prompt de preferències (ex: clients que prefereixen productes ecològics i locals)" value={segmentForm.prompt} onChange={e => setSegmentForm({ ...segmentForm, prompt: e.target.value })} />
            <div className="md:col-span-3">
              <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded">Crear segment</button>
            </div>
          </form>
        </Section>

        <Section title="CRM: Segments">
          <div className="space-y-2">
            {(segments || []).map(s => (
              <div key={s.id} className="bg-white p-3 rounded border">
                <div className="flex items-center justify-between">
                  <div className="font-medium">{s.name}</div>
                  <div className="space-x-2">
                    <button className="px-3 py-1 bg-gray-700 text-white rounded" onClick={() => toggleSegmentPreview(s.id)}>
                      {segmentPreview[s.id] ? 'Amagar vista prèvia' : 'Vista prèvia d\'usuaris'}
                    </button>
                  </div>
                </div>
                {segmentPreview[s.id] && (
                  <div className="mt-2 text-sm text-gray-700">
                                         <div>{segmentPreview[s.id]?.length || 0} usuaris (mostra)</div>
                                         <ul className="list-disc pl-5">
                       {segmentPreview[s.id]?.slice(0, 20).map(uid => <li key={uid}>{uid}</li>)}
                     </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Section>

        <Section title="CRM: Crear campanya">
          <form onSubmit={submitCreateCampaign} className="bg-white p-4 rounded border space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <input className="border p-2 rounded" placeholder="Nom" value={campaignForm.name} onChange={e => setCampaignForm({ ...campaignForm, name: e.target.value })} required />
              <input className="border p-2 rounded" placeholder="Descripció" value={campaignForm.description} onChange={e => setCampaignForm({ ...campaignForm, description: e.target.value })} />
            </div>
            <textarea className="border p-2 rounded w-full" placeholder="Missatge (opcional; si es deixa buit es generarà amb IA)" value={campaignForm.message} onChange={e => setCampaignForm({ ...campaignForm, message: e.target.value })} />
            <div>
              <div className="font-medium mb-2">Selecciona segments</div>
              <div className="grid md:grid-cols-3 gap-2">
                                 {(segments || []).map(s => (
                  <label key={s.id} className="flex items-center gap-2 bg-gray-50 border rounded p-2">
                    <input
                      type="checkbox"
                      checked={campaignForm.segmentIds.includes(s.id)}
                      onChange={e => {
                        const checked = e.target.checked;
                        setCampaignForm(prev => ({
                          ...prev,
                          segmentIds: checked ? [...prev.segmentIds, s.id] : prev.segmentIds.filter(id => id !== s.id)
                        }));
                      }}
                    />
                    <span>{s.name}</span>
                  </label>
                ))}
              </div>
            </div>
            <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded">Crear campanya</button>
          </form>
        </Section>

        <Section title="CRM: Campanyes">
          <div className="space-y-2">
            {(campaigns || []).map(c => (
              <div key={c.id} className="bg-white p-3 rounded border">
                <div className="flex items-center justify-between">
                  <div className="font-medium">{c.name}</div>
                  <div className="space-x-2">
                    <button className="px-3 py-1 bg-gray-700 text-white rounded" onClick={() => toggleCampaignPreview(c.id)}>
                      {campaignPreview[c.id] ? 'Amagar vista prèvia' : 'Vista prèvia d\'usuaris'}
                    </button>
                    <button className="px-3 py-1 bg-blue-600 text-white rounded" onClick={() => handleDispatchCampaign(c.id)}>Enviar</button>
                  </div>
                </div>
                {campaignPreview[c.id] && (
                  <div className="mt-2 text-sm text-gray-700">
                                         <div>{campaignPreview[c.id]?.length || 0} usuaris (mostra)</div>
                                         <ul className="list-disc pl-5">
                       {campaignPreview[c.id]?.slice(0, 20).map(uid => <li key={uid}>{uid}</li>)}
                     </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Section>

        <Section title="CRM: Notificacions (en cua)">
          <ul className="list-disc pl-5">
            {(notifications || []).map((n: any) => (
              <li key={n.id}>{n.message}</li>
            ))}
          </ul>
        </Section>
      </div>
    </AdminPrivateRoute>
  );
};

const StatCard: React.FC<{ label: string; value: string | number }> = ({ label, value }) => (
  <div className="bg-white p-4 rounded border">
    <div className="text-gray-500 text-sm">{label}</div>
    <div className="text-xl font-semibold">{value}</div>
  </div>
);

const Section: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <section>
    <h2 className="text-lg font-semibold mb-2">{title}</h2>
    {children}
  </section>
);

const CurrentRolePill: React.FC = () => {
  const { user } = useAuth();
  const roleLabel = useMemo(() => {
    if (!user?.role) return 'Desconegut';
    if (user.role === 'admin') return 'admin';
    if (user.role === 'vendor') return 'venedor';
    return 'usuari';
  }, [user?.role]);
  return (
    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-200">
      <ShieldCheck className="h-4 w-4" />
      <span className="text-sm">Rol actual: {roleLabel}</span>
    </div>
  );
};

export default AdminDashboard;


