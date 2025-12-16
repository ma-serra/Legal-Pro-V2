import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Link } from 'react-router-dom';
export default function NotFound() {
    return (_jsxs("div", { className: "flex flex-col items-center justify-center min-h-[60vh] gap-4", children: [_jsx("h1", { className: "text-4xl font-bold", children: "404" }), _jsx("p", { className: "text-xl text-secondary", children: "P\u00E1gina n\u00E3o encontrada" }), _jsx(Link, { to: "/", className: "mt-4 px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90", children: "Voltar para Home" })] }));
}
