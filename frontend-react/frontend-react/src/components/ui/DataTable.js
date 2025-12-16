import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
export default function DataTable({ data, columns, isLoading = false, emptyMessage = 'Nenhum dado encontrado', onRowClick }) {
    if (isLoading) {
        return (_jsx("div", { className: "flex items-center justify-center py-12", children: _jsx("div", { className: "animate-spin rounded-full h-8 w-8 border-b-2 border-primary" }) }));
    }
    if (data.length === 0) {
        return (_jsx("div", { className: "text-center py-12 text-muted-foreground", children: emptyMessage }));
    }
    return (_jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "w-full", children: [_jsx("thead", { children: _jsx("tr", { className: "border-b border-border", children: columns.map((col, idx) => (_jsx("th", { className: `text-left py-3 px-4 font-medium text-muted-foreground ${col.className || ''}`, children: col.header }, idx))) }) }), _jsx("tbody", { children: data.map((item, rowIdx) => (_jsx("tr", { onClick: () => onRowClick?.(item), className: `border-b border-border/50 hover:bg-accent/50 transition ${onRowClick ? 'cursor-pointer' : ''}`, children: columns.map((col, colIdx) => (_jsx("td", { className: `py-3 px-4 ${col.className || ''}`, children: col.render
                                ? col.render(item)
                                : String(item[col.key] ?? '-') }, colIdx))) }, rowIdx))) })] }) }));
}
