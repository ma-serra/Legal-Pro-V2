import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
};
export default function LoadingSpinner({ size = 'md', text }) {
    return (_jsxs("div", { className: "flex flex-col items-center justify-center gap-3", children: [_jsx("div", { className: `animate-spin rounded-full border-b-2 border-primary ${sizeClasses[size]}` }), text && _jsx("p", { className: "text-muted-foreground text-sm", children: text })] }));
}
