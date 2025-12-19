import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * TeseDropdown - Componente dropdown para seleção de tese nos prognósticos
 * Usado em Tributário, Trabalhista e Cível
 */
import { useState, useEffect } from 'react';
import api from '../../lib/api';
export default function TeseDropdown({ value, onChange, tributoId, placeholder = 'Selecione uma tese ou digite...', className = '', disabled = false }) {
    const [teses, setTeses] = useState([]);
    const [loading, setLoading] = useState(false);
    const [isCustom, setIsCustom] = useState(false);
    const [customText, setCustomText] = useState('');
    useEffect(() => {
        carregarTeses();
    }, [tributoId]);
    // Determinar se o valor atual é custom ou uma tese
    useEffect(() => {
        if (value && teses.length > 0) {
            const teseEncontrada = teses.find(t => t.titulo === value);
            setIsCustom(!teseEncontrada && value.length > 0);
            if (!teseEncontrada) {
                setCustomText(value);
            }
        }
    }, [value, teses]);
    const carregarTeses = async () => {
        setLoading(true);
        try {
            // Carregar teses genéricas ou por tributo
            const response = await api.get('/api/tributario/teses', {
                params: tributoId ? { tributo_id: tributoId } : {}
            });
            setTeses(response.data || []);
        }
        catch (error) {
            console.error('Erro ao carregar teses:', error);
            // Fallback com teses genéricas
            setTeses([
                { id_tese: 1, titulo: 'Reconhecimento integral do pedido' },
                { id_tese: 2, titulo: 'Procedência parcial' },
                { id_tese: 3, titulo: 'Improcedência do pedido' },
                { id_tese: 4, titulo: 'Extinção sem mérito' }
            ]);
        }
        finally {
            setLoading(false);
        }
    };
    const handleSelectChange = (e) => {
        const selectedValue = e.target.value;
        if (selectedValue === '__custom__') {
            setIsCustom(true);
            onChange(customText);
        }
        else {
            setIsCustom(false);
            onChange(selectedValue);
        }
    };
    const handleCustomChange = (e) => {
        setCustomText(e.target.value);
        onChange(e.target.value);
    };
    return (_jsxs("div", { className: "space-y-2", children: [_jsxs("select", { value: isCustom ? '__custom__' : (value || ''), onChange: handleSelectChange, disabled: disabled || loading, className: `w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none disabled:bg-muted disabled:cursor-not-allowed ${className}`, children: [_jsx("option", { value: "", children: loading ? 'Carregando...' : placeholder }), teses.map(tese => (_jsxs("option", { value: tese.titulo, children: [tese.codigo ? `${tese.codigo} - ` : '', tese.titulo, tese.probabilidade_sucesso !== undefined ? ` (${tese.probabilidade_sucesso}%)` : ''] }, tese.id_tese))), _jsx("option", { value: "__custom__", children: "\u270F\uFE0F Digitar manualmente..." })] }), isCustom && (_jsx("input", { type: "text", value: customText, onChange: handleCustomChange, placeholder: "Digite a tese manualmente", disabled: disabled, className: `w-full bg-background border border-dashed border-primary/50 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary outline-none ${className}` }))] }));
}
