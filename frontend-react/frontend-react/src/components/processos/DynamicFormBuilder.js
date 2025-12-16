import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * DynamicFormBuilder - Formulários Dinâmicos por Natureza
 * Gera campos específicos baseado no schema da natureza
 */
import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import api from '../../lib/api';
import { Loader2 } from 'lucide-react';
export default function DynamicFormBuilder({ naturezaId, onDataChange, initialData }) {
    const { register, watch } = useForm({
        defaultValues: initialData || {}
    });
    const [schema, setSchema] = useState(null);
    const [loading, setLoading] = useState(true);
    const formData = watch();
    useEffect(() => {
        fetchSchema();
    }, [naturezaId]);
    useEffect(() => {
        if (schema) {
            onDataChange(formData);
        }
    }, [formData]);
    const fetchSchema = async () => {
        setLoading(true);
        try {
            const naturezaMap = {
                1: 'Tributário',
                2: 'Trabalhista',
                3: 'Cível'
            };
            const response = await api.get(`/api/processos/schema/${naturezaMap[naturezaId]}`);
            setSchema(response.data || {});
        }
        catch (error) {
            console.error('Erro ao carregar schema:', error);
            setSchema({ fields: [] });
        }
        finally {
            setLoading(false);
        }
    };
    const renderField = (field) => {
        const baseClasses = "w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary";
        switch (field.type) {
            case 'text':
            case 'email':
            case 'url':
                return (_jsx("input", { type: field.type, ...register(field.name, { required: field.required }), className: baseClasses, placeholder: field.placeholder }));
            case 'number':
            case 'decimal':
                return (_jsx("input", { type: "number", step: field.type === 'decimal' ? '0.01' : '1', ...register(field.name, {
                        required: field.required,
                        valueAsNumber: true
                    }), className: baseClasses, placeholder: field.placeholder }));
            case 'date':
                return (_jsx("input", { type: "date", ...register(field.name, { required: field.required }), className: baseClasses }));
            case 'select':
                return (_jsxs("select", { ...register(field.name, { required: field.required }), className: baseClasses, children: [_jsx("option", { value: "", children: "Selecione..." }), field.options?.map((opt) => (_jsx("option", { value: opt.value, children: opt.label }, opt.value)))] }));
            case 'textarea':
                return (_jsx("textarea", { ...register(field.name, { required: field.required }), rows: field.rows || 3, className: baseClasses, placeholder: field.placeholder }));
            case 'checkbox':
                return (_jsxs("div", { className: "flex items-center gap-2", children: [_jsx("input", { type: "checkbox", ...register(field.name), className: "w-4 h-4 rounded border-border bg-background focus:ring-2 focus:ring-primary" }), _jsx("label", { className: "text-sm", children: field.label })] }));
            default:
                return _jsxs("p", { className: "text-sm text-muted-foreground", children: ["Tipo de campo n\u00E3o suportado: ", field.type] });
        }
    };
    if (loading) {
        return (_jsx("div", { className: "flex items-center justify-center py-12", children: _jsx(Loader2, { className: "w-8 h-8 animate-spin text-primary" }) }));
    }
    if (!schema || !schema.fields || schema.fields.length === 0) {
        return (_jsx("div", { className: "bg-accent rounded-xl p-8 text-center", children: _jsx("p", { className: "text-muted-foreground", children: "Nenhum campo espec\u00EDfico para esta natureza" }) }));
    }
    return (_jsxs("div", { className: "space-y-4", children: [_jsx("h4", { className: "font-semibold text-lg mb-4", children: schema.title || 'Campos Específicos' }), _jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: schema.fields.map((field) => (_jsxs("div", { className: field.fullWidth ? 'md:col-span-2' : '', children: [_jsxs("label", { className: "block text-sm font-medium mb-2", children: [field.label, field.required && _jsx("span", { className: "text-red-500 ml-1", children: "*" })] }), renderField(field), field.help && (_jsx("p", { className: "text-xs text-muted-foreground mt-1", children: field.help }))] }, field.name))) })] }));
}
