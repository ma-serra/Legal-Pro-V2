import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
const variantStyles = {
    primary: 'bg-primary text-primary-foreground hover:bg-primary/90',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
    success: 'bg-green-600 text-white hover:bg-green-700',
    danger: 'bg-red-600 text-white hover:bg-red-700',
    ghost: 'hover:bg-accent text-foreground'
};
const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg'
};
export default function Button({ children, variant = 'primary', size = 'md', icon: Icon, isLoading, className = '', disabled, ...props }) {
    return (_jsxs("button", { className: `inline-flex items-center justify-center gap-2 font-medium rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${variantStyles[variant]} ${sizeStyles[size]} ${className}`, disabled: disabled || isLoading, ...props, children: [isLoading ? (_jsx("div", { className: "animate-spin rounded-full h-4 w-4 border-b-2 border-current" })) : Icon ? (_jsx(Icon, { className: "w-4 h-4" })) : null, children] }));
}
