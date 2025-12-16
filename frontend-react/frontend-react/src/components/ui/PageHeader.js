import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
export default function PageHeader({ title, icon: Icon, children }) {
    return (_jsxs("div", { className: "flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4", children: [_jsxs("h1", { className: "text-2xl font-bold text-foreground flex items-center gap-2", children: [Icon && _jsx(Icon, { className: "w-7 h-7 text-primary" }), title] }), children && (_jsx("div", { className: "flex gap-2", children: children }))] }));
}
