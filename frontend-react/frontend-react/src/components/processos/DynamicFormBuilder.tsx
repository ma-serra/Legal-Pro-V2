/**
 * DynamicFormBuilder - Formulários Dinâmicos por Natureza
 * Gera campos específicos baseado no schema da natureza
 */
import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import api from '../../lib/api';
import { Loader2 } from 'lucide-react';

interface DynamicFormBuilderProps {
    naturezaId: number;
    onDataChange: (data: Record<string, any>) => void;
    initialData?: Record<string, any>;
}

export default function DynamicFormBuilder({ naturezaId, onDataChange, initialData }: DynamicFormBuilderProps) {
    const { register, watch } = useForm({
        defaultValues: initialData || {}
    });

    const [schema, setSchema] = useState<any>(null);
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
            const naturezaMap: Record<number, string> = {
                1: 'Tributário',
                2: 'Trabalhista',
                3: 'Cível'
            };

            const response = await api.get(`/api/processos/schema/${naturezaMap[naturezaId]}`);
            setSchema(response.data || {});
        } catch (error) {
            console.error('Erro ao carregar schema:', error);
            setSchema({ fields: [] });
        } finally {
            setLoading(false);
        }
    };

    const renderField = (field: any) => {
        const baseClasses = "w-full bg-background border border-border rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-primary";

        switch (field.type) {
            case 'text':
            case 'email':
            case 'url':
                return (
                    <input
                        type={field.type}
                        {...register(field.name, { required: field.required })}
                        className={baseClasses}
                        placeholder={field.placeholder}
                    />
                );

            case 'number':
            case 'decimal':
                return (
                    <input
                        type="number"
                        step={field.type === 'decimal' ? '0.01' : '1'}
                        {...register(field.name, {
                            required: field.required,
                            valueAsNumber: true
                        })}
                        className={baseClasses}
                        placeholder={field.placeholder}
                    />
                );

            case 'date':
                return (
                    <input
                        type="date"
                        {...register(field.name, { required: field.required })}
                        className={baseClasses}
                    />
                );

            case 'select':
                return (
                    <select
                        {...register(field.name, { required: field.required })}
                        className={baseClasses}
                    >
                        <option value="">Selecione...</option>
                        {field.options?.map((opt: any) => (
                            <option key={opt.value} value={opt.value}>
                                {opt.label}
                            </option>
                        ))}
                    </select>
                );

            case 'textarea':
                return (
                    <textarea
                        {...register(field.name, { required: field.required })}
                        rows={field.rows || 3}
                        className={baseClasses}
                        placeholder={field.placeholder}
                    />
                );

            case 'checkbox':
                return (
                    <div className="flex items-center gap-2">
                        <input
                            type="checkbox"
                            {...register(field.name)}
                            className="w-4 h-4 rounded border-border bg-background focus:ring-2 focus:ring-primary"
                        />
                        <label className="text-sm">{field.label}</label>
                    </div>
                );

            default:
                return <p className="text-sm text-muted-foreground">Tipo de campo não suportado: {field.type}</p>;
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
        );
    }

    if (!schema || !schema.fields || schema.fields.length === 0) {
        return (
            <div className="bg-accent rounded-xl p-8 text-center">
                <p className="text-muted-foreground">
                    Nenhum campo específico para esta natureza
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <h4 className="font-semibold text-lg mb-4">
                {schema.title || 'Campos Específicos'}
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {schema.fields.map((field: any) => (
                    <div key={field.name} className={field.fullWidth ? 'md:col-span-2' : ''}>
                        <label className="block text-sm font-medium mb-2">
                            {field.label}
                            {field.required && <span className="text-red-500 ml-1">*</span>}
                        </label>

                        {renderField(field)}

                        {field.help && (
                            <p className="text-xs text-muted-foreground mt-1">{field.help}</p>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
