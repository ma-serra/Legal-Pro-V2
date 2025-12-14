import { useState } from 'react'
import { AdminLayout } from '../../components/layouts/AdminLayout'
import { PageHeader } from '../../components/ui/AdminComponents'
import { User, Building2, Lock, Bell } from 'lucide-react'

export default function Settings() {
    const [activeTab, setActiveTab] = useState('profile')

    const tabs = [
        { id: 'profile', label: 'Perfil', icon: User },
        { id: 'organization', label: 'Organização', icon: Building2 },
        { id: 'security', label: 'Segurança', icon: Lock },
        { id: 'notifications', label: 'Notificações', icon: Bell },
    ]

    return (
        <AdminLayout>
            <PageHeader
                title="Configurações"
                description="Gerenciar preferências e configurações"
            />

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Tabs */}
                <div className="lg:col-span-1">
                    <div className="bg-white rounded-lg border border-gray-200 p-2">
                        {tabs.map(tab => {
                            const Icon = tab.icon
                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${activeTab === tab.id
                                            ? 'bg-blue-50 text-blue-600'
                                            : 'text-gray-700 hover:bg-gray-50'
                                        }`}
                                >
                                    <Icon className="w-5 h-5" />
                                    {tab.label}
                                </button>
                            )
                        })}
                    </div>
                </div>

                {/* Content */}
                <div className="lg:col-span-3">
                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                        {activeTab === 'profile' && (
                            <div className="space-y-6">
                                <h3 className="text-lg font-semibold">Informações Pessoais</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Nome
                                        </label>
                                        <input
                                            type="text"
                                            defaultValue="Denis May"
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Email
                                        </label>
                                        <input
                                            type="email"
                                            defaultValue="denis@example.com"
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                        />
                                    </div>
                                </div>
                                <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                                    Salvar Alterações
                                </button>
                            </div>
                        )}

                        {activeTab === 'organization' && (
                            <div className="space-y-6">
                                <h3 className="text-lg font-semibold">Configurações da Organização</h3>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Nome da Organização
                                    </label>
                                    <input
                                        type="text"
                                        defaultValue="Minha Empresa"
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                    />
                                </div>
                                <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                                    Salvar
                                </button>
                            </div>
                        )}

                        {activeTab === 'security' && (
                            <div className="space-y-6">
                                <h3 className="text-lg font-semibold">Segurança</h3>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Alterar Senha
                                    </label>
                                    <input
                                        type="password"
                                        placeholder="Nova senha"
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                                    />
                                </div>
                                <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                                    Atualizar Senha
                                </button>
                            </div>
                        )}

                        {activeTab === 'notifications' && (
                            <div className="space-y-6">
                                <h3 className="text-lg font-semibold">Preferências de Notificações</h3>
                                <div className="space-y-4">
                                    <label className="flex items-center gap-3">
                                        <input type="checkbox" defaultChecked className="rounded" />
                                        <span className="text-gray-700">Email notifications</span>
                                    </label>
                                    <label className="flex items-center gap-3">
                                        <input type="checkbox" defaultChecked className="rounded" />
                                        <span className="text-gray-700">Push notifications</span>
                                    </label>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </AdminLayout>
    )
}
