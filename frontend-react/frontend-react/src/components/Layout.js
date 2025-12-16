import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Outlet } from 'react-router-dom';
import Navigation from './Navigation';
export default function Layout() {
    return (_jsxs("div", { className: "min-h-screen bg-background", children: [_jsx(Navigation, {}), _jsx("main", { className: "container mx-auto px-4 py-8", children: _jsx(Outlet, {}) })] }));
}
