import { jsx as _jsx } from "react/jsx-runtime";
const variantStyles = {
    default: 'bg-gray-500/20 text-gray-300',
    success: 'bg-green-500/20 text-green-400',
    warning: 'bg-yellow-500/20 text-yellow-400',
    danger: 'bg-red-500/20 text-red-400',
    info: 'bg-blue-500/20 text-blue-400'
};
export default function Badge({ children, variant = 'default' }) {
    return (_jsx("span", { className: `inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${variantStyles[variant]}`, children: children }));
}
