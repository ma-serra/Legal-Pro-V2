import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
const variantStyles = {
    primary: 'from-blue-600 to-blue-800',
    success: 'from-green-600 to-green-800',
    warning: 'from-yellow-500 to-yellow-700',
    danger: 'from-red-600 to-red-800',
    info: 'from-cyan-600 to-cyan-800'
};
export default function StatsCard({ title, value, subtitle, icon: Icon, variant = 'primary' }) {
    return (_jsx("div", { className: `bg-gradient-to-br ${variantStyles[variant]} rounded-xl p-4 text-white shadow-lg hover:shadow-xl transition-all hover:-translate-y-1`, children: _jsxs("div", { className: "flex justify-between items-start", children: [_jsxs("div", { children: [_jsx("h6", { className: "text-sm font-medium opacity-90", children: title }), _jsx("h3", { className: "text-2xl font-bold mt-1", children: value }), subtitle && (_jsx("p", { className: "text-xs mt-1 opacity-75", children: subtitle }))] }), _jsx("div", { className: "opacity-75", children: _jsx(Icon, { className: "w-8 h-8" }) })] }) }));
}
