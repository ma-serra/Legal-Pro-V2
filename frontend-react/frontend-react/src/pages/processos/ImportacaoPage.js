import { jsx as _jsx } from "react/jsx-runtime";
/**
 * ImportacaoPage - Upload e ETL de Processos
 * Interface moderna para importação em massa
 */
import ImportadorProcessos from '../../components/processos/ImportadorProcessos';
export default function ImportacaoPage() {
    return (_jsx("div", { className: "p-6 max-w-7xl mx-auto", children: _jsx(ImportadorProcessos, {}) }));
}
