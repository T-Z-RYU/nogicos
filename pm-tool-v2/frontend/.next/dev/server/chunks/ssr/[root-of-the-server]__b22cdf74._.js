module.exports = [
"[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/action-async-storage.external.js [external] (next/dist/server/app-render/action-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/action-async-storage.external.js", () => require("next/dist/server/app-render/action-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-unit-async-storage.external.js [external] (next/dist/server/app-render/work-unit-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-unit-async-storage.external.js", () => require("next/dist/server/app-render/work-unit-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-async-storage.external.js [external] (next/dist/server/app-render/work-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-async-storage.external.js", () => require("next/dist/server/app-render/work-async-storage.external.js"));

module.exports = mod;
}),
"[project]/src/lib/api.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * PM Tool v2 - API 客户端
 */ __turbopack_context__.s([
    "applySortOrder",
    ()=>applySortOrder,
    "batchClassify",
    ()=>batchClassify,
    "clearHistory",
    ()=>clearHistory,
    "clearPendingScreenshots",
    ()=>clearPendingScreenshots,
    "deleteScreens",
    ()=>deleteScreens,
    "getAllOnboarding",
    ()=>getAllOnboarding,
    "getApowersoftConfig",
    ()=>getApowersoftConfig,
    "getCheckStatus",
    ()=>getCheckStatus,
    "getClassification",
    ()=>getClassification,
    "getDeletedScreens",
    ()=>getDeletedScreens,
    "getExportJsonUrl",
    ()=>getExportJsonUrl,
    "getExportZipUrl",
    ()=>getExportZipUrl,
    "getHistory",
    ()=>getHistory,
    "getOnboardingRange",
    ()=>getOnboardingRange,
    "getPendingScreenshots",
    ()=>getPendingScreenshots,
    "getPendingThumbnailUrl",
    ()=>getPendingThumbnailUrl,
    "getProject",
    ()=>getProject,
    "getProjects",
    ()=>getProjects,
    "getScreenshotUrl",
    ()=>getScreenshotUrl,
    "getScreenshots",
    ()=>getScreenshots,
    "getSortOrder",
    ()=>getSortOrder,
    "getStoreComparison",
    ()=>getStoreComparison,
    "getStoreIconUrl",
    ()=>getStoreIconUrl,
    "getStoreInfo",
    ()=>getStoreInfo,
    "getStoreScreenshotUrl",
    ()=>getStoreScreenshotUrl,
    "getTaxonomy",
    ()=>getTaxonomy,
    "getThumbnailUrl",
    ()=>getThumbnailUrl,
    "importFromApowersoft",
    ()=>importFromApowersoft,
    "importScreenshot",
    ()=>importScreenshot,
    "invalidateThumbnailCache",
    ()=>invalidateThumbnailCache,
    "restoreScreens",
    ()=>restoreScreens,
    "saveApowersoftConfig",
    ()=>saveApowersoftConfig,
    "saveOnboardingRange",
    ()=>saveOnboardingRange,
    "saveSortOrder",
    ()=>saveSortOrder,
    "setCheckStatus",
    ()=>setCheckStatus,
    "updateClassification",
    ()=>updateClassification,
    "uploadScreenshot",
    ()=>uploadScreenshot
]);
const API_BASE = '/api';
/**
 * 构建查询字符串
 */ function buildQueryString(params) {
    const searchParams = new URLSearchParams();
    for (const [key, value] of Object.entries(params)){
        if (value !== undefined && value !== null && value !== '') {
            searchParams.append(key, String(value));
        }
    }
    const query = searchParams.toString();
    return query ? `?${query}` : '';
}
/**
 * 通用请求函数
 */ async function fetchApi(endpoint, options) {
    const url = `${API_BASE}${endpoint}`;
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options?.headers
            }
        });
        if (!response.ok) {
            const error = await response.json().catch(()=>({
                    detail: response.statusText
                }));
            throw new Error(error.detail || `API Error: ${response.status}`);
        }
        return response.json();
    } catch (err) {
        throw err;
    }
}
async function getProjects(params) {
    const query = buildQueryString(params || {});
    return fetchApi(`/projects${query}`);
}
async function getProject(name) {
    return fetchApi(`/projects/${encodeURIComponent(name)}`);
}
async function getScreenshots(projectName, params) {
    const query = buildQueryString(params || {});
    // 使用新的 API 路径避免与 /projects/{name} 路由冲突
    return fetchApi(`/project-screenshots/${encodeURIComponent(projectName)}${query}`);
}
/**
 * 缓存版本号 - 在应用排序后更新，用于强制刷新图片
 */ let imageCacheVersion = Date.now();
function getScreenshotUrl(projectName, filename) {
    return `${API_BASE}/screenshots/${encodeURIComponent(projectName)}/${encodeURIComponent(filename)}?v=${imageCacheVersion}`;
}
function invalidateThumbnailCache() {
    imageCacheVersion = Date.now();
}
function getThumbnailUrl(projectName, filename, size = 'small') {
    return `${API_BASE}/thumbnails/${encodeURIComponent(projectName)}/${encodeURIComponent(filename)}?size=${size}&v=${imageCacheVersion}`;
}
async function getOnboardingRange(projectName) {
    return fetchApi(`/onboarding-range/${encodeURIComponent(projectName)}`);
}
async function saveOnboardingRange(projectName, start, end) {
    return fetchApi(`/onboarding-range/${encodeURIComponent(projectName)}`, {
        method: 'POST',
        body: JSON.stringify({
            start,
            end
        })
    });
}
async function getCheckStatus(projectName) {
    return fetchApi(`/check-status/${encodeURIComponent(projectName)}`);
}
async function setCheckStatus(projectName, checked) {
    return fetchApi(`/check-status/${encodeURIComponent(projectName)}`, {
        method: 'POST',
        body: JSON.stringify({
            checked
        })
    });
}
async function getAllOnboarding() {
    return fetchApi('/all-onboarding');
}
async function saveSortOrder(project, order) {
    return fetchApi('/save-sort-order', {
        method: 'POST',
        body: JSON.stringify({
            project,
            order
        })
    });
}
async function getSortOrder(projectName) {
    return fetchApi(`/sort-order/${encodeURIComponent(projectName)}`);
}
async function applySortOrder(project, order) {
    return fetchApi('/apply-sort-order', {
        method: 'POST',
        body: JSON.stringify({
            project,
            order
        })
    });
}
async function deleteScreens(project, files) {
    return fetchApi('/delete-screens', {
        method: 'POST',
        body: JSON.stringify({
            project,
            files
        })
    });
}
async function getDeletedScreens(projectName) {
    return fetchApi(`/deleted-screens/${encodeURIComponent(projectName)}`);
}
async function restoreScreens(project, batch) {
    return fetchApi('/restore-screens', {
        method: 'POST',
        body: JSON.stringify({
            project,
            batch
        })
    });
}
async function getTaxonomy() {
    return fetchApi('/taxonomy');
}
async function getClassification(projectName) {
    return fetchApi(`/classification/${encodeURIComponent(projectName)}`);
}
async function updateClassification(project, changes) {
    return fetchApi('/update-classification', {
        method: 'POST',
        body: JSON.stringify({
            project,
            changes
        })
    });
}
async function batchClassify(project, files, classification) {
    return fetchApi('/batch-classify', {
        method: 'POST',
        body: JSON.stringify({
            project,
            files,
            classification
        })
    });
}
async function getStoreComparison() {
    return fetchApi('/store-comparison');
}
async function getStoreInfo(projectName) {
    return fetchApi(`/store-info/${encodeURIComponent(projectName)}`);
}
function getStoreScreenshotUrl(projectName, filename) {
    return `${API_BASE}/store-screenshot/${encodeURIComponent(projectName)}/${encodeURIComponent(filename)}`;
}
function getStoreIconUrl(projectName) {
    return `${API_BASE}/store-icon/${encodeURIComponent(projectName)}`;
}
async function getHistory(limit = 50) {
    return fetchApi(`/history?limit=${limit}`);
}
async function clearHistory() {
    return fetchApi('/history/clear', {
        method: 'POST'
    });
}
function getExportJsonUrl(projectName) {
    return `${API_BASE}/export/${encodeURIComponent(projectName)}/json`;
}
function getExportZipUrl(projectName) {
    return `${API_BASE}/export/${encodeURIComponent(projectName)}/zip`;
}
async function getPendingScreenshots() {
    return fetchApi('/pending-screenshots');
}
function getPendingThumbnailUrl(filename) {
    return `${API_BASE}/pending-thumbnail/${encodeURIComponent(filename)}`;
}
async function importScreenshot(project, filename, position = -1) {
    return fetchApi('/import-screenshot', {
        method: 'POST',
        body: JSON.stringify({
            project,
            filename,
            position
        })
    });
}
async function uploadScreenshot(project, file) {
    const formData = new FormData();
    formData.append('project', project);
    formData.append('file', file);
    const response = await fetch(`${API_BASE}/upload-screenshot`, {
        method: 'POST',
        body: formData
    });
    if (!response.ok) {
        const error = await response.json().catch(()=>({
                detail: 'Upload failed'
            }));
        throw new Error(error.detail || 'Upload failed');
    }
    return response.json();
}
async function getApowersoftConfig() {
    return fetchApi('/apowersoft-config');
}
async function saveApowersoftConfig(path, auto_import = false) {
    return fetchApi('/apowersoft-config', {
        method: 'POST',
        body: JSON.stringify({
            path,
            auto_import
        })
    });
}
async function importFromApowersoft() {
    return fetchApi('/import-from-apowersoft', {
        method: 'POST'
    });
}
async function clearPendingScreenshots() {
    return fetchApi('/clear-pending-screenshots', {
        method: 'POST'
    });
}
}),
"[project]/src/store/project-store.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * 项目状态管理
 */ __turbopack_context__.s([
    "useProjectStore",
    ()=>useProjectStore
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/zustand/esm/react.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/lib/api.ts [app-ssr] (ecmascript)");
;
;
const useProjectStore = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["create"])((set, get)=>({
        // 初始状态
        projects: [],
        total: 0,
        stats: null,
        search: '',
        sourceFilter: 'all',
        loading: false,
        error: null,
        // 获取项目列表
        fetchProjects: async ()=>{
            set({
                loading: true,
                error: null
            });
            try {
                const { search, sourceFilter } = get();
                const params = {};
                if (search) params.search = search;
                if (sourceFilter !== 'all') params.source = sourceFilter;
                const response = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getProjects"])(params);
                set({
                    projects: response.projects,
                    total: response.total,
                    stats: response.stats || null,
                    loading: false
                });
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : '获取项目失败',
                    loading: false
                });
            }
        },
        // 设置搜索
        setSearch: (search)=>{
            set({
                search
            });
        },
        // 设置来源筛选
        setSourceFilter: (source)=>{
            set({
                sourceFilter: source
            });
        }
    }));
}),
"[project]/src/components/layout/sidebar.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "Sidebar",
    ()=>Sidebar
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/client/app-dir/link.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/framer-motion/dist/es/render/components/motion/proxy.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$components$2f$AnimatePresence$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/framer-motion/dist/es/components/AnimatePresence/index.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$project$2d$store$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/store/project-store.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$house$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Home$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/house.js [app-ssr] (ecmascript) <export default as Home>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$settings$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Settings$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/settings.js [app-ssr] (ecmascript) <export default as Settings>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$layout$2d$grid$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__LayoutGrid$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/layout-grid.js [app-ssr] (ecmascript) <export default as LayoutGrid>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$play$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Play$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/play.js [app-ssr] (ecmascript) <export default as Play>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$arrow$2d$up$2d$down$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ArrowUpDown$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/arrow-up-down.js [app-ssr] (ecmascript) <export default as ArrowUpDown>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$tags$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Tags$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/tags.js [app-ssr] (ecmascript) <export default as Tags>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$store$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Store$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/store.js [app-ssr] (ecmascript) <export default as Store>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$git$2d$branch$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__GitBranch$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/git-branch.js [app-ssr] (ecmascript) <export default as GitBranch>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$flask$2d$conical$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__FlaskConical$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/flask-conical.js [app-ssr] (ecmascript) <export default as FlaskConical>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chart$2d$column$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__BarChart3$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chart-column.js [app-ssr] (ecmascript) <export default as BarChart3>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sparkles$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Sparkles$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/sparkles.js [app-ssr] (ecmascript) <export default as Sparkles>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$smartphone$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Smartphone$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/smartphone.js [app-ssr] (ecmascript) <export default as Smartphone>");
'use client';
;
;
;
;
;
;
;
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
// Logo URL helper
function getLogoUrl(projectName) {
    // 从 downloads_2024/Fitbit 提取 Fitbit
    const appName = projectName.includes('/') ? projectName.split('/').pop() : projectName;
    return `${API_BASE}/api/logo/${appName}`;
}
function Sidebar() {
    const pathname = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["usePathname"])();
    const { projects, fetchProjects, loading } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$project$2d$store$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useProjectStore"])();
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        fetchProjects();
    }, [
        fetchProjects
    ]);
    // 获取当前选中的项目
    const currentProject = pathname.startsWith('/project/') ? decodeURIComponent(pathname.replace('/project/', '')) : null;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("aside", {
        className: "sidebar",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "sidebar-header",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                    href: "/",
                    className: "logo",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$layout$2d$grid$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__LayoutGrid$3e$__["LayoutGrid"], {
                            className: "logo-icon"
                        }, void 0, false, {
                            fileName: "[project]/src/components/layout/sidebar.tsx",
                            lineNumber: 40,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            children: "PM Lab"
                        }, void 0, false, {
                            fileName: "[project]/src/components/layout/sidebar.tsx",
                            lineNumber: 41,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/src/components/layout/sidebar.tsx",
                    lineNumber: 39,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/src/components/layout/sidebar.tsx",
                lineNumber: 38,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "sidebar-section",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h3", {
                        children: "导航"
                    }, void 0, false, {
                        fileName: "[project]/src/components/layout/sidebar.tsx",
                        lineNumber: 47,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("nav", {
                        className: "project-list",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                            href: "/",
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["motion"].div, {
                                className: `project-item ${pathname === '/' ? 'active' : ''}`,
                                whileHover: {
                                    x: 2
                                },
                                transition: {
                                    duration: 0.15
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$house$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Home$3e$__["Home"], {
                                        size: 18,
                                        style: {
                                            opacity: 0.7
                                        }
                                    }, void 0, false, {
                                        fileName: "[project]/src/components/layout/sidebar.tsx",
                                        lineNumber: 55,
                                        columnNumber: 15
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        className: "project-name",
                                        children: "全部项目"
                                    }, void 0, false, {
                                        fileName: "[project]/src/components/layout/sidebar.tsx",
                                        lineNumber: 56,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/components/layout/sidebar.tsx",
                                lineNumber: 50,
                                columnNumber: 13
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/src/components/layout/sidebar.tsx",
                            lineNumber: 49,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/src/components/layout/sidebar.tsx",
                        lineNumber: 48,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/layout/sidebar.tsx",
                lineNumber: 46,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "sidebar-section",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h3", {
                        children: "工具"
                    }, void 0, false, {
                        fileName: "[project]/src/components/layout/sidebar.tsx",
                        lineNumber: 64,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("nav", {
                        className: "project-list",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                href: "/onboarding",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["motion"].div, {
                                    className: `project-item ${pathname === '/onboarding' ? 'active' : ''}`,
                                    whileHover: {
                                        x: 2
                                    },
                                    transition: {
                                        duration: 0.15
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$play$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Play$3e$__["Play"], {
                                            size: 18,
                                            style: {
                                                opacity: 0.7
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 72,
                                            columnNumber: 15
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            className: "project-name",
                                            children: "Onboarding"
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 73,
                                            columnNumber: 15
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/src/components/layout/sidebar.tsx",
                                    lineNumber: 67,
                                    columnNumber: 13
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/src/components/layout/sidebar.tsx",
                                lineNumber: 66,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                href: "/sort",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["motion"].div, {
                                    className: `project-item ${pathname === '/sort' ? 'active' : ''}`,
                                    whileHover: {
                                        x: 2
                                    },
                                    transition: {
                                        duration: 0.15
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$arrow$2d$up$2d$down$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ArrowUpDown$3e$__["ArrowUpDown"], {
                                            size: 18,
                                            style: {
                                                opacity: 0.7
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 82,
                                            columnNumber: 15
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            className: "project-name",
                                            children: "排序"
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 83,
                                            columnNumber: 15
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/src/components/layout/sidebar.tsx",
                                    lineNumber: 77,
                                    columnNumber: 13
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/src/components/layout/sidebar.tsx",
                                lineNumber: 76,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                href: "/classify",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["motion"].div, {
                                    className: `project-item ${pathname.startsWith('/classify') ? 'active' : ''}`,
                                    whileHover: {
                                        x: 2
                                    },
                                    transition: {
                                        duration: 0.15
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$tags$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Tags$3e$__["Tags"], {
                                            size: 18,
                                            style: {
                                                opacity: 0.7
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 92,
                                            columnNumber: 15
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            className: "project-name",
                                            children: "分类"
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 93,
                                            columnNumber: 15
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/src/components/layout/sidebar.tsx",
                                    lineNumber: 87,
                                    columnNumber: 13
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/src/components/layout/sidebar.tsx",
                                lineNumber: 86,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                href: "/branch",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["motion"].div, {
                                    className: `project-item ${pathname === '/branch' ? 'active' : ''}`,
                                    whileHover: {
                                        x: 2
                                    },
                                    transition: {
                                        duration: 0.15
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$git$2d$branch$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__GitBranch$3e$__["GitBranch"], {
                                            size: 18,
                                            style: {
                                                opacity: 0.7
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 102,
                                            columnNumber: 15
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            className: "project-name",
                                            children: "分支流程"
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 103,
                                            columnNumber: 15
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/src/components/layout/sidebar.tsx",
                                    lineNumber: 97,
                                    columnNumber: 13
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/src/components/layout/sidebar.tsx",
                                lineNumber: 96,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                href: "/store",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["motion"].div, {
                                    className: `project-item ${pathname === '/store' ? 'active' : ''}`,
                                    whileHover: {
                                        x: 2
                                    },
                                    transition: {
                                        duration: 0.15
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$store$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Store$3e$__["Store"], {
                                            size: 18,
                                            style: {
                                                opacity: 0.7
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 112,
                                            columnNumber: 15
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            className: "project-name",
                                            children: "商店对比"
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 113,
                                            columnNumber: 15
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/src/components/layout/sidebar.tsx",
                                    lineNumber: 107,
                                    columnNumber: 13
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/src/components/layout/sidebar.tsx",
                                lineNumber: 106,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                href: "/flow-lab",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["motion"].div, {
                                    className: `project-item ${pathname === '/flow-lab' ? 'active' : ''}`,
                                    whileHover: {
                                        x: 2
                                    },
                                    transition: {
                                        duration: 0.15
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$flask$2d$conical$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__FlaskConical$3e$__["FlaskConical"], {
                                            size: 18,
                                            style: {
                                                opacity: 0.7,
                                                color: '#f59e0b'
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 122,
                                            columnNumber: 15
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            className: "project-name",
                                            children: "Flow Lab"
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 123,
                                            columnNumber: 15
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            style: {
                                                fontSize: '10px',
                                                color: '#f59e0b',
                                                marginLeft: '4px'
                                            },
                                            children: "实验"
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 124,
                                            columnNumber: 15
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/src/components/layout/sidebar.tsx",
                                    lineNumber: 117,
                                    columnNumber: 13
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/src/components/layout/sidebar.tsx",
                                lineNumber: 116,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                href: "/analysis/compare",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["motion"].div, {
                                    className: `project-item ${pathname.startsWith('/analysis') ? 'active' : ''}`,
                                    whileHover: {
                                        x: 2
                                    },
                                    transition: {
                                        duration: 0.15
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chart$2d$column$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__BarChart3$3e$__["BarChart3"], {
                                            size: 18,
                                            style: {
                                                opacity: 0.7,
                                                color: '#ec4899'
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 133,
                                            columnNumber: 15
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            className: "project-name",
                                            children: "竞品分析"
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 134,
                                            columnNumber: 15
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            style: {
                                                fontSize: '10px',
                                                color: '#ec4899',
                                                marginLeft: '4px'
                                            },
                                            children: "NEW"
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 135,
                                            columnNumber: 15
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/src/components/layout/sidebar.tsx",
                                    lineNumber: 128,
                                    columnNumber: 13
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/src/components/layout/sidebar.tsx",
                                lineNumber: 127,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                href: "/builder",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["motion"].div, {
                                    className: `project-item ${pathname === '/builder' ? 'active' : ''}`,
                                    whileHover: {
                                        x: 2
                                    },
                                    transition: {
                                        duration: 0.15
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sparkles$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Sparkles$3e$__["Sparkles"], {
                                            size: 18,
                                            style: {
                                                opacity: 0.7,
                                                color: '#a855f7'
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 144,
                                            columnNumber: 15
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            className: "project-name",
                                            children: "构建器"
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 145,
                                            columnNumber: 15
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            style: {
                                                fontSize: '10px',
                                                color: '#a855f7',
                                                marginLeft: '4px'
                                            },
                                            children: "NEW"
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 146,
                                            columnNumber: 15
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/src/components/layout/sidebar.tsx",
                                    lineNumber: 139,
                                    columnNumber: 13
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/src/components/layout/sidebar.tsx",
                                lineNumber: 138,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                href: "/onboarding-demo",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["motion"].div, {
                                    className: `project-item ${pathname === '/onboarding-demo' ? 'active' : ''}`,
                                    whileHover: {
                                        x: 2
                                    },
                                    transition: {
                                        duration: 0.15
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$smartphone$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Smartphone$3e$__["Smartphone"], {
                                            size: 18,
                                            style: {
                                                opacity: 0.7,
                                                color: '#ec4899'
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 155,
                                            columnNumber: 15
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            className: "project-name",
                                            children: "VitaFlow Demo"
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 156,
                                            columnNumber: 15
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            style: {
                                                fontSize: '10px',
                                                color: '#ec4899',
                                                marginLeft: '4px'
                                            },
                                            children: "🎯"
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/layout/sidebar.tsx",
                                            lineNumber: 157,
                                            columnNumber: 15
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/src/components/layout/sidebar.tsx",
                                    lineNumber: 150,
                                    columnNumber: 13
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/src/components/layout/sidebar.tsx",
                                lineNumber: 149,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/layout/sidebar.tsx",
                        lineNumber: 65,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/layout/sidebar.tsx",
                lineNumber: 63,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "sidebar-section",
                style: {
                    flex: 1,
                    overflow: 'auto',
                    borderBottom: 'none'
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h3", {
                        children: [
                            "项目 ",
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                children: projects.length
                            }, void 0, false, {
                                fileName: "[project]/src/components/layout/sidebar.tsx",
                                lineNumber: 166,
                                columnNumber: 14
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/layout/sidebar.tsx",
                        lineNumber: 165,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "project-list",
                        children: loading ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "project-item",
                            style: {
                                cursor: 'default'
                            },
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                className: "text-muted",
                                children: "加载中..."
                            }, void 0, false, {
                                fileName: "[project]/src/components/layout/sidebar.tsx",
                                lineNumber: 171,
                                columnNumber: 15
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/src/components/layout/sidebar.tsx",
                            lineNumber: 170,
                            columnNumber: 13
                        }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$components$2f$AnimatePresence$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["AnimatePresence"], {
                            children: projects.map((project, index)=>{
                                const isActive = currentProject === project.name;
                                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                                    href: `/project/${encodeURIComponent(project.name)}`,
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["motion"].div, {
                                        className: `project-item ${isActive ? 'active' : ''}`,
                                        initial: {
                                            opacity: 0,
                                            x: -10
                                        },
                                        animate: {
                                            opacity: 1,
                                            x: 0
                                        },
                                        transition: {
                                            delay: index * 0.02,
                                            duration: 0.2
                                        },
                                        whileHover: {
                                            x: 2
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                className: "project-logo",
                                                style: {
                                                    backgroundColor: 'transparent',
                                                    overflow: 'hidden',
                                                    padding: 0
                                                },
                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("img", {
                                                    src: getLogoUrl(project.name),
                                                    alt: project.display_name,
                                                    width: 24,
                                                    height: 24,
                                                    style: {
                                                        width: '100%',
                                                        height: '100%',
                                                        objectFit: 'cover',
                                                        borderRadius: '6px'
                                                    },
                                                    onError: (e)=>{
                                                        // 加载失败时显示首字母
                                                        const target = e.target;
                                                        target.style.display = 'none';
                                                        const parent = target.parentElement;
                                                        if (parent) {
                                                            parent.style.backgroundColor = project.color;
                                                            parent.textContent = project.initial;
                                                        }
                                                    }
                                                }, void 0, false, {
                                                    fileName: "[project]/src/components/layout/sidebar.tsx",
                                                    lineNumber: 195,
                                                    columnNumber: 25
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/src/components/layout/sidebar.tsx",
                                                lineNumber: 187,
                                                columnNumber: 23
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                className: "project-name",
                                                children: project.display_name
                                            }, void 0, false, {
                                                fileName: "[project]/src/components/layout/sidebar.tsx",
                                                lineNumber: 219,
                                                columnNumber: 23
                                            }, this),
                                            project.data_source && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                className: "text-xs",
                                                style: {
                                                    color: project.data_source === 'Mobbin' ? '#A78BFA' : '#34D399',
                                                    opacity: 0.8,
                                                    marginLeft: '4px'
                                                },
                                                children: project.data_source === 'Mobbin' ? 'M' : 'S'
                                            }, void 0, false, {
                                                fileName: "[project]/src/components/layout/sidebar.tsx",
                                                lineNumber: 222,
                                                columnNumber: 25
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                className: "project-count",
                                                children: project.screen_count
                                            }, void 0, false, {
                                                fileName: "[project]/src/components/layout/sidebar.tsx",
                                                lineNumber: 234,
                                                columnNumber: 23
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/src/components/layout/sidebar.tsx",
                                        lineNumber: 179,
                                        columnNumber: 21
                                    }, this)
                                }, project.name, false, {
                                    fileName: "[project]/src/components/layout/sidebar.tsx",
                                    lineNumber: 178,
                                    columnNumber: 19
                                }, this);
                            })
                        }, void 0, false, {
                            fileName: "[project]/src/components/layout/sidebar.tsx",
                            lineNumber: 174,
                            columnNumber: 13
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/src/components/layout/sidebar.tsx",
                        lineNumber: 168,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/layout/sidebar.tsx",
                lineNumber: 164,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "sidebar-section",
                style: {
                    borderTop: '1px solid var(--border-subtle)'
                },
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$client$2f$app$2d$dir$2f$link$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                    href: "/settings",
                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["motion"].div, {
                        className: `project-item ${pathname === '/settings' ? 'active' : ''}`,
                        whileHover: {
                            x: 2
                        },
                        transition: {
                            duration: 0.15
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$settings$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Settings$3e$__["Settings"], {
                                size: 18,
                                style: {
                                    opacity: 0.7
                                }
                            }, void 0, false, {
                                fileName: "[project]/src/components/layout/sidebar.tsx",
                                lineNumber: 252,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                className: "project-name",
                                children: "设置"
                            }, void 0, false, {
                                fileName: "[project]/src/components/layout/sidebar.tsx",
                                lineNumber: 253,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/layout/sidebar.tsx",
                        lineNumber: 247,
                        columnNumber: 11
                    }, this)
                }, void 0, false, {
                    fileName: "[project]/src/components/layout/sidebar.tsx",
                    lineNumber: 246,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/src/components/layout/sidebar.tsx",
                lineNumber: 245,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/src/components/layout/sidebar.tsx",
        lineNumber: 36,
        columnNumber: 5
    }, this);
}
}),
"[project]/src/components/layout/app-layout.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "AppLayout",
    ()=>AppLayout
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$layout$2f$sidebar$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/layout/sidebar.tsx [app-ssr] (ecmascript)");
'use client';
;
;
function AppLayout({ children }) {
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "app-layout",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$layout$2f$sidebar$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Sidebar"], {}, void 0, false, {
                fileName: "[project]/src/components/layout/app-layout.tsx",
                lineNumber: 13,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
                className: "main-content",
                children: children
            }, void 0, false, {
                fileName: "[project]/src/components/layout/app-layout.tsx",
                lineNumber: 14,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/src/components/layout/app-layout.tsx",
        lineNumber: 12,
        columnNumber: 5
    }, this);
}
}),
"[project]/src/components/layout/index.ts [app-ssr] (ecmascript) <locals>", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([]);
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$layout$2f$sidebar$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/layout/sidebar.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$layout$2f$app$2d$layout$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/layout/app-layout.tsx [app-ssr] (ecmascript)");
;
;
}),
"[project]/src/components/sort/PreviewPanel.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "PreviewPanel",
    ()=>PreviewPanel
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/framer-motion/dist/es/render/components/motion/proxy.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$components$2f$AnimatePresence$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/framer-motion/dist/es/components/AnimatePresence/index.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$left$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronLeft$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-left.js [app-ssr] (ecmascript) <export default as ChevronLeft>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$right$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronRight$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-right.js [app-ssr] (ecmascript) <export default as ChevronRight>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/x.js [app-ssr] (ecmascript) <export default as X>");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/lib/api.ts [app-ssr] (ecmascript)");
'use client';
;
;
;
;
function PreviewPanel({ screenshot, projectName, currentIndex, total, onClose, onPrev, onNext, onboardingStart, onboardingEnd }) {
    const isInOnboarding = onboardingStart >= 0 && onboardingEnd >= 0 && currentIndex >= onboardingStart && currentIndex <= onboardingEnd;
    const isStart = currentIndex === onboardingStart;
    const isEnd = currentIndex === onboardingEnd;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: {
            width: '320px',
            background: '#0a0a0a',
            borderLeft: '1px solid rgba(255,255,255,0.06)',
            display: 'flex',
            flexDirection: 'column',
            flexShrink: 0
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    padding: '12px 16px',
                    background: '#111111',
                    borderBottom: '1px solid rgba(255,255,255,0.06)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        style: {
                            fontSize: '13px',
                            fontWeight: 600,
                            color: '#fff'
                        },
                        children: "预览"
                    }, void 0, false, {
                        fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                        lineNumber: 62,
                        columnNumber: 9
                    }, this),
                    screenshot && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        onClick: onClose,
                        style: {
                            background: 'none',
                            border: 'none',
                            color: '#6b7280',
                            cursor: 'pointer',
                            padding: '4px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        },
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
                            size: 16
                        }, void 0, false, {
                            fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                            lineNumber: 79,
                            columnNumber: 13
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                        lineNumber: 66,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                lineNumber: 52,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    flex: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '8px',
                    overflow: 'hidden',
                    minHeight: 0
                },
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$components$2f$AnimatePresence$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["AnimatePresence"], {
                    mode: "wait",
                    children: screenshot ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["motion"].div, {
                        initial: {
                            opacity: 0,
                            scale: 0.95
                        },
                        animate: {
                            opacity: 1,
                            scale: 1
                        },
                        exit: {
                            opacity: 0,
                            scale: 0.95
                        },
                        transition: {
                            duration: 0.15
                        },
                        style: {
                            width: '100%',
                            height: '100%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        },
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("img", {
                            src: (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getScreenshotUrl"])(projectName, screenshot.filename),
                            alt: screenshot.filename,
                            style: {
                                width: '100%',
                                height: '100%',
                                objectFit: 'contain',
                                borderRadius: '12px',
                                boxShadow: '0 8px 32px rgba(0,0,0,0.5)'
                            }
                        }, void 0, false, {
                            fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                            lineNumber: 112,
                            columnNumber: 15
                        }, this)
                    }, screenshot.filename, false, {
                        fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                        lineNumber: 98,
                        columnNumber: 13
                    }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        style: {
                            color: '#6b7280',
                            fontSize: '13px'
                        },
                        children: "点击卡片查看大图"
                    }, void 0, false, {
                        fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                        lineNumber: 125,
                        columnNumber: 13
                    }, this)
                }, void 0, false, {
                    fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                    lineNumber: 96,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                lineNumber: 85,
                columnNumber: 7
            }, this),
            screenshot && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    padding: '12px 16px',
                    background: '#111111',
                    borderTop: '1px solid rgba(255,255,255,0.06)'
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            fontSize: '12px',
                            color: '#fff',
                            fontWeight: 500,
                            marginBottom: '8px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    fontFamily: 'var(--font-mono)'
                                },
                                children: [
                                    "#",
                                    currentIndex + 1
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                                lineNumber: 153,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    color: '#6b7280'
                                },
                                children: screenshot.filename
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                                lineNumber: 156,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                        lineNumber: 142,
                        columnNumber: 11
                    }, this),
                    isInOnboarding && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: 'flex',
                            gap: '6px',
                            marginBottom: '8px'
                        },
                        children: [
                            isStart && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    padding: '2px 8px',
                                    background: '#22c55e',
                                    color: '#fff',
                                    borderRadius: '4px',
                                    fontSize: '10px',
                                    fontWeight: 600
                                },
                                children: "START"
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                                lineNumber: 169,
                                columnNumber: 17
                            }, this),
                            isEnd && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    padding: '2px 8px',
                                    background: '#f59e0b',
                                    color: '#fff',
                                    borderRadius: '4px',
                                    fontSize: '10px',
                                    fontWeight: 600
                                },
                                children: "END"
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                                lineNumber: 183,
                                columnNumber: 17
                            }, this),
                            !isStart && !isEnd && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    padding: '2px 8px',
                                    background: 'rgba(34, 197, 94, 0.2)',
                                    color: '#22c55e',
                                    borderRadius: '4px',
                                    fontSize: '10px',
                                    fontWeight: 500
                                },
                                children: "Onboarding"
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                                lineNumber: 197,
                                columnNumber: 17
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                        lineNumber: 161,
                        columnNumber: 13
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            marginTop: '8px'
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                onClick: onPrev,
                                disabled: currentIndex === 0,
                                style: {
                                    background: 'rgba(255,255,255,0.06)',
                                    border: 'none',
                                    borderRadius: '6px',
                                    padding: '6px 12px',
                                    color: currentIndex === 0 ? '#4b5563' : '#fff',
                                    cursor: currentIndex === 0 ? 'not-allowed' : 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '4px',
                                    fontSize: '12px'
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$left$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronLeft$3e$__["ChevronLeft"], {
                                        size: 14
                                    }, void 0, false, {
                                        fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                                        lineNumber: 238,
                                        columnNumber: 15
                                    }, this),
                                    "上一张"
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                                lineNumber: 222,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    color: '#6b7280',
                                    fontSize: '12px'
                                },
                                children: [
                                    currentIndex + 1,
                                    " / ",
                                    total
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                                lineNumber: 242,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                onClick: onNext,
                                disabled: currentIndex === total - 1,
                                style: {
                                    background: 'rgba(255,255,255,0.06)',
                                    border: 'none',
                                    borderRadius: '6px',
                                    padding: '6px 12px',
                                    color: currentIndex === total - 1 ? '#4b5563' : '#fff',
                                    cursor: currentIndex === total - 1 ? 'not-allowed' : 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '4px',
                                    fontSize: '12px'
                                },
                                children: [
                                    "下一张",
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$right$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronRight$3e$__["ChevronRight"], {
                                        size: 14
                                    }, void 0, false, {
                                        fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                                        lineNumber: 263,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                                lineNumber: 246,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                        lineNumber: 214,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/sort/PreviewPanel.tsx",
                lineNumber: 134,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/src/components/sort/PreviewPanel.tsx",
        lineNumber: 41,
        columnNumber: 5
    }, this);
}
}),
"[project]/src/components/sort/PendingPanel.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "PendingPanel",
    ()=>PendingPanel,
    "default",
    ()=>__TURBOPACK__default__export__
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/framer-motion/dist/es/render/components/motion/proxy.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$components$2f$AnimatePresence$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/framer-motion/dist/es/components/AnimatePresence/index.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/lib/api.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$folder$2d$open$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__FolderOpen$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/folder-open.js [app-ssr] (ecmascript) <export default as FolderOpen>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$settings$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Settings$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/settings.js [app-ssr] (ecmascript) <export default as Settings>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$refresh$2d$cw$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__RefreshCw$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/refresh-cw.js [app-ssr] (ecmascript) <export default as RefreshCw>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$check$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Check$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/check.js [app-ssr] (ecmascript) <export default as Check>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$image$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ImageIcon$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/image.js [app-ssr] (ecmascript) <export default as ImageIcon>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/trash-2.js [app-ssr] (ecmascript) <export default as Trash2>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$zap$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Zap$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/zap.js [app-ssr] (ecmascript) <export default as Zap>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/sonner/dist/index.mjs [app-ssr] (ecmascript)");
'use client';
;
;
;
;
;
;
function PendingPanel({ selectedProject, onImportSuccess, onAppendScreenshot, externalImportedFile }) {
    const [screenshots, setScreenshots] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])([]);
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [config, setConfig] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [showConfig, setShowConfig] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [configPath, setConfigPath] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])('');
    const [saving, setSaving] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [importing, setImporting] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [lastImported, setLastImported] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [importedFiles, setImportedFiles] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(new Set()) // 已导入的文件列表
    ;
    // 自动导入模式
    const [autoImport, setAutoImport] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const knownFilesRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useRef"])(new Set()) // 使用 ref 避免 stale closure
    ;
    const isAutoImportingRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useRef"])(false) // 锁机制防止并发
    ;
    const selectedProjectRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useRef"])(selectedProject) // 保持最新引用
    ;
    // 同步 selectedProject 到 ref
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        selectedProjectRef.current = selectedProject;
        // 切换项目时关闭自动导入
        if (!selectedProject) {
            setAutoImport(false);
        }
    }, [
        selectedProject
    ]);
    // 处理外部导入（从拖拽导入）
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        if (externalImportedFile) {
            setImportedFiles((prev)=>new Set(prev).add(externalImportedFile));
        }
    }, [
        externalImportedFile
    ]);
    // 自动导入新截图
    const autoImportNewFiles = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useCallback"])(async (newScreenshots)=>{
        const currentProject = selectedProjectRef.current;
        if (!currentProject || isAutoImportingRef.current) return;
        // 检测新文件
        const newFiles = newScreenshots.filter((s)=>!knownFilesRef.current.has(s.filename));
        if (newFiles.length === 0) return;
        // 按创建时间排序（确保顺序正确）
        const sortedNewFiles = newFiles.sort((a, b)=>new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
        isAutoImportingRef.current = true;
        try {
            for (const file of sortedNewFiles){
                // 再次检查项目是否改变
                if (selectedProjectRef.current !== currentProject) break;
                const result = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["importScreenshot"])(currentProject, file.filename);
                if (result.success && result.new_filename) {
                    // 使用父组件回调追加截图，确保使用同一个 store 实例
                    if (onAppendScreenshot) {
                        onAppendScreenshot(result.new_filename);
                    }
                    setImportedFiles((prev)=>new Set(prev).add(file.filename));
                    setLastImported(result.new_filename);
                    __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["toast"].success(`自动导入 ${result.new_filename}`, {
                        duration: 1500
                    });
                }
            }
        } finally{
            isAutoImportingRef.current = false;
        }
    }, [
        onAppendScreenshot
    ]);
    // 加载待处理截图
    const loadPending = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useCallback"])(async ()=>{
        setLoading(true);
        try {
            const data = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getPendingScreenshots"])();
            const currentFiles = new Set(data.screenshots.map((s)=>s.filename));
            // 自动导入模式：检测并导入新文件
            if (autoImport && selectedProjectRef.current) {
                await autoImportNewFiles(data.screenshots);
            }
            // 更新已知文件列表
            knownFilesRef.current = currentFiles;
            setScreenshots(data.screenshots);
        } catch (error) {
            console.error('Failed to load pending screenshots:', error);
        } finally{
            setLoading(false);
        }
    }, [
        autoImport,
        autoImportNewFiles
    ]);
    // 加载配置
    const loadConfig = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useCallback"])(async ()=>{
        try {
            const data = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getApowersoftConfig"])();
            setConfig(data);
            setConfigPath(data.path || '');
        } catch (error) {
            console.error('Failed to load config:', error);
        }
    }, []);
    // 初始化
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        loadPending();
        loadConfig();
        // 每 1 秒刷新一次
        const interval = setInterval(loadPending, 1000);
        return ()=>clearInterval(interval);
    }, [
        loadPending,
        loadConfig
    ]);
    // 切换自动导入模式
    const toggleAutoImport = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useCallback"])(()=>{
        if (!selectedProject) {
            __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["toast"].error('请先选择一个项目');
            return;
        }
        setAutoImport((prev)=>{
            const newValue = !prev;
            if (newValue) {
                // 开启时，记录当前所有文件为已知（不导入旧文件）
                knownFilesRef.current = new Set(screenshots.map((s)=>s.filename));
                __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["toast"].success('自动导入已开启：新截图将自动追加到项目末尾');
            } else {
                __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["toast"].info('自动导入已关闭');
            }
            return newValue;
        });
    }, [
        selectedProject,
        screenshots
    ]);
    // 保存配置
    const handleSaveConfig = async ()=>{
        setSaving(true);
        try {
            await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["saveApowersoftConfig"])(configPath, config?.auto_import || false);
            await loadConfig();
            await loadPending();
            setShowConfig(false);
        } catch (error) {
            console.error('Failed to save config:', error);
            __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["toast"].error('保存配置失败: ' + error.message);
        } finally{
            setSaving(false);
        }
    };
    // 清除所有待处理截图
    const handleClearAll = async ()=>{
        if (screenshots.length === 0) {
            __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["toast"].info('没有需要清除的截图');
            return;
        }
        if (!confirm(`确定要清除全部 ${screenshots.length} 张待处理截图吗？\n\n此操作不可恢复！`)) {
            return;
        }
        try {
            const result = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["clearPendingScreenshots"])();
            if (result.success) {
                __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["toast"].success(result.message);
                setImportedFiles(new Set()); // 清空已导入标记
                await loadPending();
            }
        } catch (error) {
            console.error('Failed to clear screenshots:', error);
            __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["toast"].error('清除失败: ' + error.message);
        }
    };
    // 导入截图
    const handleImport = async (filename)=>{
        if (!selectedProject) {
            __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["toast"].error('请先选择一个项目');
            return;
        }
        setImporting(filename);
        try {
            const result = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["importScreenshot"])(selectedProject, filename);
            if (result.success) {
                // 显示成功提示
                setLastImported(result.new_filename || filename);
                __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["toast"].success(`已导入 ${result.new_filename || filename}`);
                setTimeout(()=>setLastImported(null), 3000);
                // 标记为已导入
                setImportedFiles((prev)=>new Set(prev).add(filename));
                await loadPending();
                onImportSuccess();
            } else {
                __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["toast"].error('导入失败: ' + result.message);
            }
        } catch (error) {
            console.error('Failed to import:', error);
            __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["toast"].error('导入失败: ' + error.message);
        } finally{
            setImporting(null);
        }
    };
    // 处理拖拽
    const handleDragStart = (e, screenshot)=>{
        e.dataTransfer.setData('application/x-pending-screenshot', JSON.stringify({
            filename: screenshot.filename,
            type: 'pending'
        }));
        e.dataTransfer.effectAllowed = 'copy';
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: {
            background: 'var(--bg-card)',
            borderRadius: '8px',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
            height: '100%'
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 16px',
                    borderBottom: '1px solid var(--border-default)'
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$image$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ImageIcon$3e$__["ImageIcon"], {
                                size: 16,
                                style: {
                                    color: 'var(--text-muted)'
                                }
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                lineNumber: 270,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    fontWeight: 500,
                                    fontSize: '13px'
                                },
                                children: "待处理 Pending"
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                lineNumber: 271,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    padding: '2px 6px',
                                    background: 'var(--bg-secondary)',
                                    borderRadius: '10px',
                                    fontSize: '11px',
                                    color: 'var(--text-muted)'
                                },
                                children: screenshots.length
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                lineNumber: 274,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/sort/PendingPanel.tsx",
                        lineNumber: 269,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: 'flex',
                            gap: '4px'
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                onClick: toggleAutoImport,
                                disabled: !selectedProject,
                                style: {
                                    padding: '4px',
                                    background: autoImport ? 'var(--warning)' : 'transparent',
                                    border: 'none',
                                    color: autoImport ? '#000' : selectedProject ? 'var(--text-muted)' : 'var(--text-muted)',
                                    cursor: selectedProject ? 'pointer' : 'not-allowed',
                                    borderRadius: '4px',
                                    opacity: selectedProject ? 1 : 0.5,
                                    transition: 'all 0.2s'
                                },
                                title: autoImport ? '关闭自动导入' : '开启自动导入（新截图自动追加到末尾）',
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$zap$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Zap$3e$__["Zap"], {
                                    size: 14
                                }, void 0, false, {
                                    fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                    lineNumber: 304,
                                    columnNumber: 13
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                lineNumber: 289,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                onClick: loadPending,
                                disabled: loading,
                                style: {
                                    padding: '4px',
                                    background: 'transparent',
                                    border: 'none',
                                    color: 'var(--text-muted)',
                                    cursor: 'pointer',
                                    borderRadius: '4px'
                                },
                                title: "刷新",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$refresh$2d$cw$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__RefreshCw$3e$__["RefreshCw"], {
                                    size: 14,
                                    className: loading ? 'animate-spin' : ''
                                }, void 0, false, {
                                    fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                    lineNumber: 319,
                                    columnNumber: 13
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                lineNumber: 306,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                onClick: handleClearAll,
                                disabled: screenshots.length === 0,
                                style: {
                                    padding: '4px',
                                    background: 'transparent',
                                    border: 'none',
                                    color: screenshots.length > 0 ? 'var(--error)' : 'var(--text-muted)',
                                    cursor: screenshots.length > 0 ? 'pointer' : 'not-allowed',
                                    borderRadius: '4px',
                                    opacity: screenshots.length === 0 ? 0.5 : 1
                                },
                                title: "清除全部",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__["Trash2"], {
                                    size: 14
                                }, void 0, false, {
                                    fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                    lineNumber: 335,
                                    columnNumber: 13
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                lineNumber: 321,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                onClick: ()=>setShowConfig(!showConfig),
                                style: {
                                    padding: '4px',
                                    background: showConfig ? 'var(--bg-secondary)' : 'transparent',
                                    border: 'none',
                                    color: 'var(--text-muted)',
                                    cursor: 'pointer',
                                    borderRadius: '4px'
                                },
                                title: "配置",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$settings$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Settings$3e$__["Settings"], {
                                    size: 14
                                }, void 0, false, {
                                    fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                    lineNumber: 349,
                                    columnNumber: 13
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                lineNumber: 337,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/sort/PendingPanel.tsx",
                        lineNumber: 287,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/sort/PendingPanel.tsx",
                lineNumber: 260,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$components$2f$AnimatePresence$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["AnimatePresence"], {
                children: showConfig && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["motion"].div, {
                    initial: {
                        opacity: 0,
                        height: 0
                    },
                    animate: {
                        opacity: 1,
                        height: 'auto'
                    },
                    exit: {
                        opacity: 0,
                        height: 0
                    },
                    style: {
                        padding: '12px 16px',
                        borderBottom: '1px solid var(--border-default)',
                        background: 'var(--bg-secondary)'
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                marginBottom: '8px',
                                fontSize: '12px',
                                color: 'var(--text-muted)'
                            },
                            children: "傲软投屏截图目录"
                        }, void 0, false, {
                            fileName: "[project]/src/components/sort/PendingPanel.tsx",
                            lineNumber: 367,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: 'flex',
                                flexDirection: 'column',
                                gap: '8px'
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                    type: "text",
                                    value: configPath,
                                    onChange: (e)=>setConfigPath(e.target.value),
                                    placeholder: "C:\\Users\\...\\Pictures\\Apowersoft",
                                    style: {
                                        width: '100%',
                                        padding: '8px 10px',
                                        background: 'var(--bg-primary)',
                                        border: '1px solid var(--border-default)',
                                        borderRadius: '4px',
                                        color: 'var(--text-primary)',
                                        fontSize: '12px',
                                        boxSizing: 'border-box'
                                    }
                                }, void 0, false, {
                                    fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                    lineNumber: 372,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                    onClick: handleSaveConfig,
                                    disabled: saving,
                                    style: {
                                        width: '100%',
                                        padding: '8px 12px',
                                        background: 'var(--success)',
                                        border: 'none',
                                        borderRadius: '4px',
                                        color: '#fff',
                                        fontSize: '12px',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        gap: '4px'
                                    },
                                    children: [
                                        saving ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$refresh$2d$cw$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__RefreshCw$3e$__["RefreshCw"], {
                                            size: 12,
                                            className: "animate-spin"
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                            lineNumber: 406,
                                            columnNumber: 27
                                        }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$check$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Check$3e$__["Check"], {
                                            size: 12
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                            lineNumber: 406,
                                            columnNumber: 78
                                        }, this),
                                        "保存配置"
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                    lineNumber: 388,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/src/components/sort/PendingPanel.tsx",
                            lineNumber: 371,
                            columnNumber: 13
                        }, this),
                        config?.detected && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                marginTop: '6px',
                                fontSize: '11px',
                                color: 'var(--success)'
                            },
                            children: "✓ 已自动检测到傲软目录"
                        }, void 0, false, {
                            fileName: "[project]/src/components/sort/PendingPanel.tsx",
                            lineNumber: 411,
                            columnNumber: 15
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/src/components/sort/PendingPanel.tsx",
                    lineNumber: 357,
                    columnNumber: 11
                }, this)
            }, void 0, false, {
                fileName: "[project]/src/components/sort/PendingPanel.tsx",
                lineNumber: 355,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    padding: '12px',
                    flex: 1,
                    overflowY: 'auto'
                },
                children: [
                    loading && screenshots.length === 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            textAlign: 'center',
                            padding: '20px',
                            color: 'var(--text-muted)',
                            fontSize: '12px'
                        },
                        children: "加载中..."
                    }, void 0, false, {
                        fileName: "[project]/src/components/sort/PendingPanel.tsx",
                        lineNumber: 428,
                        columnNumber: 11
                    }, this) : screenshots.length === 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            textAlign: 'center',
                            padding: '20px',
                            color: 'var(--text-muted)',
                            fontSize: '12px'
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$folder$2d$open$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__FolderOpen$3e$__["FolderOpen"], {
                                size: 24,
                                style: {
                                    marginBottom: '8px',
                                    opacity: 0.5
                                }
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                lineNumber: 433,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                children: "暂无待处理截图"
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                lineNumber: 434,
                                columnNumber: 13
                            }, this),
                            !config?.path && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    marginTop: '4px',
                                    fontSize: '11px'
                                },
                                children: "请先配置傲软截图目录"
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                lineNumber: 436,
                                columnNumber: 15
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/sort/PendingPanel.tsx",
                        lineNumber: 432,
                        columnNumber: 11
                    }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: 'grid',
                            gridTemplateColumns: 'repeat(2, 1fr)',
                            gap: '10px'
                        },
                        children: screenshots.slice(0, 12).map((screenshot)=>{
                            const isImported = importedFiles.has(screenshot.filename);
                            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                draggable: !!selectedProject,
                                onDragStart: (e)=>handleDragStart(e, screenshot),
                                style: {
                                    aspectRatio: '9/16',
                                    background: 'var(--bg-secondary)',
                                    borderRadius: '4px',
                                    overflow: 'hidden',
                                    cursor: selectedProject ? 'grab' : 'not-allowed',
                                    position: 'relative',
                                    opacity: importing === screenshot.filename ? 0.5 : isImported ? 0.6 : 1,
                                    transition: 'transform 0.15s, box-shadow 0.15s',
                                    border: isImported ? '2px solid var(--success)' : 'none'
                                },
                                title: isImported ? '已导入' : selectedProject ? `拖拽到右侧排序区域导入` : '请先选择项目',
                                onMouseEnter: (e)=>{
                                    if (selectedProject) {
                                        e.currentTarget.style.transform = 'scale(1.05)';
                                        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
                                    }
                                },
                                onMouseLeave: (e)=>{
                                    e.currentTarget.style.transform = 'scale(1)';
                                    e.currentTarget.style.boxShadow = 'none';
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("img", {
                                        src: (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getPendingThumbnailUrl"])(screenshot.filename),
                                        alt: screenshot.filename,
                                        style: {
                                            width: '100%',
                                            height: '100%',
                                            objectFit: 'cover'
                                        },
                                        loading: "lazy",
                                        onError: (e)=>{
                                            const target = e.target;
                                            target.style.display = 'none';
                                            // 显示占位图标
                                            const parent = target.parentElement;
                                            if (parent && !parent.querySelector('.img-placeholder')) {
                                                const placeholder = document.createElement('div');
                                                placeholder.className = 'img-placeholder';
                                                placeholder.style.cssText = 'position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:var(--text-muted);';
                                                placeholder.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21,15 16,10 5,21"/></svg>';
                                                parent.appendChild(placeholder);
                                            }
                                        }
                                    }, void 0, false, {
                                        fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                        lineNumber: 479,
                                        columnNumber: 17
                                    }, this),
                                    importing === screenshot.filename && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            position: 'absolute',
                                            inset: 0,
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            background: 'rgba(0,0,0,0.5)'
                                        },
                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$refresh$2d$cw$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__RefreshCw$3e$__["RefreshCw"], {
                                            size: 16,
                                            className: "animate-spin",
                                            style: {
                                                color: '#fff'
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                            lineNumber: 513,
                                            columnNumber: 21
                                        }, this)
                                    }, void 0, false, {
                                        fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                        lineNumber: 503,
                                        columnNumber: 19
                                    }, this),
                                    isImported && !importing && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            position: 'absolute',
                                            top: '4px',
                                            right: '4px',
                                            background: 'var(--success)',
                                            borderRadius: '50%',
                                            width: '20px',
                                            height: '20px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center'
                                        },
                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$check$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Check$3e$__["Check"], {
                                            size: 12,
                                            style: {
                                                color: '#fff'
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                            lineNumber: 532,
                                            columnNumber: 21
                                        }, this)
                                    }, void 0, false, {
                                        fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                        lineNumber: 518,
                                        columnNumber: 19
                                    }, this)
                                ]
                            }, screenshot.filename, true, {
                                fileName: "[project]/src/components/sort/PendingPanel.tsx",
                                lineNumber: 452,
                                columnNumber: 15
                            }, this);
                        })
                    }, void 0, false, {
                        fileName: "[project]/src/components/sort/PendingPanel.tsx",
                        lineNumber: 442,
                        columnNumber: 11
                    }, this),
                    screenshots.length > 12 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            textAlign: 'center',
                            marginTop: '8px',
                            fontSize: '11px',
                            color: 'var(--text-muted)'
                        },
                        children: [
                            "还有 ",
                            screenshots.length - 12,
                            " 张截图..."
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/sort/PendingPanel.tsx",
                        lineNumber: 541,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/sort/PendingPanel.tsx",
                lineNumber: 420,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    padding: '8px 12px',
                    borderTop: '1px solid var(--border-default)',
                    fontSize: '11px',
                    color: autoImport ? 'var(--warning)' : lastImported ? 'var(--success)' : 'var(--text-muted)',
                    textAlign: 'center',
                    transition: 'color 0.2s',
                    background: autoImport ? 'rgba(251, 191, 36, 0.1)' : 'transparent'
                },
                children: autoImport ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
                    children: "⚡ 自动导入中... 截图将自动追加"
                }, void 0, false) : lastImported ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
                    children: [
                        "✓ 已导入 ",
                        lastImported
                    ]
                }, void 0, true) : selectedProject ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
                    children: "拖拽到右侧导入 或 点击 ⚡ 开启自动导入"
                }, void 0, false) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
                    children: "请先选择项目"
                }, void 0, false)
            }, void 0, false, {
                fileName: "[project]/src/components/sort/PendingPanel.tsx",
                lineNumber: 555,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/src/components/sort/PendingPanel.tsx",
        lineNumber: 249,
        columnNumber: 5
    }, this);
}
const __TURBOPACK__default__export__ = PendingPanel;
}),
"[project]/src/components/sort/StatusBar.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "StatusBar",
    ()=>StatusBar
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$play$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Play$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/play.js [app-ssr] (ecmascript) <export default as Play>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$flag$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Flag$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/flag.js [app-ssr] (ecmascript) <export default as Flag>");
'use client';
;
;
function StatusBar({ projectName, total, selected, moved, onboardingStart, onboardingEnd }) {
    const hasOnboarding = onboardingStart >= 0 && onboardingEnd >= 0;
    const onboardingCount = hasOnboarding ? onboardingEnd - onboardingStart + 1 : 0;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: {
            padding: '8px 20px',
            background: '#0a0a0a',
            borderBottom: '1px solid rgba(255,255,255,0.04)',
            display: 'flex',
            alignItems: 'center',
            gap: '24px',
            fontSize: '12px',
            color: '#6b7280'
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("strong", {
                    style: {
                        color: '#fff'
                    },
                    children: projectName
                }, void 0, false, {
                    fileName: "[project]/src/components/sort/StatusBar.tsx",
                    lineNumber: 40,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/src/components/sort/StatusBar.tsx",
                lineNumber: 39,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    display: 'flex',
                    gap: '16px'
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        children: [
                            "总数: ",
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    color: '#fff'
                                },
                                children: total
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/StatusBar.tsx",
                                lineNumber: 46,
                                columnNumber: 15
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/sort/StatusBar.tsx",
                        lineNumber: 45,
                        columnNumber: 9
                    }, this),
                    selected > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        children: [
                            "选中: ",
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    color: '#fff'
                                },
                                children: selected
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/StatusBar.tsx",
                                lineNumber: 50,
                                columnNumber: 17
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/sort/StatusBar.tsx",
                        lineNumber: 49,
                        columnNumber: 11
                    }, this),
                    moved > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        children: [
                            "已移动: ",
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    color: '#9ca3af'
                                },
                                children: moved
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/StatusBar.tsx",
                                lineNumber: 55,
                                columnNumber: 18
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/sort/StatusBar.tsx",
                        lineNumber: 54,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/sort/StatusBar.tsx",
                lineNumber: 44,
                columnNumber: 7
            }, this),
            hasOnboarding && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    marginLeft: 'auto',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        style: {
                            color: '#22c55e',
                            fontWeight: 500
                        },
                        children: "Onboarding"
                    }, void 0, false, {
                        fileName: "[project]/src/components/sort/StatusBar.tsx",
                        lineNumber: 70,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                            background: 'rgba(34, 197, 94, 0.1)',
                            padding: '4px 8px',
                            borderRadius: '4px'
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$play$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Play$3e$__["Play"], {
                                size: 10,
                                style: {
                                    color: '#22c55e'
                                }
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/StatusBar.tsx",
                                lineNumber: 81,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    color: '#22c55e'
                                },
                                children: [
                                    "#",
                                    onboardingStart + 1
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/components/sort/StatusBar.tsx",
                                lineNumber: 82,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    color: '#6b7280'
                                },
                                children: "→"
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/StatusBar.tsx",
                                lineNumber: 83,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$flag$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Flag$3e$__["Flag"], {
                                size: 10,
                                style: {
                                    color: '#f59e0b'
                                }
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/StatusBar.tsx",
                                lineNumber: 84,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    color: '#f59e0b'
                                },
                                children: [
                                    "#",
                                    onboardingEnd + 1
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/components/sort/StatusBar.tsx",
                                lineNumber: 85,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    color: '#9ca3af',
                                    marginLeft: '4px'
                                },
                                children: [
                                    "(",
                                    onboardingCount,
                                    "张)"
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/components/sort/StatusBar.tsx",
                                lineNumber: 86,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/components/sort/StatusBar.tsx",
                        lineNumber: 71,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/sort/StatusBar.tsx",
                lineNumber: 62,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/src/components/sort/StatusBar.tsx",
        lineNumber: 26,
        columnNumber: 5
    }, this);
}
}),
"[project]/src/components/sort/ShortcutsHint.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "ShortcutsHint",
    ()=>ShortcutsHint
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/framer-motion/dist/es/render/components/motion/proxy.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$components$2f$AnimatePresence$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/framer-motion/dist/es/components/AnimatePresence/index.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$keyboard$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Keyboard$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/keyboard.js [app-ssr] (ecmascript) <export default as Keyboard>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$up$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronUp$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-up.js [app-ssr] (ecmascript) <export default as ChevronUp>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-down.js [app-ssr] (ecmascript) <export default as ChevronDown>");
'use client';
;
;
;
;
const shortcuts = [
    {
        key: 'Ctrl+A',
        action: '全选'
    },
    {
        key: 'Delete',
        action: '删除选中'
    },
    {
        key: 'Ctrl+Z',
        action: '撤销'
    },
    {
        key: '← →',
        action: '导航'
    },
    {
        key: 'Esc',
        action: '取消选择'
    },
    {
        key: '拖拽',
        action: '排序/插入'
    }
];
function ShortcutsHint() {
    const [expanded, setExpanded] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: {
            position: 'fixed',
            bottom: '20px',
            left: '260px',
            zIndex: 100
        },
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["motion"].div, {
            initial: false,
            animate: {
                height: expanded ? 'auto' : '36px'
            },
            style: {
                background: '#111111',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '8px',
                overflow: 'hidden',
                boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
            },
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                    onClick: ()=>setExpanded(!expanded),
                    style: {
                        width: '100%',
                        padding: '8px 12px',
                        background: 'none',
                        border: 'none',
                        color: '#9ca3af',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '12px'
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$keyboard$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Keyboard$3e$__["Keyboard"], {
                            size: 14
                        }, void 0, false, {
                            fileName: "[project]/src/components/sort/ShortcutsHint.tsx",
                            lineNumber: 57,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            children: "快捷键"
                        }, void 0, false, {
                            fileName: "[project]/src/components/sort/ShortcutsHint.tsx",
                            lineNumber: 58,
                            columnNumber: 11
                        }, this),
                        expanded ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__["ChevronDown"], {
                            size: 14
                        }, void 0, false, {
                            fileName: "[project]/src/components/sort/ShortcutsHint.tsx",
                            lineNumber: 59,
                            columnNumber: 23
                        }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$up$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronUp$3e$__["ChevronUp"], {
                            size: 14
                        }, void 0, false, {
                            fileName: "[project]/src/components/sort/ShortcutsHint.tsx",
                            lineNumber: 59,
                            columnNumber: 51
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/src/components/sort/ShortcutsHint.tsx",
                    lineNumber: 42,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$components$2f$AnimatePresence$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["AnimatePresence"], {
                    children: expanded && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["motion"].div, {
                        initial: {
                            opacity: 0
                        },
                        animate: {
                            opacity: 1
                        },
                        exit: {
                            opacity: 0
                        },
                        style: {
                            padding: '0 12px 12px',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '6px'
                        },
                        children: shortcuts.map(({ key, action })=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px',
                                    fontSize: '11px'
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("kbd", {
                                        style: {
                                            background: 'rgba(255,255,255,0.06)',
                                            padding: '2px 6px',
                                            borderRadius: '4px',
                                            color: '#fff',
                                            fontFamily: 'var(--font-mono)',
                                            fontSize: '10px',
                                            minWidth: '50px',
                                            textAlign: 'center'
                                        },
                                        children: key
                                    }, void 0, false, {
                                        fileName: "[project]/src/components/sort/ShortcutsHint.tsx",
                                        lineNumber: 86,
                                        columnNumber: 19
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        style: {
                                            color: '#6b7280'
                                        },
                                        children: action
                                    }, void 0, false, {
                                        fileName: "[project]/src/components/sort/ShortcutsHint.tsx",
                                        lineNumber: 100,
                                        columnNumber: 19
                                    }, this)
                                ]
                            }, key, true, {
                                fileName: "[project]/src/components/sort/ShortcutsHint.tsx",
                                lineNumber: 77,
                                columnNumber: 17
                            }, this))
                    }, void 0, false, {
                        fileName: "[project]/src/components/sort/ShortcutsHint.tsx",
                        lineNumber: 65,
                        columnNumber: 13
                    }, this)
                }, void 0, false, {
                    fileName: "[project]/src/components/sort/ShortcutsHint.tsx",
                    lineNumber: 63,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/src/components/sort/ShortcutsHint.tsx",
            lineNumber: 28,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/src/components/sort/ShortcutsHint.tsx",
        lineNumber: 20,
        columnNumber: 5
    }, this);
}
}),
"[project]/src/components/sort/ProjectSelector.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "ProjectSelector",
    ()=>ProjectSelector
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/framer-motion/dist/es/render/components/motion/proxy.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$components$2f$AnimatePresence$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/framer-motion/dist/es/components/AnimatePresence/index.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-down.js [app-ssr] (ecmascript) <export default as ChevronDown>");
'use client';
;
;
;
;
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
function getLogoUrl(projectName) {
    const appName = projectName.includes('/') ? projectName.split('/').pop() : projectName;
    return `${API_BASE}/api/logo/${appName}`;
}
// 内联样式定义（替代 style jsx 解决 scoped CSS 问题）
const styles = {
    container: {
        position: 'relative',
        minWidth: '240px'
    },
    trigger: {
        width: '100%',
        padding: '8px 12px',
        borderRadius: '8px',
        background: 'var(--bg-secondary)',
        color: 'var(--text-primary)',
        border: '1px solid var(--border-default)',
        fontSize: '14px',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: '10px'
    },
    logo: {
        width: '24px',
        height: '24px',
        borderRadius: '5px',
        objectFit: 'cover'
    },
    name: {
        flex: 1,
        textAlign: 'left'
    },
    count: {
        color: 'var(--text-secondary)',
        fontSize: '12px'
    },
    placeholder: {
        flex: 1,
        textAlign: 'left',
        color: 'var(--text-secondary)'
    },
    icon: {
        opacity: 0.5
    },
    dropdown: {
        position: 'absolute',
        top: '100%',
        left: 0,
        right: 0,
        marginTop: '4px',
        background: '#1a1a1a',
        border: '1px solid var(--border-default)',
        borderRadius: '8px',
        boxShadow: '0 10px 40px rgba(0,0,0,0.5)',
        maxHeight: '400px',
        overflowY: 'auto',
        zIndex: 100
    },
    option: {
        width: '100%',
        padding: '10px 12px',
        background: 'transparent',
        border: 'none',
        borderBottom: '1px solid rgba(255,255,255,0.04)',
        color: '#fff',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        fontSize: '13px',
        textAlign: 'left'
    },
    optionSelected: {
        background: 'rgba(255,255,255,0.08)'
    },
    optionLogo: {
        width: '28px',
        height: '28px',
        borderRadius: '6px',
        objectFit: 'cover'
    },
    optionName: {
        flex: 1
    },
    optionCount: {
        color: '#6b7280',
        fontSize: '12px'
    }
};
function ProjectSelector({ projects, selectedProject, onSelect }) {
    const [isOpen, setIsOpen] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [hoveredOption, setHoveredOption] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const dropdownRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useRef"])(null);
    // 点击外部关闭
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        const handleClickOutside = (e)=>{
            if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return ()=>document.removeEventListener('mousedown', handleClickOutside);
    }, []);
    const selectedProjectData = projects.find((p)=>p.name === selectedProject);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        ref: dropdownRef,
        style: styles.container,
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                onClick: ()=>setIsOpen(!isOpen),
                style: styles.trigger,
                children: [
                    selectedProjectData ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("img", {
                                src: getLogoUrl(selectedProjectData.name),
                                alt: selectedProjectData.display_name,
                                style: styles.logo,
                                onError: (e)=>{
                                    const target = e.target;
                                    target.style.display = 'none';
                                }
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/ProjectSelector.tsx",
                                lineNumber: 135,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: styles.name,
                                children: selectedProjectData.display_name
                            }, void 0, false, {
                                fileName: "[project]/src/components/sort/ProjectSelector.tsx",
                                lineNumber: 144,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: styles.count,
                                children: [
                                    "(",
                                    selectedProjectData.screen_count,
                                    ")"
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/components/sort/ProjectSelector.tsx",
                                lineNumber: 147,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        style: styles.placeholder,
                        children: "选择项目..."
                    }, void 0, false, {
                        fileName: "[project]/src/components/sort/ProjectSelector.tsx",
                        lineNumber: 152,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__["ChevronDown"], {
                        size: 16,
                        style: styles.icon
                    }, void 0, false, {
                        fileName: "[project]/src/components/sort/ProjectSelector.tsx",
                        lineNumber: 156,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/sort/ProjectSelector.tsx",
                lineNumber: 129,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$components$2f$AnimatePresence$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["AnimatePresence"], {
                children: isOpen && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["motion"].div, {
                    initial: {
                        opacity: 0,
                        y: -8
                    },
                    animate: {
                        opacity: 1,
                        y: 0
                    },
                    exit: {
                        opacity: 0,
                        y: -8
                    },
                    transition: {
                        duration: 0.15
                    },
                    style: styles.dropdown,
                    children: projects.map((project)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            onClick: ()=>{
                                onSelect(project.name);
                                setIsOpen(false);
                            },
                            onMouseEnter: ()=>setHoveredOption(project.name),
                            onMouseLeave: ()=>setHoveredOption(null),
                            style: {
                                ...styles.option,
                                ...selectedProject === project.name ? styles.optionSelected : {},
                                ...hoveredOption === project.name ? {
                                    background: 'rgba(255,255,255,0.05)'
                                } : {}
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("img", {
                                    src: getLogoUrl(project.name),
                                    alt: project.display_name,
                                    style: styles.optionLogo,
                                    onError: (e)=>{
                                        const target = e.target;
                                        target.style.display = 'none';
                                    }
                                }, void 0, false, {
                                    fileName: "[project]/src/components/sort/ProjectSelector.tsx",
                                    lineNumber: 184,
                                    columnNumber: 17
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: styles.optionName,
                                    children: project.display_name
                                }, void 0, false, {
                                    fileName: "[project]/src/components/sort/ProjectSelector.tsx",
                                    lineNumber: 193,
                                    columnNumber: 17
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: styles.optionCount,
                                    children: project.screen_count
                                }, void 0, false, {
                                    fileName: "[project]/src/components/sort/ProjectSelector.tsx",
                                    lineNumber: 196,
                                    columnNumber: 17
                                }, this)
                            ]
                        }, project.name, true, {
                            fileName: "[project]/src/components/sort/ProjectSelector.tsx",
                            lineNumber: 170,
                            columnNumber: 15
                        }, this))
                }, void 0, false, {
                    fileName: "[project]/src/components/sort/ProjectSelector.tsx",
                    lineNumber: 162,
                    columnNumber: 11
                }, this)
            }, void 0, false, {
                fileName: "[project]/src/components/sort/ProjectSelector.tsx",
                lineNumber: 160,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/src/components/sort/ProjectSelector.tsx",
        lineNumber: 127,
        columnNumber: 5
    }, this);
}
}),
"[project]/src/components/sort/SortableScreenshot.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "SortableScreenshot",
    ()=>SortableScreenshot
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$dnd$2d$kit$2f$sortable$2f$dist$2f$sortable$2e$esm$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@dnd-kit/sortable/dist/sortable.esm.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$dnd$2d$kit$2f$utilities$2f$dist$2f$utilities$2e$esm$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@dnd-kit/utilities/dist/utilities.esm.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$check$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Check$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/check.js [app-ssr] (ecmascript) <export default as Check>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$play$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Play$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/play.js [app-ssr] (ecmascript) <export default as Play>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$flag$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Flag$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/flag.js [app-ssr] (ecmascript) <export default as Flag>");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/lib/api.ts [app-ssr] (ecmascript)");
'use client';
;
;
;
;
;
// 内联样式定义（替代 style jsx 解决 scoped CSS 问题）
const styles = {
    card: {
        position: 'relative',
        aspectRatio: '9/16',
        overflow: 'hidden',
        background: 'var(--bg-secondary)',
        cursor: 'pointer',
        borderRadius: '6px',
        transition: 'border 150ms, box-shadow 150ms'
    },
    dragHandle: {
        position: 'absolute',
        inset: 0
    },
    image: {
        width: '100%',
        height: '100%',
        objectFit: 'cover',
        pointerEvents: 'none'
    },
    selectedOverlay: {
        position: 'absolute',
        inset: 0,
        background: 'rgba(59, 130, 246, 0.35)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        pointerEvents: 'none'
    },
    checkIcon: {
        width: '40px',
        height: '40px',
        borderRadius: '50%',
        background: '#fff',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
    },
    index: {
        position: 'absolute',
        top: '4px',
        left: '4px',
        padding: '2px 6px',
        background: 'rgba(0, 0, 0, 0.7)',
        borderRadius: '4px',
        fontSize: '10px',
        color: 'var(--text-secondary)',
        fontFamily: 'var(--font-mono)'
    },
    badge: {
        position: 'absolute',
        bottom: '4px',
        left: '4px',
        padding: '2px 6px',
        borderRadius: '4px',
        fontSize: '9px',
        color: '#fff',
        fontWeight: 600,
        display: 'flex',
        alignItems: 'center',
        gap: '2px'
    },
    onboardingDot: {
        position: 'absolute',
        bottom: '4px',
        left: '4px',
        width: '6px',
        height: '6px',
        background: '#22c55e',
        borderRadius: '50%'
    },
    newBadge: {
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        padding: '4px 8px',
        background: '#f59e0b',
        borderRadius: '4px',
        fontSize: '10px',
        color: '#fff',
        fontWeight: 700,
        textTransform: 'uppercase'
    }
};
function SortableScreenshot({ screenshot, projectName, index, isSelected, isNewlyAdded = false, onCardClick, onboardingStart, onboardingEnd }) {
    const { attributes, listeners, setNodeRef, transform, transition, isDragging } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$dnd$2d$kit$2f$sortable$2f$dist$2f$sortable$2e$esm$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useSortable"])({
        id: screenshot.filename,
        transition: {
            duration: 200,
            easing: 'cubic-bezier(0.25, 1, 0.5, 1)'
        }
    });
    const isInOnboarding = onboardingStart >= 0 && onboardingEnd >= 0 && index >= onboardingStart && index <= onboardingEnd;
    const isStart = index === onboardingStart;
    const isEnd = index === onboardingEnd;
    const wrapperStyle = {
        transform: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$dnd$2d$kit$2f$utilities$2f$dist$2f$utilities$2e$esm$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["CSS"].Transform.toString(transform),
        transition: transition || 'transform 200ms cubic-bezier(0.25, 1, 0.5, 1)',
        opacity: isDragging ? 0.3 : 1,
        zIndex: isDragging ? 100 : 'auto'
    };
    const getBorderStyle = ()=>{
        if (isDragging) return '2px dashed rgba(255,255,255,0.4)';
        if (isNewlyAdded) return '3px solid #f59e0b';
        if (isSelected) return '3px solid #3b82f6';
        if (isInOnboarding) return '2px solid #22c55e';
        return '2px solid rgba(255,255,255,0.15)';
    };
    const getBoxShadow = ()=>{
        if (isNewlyAdded) return '0 0 20px rgba(245, 158, 11, 0.5)';
        if (isSelected) return '0 0 0 2px rgba(59, 130, 246, 0.5)';
        if (isDragging) return '0 20px 40px rgba(0, 0, 0, 0.4)';
        return undefined;
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        ref: setNodeRef,
        style: wrapperStyle,
        ...attributes,
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            onClick: onCardClick,
            style: {
                ...styles.card,
                border: getBorderStyle(),
                boxShadow: getBoxShadow()
            },
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    ...listeners,
                    style: {
                        ...styles.dragHandle,
                        cursor: isDragging ? 'grabbing' : 'grab'
                    }
                }, void 0, false, {
                    fileName: "[project]/src/components/sort/SortableScreenshot.tsx",
                    lineNumber: 168,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("img", {
                    src: (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getThumbnailUrl"])(projectName, screenshot.filename, 'small'),
                    alt: screenshot.filename,
                    style: styles.image,
                    loading: "lazy"
                }, void 0, false, {
                    fileName: "[project]/src/components/sort/SortableScreenshot.tsx",
                    lineNumber: 173,
                    columnNumber: 9
                }, this),
                isSelected && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: styles.selectedOverlay,
                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: styles.checkIcon,
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$check$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Check$3e$__["Check"], {
                            size: 24,
                            style: {
                                color: '#3b82f6'
                            }
                        }, void 0, false, {
                            fileName: "[project]/src/components/sort/SortableScreenshot.tsx",
                            lineNumber: 184,
                            columnNumber: 15
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/src/components/sort/SortableScreenshot.tsx",
                        lineNumber: 183,
                        columnNumber: 13
                    }, this)
                }, void 0, false, {
                    fileName: "[project]/src/components/sort/SortableScreenshot.tsx",
                    lineNumber: 182,
                    columnNumber: 11
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: styles.index,
                    children: String(index + 1).padStart(4, '0')
                }, void 0, false, {
                    fileName: "[project]/src/components/sort/SortableScreenshot.tsx",
                    lineNumber: 190,
                    columnNumber: 9
                }, this),
                isStart && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        ...styles.badge,
                        background: '#22c55e'
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$play$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Play$3e$__["Play"], {
                            size: 8
                        }, void 0, false, {
                            fileName: "[project]/src/components/sort/SortableScreenshot.tsx",
                            lineNumber: 197,
                            columnNumber: 13
                        }, this),
                        " START"
                    ]
                }, void 0, true, {
                    fileName: "[project]/src/components/sort/SortableScreenshot.tsx",
                    lineNumber: 196,
                    columnNumber: 11
                }, this),
                isEnd && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        ...styles.badge,
                        background: '#f59e0b'
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$flag$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Flag$3e$__["Flag"], {
                            size: 8
                        }, void 0, false, {
                            fileName: "[project]/src/components/sort/SortableScreenshot.tsx",
                            lineNumber: 202,
                            columnNumber: 13
                        }, this),
                        " END"
                    ]
                }, void 0, true, {
                    fileName: "[project]/src/components/sort/SortableScreenshot.tsx",
                    lineNumber: 201,
                    columnNumber: 11
                }, this),
                isInOnboarding && !isStart && !isEnd && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: styles.onboardingDot
                }, void 0, false, {
                    fileName: "[project]/src/components/sort/SortableScreenshot.tsx",
                    lineNumber: 208,
                    columnNumber: 11
                }, this),
                isNewlyAdded && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: styles.newBadge,
                    children: "NEW"
                }, void 0, false, {
                    fileName: "[project]/src/components/sort/SortableScreenshot.tsx",
                    lineNumber: 213,
                    columnNumber: 11
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/src/components/sort/SortableScreenshot.tsx",
            lineNumber: 159,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/src/components/sort/SortableScreenshot.tsx",
        lineNumber: 154,
        columnNumber: 5
    }, this);
}
}),
"[project]/src/components/sort/DragPreview.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "DragPreview",
    ()=>DragPreview
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/framer-motion/dist/es/render/components/motion/proxy.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/lib/api.ts [app-ssr] (ecmascript)");
'use client';
;
;
;
// 内联样式定义
const styles = {
    container: {
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5), 0 0 0 2px rgba(255,255,255,0.8)',
        borderRadius: '8px',
        overflow: 'hidden',
        cursor: 'grabbing',
        position: 'relative'
    },
    imageWrapper: {
        aspectRatio: '9/16',
        overflow: 'hidden',
        background: 'var(--bg-secondary)'
    },
    image: {
        width: '100%',
        height: '100%',
        objectFit: 'cover',
        pointerEvents: 'none'
    },
    label: {
        position: 'absolute',
        bottom: '4px',
        left: '50%',
        transform: 'translateX(-50%)',
        padding: '2px 8px',
        background: 'rgba(0,0,0,0.8)',
        borderRadius: '4px',
        fontSize: '10px',
        color: '#fff',
        fontWeight: 500,
        whiteSpace: 'nowrap'
    }
};
function DragPreview({ screenshot, projectName, zoom = 100 }) {
    const previewWidth = Math.round(120 * (zoom / 100));
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["motion"].div, {
        initial: {
            scale: 1,
            rotate: 0
        },
        animate: {
            scale: 1.05,
            rotate: 2
        },
        transition: {
            duration: 0.15,
            ease: 'easeOut'
        },
        style: {
            ...styles.container,
            width: `${previewWidth}px`
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: styles.imageWrapper,
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("img", {
                    src: (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getThumbnailUrl"])(projectName, screenshot.filename, 'small'),
                    alt: screenshot.filename,
                    style: styles.image
                }, void 0, false, {
                    fileName: "[project]/src/components/sort/DragPreview.tsx",
                    lineNumber: 57,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/src/components/sort/DragPreview.tsx",
                lineNumber: 56,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: styles.label,
                children: "拖拽中..."
            }, void 0, false, {
                fileName: "[project]/src/components/sort/DragPreview.tsx",
                lineNumber: 64,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/src/components/sort/DragPreview.tsx",
        lineNumber: 50,
        columnNumber: 5
    }, this);
}
}),
"[project]/src/types/sort.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * 排序模块类型定义
 */ __turbopack_context__.s([
    "ZOOM_CONFIG",
    ()=>ZOOM_CONFIG
]);
const ZOOM_CONFIG = {
    min: 50,
    max: 200,
    step: 25,
    default: 100
};
}),
"[project]/src/components/sort/ZoomControl.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "ZoomControl",
    ()=>ZoomControl
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$zoom$2d$in$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ZoomIn$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/zoom-in.js [app-ssr] (ecmascript) <export default as ZoomIn>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$zoom$2d$out$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ZoomOut$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/zoom-out.js [app-ssr] (ecmascript) <export default as ZoomOut>");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$types$2f$sort$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/types/sort.ts [app-ssr] (ecmascript)");
'use client';
;
;
;
;
// 内联样式定义
const styles = {
    container: {
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
        padding: '4px 8px',
        background: 'var(--bg-secondary)',
        borderRadius: '8px'
    },
    btn: {
        padding: '4px',
        background: 'transparent',
        border: 'none',
        borderRadius: '4px',
        color: 'var(--text-secondary)',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'color 150ms, background 150ms'
    },
    btnDisabled: {
        color: 'var(--text-muted)',
        cursor: 'not-allowed'
    },
    btnHover: {
        background: 'rgba(255,255,255,0.1)',
        color: 'var(--text-primary)'
    },
    value: {
        padding: '2px 8px',
        background: 'transparent',
        border: 'none',
        borderRadius: '4px',
        color: 'var(--text-primary)',
        cursor: 'pointer',
        fontSize: '12px',
        fontFamily: 'var(--font-mono)',
        fontWeight: 500,
        minWidth: '48px',
        transition: 'background 150ms'
    },
    valueChanged: {
        background: 'rgba(59, 130, 246, 0.2)'
    }
};
function ZoomControl({ zoom, onZoomIn, onZoomOut, onReset, min = __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$types$2f$sort$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ZOOM_CONFIG"].min, max = __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$types$2f$sort$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ZOOM_CONFIG"].max }) {
    const isAtMin = zoom <= min;
    const isAtMax = zoom >= max;
    const isDefault = zoom === __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$types$2f$sort$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ZOOM_CONFIG"].default;
    const [hoveredBtn, setHoveredBtn] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: styles.container,
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                onClick: onZoomOut,
                disabled: isAtMin,
                style: {
                    ...styles.btn,
                    ...isAtMin ? styles.btnDisabled : {},
                    ...hoveredBtn === 'out' && !isAtMin ? styles.btnHover : {}
                },
                onMouseEnter: ()=>setHoveredBtn('out'),
                onMouseLeave: ()=>setHoveredBtn(null),
                title: "缩小 (Ctrl+-)",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$zoom$2d$out$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ZoomOut$3e$__["ZoomOut"], {
                    size: 16
                }, void 0, false, {
                    fileName: "[project]/src/components/sort/ZoomControl.tsx",
                    lineNumber: 83,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/src/components/sort/ZoomControl.tsx",
                lineNumber: 71,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                onClick: onReset,
                style: {
                    ...styles.value,
                    ...!isDefault ? styles.valueChanged : {},
                    ...hoveredBtn === 'reset' ? {
                        background: 'rgba(255,255,255,0.1)'
                    } : {}
                },
                onMouseEnter: ()=>setHoveredBtn('reset'),
                onMouseLeave: ()=>setHoveredBtn(null),
                title: "重置缩放 (Ctrl+0)",
                children: [
                    zoom,
                    "%"
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/sort/ZoomControl.tsx",
                lineNumber: 86,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                onClick: onZoomIn,
                disabled: isAtMax,
                style: {
                    ...styles.btn,
                    ...isAtMax ? styles.btnDisabled : {},
                    ...hoveredBtn === 'in' && !isAtMax ? styles.btnHover : {}
                },
                onMouseEnter: ()=>setHoveredBtn('in'),
                onMouseLeave: ()=>setHoveredBtn(null),
                title: "放大 (Ctrl++)",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$zoom$2d$in$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__ZoomIn$3e$__["ZoomIn"], {
                    size: 16
                }, void 0, false, {
                    fileName: "[project]/src/components/sort/ZoomControl.tsx",
                    lineNumber: 112,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/src/components/sort/ZoomControl.tsx",
                lineNumber: 100,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/src/components/sort/ZoomControl.tsx",
        lineNumber: 70,
        columnNumber: 5
    }, this);
}
}),
"[project]/src/components/sort/SelectionBar.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "SelectionBar",
    ()=>SelectionBar
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/framer-motion/dist/es/render/components/motion/proxy.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$square$2d$check$2d$big$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__CheckSquare$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/square-check-big.js [app-ssr] (ecmascript) <export default as CheckSquare>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/x.js [app-ssr] (ecmascript) <export default as X>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/trash-2.js [app-ssr] (ecmascript) <export default as Trash2>");
'use client';
;
;
;
// 内联样式定义（替代 style jsx 解决 scoped CSS 问题）
const styles = {
    bar: {
        position: 'fixed',
        bottom: '24px',
        left: '50%',
        transform: 'translateX(-50%)',
        background: 'rgba(30, 30, 30, 0.95)',
        backdropFilter: 'blur(12px)',
        borderRadius: '12px',
        padding: '12px 20px',
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255,255,255,0.1)',
        zIndex: 1000
    },
    info: {
        color: '#fff',
        fontSize: '14px',
        fontWeight: 500,
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
    },
    icon: {
        color: '#3b82f6'
    },
    divider: {
        width: '1px',
        height: '24px',
        background: 'rgba(255,255,255,0.2)'
    },
    btn: {
        padding: '8px 16px',
        border: 'none',
        borderRadius: '8px',
        fontSize: '13px',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        transition: 'background 150ms, opacity 150ms'
    },
    btnSecondary: {
        background: 'rgba(255,255,255,0.1)',
        color: '#fff'
    },
    btnDanger: {
        background: '#ef4444',
        color: '#fff'
    }
};
function SelectionBar({ selectedCount, onDeselect, onDelete, disabled = false }) {
    if (selectedCount === 0) return null;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$render$2f$components$2f$motion$2f$proxy$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["motion"].div, {
        initial: {
            opacity: 0,
            y: 50
        },
        animate: {
            opacity: 1,
            y: 0
        },
        exit: {
            opacity: 0,
            y: 50
        },
        transition: {
            duration: 0.2,
            ease: [
                0.25,
                1,
                0.5,
                1
            ]
        },
        style: styles.bar,
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                style: styles.info,
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$square$2d$check$2d$big$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__CheckSquare$3e$__["CheckSquare"], {
                        size: 18,
                        style: styles.icon
                    }, void 0, false, {
                        fileName: "[project]/src/components/sort/SelectionBar.tsx",
                        lineNumber: 78,
                        columnNumber: 9
                    }, this),
                    "已选择 ",
                    selectedCount,
                    " 张截图"
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/sort/SelectionBar.tsx",
                lineNumber: 77,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: styles.divider
            }, void 0, false, {
                fileName: "[project]/src/components/sort/SelectionBar.tsx",
                lineNumber: 82,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                onClick: onDeselect,
                style: {
                    ...styles.btn,
                    ...styles.btnSecondary
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
                        size: 14
                    }, void 0, false, {
                        fileName: "[project]/src/components/sort/SelectionBar.tsx",
                        lineNumber: 88,
                        columnNumber: 9
                    }, this),
                    "取消选择"
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/sort/SelectionBar.tsx",
                lineNumber: 84,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                onClick: onDelete,
                disabled: disabled,
                style: {
                    ...styles.btn,
                    ...styles.btnDanger,
                    opacity: disabled ? 0.6 : 1,
                    cursor: disabled ? 'not-allowed' : 'pointer'
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__["Trash2"], {
                        size: 14
                    }, void 0, false, {
                        fileName: "[project]/src/components/sort/SelectionBar.tsx",
                        lineNumber: 102,
                        columnNumber: 9
                    }, this),
                    "删除选中"
                ]
            }, void 0, true, {
                fileName: "[project]/src/components/sort/SelectionBar.tsx",
                lineNumber: 92,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/src/components/sort/SelectionBar.tsx",
        lineNumber: 70,
        columnNumber: 5
    }, this);
}
}),
"[project]/src/components/sort/index.ts [app-ssr] (ecmascript) <locals>", ((__turbopack_context__) => {
"use strict";

// Layout Components
__turbopack_context__.s([]);
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$PreviewPanel$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/sort/PreviewPanel.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$PendingPanel$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/sort/PendingPanel.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$StatusBar$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/sort/StatusBar.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$ShortcutsHint$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/sort/ShortcutsHint.tsx [app-ssr] (ecmascript)");
// Interactive Components
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$ProjectSelector$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/sort/ProjectSelector.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$SortableScreenshot$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/sort/SortableScreenshot.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$DragPreview$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/sort/DragPreview.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$ZoomControl$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/sort/ZoomControl.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$SelectionBar$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/sort/SelectionBar.tsx [app-ssr] (ecmascript)");
;
;
;
;
;
;
;
;
;
}),
"[project]/src/store/sort/data-slice.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * 数据 Slice - 管理截图数据的加载、保存和操作
 */ __turbopack_context__.s([
    "createDataSlice",
    ()=>createDataSlice
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/lib/api.ts [app-ssr] (ecmascript)");
;
const createDataSlice = (set, get)=>({
        screenshots: [],
        sortedScreenshots: [],
        deletedBatches: [],
        onboardingRange: {
            start: -1,
            end: -1
        },
        fetchData: async (projectName)=>{
            set({
                loading: true,
                error: null
            });
            (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["invalidateThumbnailCache"])();
            try {
                const [screenshotsRes, deletedRes, onboardingRes] = await Promise.all([
                    (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getScreenshots"])(projectName),
                    (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getDeletedScreens"])(projectName),
                    (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getOnboardingRange"])(projectName).catch(()=>({
                            start: -1,
                            end: -1
                        }))
                ]);
                set({
                    screenshots: screenshotsRes.screenshots,
                    sortedScreenshots: [
                        ...screenshotsRes.screenshots
                    ],
                    deletedBatches: deletedRes.batches,
                    onboardingRange: onboardingRes,
                    selectedFiles: new Set(),
                    previewIndex: null,
                    hasChanges: false,
                    loading: false
                });
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : '加载失败',
                    loading: false
                });
            }
        },
        reorder: (oldIndex, newIndex)=>{
            const { sortedScreenshots } = get();
            const newSorted = [
                ...sortedScreenshots
            ];
            const [removed] = newSorted.splice(oldIndex, 1);
            newSorted.splice(newIndex, 0, removed);
            set({
                sortedScreenshots: newSorted,
                hasChanges: true
            });
        },
        deleteSelected: async (projectName)=>{
            const { selectedFiles, sortedScreenshots } = get();
            if (selectedFiles.size === 0) return;
            set({
                saving: true,
                error: null
            });
            try {
                await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["deleteScreens"])(projectName, Array.from(selectedFiles));
                const newSorted = sortedScreenshots.filter((s)=>!selectedFiles.has(s.filename));
                const deletedRes = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getDeletedScreens"])(projectName);
                set({
                    sortedScreenshots: newSorted,
                    deletedBatches: deletedRes.batches,
                    selectedFiles: new Set(),
                    hasChanges: true,
                    saving: false
                });
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : '删除失败',
                    saving: false
                });
            }
        },
        restoreBatch: async (projectName, batch)=>{
            set({
                saving: true,
                error: null
            });
            try {
                await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["restoreScreens"])(projectName, batch);
                await get().fetchData(projectName);
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : '恢复失败',
                    saving: false
                });
            }
        },
        saveSortOrder: async (projectName)=>{
            const { sortedScreenshots } = get();
            set({
                saving: true,
                error: null
            });
            try {
                const order = sortedScreenshots.map((s, index)=>({
                        original_file: s.filename,
                        new_index: index + 1
                    }));
                await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["saveSortOrder"])(projectName, order);
                set({
                    saving: false,
                    hasChanges: false
                });
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : '保存失败',
                    saving: false
                });
            }
        },
        applySortOrder: async (projectName)=>{
            const { sortedScreenshots } = get();
            set({
                saving: true,
                error: null
            });
            try {
                const order = sortedScreenshots.map((s, index)=>({
                        original_file: s.filename,
                        new_index: index + 1
                    }));
                await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["applySortOrder"])(projectName, order);
                (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["invalidateThumbnailCache"])();
                const updatedScreenshots = sortedScreenshots.map((s, index)=>{
                    const ext = s.filename.split('.').pop() || 'png';
                    const newFilename = `${String(index + 1).padStart(4, '0')}.${ext}`;
                    return {
                        ...s,
                        filename: newFilename
                    };
                });
                set({
                    screenshots: updatedScreenshots,
                    sortedScreenshots: updatedScreenshots,
                    hasChanges: false,
                    saving: false
                });
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : '应用失败',
                    saving: false
                });
            }
        },
        insertScreenshotAt: (screenshot, index)=>{
            const { sortedScreenshots } = get();
            const newSorted = [
                ...sortedScreenshots
            ];
            newSorted.splice(index, 0, screenshot);
            set({
                sortedScreenshots: newSorted,
                hasChanges: true
            });
        }
    });
}),
"[project]/src/store/sort/selection-slice.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * 选择 Slice - 管理截图的选择状态
 */ __turbopack_context__.s([
    "createSelectionSlice",
    ()=>createSelectionSlice
]);
const createSelectionSlice = (set, get)=>({
        selectedFiles: new Set(),
        lastClickedIndex: null,
        toggleSelect: (filename)=>{
            const { selectedFiles } = get();
            const newSelected = new Set(selectedFiles);
            if (newSelected.has(filename)) {
                newSelected.delete(filename);
            } else {
                newSelected.add(filename);
            }
            set({
                selectedFiles: newSelected
            });
        },
        selectAll: ()=>{
            const { sortedScreenshots } = get();
            set({
                selectedFiles: new Set(sortedScreenshots.map((s)=>s.filename))
            });
        },
        deselectAll: ()=>{
            set({
                selectedFiles: new Set()
            });
        },
        setSelectedFiles: (files)=>{
            set({
                selectedFiles: files
            });
        },
        setLastClickedIndex: (index)=>{
            set({
                lastClickedIndex: index
            });
        }
    });
}),
"[project]/src/store/sort/preview-slice.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * 预览 Slice - 管理截图预览状态
 */ __turbopack_context__.s([
    "createPreviewSlice",
    ()=>createPreviewSlice
]);
const createPreviewSlice = (set, get)=>({
        previewIndex: null,
        setPreviewIndex: (index)=>{
            set({
                previewIndex: index
            });
        },
        prevPreview: ()=>{
            const { previewIndex } = get();
            if (previewIndex !== null && previewIndex > 0) {
                set({
                    previewIndex: previewIndex - 1
                });
            }
        },
        nextPreview: ()=>{
            const { previewIndex, sortedScreenshots } = get();
            if (previewIndex !== null && previewIndex < sortedScreenshots.length - 1) {
                set({
                    previewIndex: previewIndex + 1
                });
            }
        }
    });
}),
"[project]/src/store/sort/ui-slice.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * UI Slice - 管理 UI 状态
 */ __turbopack_context__.s([
    "createUISlice",
    ()=>createUISlice
]);
const createUISlice = (set)=>({
        loading: false,
        saving: false,
        error: null,
        hasChanges: false,
        setLoading: (loading)=>{
            set({
                loading
            });
        },
        setSaving: (saving)=>{
            set({
                saving
            });
        },
        setError: (error)=>{
            set({
                error
            });
        },
        setHasChanges: (hasChanges)=>{
            set({
                hasChanges
            });
        }
    });
}),
"[project]/src/store/sort/zoom-slice.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * 缩放 Slice - 管理缩放状态
 */ __turbopack_context__.s([
    "createZoomSlice",
    ()=>createZoomSlice
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$types$2f$sort$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/types/sort.ts [app-ssr] (ecmascript)");
;
const createZoomSlice = (set, get)=>({
        zoom: __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$types$2f$sort$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ZOOM_CONFIG"].default,
        zoomIn: ()=>{
            const { zoom } = get();
            set({
                zoom: Math.min(zoom + __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$types$2f$sort$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ZOOM_CONFIG"].step, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$types$2f$sort$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ZOOM_CONFIG"].max)
            });
        },
        zoomOut: ()=>{
            const { zoom } = get();
            set({
                zoom: Math.max(zoom - __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$types$2f$sort$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ZOOM_CONFIG"].step, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$types$2f$sort$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ZOOM_CONFIG"].min)
            });
        },
        resetZoom: ()=>{
            set({
                zoom: __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$types$2f$sort$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ZOOM_CONFIG"].default
            });
        },
        setZoom: (zoom)=>{
            set({
                zoom: Math.max(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$types$2f$sort$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ZOOM_CONFIG"].min, Math.min(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$types$2f$sort$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ZOOM_CONFIG"].max, zoom))
            });
        }
    });
}),
"[project]/src/store/sort/index.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Sort Store - 使用 Slices Pattern 组织的排序状态管理
 * 
 * 遵循 Zustand 最佳实践：
 * - 状态按功能拆分为独立 Slices
 * - 每个 Slice 管理自己的状态和操作
 * - 合并为单一 Store 导出
 */ __turbopack_context__.s([
    "useSortStore",
    ()=>useSortStore
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/zustand/esm/react.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$middleware$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/zustand/esm/middleware.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$types$2f$sort$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/types/sort.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$sort$2f$data$2d$slice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/store/sort/data-slice.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$sort$2f$selection$2d$slice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/store/sort/selection-slice.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$sort$2f$preview$2d$slice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/store/sort/preview-slice.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$sort$2f$ui$2d$slice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/store/sort/ui-slice.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$sort$2f$zoom$2d$slice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/store/sort/zoom-slice.ts [app-ssr] (ecmascript)");
;
;
;
;
;
;
;
;
// 初始状态（用于 reset）
const initialState = {
    // Data
    screenshots: [],
    sortedScreenshots: [],
    deletedBatches: [],
    onboardingRange: {
        start: -1,
        end: -1
    },
    // Selection
    selectedFiles: new Set(),
    lastClickedIndex: null,
    // Preview
    previewIndex: null,
    // UI
    loading: false,
    saving: false,
    error: null,
    hasChanges: false,
    // Zoom
    zoom: __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$types$2f$sort$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ZOOM_CONFIG"].default
};
const useSortStore = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["create"])()((0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$middleware$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["devtools"])((...args)=>({
        ...(0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$sort$2f$data$2d$slice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["createDataSlice"])(...args),
        ...(0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$sort$2f$selection$2d$slice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["createSelectionSlice"])(...args),
        ...(0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$sort$2f$preview$2d$slice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["createPreviewSlice"])(...args),
        ...(0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$sort$2f$ui$2d$slice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["createUISlice"])(...args),
        ...(0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$sort$2f$zoom$2d$slice$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["createZoomSlice"])(...args),
        // 重置所有状态
        reset: ()=>{
            const [set] = args;
            set(initialState);
        }
    }), {
    name: 'SortStore'
}));
}),
"[project]/src/store/branch-store.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * 分支流程状态管理
 */ __turbopack_context__.s([
    "BRANCH_COLORS",
    ()=>BRANCH_COLORS,
    "addBranch",
    ()=>addBranch,
    "addForkPoint",
    ()=>addForkPoint,
    "addMergePoint",
    ()=>addMergePoint,
    "clearBranchData",
    ()=>clearBranchData,
    "deleteBranch",
    ()=>deleteBranch,
    "getBranchData",
    ()=>getBranchData,
    "removeForkPoint",
    ()=>removeForkPoint,
    "removeMergePoint",
    ()=>removeMergePoint,
    "saveBranchData",
    ()=>saveBranchData,
    "updateBranch",
    ()=>updateBranch,
    "useBranchStore",
    ()=>useBranchStore
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/zustand/esm/react.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/lib/api.ts [app-ssr] (ecmascript)");
;
;
// ============ API 函数 ============
// 新 URL 结构：操作类型在 project_name 之前，避免 :path 贪婪匹配
const API_BASE = '/api';
async function getBranchData(projectName) {
    const response = await fetch(`${API_BASE}/branch/data/${projectName}`);
    if (!response.ok) {
        throw new Error('获取分支数据失败');
    }
    return response.json();
}
async function saveBranchData(projectName, data) {
    const response = await fetch(`${API_BASE}/branch/data/${projectName}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    if (!response.ok) {
        throw new Error('保存分支数据失败');
    }
    return response.json();
}
async function addForkPoint(projectName, index, name = '') {
    const response = await fetch(`${API_BASE}/branch/fork-point/${projectName}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            index,
            name
        })
    });
    if (!response.ok) {
        throw new Error('添加分支点失败');
    }
    return response.json();
}
async function removeForkPoint(projectName, index) {
    const response = await fetch(`${API_BASE}/branch/fork-point/${index}/${projectName}`, {
        method: 'DELETE'
    });
    if (!response.ok) {
        throw new Error('删除分支点失败');
    }
    return response.json();
}
async function addMergePoint(projectName, index) {
    const response = await fetch(`${API_BASE}/branch/merge-point/${projectName}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            index
        })
    });
    if (!response.ok) {
        throw new Error('添加汇合点失败');
    }
    return response.json();
}
async function removeMergePoint(projectName, index) {
    const response = await fetch(`${API_BASE}/branch/merge-point/${index}/${projectName}`, {
        method: 'DELETE'
    });
    if (!response.ok) {
        throw new Error('删除汇合点失败');
    }
    return response.json();
}
async function addBranch(projectName, branch) {
    const response = await fetch(`${API_BASE}/branch/path/${projectName}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(branch)
    });
    if (!response.ok) {
        throw new Error('添加分支失败');
    }
    return response.json();
}
async function updateBranch(projectName, branchId, branch) {
    const response = await fetch(`${API_BASE}/branch/path/${branchId}/${projectName}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(branch)
    });
    if (!response.ok) {
        throw new Error('更新分支失败');
    }
    return response.json();
}
async function deleteBranch(projectName, branchId) {
    const response = await fetch(`${API_BASE}/branch/path/${branchId}/${projectName}`, {
        method: 'DELETE'
    });
    if (!response.ok) {
        throw new Error('删除分支失败');
    }
    return response.json();
}
async function clearBranchData(projectName) {
    const response = await fetch(`${API_BASE}/branch/clear/${projectName}`, {
        method: 'DELETE'
    });
    if (!response.ok) {
        throw new Error('清空分支数据失败');
    }
    return response.json();
}
const BRANCH_COLORS = [
    {
        name: '绿色',
        value: '#22c55e'
    },
    {
        name: '蓝色',
        value: '#3b82f6'
    },
    {
        name: '紫色',
        value: '#a855f7'
    },
    {
        name: '橙色',
        value: '#f59e0b'
    },
    {
        name: '粉色',
        value: '#ec4899'
    },
    {
        name: '青色',
        value: '#06b6d4'
    },
    {
        name: '红色',
        value: '#ef4444'
    },
    {
        name: '靛蓝',
        value: '#6366f1'
    }
];
const initialState = {
    branchData: {
        version: '1.0',
        fork_points: [],
        merge_points: [],
        branches: [],
        updated_at: null
    },
    screenshots: [],
    onboardingRange: {
        start: -1,
        end: -1
    },
    editMode: 'none',
    selectedBranch: null,
    pendingBranchScreens: [],
    loading: false,
    saving: false,
    error: null
};
const useBranchStore = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["create"])((set, get)=>({
        ...initialState,
        fetchData: async (projectName)=>{
            set({
                loading: true,
                error: null
            });
            try {
                // 并行获取分支数据、截图列表和 Onboarding 范围
                const [branchData, screenshotsRes, onboardingRange] = await Promise.all([
                    getBranchData(projectName),
                    fetch(`/api/project-screenshots/${encodeURIComponent(projectName)}`).then((r)=>r.json()),
                    (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getOnboardingRange"])(projectName)
                ]);
                set({
                    branchData,
                    screenshots: screenshotsRes.screenshots || [],
                    onboardingRange,
                    loading: false
                });
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : '加载失败',
                    loading: false
                });
            }
        },
        setEditMode: (mode)=>{
            set({
                editMode: mode,
                pendingBranchScreens: []
            });
        },
        toggleForkPoint: async (projectName, index)=>{
            const { branchData } = get();
            set({
                saving: true,
                error: null
            });
            try {
                const exists = branchData.fork_points.some((fp)=>fp.index === index);
                if (exists) {
                    const result = await removeForkPoint(projectName, index);
                    set((state)=>({
                            branchData: {
                                ...state.branchData,
                                fork_points: result.fork_points
                            },
                            saving: false
                        }));
                } else {
                    const result = await addForkPoint(projectName, index);
                    set((state)=>({
                            branchData: {
                                ...state.branchData,
                                fork_points: result.fork_points
                            },
                            saving: false
                        }));
                }
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : '操作失败',
                    saving: false
                });
            }
        },
        updateForkPointName: async (projectName, index, name)=>{
            set({
                saving: true,
                error: null
            });
            try {
                const result = await addForkPoint(projectName, index, name);
                set((state)=>({
                        branchData: {
                            ...state.branchData,
                            fork_points: result.fork_points
                        },
                        saving: false
                    }));
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : '操作失败',
                    saving: false
                });
            }
        },
        toggleMergePoint: async (projectName, index)=>{
            const { branchData } = get();
            set({
                saving: true,
                error: null
            });
            try {
                const exists = branchData.merge_points.includes(index);
                if (exists) {
                    const result = await removeMergePoint(projectName, index);
                    set((state)=>({
                            branchData: {
                                ...state.branchData,
                                merge_points: result.merge_points
                            },
                            saving: false
                        }));
                } else {
                    const result = await addMergePoint(projectName, index);
                    set((state)=>({
                            branchData: {
                                ...state.branchData,
                                merge_points: result.merge_points
                            },
                            saving: false
                        }));
                }
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : '操作失败',
                    saving: false
                });
            }
        },
        toggleScreenInPending: (index)=>{
            set((state)=>{
                const exists = state.pendingBranchScreens.includes(index);
                return {
                    pendingBranchScreens: exists ? state.pendingBranchScreens.filter((i)=>i !== index) : [
                        ...state.pendingBranchScreens,
                        index
                    ].sort((a, b)=>a - b)
                };
            });
        },
        clearPendingScreens: ()=>{
            set({
                pendingBranchScreens: []
            });
        },
        createBranch: async (projectName, name, color, forkFrom, mergeTo)=>{
            const { pendingBranchScreens } = get();
            if (pendingBranchScreens.length === 0) {
                set({
                    error: '请先选择分支包含的截图'
                });
                return;
            }
            set({
                saving: true,
                error: null
            });
            try {
                const result = await addBranch(projectName, {
                    name,
                    color,
                    fork_from: forkFrom,
                    screens: pendingBranchScreens,
                    merge_to: mergeTo
                });
                set((state)=>({
                        branchData: {
                            ...state.branchData,
                            branches: [
                                ...state.branchData.branches,
                                result.branch
                            ]
                        },
                        pendingBranchScreens: [],
                        editMode: 'none',
                        saving: false
                    }));
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : '创建分支失败',
                    saving: false
                });
            }
        },
        removeBranch: async (projectName, branchId)=>{
            set({
                saving: true,
                error: null
            });
            try {
                await deleteBranch(projectName, branchId);
                set((state)=>({
                        branchData: {
                            ...state.branchData,
                            branches: state.branchData.branches.filter((b)=>b.id !== branchId)
                        },
                        selectedBranch: state.selectedBranch === branchId ? null : state.selectedBranch,
                        saving: false
                    }));
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : '删除分支失败',
                    saving: false
                });
            }
        },
        selectBranch: (branchId)=>{
            set({
                selectedBranch: branchId
            });
        },
        clearAll: async (projectName)=>{
            set({
                saving: true,
                error: null
            });
            try {
                await clearBranchData(projectName);
                set({
                    branchData: {
                        version: '1.0',
                        fork_points: [],
                        merge_points: [],
                        branches: [],
                        updated_at: null
                    },
                    selectedBranch: null,
                    pendingBranchScreens: [],
                    saving: false
                });
            } catch (error) {
                set({
                    error: error instanceof Error ? error.message : '清空失败',
                    saving: false
                });
            }
        },
        reset: ()=>{
            set(initialState);
        }
    }));
}),
"[project]/src/app/flow-lab/page.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>FlowLabPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$components$2f$AnimatePresence$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/framer-motion/dist/es/components/AnimatePresence/index.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$dnd$2d$kit$2f$core$2f$dist$2f$core$2e$esm$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@dnd-kit/core/dist/core.esm.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$dnd$2d$kit$2f$sortable$2f$dist$2f$sortable$2e$esm$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@dnd-kit/sortable/dist/sortable.esm.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$layout$2f$index$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/src/components/layout/index.ts [app-ssr] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$layout$2f$app$2d$layout$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/layout/app-layout.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$index$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/src/components/sort/index.ts [app-ssr] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$PreviewPanel$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/sort/PreviewPanel.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$PendingPanel$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/sort/PendingPanel.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$StatusBar$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/sort/StatusBar.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$ShortcutsHint$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/sort/ShortcutsHint.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$ProjectSelector$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/sort/ProjectSelector.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$SortableScreenshot$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/sort/SortableScreenshot.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$DragPreview$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/sort/DragPreview.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$ZoomControl$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/sort/ZoomControl.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$SelectionBar$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/components/sort/SelectionBar.tsx [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$project$2d$store$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/store/project-store.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$sort$2f$index$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/store/sort/index.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$branch$2d$store$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/store/branch-store.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/src/lib/api.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$save$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Save$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/save.js [app-ssr] (ecmascript) <export default as Save>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$check$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Check$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/check.js [app-ssr] (ecmascript) <export default as Check>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/trash-2.js [app-ssr] (ecmascript) <export default as Trash2>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$rotate$2d$ccw$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__RotateCcw$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/rotate-ccw.js [app-ssr] (ecmascript) <export default as RotateCcw>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$square$2d$check$2d$big$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__CheckSquare$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/square-check-big.js [app-ssr] (ecmascript) <export default as CheckSquare>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/x.js [app-ssr] (ecmascript) <export default as X>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$layout$2d$grid$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__LayoutGrid$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/layout-grid.js [app-ssr] (ecmascript) <export default as LayoutGrid>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$git$2d$branch$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__GitBranch$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/git-branch.js [app-ssr] (ecmascript) <export default as GitBranch>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$git$2d$fork$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__GitFork$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/git-fork.js [app-ssr] (ecmascript) <export default as GitFork>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$git$2d$merge$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__GitMerge$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/git-merge.js [app-ssr] (ecmascript) <export default as GitMerge>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$flask$2d$conical$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__FlaskConical$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/flask-conical.js [app-ssr] (ecmascript) <export default as FlaskConical>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/sonner/dist/index.mjs [app-ssr] (ecmascript)");
'use client';
;
;
;
;
;
;
;
;
;
;
;
;
;
// ==================== 配置 ====================
const dropAnimation = {
    sideEffects: (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$dnd$2d$kit$2f$core$2f$dist$2f$core$2e$esm$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["defaultDropAnimationSideEffects"])({
        styles: {
            active: {
                opacity: '0.5'
            }
        }
    }),
    duration: 250,
    easing: 'cubic-bezier(0.25, 1, 0.5, 1)'
};
function getCardMinWidth(zoom) {
    return Math.round(100 * (zoom / 100));
}
function FlowLabPage() {
    // Store - 排序
    const { projects, fetchProjects } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$project$2d$store$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useProjectStore"])();
    const { sortedScreenshots, deletedBatches, selectedFiles, onboardingRange, previewIndex, loading, saving, error, hasChanges, zoom, fetchData, reorder, toggleSelect, selectAll, deselectAll, setSelectedFiles, deleteSelected, restoreBatch, saveSortOrder, applySortOrder, setPreviewIndex, prevPreview, nextPreview, reset, zoomIn, zoomOut, resetZoom, setLastClickedIndex, lastClickedIndex } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$sort$2f$index$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useSortStore"])();
    // Store - 分支
    const { branchData, editMode, pendingBranchScreens, fetchData: fetchBranchData, setEditMode, toggleForkPoint, toggleMergePoint, toggleScreenInPending, clearPendingScreens, createBranch, removeBranch, clearAll: clearBranchData } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$branch$2d$store$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useBranchStore"])();
    // Local State
    const [selectedProject, setSelectedProject] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [activeId, setActiveId] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [showDeleted, setShowDeleted] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [isDragOver, setIsDragOver] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [dropTargetIndex, setDropTargetIndex] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [uploadMessage, setUploadMessage] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [newlyAdded, setNewlyAdded] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [viewMode, setViewMode] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])('flow');
    // Refs
    const contentRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useRef"])(null);
    const gridRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useRef"])(null);
    // DnD Sensors
    const sensors = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$dnd$2d$kit$2f$core$2f$dist$2f$core$2e$esm$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useSensors"])((0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$dnd$2d$kit$2f$core$2f$dist$2f$core$2e$esm$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useSensor"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$dnd$2d$kit$2f$core$2f$dist$2f$core$2e$esm$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["PointerSensor"], {
        activationConstraint: {
            distance: 8
        }
    }), (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$dnd$2d$kit$2f$core$2f$dist$2f$core$2e$esm$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useSensor"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$dnd$2d$kit$2f$core$2f$dist$2f$core$2e$esm$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["KeyboardSensor"], {
        coordinateGetter: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$dnd$2d$kit$2f$sortable$2f$dist$2f$sortable$2e$esm$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["sortableKeyboardCoordinates"]
    }));
    // ==================== Effects ====================
    // 加载项目列表
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        fetchProjects();
    }, [
        fetchProjects
    ]);
    // 离开页面提示
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        const handleBeforeUnload = (e)=>{
            if (hasChanges) {
                e.preventDefault();
                e.returnValue = '你有未保存的排序更改，确定要离开吗？';
            }
        };
        window.addEventListener('beforeunload', handleBeforeUnload);
        return ()=>window.removeEventListener('beforeunload', handleBeforeUnload);
    }, [
        hasChanges
    ]);
    // 切换项目时加载数据
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        if (selectedProject) {
            fetchData(selectedProject);
            fetchBranchData(selectedProject);
        } else {
            reset();
        }
    }, [
        selectedProject,
        fetchData,
        fetchBranchData,
        reset
    ]);
    // 滚轮缩放
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        if (!selectedProject) return;
        const handleWheel = (e)=>{
            if (e.ctrlKey) {
                e.preventDefault();
                e.deltaY < 0 ? zoomIn() : zoomOut();
            }
        };
        const contentArea = contentRef.current;
        if (contentArea) {
            contentArea.addEventListener('wheel', handleWheel, {
                passive: false
            });
            return ()=>contentArea.removeEventListener('wheel', handleWheel);
        }
    }, [
        selectedProject,
        zoomIn,
        zoomOut
    ]);
    // 全局快捷键
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        if (!selectedProject) return;
        const handleKeyDown = (e)=>{
            if (e.ctrlKey && e.key === 'a') {
                e.preventDefault();
                selectAll();
            }
            if (e.ctrlKey && (e.key === '=' || e.key === '+')) {
                e.preventDefault();
                zoomIn();
            }
            if (e.ctrlKey && e.key === '-') {
                e.preventDefault();
                zoomOut();
            }
            if (e.ctrlKey && e.key === '0') {
                e.preventDefault();
                resetZoom();
            }
            if (e.key === 'Delete' && selectedFiles.size > 0) {
                const count = selectedFiles.size;
                if (count <= 10 || window.confirm(`确定要删除 ${count} 张截图吗？`)) {
                    deleteSelected(selectedProject);
                }
            }
            if (e.key === 'Escape') {
                deselectAll();
                setPreviewIndex(null);
                setEditMode('none');
                clearPendingScreens();
            }
            if (e.key === 'ArrowLeft' && previewIndex !== null) {
                prevPreview();
            }
            if (e.key === 'ArrowRight' && previewIndex !== null) {
                nextPreview();
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return ()=>window.removeEventListener('keydown', handleKeyDown);
    }, [
        selectedProject,
        selectedFiles,
        previewIndex,
        selectAll,
        deselectAll,
        deleteSelected,
        setPreviewIndex,
        prevPreview,
        nextPreview,
        zoomIn,
        zoomOut,
        resetZoom,
        setEditMode,
        clearPendingScreens
    ]);
    // ==================== Handlers ====================
    const handleDragStart = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useCallback"])((event)=>{
        setActiveId(event.active.id);
    }, []);
    const handleDragEnd = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useCallback"])((event)=>{
        const { active, over } = event;
        setActiveId(null);
        if (over && active.id !== over.id) {
            const oldIndex = sortedScreenshots.findIndex((s)=>s.filename === active.id);
            const newIndex = sortedScreenshots.findIndex((s)=>s.filename === over.id);
            if (previewIndex !== null) {
                if (previewIndex === oldIndex) {
                    setPreviewIndex(newIndex);
                } else if (oldIndex < previewIndex && newIndex >= previewIndex) {
                    setPreviewIndex(previewIndex - 1);
                } else if (oldIndex > previewIndex && newIndex <= previewIndex) {
                    setPreviewIndex(previewIndex + 1);
                }
            }
            reorder(oldIndex, newIndex);
        }
    }, [
        sortedScreenshots,
        reorder,
        previewIndex,
        setPreviewIndex
    ]);
    const handleCardClick = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useCallback"])((e, index, filename)=>{
        // 如果在分支编辑模式，处理分支相关点击
        if (editMode === 'fork' && selectedProject) {
            toggleForkPoint(selectedProject, index);
            return;
        }
        if (editMode === 'merge' && selectedProject) {
            toggleMergePoint(selectedProject, index);
            return;
        }
        if (editMode === 'branch') {
            toggleScreenInPending(index);
            return;
        }
        // 普通模式
        setPreviewIndex(index);
        if (e.shiftKey && lastClickedIndex !== null) {
            const start = Math.min(lastClickedIndex, index);
            const end = Math.max(lastClickedIndex, index);
            setSelectedFiles(new Set(sortedScreenshots.slice(start, end + 1).map((s)=>s.filename)));
        } else if (e.ctrlKey || e.metaKey) {
            toggleSelect(filename);
        } else {
            setSelectedFiles(new Set([
                filename
            ]));
        }
        setLastClickedIndex(index);
    }, [
        editMode,
        selectedProject,
        lastClickedIndex,
        sortedScreenshots,
        setPreviewIndex,
        setSelectedFiles,
        toggleSelect,
        setLastClickedIndex,
        toggleForkPoint,
        toggleMergePoint,
        toggleScreenInPending
    ]);
    const handleDragOver = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useCallback"])((e)=>{
        e.preventDefault();
        e.stopPropagation();
        if (!selectedProject || viewMode !== 'grid') return;
        const hasFiles = e.dataTransfer.types.includes('Files');
        const hasPending = e.dataTransfer.types.includes('application/x-pending-screenshot');
        if (hasFiles || hasPending) {
            setIsDragOver(true);
            e.dataTransfer.dropEffect = 'copy';
            if (gridRef.current) {
                const cards = gridRef.current.querySelectorAll('[data-screenshot-card]');
                let targetIndex = sortedScreenshots.length;
                for(let i = 0; i < cards.length; i++){
                    const card = cards[i];
                    const rect = card.getBoundingClientRect();
                    const cardCenterX = rect.left + rect.width / 2;
                    if (e.clientY < rect.bottom && e.clientY > rect.top - 20) {
                        if (e.clientX < cardCenterX) {
                            targetIndex = i;
                            break;
                        } else if (i === cards.length - 1 || e.clientX < rect.right) {
                            targetIndex = i + 1;
                            break;
                        }
                    }
                }
                setDropTargetIndex(targetIndex);
            }
        }
    }, [
        selectedProject,
        sortedScreenshots.length,
        viewMode
    ]);
    const handleDragLeave = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useCallback"])((e)=>{
        e.preventDefault();
        const relatedTarget = e.relatedTarget;
        if (!contentRef.current?.contains(relatedTarget)) {
            setIsDragOver(false);
            setDropTargetIndex(null);
        }
    }, []);
    const handleDrop = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useCallback"])(async (e)=>{
        e.preventDefault();
        const targetIndex = dropTargetIndex ?? sortedScreenshots.length;
        setIsDragOver(false);
        setDropTargetIndex(null);
        if (!selectedProject) {
            __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["toast"].error('请先选择一个项目');
            return;
        }
        const pendingData = e.dataTransfer.getData('application/x-pending-screenshot');
        if (pendingData) {
            try {
                const { filename } = JSON.parse(pendingData);
                const result = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["importScreenshot"])(selectedProject, filename);
                if (result.success && result.new_filename) {
                    const newScreenshot = {
                        filename: result.new_filename,
                        index: targetIndex
                    };
                    const current = __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$sort$2f$index$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useSortStore"].getState().sortedScreenshots;
                    __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$sort$2f$index$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useSortStore"].setState({
                        sortedScreenshots: [
                            ...current.slice(0, targetIndex),
                            newScreenshot,
                            ...current.slice(targetIndex)
                        ],
                        hasChanges: true
                    });
                    setUploadMessage(`✓ 已插入 ${result.new_filename}`);
                    setNewlyAdded(result.new_filename);
                    setTimeout(()=>{
                        setUploadMessage(null);
                        setNewlyAdded(null);
                    }, 3000);
                }
            } catch (error) {
                __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["toast"].error('导入失败: ' + error.message);
            }
            return;
        }
        const files = Array.from(e.dataTransfer.files).filter((f)=>f.type.startsWith('image/') || /\.(png|jpg|jpeg|webp)$/i.test(f.name));
        if (files.length === 0) {
            __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["toast"].error('请拖入图片文件');
            return;
        }
        const uploadedFiles = [];
        for (const file of files){
            try {
                const result = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$lib$2f$api$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["uploadScreenshot"])(selectedProject, file);
                if (result.success && result.new_filename) uploadedFiles.push(result.new_filename);
            } catch (error) {
                console.error('Upload failed:', error);
            }
        }
        if (uploadedFiles.length > 0) {
            const newScreenshots = uploadedFiles.map((filename)=>({
                    filename,
                    path: ''
                }));
            const current = __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$sort$2f$index$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useSortStore"].getState().sortedScreenshots;
            __TURBOPACK__imported__module__$5b$project$5d2f$src$2f$store$2f$sort$2f$index$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useSortStore"].setState({
                sortedScreenshots: [
                    ...current.slice(0, targetIndex),
                    ...newScreenshots,
                    ...current.slice(targetIndex)
                ],
                hasChanges: true
            });
            setUploadMessage(`✓ 已导入 ${uploadedFiles.length} 张截图`);
            setNewlyAdded(uploadedFiles[uploadedFiles.length - 1]);
            setTimeout(()=>{
                setUploadMessage(null);
                setNewlyAdded(null);
            }, 3000);
        }
    }, [
        selectedProject,
        dropTargetIndex,
        sortedScreenshots.length
    ]);
    const handleImportSuccess = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useCallback"])(()=>{
        if (selectedProject) fetchData(selectedProject);
    }, [
        selectedProject,
        fetchData
    ]);
    const handleDeleteSelected = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useCallback"])(()=>{
        if (!selectedProject) return;
        const count = selectedFiles.size;
        if (count <= 10 || window.confirm(`确定要删除 ${count} 张截图吗？`)) {
            deleteSelected(selectedProject);
        }
    }, [
        selectedProject,
        selectedFiles.size,
        deleteSelected
    ]);
    // ==================== Helper Functions ====================
    // 获取截图类型（分支点、汇合点、属于哪个分支）
    const getScreenType = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useCallback"])((index)=>{
        const isForkPoint = branchData.fork_points.some((fp)=>fp.index === index);
        const isMergePoint = branchData.merge_points.includes(index);
        const inBranch = branchData.branches.find((b)=>b.screens.includes(index));
        const isPending = pendingBranchScreens.includes(index);
        return {
            isForkPoint,
            isMergePoint,
            inBranch,
            isPending
        };
    }, [
        branchData,
        pendingBranchScreens
    ]);
    // ==================== Derived State ====================
    const activeScreenshot = activeId ? sortedScreenshots.find((s)=>s.filename === activeId) : null;
    const previewScreenshot = previewIndex !== null ? sortedScreenshots[previewIndex] : null;
    const displayProjectName = selectedProject?.replace('downloads_2024/', '') || '';
    // Onboarding 范围内的截图
    const onboardingScreenshots = onboardingRange.start >= 0 && onboardingRange.end >= 0 ? sortedScreenshots.slice(onboardingRange.start, onboardingRange.end + 1) : sortedScreenshots;
    // ==================== Styles ====================
    const pageStyles = {
        pendingSidebar: {
            width: '280px',
            flexShrink: 0,
            borderRight: '1px solid var(--border-default)',
            overflowY: 'auto',
            padding: '12px'
        },
        mainContent: {
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            minWidth: 0
        },
        topbarActions: {
            display: 'flex',
            gap: '8px',
            marginLeft: '16px',
            alignItems: 'center',
            flexShrink: 1,
            minWidth: 0,
            overflowX: 'auto',
            overflowY: 'hidden',
            paddingBottom: '2px'
        },
        btnGhost: {
            background: 'none',
            color: 'var(--text-muted)',
            border: '1px solid transparent',
            padding: '6px 12px',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '13px',
            fontWeight: 500,
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            whiteSpace: 'nowrap',
            lineHeight: 1.4
        },
        btnGhostDanger: {
            color: 'var(--danger)'
        },
        btnGhostActive: {
            color: '#fff',
            background: 'var(--bg-active)'
        },
        btnGhostSuccess: {
            background: 'var(--success)',
            color: '#fff'
        },
        contentArea: {
            flex: 1,
            overflow: 'auto',
            position: 'relative'
        },
        dropOverlay: {
            position: 'absolute',
            inset: 0,
            background: 'rgba(245, 158, 11, 0.05)',
            border: '3px dashed #f59e0b',
            borderRadius: '12px',
            zIndex: 5,
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'center',
            paddingTop: '20px',
            pointerEvents: 'none'
        },
        dropMessage: {
            background: 'rgba(0,0,0,0.9)',
            padding: '12px 24px',
            borderRadius: '8px',
            color: '#f59e0b',
            fontSize: '14px',
            fontWeight: 500
        },
        uploadToast: {
            position: 'fixed',
            bottom: '24px',
            left: '50%',
            transform: 'translateX(-50%)',
            background: '#22c55e',
            color: '#fff',
            padding: '12px 24px',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: 500,
            zIndex: 100,
            boxShadow: '0 4px 20px rgba(34, 197, 94, 0.4)'
        },
        emptyState: {
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '400px',
            color: 'var(--text-muted)',
            gap: '16px'
        },
        loadingState: {
            display: 'flex',
            height: '256px',
            alignItems: 'center',
            justifyContent: 'center'
        },
        errorMessage: {
            padding: '12px 16px',
            background: 'rgba(239, 68, 68, 0.2)',
            color: 'var(--danger)',
            borderRadius: '8px',
            marginBottom: '16px'
        },
        deletedPanel: {
            background: 'var(--bg-card)',
            borderRadius: '8px',
            marginBottom: '16px',
            padding: '16px'
        },
        deletedBatch: {
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '8px 12px',
            background: 'var(--bg-secondary)',
            borderRadius: '6px',
            marginTop: '8px',
            fontSize: '13px'
        },
        sortGrid: {
            display: 'grid',
            position: 'relative',
            transition: 'gap 200ms ease'
        },
        dropIndicator: {
            position: 'absolute',
            left: '-6px',
            top: 0,
            bottom: 0,
            width: '4px',
            background: '#f59e0b',
            borderRadius: '2px',
            zIndex: 10,
            boxShadow: '0 0 10px rgba(245, 158, 11, 0.8)'
        },
        viewToggle: {
            display: 'flex',
            gap: '4px',
            background: 'var(--bg-secondary)',
            padding: '4px',
            borderRadius: '8px'
        },
        viewToggleBtn: {
            padding: '6px 12px',
            borderRadius: '6px',
            border: 'none',
            cursor: 'pointer',
            fontSize: '13px',
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            transition: 'all 0.2s'
        },
        branchToolbar: {
            display: 'flex',
            gap: '8px',
            padding: '8px 16px',
            background: 'var(--bg-secondary)',
            borderBottom: '1px solid var(--border-default)',
            alignItems: 'center'
        }
    };
    // ==================== Render ====================
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$layout$2f$app$2d$layout$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["AppLayout"], {
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    display: 'flex',
                    flex: 1,
                    overflow: 'hidden'
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: pageStyles.pendingSidebar,
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$PendingPanel$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["PendingPanel"], {
                            selectedProject: selectedProject,
                            onImportSuccess: handleImportSuccess
                        }, void 0, false, {
                            fileName: "[project]/src/app/flow-lab/page.tsx",
                            lineNumber: 595,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/src/app/flow-lab/page.tsx",
                        lineNumber: 594,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: pageStyles.mainContent,
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "topbar",
                                style: {
                                    overflow: 'visible'
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '8px'
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$flask$2d$conical$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__FlaskConical$3e$__["FlaskConical"], {
                                                size: 18,
                                                color: "#f59e0b"
                                            }, void 0, false, {
                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                lineNumber: 603,
                                                columnNumber: 15
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                                                style: {
                                                    fontSize: '15px',
                                                    fontWeight: 600,
                                                    color: '#fff',
                                                    whiteSpace: 'nowrap'
                                                },
                                                children: "Flow Lab"
                                            }, void 0, false, {
                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                lineNumber: 604,
                                                columnNumber: 15
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                style: {
                                                    fontSize: '11px',
                                                    color: 'var(--text-muted)',
                                                    background: 'var(--bg-secondary)',
                                                    padding: '2px 8px',
                                                    borderRadius: '4px'
                                                },
                                                children: "实验"
                                            }, void 0, false, {
                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                lineNumber: 607,
                                                columnNumber: 15
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 602,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            flex: 1,
                                            minWidth: '8px'
                                        }
                                    }, void 0, false, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 611,
                                        columnNumber: 13
                                    }, this),
                                    selectedProject && sortedScreenshots.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: pageStyles.viewToggle,
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                style: {
                                                    ...pageStyles.viewToggleBtn,
                                                    background: viewMode === 'grid' ? 'var(--bg-active)' : 'transparent',
                                                    color: viewMode === 'grid' ? '#fff' : 'var(--text-muted)'
                                                },
                                                onClick: ()=>setViewMode('grid'),
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$layout$2d$grid$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__LayoutGrid$3e$__["LayoutGrid"], {
                                                        size: 14
                                                    }, void 0, false, {
                                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                                        lineNumber: 624,
                                                        columnNumber: 19
                                                    }, this),
                                                    "网格"
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                lineNumber: 616,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                style: {
                                                    ...pageStyles.viewToggleBtn,
                                                    background: viewMode === 'flow' ? 'var(--bg-active)' : 'transparent',
                                                    color: viewMode === 'flow' ? '#fff' : 'var(--text-muted)'
                                                },
                                                onClick: ()=>setViewMode('flow'),
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$git$2d$branch$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__GitBranch$3e$__["GitBranch"], {
                                                        size: 14
                                                    }, void 0, false, {
                                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                                        lineNumber: 635,
                                                        columnNumber: 19
                                                    }, this),
                                                    "流程"
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                lineNumber: 627,
                                                columnNumber: 17
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 615,
                                        columnNumber: 15
                                    }, this),
                                    selectedProject && sortedScreenshots.length > 0 && viewMode === 'grid' && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$ZoomControl$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ZoomControl"], {
                                        zoom: zoom,
                                        onZoomIn: zoomIn,
                                        onZoomOut: zoomOut,
                                        onReset: resetZoom
                                    }, void 0, false, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 643,
                                        columnNumber: 15
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            marginLeft: 12
                                        },
                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$ProjectSelector$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ProjectSelector"], {
                                            projects: projects,
                                            selectedProject: selectedProject,
                                            onSelect: setSelectedProject
                                        }, void 0, false, {
                                            fileName: "[project]/src/app/flow-lab/page.tsx",
                                            lineNumber: 653,
                                            columnNumber: 15
                                        }, this)
                                    }, void 0, false, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 652,
                                        columnNumber: 13
                                    }, this),
                                    selectedProject && sortedScreenshots.length > 0 && viewMode === 'grid' && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: pageStyles.topbarActions,
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                style: pageStyles.btnGhost,
                                                onClick: ()=>selectedFiles.size > 0 ? deselectAll() : selectAll(),
                                                children: selectedFiles.size > 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
                                                            size: 16
                                                        }, void 0, false, {
                                                            fileName: "[project]/src/app/flow-lab/page.tsx",
                                                            lineNumber: 664,
                                                            columnNumber: 47
                                                        }, this),
                                                        "取消 (",
                                                        selectedFiles.size,
                                                        ")"
                                                    ]
                                                }, void 0, true) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$square$2d$check$2d$big$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__CheckSquare$3e$__["CheckSquare"], {
                                                            size: 16
                                                        }, void 0, false, {
                                                            fileName: "[project]/src/app/flow-lab/page.tsx",
                                                            lineNumber: 664,
                                                            columnNumber: 95
                                                        }, this),
                                                        "全选"
                                                    ]
                                                }, void 0, true)
                                            }, void 0, false, {
                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                lineNumber: 663,
                                                columnNumber: 17
                                            }, this),
                                            selectedFiles.size > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                style: {
                                                    ...pageStyles.btnGhost,
                                                    ...pageStyles.btnGhostDanger
                                                },
                                                onClick: handleDeleteSelected,
                                                disabled: saving,
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__["Trash2"], {
                                                        size: 16
                                                    }, void 0, false, {
                                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                                        lineNumber: 669,
                                                        columnNumber: 21
                                                    }, this),
                                                    "删除 (",
                                                    selectedFiles.size,
                                                    ")"
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                lineNumber: 668,
                                                columnNumber: 19
                                            }, this),
                                            deletedBatches.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                style: {
                                                    ...pageStyles.btnGhost,
                                                    ...showDeleted ? pageStyles.btnGhostActive : {}
                                                },
                                                onClick: ()=>setShowDeleted(!showDeleted),
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$rotate$2d$ccw$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__RotateCcw$3e$__["RotateCcw"], {
                                                        size: 16
                                                    }, void 0, false, {
                                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                                        lineNumber: 675,
                                                        columnNumber: 21
                                                    }, this),
                                                    "已删除 (",
                                                    deletedBatches.reduce((a, b)=>a + b.count, 0),
                                                    ")"
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                lineNumber: 674,
                                                columnNumber: 19
                                            }, this),
                                            hasChanges && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                        style: pageStyles.btnGhost,
                                                        onClick: ()=>selectedProject && saveSortOrder(selectedProject),
                                                        disabled: saving,
                                                        children: [
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$save$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Save$3e$__["Save"], {
                                                                size: 16
                                                            }, void 0, false, {
                                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                                lineNumber: 682,
                                                                columnNumber: 23
                                                            }, this),
                                                            "保存排序"
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                                        lineNumber: 681,
                                                        columnNumber: 21
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                        style: {
                                                            ...pageStyles.btnGhost,
                                                            ...pageStyles.btnGhostSuccess
                                                        },
                                                        onClick: ()=>selectedProject && applySortOrder(selectedProject),
                                                        disabled: saving,
                                                        children: [
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$check$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Check$3e$__["Check"], {
                                                                size: 16
                                                            }, void 0, false, {
                                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                                lineNumber: 689,
                                                                columnNumber: 23
                                                            }, this),
                                                            saving ? '应用中...' : '应用并重命名'
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                                        lineNumber: 684,
                                                        columnNumber: 21
                                                    }, this)
                                                ]
                                            }, void 0, true)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 662,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                lineNumber: 601,
                                columnNumber: 11
                            }, this),
                            selectedProject && sortedScreenshots.length > 0 && viewMode === 'flow' && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: pageStyles.branchToolbar,
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        style: {
                                            fontSize: '13px',
                                            color: 'var(--text-muted)',
                                            marginRight: '8px'
                                        },
                                        children: "标记模式:"
                                    }, void 0, false, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 700,
                                        columnNumber: 15
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        style: {
                                            ...pageStyles.btnGhost,
                                            ...editMode === 'fork' ? {
                                                background: '#ef4444',
                                                color: '#fff'
                                            } : {}
                                        },
                                        onClick: ()=>setEditMode(editMode === 'fork' ? 'none' : 'fork'),
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$git$2d$fork$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__GitFork$3e$__["GitFork"], {
                                                size: 14
                                            }, void 0, false, {
                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                lineNumber: 708,
                                                columnNumber: 17
                                            }, this),
                                            "分支点"
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 701,
                                        columnNumber: 15
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        style: {
                                            ...pageStyles.btnGhost,
                                            ...editMode === 'merge' ? {
                                                background: '#8b5cf6',
                                                color: '#fff'
                                            } : {}
                                        },
                                        onClick: ()=>setEditMode(editMode === 'merge' ? 'none' : 'merge'),
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$git$2d$merge$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__GitMerge$3e$__["GitMerge"], {
                                                size: 14
                                            }, void 0, false, {
                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                lineNumber: 718,
                                                columnNumber: 17
                                            }, this),
                                            "汇合点"
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 711,
                                        columnNumber: 15
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        style: {
                                            ...pageStyles.btnGhost,
                                            ...editMode === 'branch' ? {
                                                background: '#22c55e',
                                                color: '#fff'
                                            } : {}
                                        },
                                        onClick: ()=>setEditMode(editMode === 'branch' ? 'none' : 'branch'),
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$git$2d$branch$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__GitBranch$3e$__["GitBranch"], {
                                                size: 14
                                            }, void 0, false, {
                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                lineNumber: 728,
                                                columnNumber: 17
                                            }, this),
                                            "选择分支截图"
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 721,
                                        columnNumber: 15
                                    }, this),
                                    pendingBranchScreens.length > 0 && branchData.fork_points.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        style: {
                                            ...pageStyles.btnGhost,
                                            background: '#3b82f6',
                                            color: '#fff'
                                        },
                                        onClick: ()=>{
                                            // #region agent log
                                            fetch('http://127.0.0.1:7242/ingest/1146cc51-3fe3-46a3-9e1a-4801e1a50de0', {
                                                method: 'POST',
                                                headers: {
                                                    'Content-Type': 'application/json'
                                                },
                                                body: JSON.stringify({
                                                    location: 'flow-lab:createBranch',
                                                    message: 'Create branch clicked',
                                                    data: {
                                                        pendingScreens: pendingBranchScreens,
                                                        forkPoints: branchData.fork_points
                                                    },
                                                    timestamp: Date.now(),
                                                    hypothesisId: 'H1'
                                                })
                                            }).catch(()=>{});
                                            // #endregion
                                            // 使用第一个分支点作为起点
                                            const forkFrom = branchData.fork_points[0].index;
                                            createBranch(selectedProject, `分支${branchData.branches.length + 1}`, '#22c55e', forkFrom, null);
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$check$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__Check$3e$__["Check"], {
                                                size: 14
                                            }, void 0, false, {
                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                lineNumber: 749,
                                                columnNumber: 19
                                            }, this),
                                            "创建分支 (",
                                            pendingBranchScreens.length,
                                            "张)"
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 734,
                                        columnNumber: 17
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            flex: 1
                                        }
                                    }, void 0, false, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 754,
                                        columnNumber: 15
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        style: {
                                            fontSize: '12px',
                                            color: 'var(--text-muted)'
                                        },
                                        children: [
                                            "分支点: ",
                                            branchData.fork_points.length,
                                            " | 汇合点: ",
                                            branchData.merge_points.length,
                                            " | 分支: ",
                                            branchData.branches.length,
                                            pendingBranchScreens.length > 0 && ` | 待选: ${pendingBranchScreens.length}`
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 756,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                lineNumber: 699,
                                columnNumber: 13
                            }, this),
                            selectedProject && sortedScreenshots.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$StatusBar$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["StatusBar"], {
                                projectName: displayProjectName,
                                total: sortedScreenshots.length,
                                selected: selectedFiles.size,
                                moved: hasChanges ? 1 : 0,
                                onboardingStart: onboardingRange.start,
                                onboardingEnd: onboardingRange.end
                            }, void 0, false, {
                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                lineNumber: 765,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                ref: contentRef,
                                style: pageStyles.contentArea,
                                onDragOver: viewMode === 'grid' ? handleDragOver : undefined,
                                onDragLeave: viewMode === 'grid' ? handleDragLeave : undefined,
                                onDrop: viewMode === 'grid' ? handleDrop : undefined,
                                children: [
                                    isDragOver && viewMode === 'grid' && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: pageStyles.dropOverlay,
                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: pageStyles.dropMessage,
                                            children: dropTargetIndex !== null && dropTargetIndex < sortedScreenshots.length ? `释放插入到位置 ${dropTargetIndex + 1}` : '释放添加到末尾'
                                        }, void 0, false, {
                                            fileName: "[project]/src/app/flow-lab/page.tsx",
                                            lineNumber: 786,
                                            columnNumber: 17
                                        }, this)
                                    }, void 0, false, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 785,
                                        columnNumber: 15
                                    }, this),
                                    uploadMessage && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: pageStyles.uploadToast,
                                        children: uploadMessage
                                    }, void 0, false, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 795,
                                        columnNumber: 31
                                    }, this),
                                    !selectedProject && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: pageStyles.emptyState,
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$flask$2d$conical$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__FlaskConical$3e$__["FlaskConical"], {
                                                size: 48
                                            }, void 0, false, {
                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                lineNumber: 800,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                                children: "请选择一个项目来使用 Flow Lab"
                                            }, void 0, false, {
                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                lineNumber: 801,
                                                columnNumber: 17
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 799,
                                        columnNumber: 15
                                    }, this),
                                    selectedProject && loading && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: pageStyles.loadingState,
                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            className: "spinner"
                                        }, void 0, false, {
                                            fileName: "[project]/src/app/flow-lab/page.tsx",
                                            lineNumber: 807,
                                            columnNumber: 52
                                        }, this)
                                    }, void 0, false, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 807,
                                        columnNumber: 15
                                    }, this),
                                    error && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: pageStyles.errorMessage,
                                        children: error
                                    }, void 0, false, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 811,
                                        columnNumber: 23
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$components$2f$AnimatePresence$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["AnimatePresence"], {
                                        children: showDeleted && deletedBatches.length > 0 && viewMode === 'grid' && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: pageStyles.deletedPanel,
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h3", {
                                                    style: {
                                                        fontSize: '14px',
                                                        fontWeight: 600,
                                                        marginBottom: '12px'
                                                    },
                                                    children: "已删除的截图"
                                                }, void 0, false, {
                                                    fileName: "[project]/src/app/flow-lab/page.tsx",
                                                    lineNumber: 817,
                                                    columnNumber: 19
                                                }, this),
                                                deletedBatches.map((batch)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: pageStyles.deletedBatch,
                                                        children: [
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                children: [
                                                                    batch.count,
                                                                    " 张截图 - ",
                                                                    batch.timestamp
                                                                ]
                                                            }, void 0, true, {
                                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                                lineNumber: 820,
                                                                columnNumber: 23
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                                onClick: ()=>selectedProject && restoreBatch(selectedProject, batch.timestamp),
                                                                disabled: saving,
                                                                style: {
                                                                    padding: '4px 8px',
                                                                    fontSize: '12px',
                                                                    background: 'transparent',
                                                                    border: '1px solid var(--border-default)',
                                                                    borderRadius: '4px',
                                                                    cursor: 'pointer',
                                                                    display: 'flex',
                                                                    alignItems: 'center',
                                                                    gap: '4px',
                                                                    color: 'var(--text-primary)'
                                                                },
                                                                children: [
                                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$rotate$2d$ccw$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__RotateCcw$3e$__["RotateCcw"], {
                                                                        size: 12
                                                                    }, void 0, false, {
                                                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                                                        lineNumber: 837,
                                                                        columnNumber: 25
                                                                    }, this),
                                                                    "恢复"
                                                                ]
                                                            }, void 0, true, {
                                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                                lineNumber: 821,
                                                                columnNumber: 23
                                                            }, this)
                                                        ]
                                                    }, batch.timestamp, true, {
                                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                                        lineNumber: 819,
                                                        columnNumber: 21
                                                    }, this))
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/src/app/flow-lab/page.tsx",
                                            lineNumber: 816,
                                            columnNumber: 17
                                        }, this)
                                    }, void 0, false, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 814,
                                        columnNumber: 13
                                    }, this),
                                    selectedProject && !loading && sortedScreenshots.length > 0 && viewMode === 'grid' && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$dnd$2d$kit$2f$core$2f$dist$2f$core$2e$esm$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["DndContext"], {
                                        sensors: sensors,
                                        collisionDetection: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$dnd$2d$kit$2f$core$2f$dist$2f$core$2e$esm$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["closestCenter"],
                                        onDragStart: handleDragStart,
                                        onDragEnd: handleDragEnd,
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$dnd$2d$kit$2f$sortable$2f$dist$2f$sortable$2e$esm$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["SortableContext"], {
                                                items: sortedScreenshots.map((s)=>s.filename),
                                                strategy: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$dnd$2d$kit$2f$sortable$2f$dist$2f$sortable$2e$esm$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["rectSortingStrategy"],
                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    ref: gridRef,
                                                    style: {
                                                        ...pageStyles.sortGrid,
                                                        gridTemplateColumns: `repeat(auto-fill, minmax(${getCardMinWidth(zoom)}px, 1fr))`,
                                                        gap: `${Math.round(10 * (zoom / 100))}px`
                                                    },
                                                    children: sortedScreenshots.map((screenshot, index)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                            style: {
                                                                position: 'relative'
                                                            },
                                                            children: [
                                                                isDragOver && dropTargetIndex === index && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                    style: pageStyles.dropIndicator
                                                                }, void 0, false, {
                                                                    fileName: "[project]/src/app/flow-lab/page.tsx",
                                                                    lineNumber: 864,
                                                                    columnNumber: 69
                                                                }, this),
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                                    "data-screenshot-card": true,
                                                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$SortableScreenshot$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["SortableScreenshot"], {
                                                                        screenshot: screenshot,
                                                                        projectName: selectedProject,
                                                                        index: index,
                                                                        isSelected: selectedFiles.has(screenshot.filename),
                                                                        isNewlyAdded: screenshot.filename === newlyAdded,
                                                                        onCardClick: (e)=>handleCardClick(e, index, screenshot.filename),
                                                                        onboardingStart: onboardingRange.start,
                                                                        onboardingEnd: onboardingRange.end
                                                                    }, void 0, false, {
                                                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                                                        lineNumber: 866,
                                                                        columnNumber: 27
                                                                    }, this)
                                                                }, void 0, false, {
                                                                    fileName: "[project]/src/app/flow-lab/page.tsx",
                                                                    lineNumber: 865,
                                                                    columnNumber: 25
                                                                }, this)
                                                            ]
                                                        }, screenshot.filename, true, {
                                                            fileName: "[project]/src/app/flow-lab/page.tsx",
                                                            lineNumber: 863,
                                                            columnNumber: 23
                                                        }, this))
                                                }, void 0, false, {
                                                    fileName: "[project]/src/app/flow-lab/page.tsx",
                                                    lineNumber: 854,
                                                    columnNumber: 19
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                lineNumber: 853,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$dnd$2d$kit$2f$core$2f$dist$2f$core$2e$esm$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["DragOverlay"], {
                                                dropAnimation: dropAnimation,
                                                children: activeScreenshot && selectedProject && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$DragPreview$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["DragPreview"], {
                                                    screenshot: activeScreenshot,
                                                    projectName: selectedProject,
                                                    zoom: zoom
                                                }, void 0, false, {
                                                    fileName: "[project]/src/app/flow-lab/page.tsx",
                                                    lineNumber: 884,
                                                    columnNumber: 21
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                lineNumber: 882,
                                                columnNumber: 17
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 847,
                                        columnNumber: 15
                                    }, this),
                                    selectedProject && !loading && sortedScreenshots.length > 0 && viewMode === 'flow' && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(FlowView, {
                                        screenshots: sortedScreenshots,
                                        onboardingRange: onboardingRange,
                                        branchData: branchData,
                                        editMode: editMode,
                                        pendingBranchScreens: pendingBranchScreens,
                                        selectedProject: selectedProject,
                                        onScreenClick: handleCardClick,
                                        getScreenType: getScreenType
                                    }, void 0, false, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 892,
                                        columnNumber: 15
                                    }, this),
                                    selectedProject && !loading && sortedScreenshots.length === 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: pageStyles.emptyState,
                                        children: "该项目没有截图"
                                    }, void 0, false, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 906,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                lineNumber: 776,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/src/app/flow-lab/page.tsx",
                        lineNumber: 599,
                        columnNumber: 9
                    }, this),
                    selectedProject && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$PreviewPanel$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["PreviewPanel"], {
                        screenshot: previewScreenshot,
                        projectName: selectedProject,
                        currentIndex: previewIndex !== null ? previewIndex : -1,
                        total: sortedScreenshots.length,
                        onClose: ()=>setPreviewIndex(null),
                        onPrev: prevPreview,
                        onNext: nextPreview,
                        onboardingStart: onboardingRange.start,
                        onboardingEnd: onboardingRange.end
                    }, void 0, false, {
                        fileName: "[project]/src/app/flow-lab/page.tsx",
                        lineNumber: 913,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/src/app/flow-lab/page.tsx",
                lineNumber: 592,
                columnNumber: 7
            }, this),
            selectedProject && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$ShortcutsHint$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ShortcutsHint"], {}, void 0, false, {
                fileName: "[project]/src/app/flow-lab/page.tsx",
                lineNumber: 928,
                columnNumber: 27
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$framer$2d$motion$2f$dist$2f$es$2f$components$2f$AnimatePresence$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["AnimatePresence"], {
                children: selectedFiles.size > 0 && selectedProject && viewMode === 'grid' && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$src$2f$components$2f$sort$2f$SelectionBar$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["SelectionBar"], {
                    selectedCount: selectedFiles.size,
                    onDeselect: deselectAll,
                    onDelete: handleDeleteSelected,
                    disabled: saving
                }, void 0, false, {
                    fileName: "[project]/src/app/flow-lab/page.tsx",
                    lineNumber: 933,
                    columnNumber: 11
                }, this)
            }, void 0, false, {
                fileName: "[project]/src/app/flow-lab/page.tsx",
                lineNumber: 931,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/src/app/flow-lab/page.tsx",
        lineNumber: 591,
        columnNumber: 5
    }, this);
}
function FlowView({ screenshots, onboardingRange, branchData, editMode, pendingBranchScreens, selectedProject, onScreenClick, getScreenType }) {
    // 计算 Onboarding 范围
    const startIdx = onboardingRange.start >= 0 ? onboardingRange.start : 0;
    const endIdx = onboardingRange.end >= 0 ? onboardingRange.end + 1 : screenshots.length;
    const onboardingScreenshots = screenshots.slice(startIdx, endIdx);
    // 缩略图 URL
    const getThumbnailUrl = (filename)=>{
        const url = `/api/thumbnails/${encodeURIComponent(selectedProject)}/${encodeURIComponent(filename)}?size=small`;
        // #region agent log
        if (filename === onboardingScreenshots[0]?.filename) {
            fetch('http://127.0.0.1:7242/ingest/1146cc51-3fe3-46a3-9e1a-4801e1a50de0', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    location: 'flow-lab/page.tsx:getThumbnailUrl',
                    message: 'Thumbnail URL generated',
                    data: {
                        url,
                        filename,
                        project: selectedProject
                    },
                    timestamp: Date.now(),
                    hypothesisId: 'H1'
                })
            }).catch(()=>{});
        }
        // #endregion
        return url;
    };
    // 计算每个截图的宽度（用于分支定位）
    const CARD_WIDTH = 60;
    const CARD_GAP = 8;
    const CARD_HEIGHT = 100;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: {
            width: '100%',
            height: '100%',
            overflow: 'auto',
            padding: '24px'
        },
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            style: {
                minWidth: 'fit-content'
            },
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        display: 'flex',
                        alignItems: 'center',
                        marginBottom: '24px'
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                fontSize: '12px',
                                color: 'var(--text-muted)',
                                width: '60px',
                                flexShrink: 0
                            },
                            children: "主流程"
                        }, void 0, false, {
                            fileName: "[project]/src/app/flow-lab/page.tsx",
                            lineNumber: 1022,
                            columnNumber: 11
                        }, this),
                        onboardingScreenshots.map((screenshot, displayIndex)=>{
                            const realIndex = startIdx + displayIndex;
                            const { isForkPoint, isMergePoint, inBranch, isPending } = getScreenType(realIndex);
                            const branchesFromHere = branchData.branches.filter((b)=>b.fork_from === realIndex);
                            const ITEM_WIDTH = CARD_WIDTH + 16 // 固定宽度：图片60 + 箭头区域16
                            ;
                            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    display: 'flex',
                                    alignItems: 'center',
                                    width: displayIndex < onboardingScreenshots.length - 1 ? `${ITEM_WIDTH}px` : 'auto',
                                    flexShrink: 0
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            position: 'relative'
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                onClick: (e)=>onScreenClick(e, realIndex, screenshot.filename),
                                                style: {
                                                    width: `${CARD_WIDTH}px`,
                                                    height: `${CARD_HEIGHT}px`,
                                                    borderRadius: '6px',
                                                    overflow: 'hidden',
                                                    cursor: 'pointer',
                                                    border: isForkPoint ? '3px solid #ef4444' : isMergePoint ? '3px solid #8b5cf6' : isPending ? '3px solid #22c55e' : inBranch ? `2px solid ${inBranch.color}` : '2px solid var(--border-default)',
                                                    opacity: inBranch && !isForkPoint && !isMergePoint ? 0.5 : 1,
                                                    transition: 'all 0.2s',
                                                    position: 'relative'
                                                },
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("img", {
                                                        src: getThumbnailUrl(screenshot.filename),
                                                        alt: screenshot.filename,
                                                        style: {
                                                            width: '100%',
                                                            height: '100%',
                                                            objectFit: 'cover'
                                                        }
                                                    }, void 0, false, {
                                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                                        lineNumber: 1071,
                                                        columnNumber: 21
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: {
                                                            position: 'absolute',
                                                            top: '2px',
                                                            left: '2px',
                                                            fontSize: '10px',
                                                            background: 'rgba(0,0,0,0.7)',
                                                            color: '#fff',
                                                            padding: '1px 4px',
                                                            borderRadius: '3px'
                                                        },
                                                        children: realIndex + 1
                                                    }, void 0, false, {
                                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                                        lineNumber: 1081,
                                                        columnNumber: 21
                                                    }, this),
                                                    isForkPoint && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: {
                                                            position: 'absolute',
                                                            bottom: '2px',
                                                            right: '2px',
                                                            background: '#ef4444',
                                                            borderRadius: '50%',
                                                            width: '16px',
                                                            height: '16px',
                                                            display: 'flex',
                                                            alignItems: 'center',
                                                            justifyContent: 'center'
                                                        },
                                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$git$2d$fork$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__GitFork$3e$__["GitFork"], {
                                                            size: 10,
                                                            color: "#fff"
                                                        }, void 0, false, {
                                                            fileName: "[project]/src/app/flow-lab/page.tsx",
                                                            lineNumber: 1107,
                                                            columnNumber: 25
                                                        }, this)
                                                    }, void 0, false, {
                                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                                        lineNumber: 1095,
                                                        columnNumber: 23
                                                    }, this),
                                                    isMergePoint && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: {
                                                            position: 'absolute',
                                                            bottom: '2px',
                                                            left: '2px',
                                                            background: '#8b5cf6',
                                                            borderRadius: '50%',
                                                            width: '16px',
                                                            height: '16px',
                                                            display: 'flex',
                                                            alignItems: 'center',
                                                            justifyContent: 'center'
                                                        },
                                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$git$2d$merge$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$export__default__as__GitMerge$3e$__["GitMerge"], {
                                                            size: 10,
                                                            color: "#fff"
                                                        }, void 0, false, {
                                                            fileName: "[project]/src/app/flow-lab/page.tsx",
                                                            lineNumber: 1124,
                                                            columnNumber: 25
                                                        }, this)
                                                    }, void 0, false, {
                                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                                        lineNumber: 1112,
                                                        columnNumber: 23
                                                    }, this)
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                lineNumber: 1049,
                                                columnNumber: 19
                                            }, this),
                                            inBranch && !isForkPoint && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    position: 'absolute',
                                                    bottom: '-18px',
                                                    left: '50%',
                                                    transform: 'translateX(-50%)',
                                                    fontSize: '9px',
                                                    color: inBranch.color,
                                                    whiteSpace: 'nowrap',
                                                    background: 'var(--bg-primary)',
                                                    padding: '1px 4px',
                                                    borderRadius: '3px'
                                                },
                                                children: inBranch.name
                                            }, void 0, false, {
                                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                                lineNumber: 1130,
                                                columnNumber: 21
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 1047,
                                        columnNumber: 17
                                    }, this),
                                    displayIndex < onboardingScreenshots.length - 1 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            padding: '0 4px',
                                            color: 'var(--text-muted)',
                                            fontSize: '14px',
                                            flexShrink: 0
                                        },
                                        children: "→"
                                    }, void 0, false, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 1149,
                                        columnNumber: 19
                                    }, this)
                                ]
                            }, screenshot.filename, true, {
                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                lineNumber: 1037,
                                columnNumber: 15
                            }, this);
                        })
                    ]
                }, void 0, true, {
                    fileName: "[project]/src/app/flow-lab/page.tsx",
                    lineNumber: 1017,
                    columnNumber: 9
                }, this),
                branchData.branches.map((branch, branchIdx)=>{
                    const ITEM_WIDTH = CARD_WIDTH + 16 // 图片宽度 + 箭头区域
                    ;
                    const forkDisplayIdx = branch.fork_from - startIdx;
                    // 分支从 fork_from + 1 开始显示
                    const branchStartDisplayIdx = forkDisplayIdx + 1;
                    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: 'flex',
                            alignItems: 'center',
                            marginTop: '20px'
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    width: '60px',
                                    flexShrink: 0,
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '4px'
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            width: '10px',
                                            height: '10px',
                                            background: branch.color,
                                            borderRadius: '2px',
                                            flexShrink: 0
                                        }
                                    }, void 0, false, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 1188,
                                        columnNumber: 17
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        style: {
                                            fontSize: '11px',
                                            color: branch.color,
                                            fontWeight: 600,
                                            whiteSpace: 'nowrap',
                                            overflow: 'hidden',
                                            textOverflow: 'ellipsis'
                                        },
                                        children: branch.name || `分支${branchIdx + 1}`
                                    }, void 0, false, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 1196,
                                        columnNumber: 17
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/src/app/flow-lab/page.tsx",
                                lineNumber: 1180,
                                columnNumber: 15
                            }, this),
                            Array.from({
                                length: branchStartDisplayIdx
                            }).map((_, i)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        width: `${ITEM_WIDTH}px`,
                                        height: `${CARD_HEIGHT}px`,
                                        flexShrink: 0,
                                        position: 'relative'
                                    },
                                    children: i === forkDisplayIdx && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                                        style: {
                                            position: 'absolute',
                                            top: '0',
                                            left: `${CARD_WIDTH / 2}px`,
                                            overflow: 'visible',
                                            pointerEvents: 'none'
                                        },
                                        width: ITEM_WIDTH,
                                        height: CARD_HEIGHT + 20,
                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("line", {
                                            x1: "0",
                                            y1: "0",
                                            x2: ITEM_WIDTH - 8,
                                            y2: CARD_HEIGHT,
                                            stroke: branch.color,
                                            strokeWidth: "2"
                                        }, void 0, false, {
                                            fileName: "[project]/src/app/flow-lab/page.tsx",
                                            lineNumber: 1232,
                                            columnNumber: 23
                                        }, this)
                                    }, void 0, false, {
                                        fileName: "[project]/src/app/flow-lab/page.tsx",
                                        lineNumber: 1221,
                                        columnNumber: 21
                                    }, this)
                                }, `placeholder-${i}`, false, {
                                    fileName: "[project]/src/app/flow-lab/page.tsx",
                                    lineNumber: 1210,
                                    columnNumber: 17
                                }, this)),
                            branch.screens.filter((screenIdx)=>screenIdx > branch.fork_from).map((screenIdx, i, filteredScreens)=>{
                                const screenshot = screenshots[screenIdx];
                                if (!screenshot) return null;
                                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: 'flex',
                                        alignItems: 'center',
                                        width: i < filteredScreens.length - 1 ? `${ITEM_WIDTH}px` : 'auto',
                                        flexShrink: 0
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            onClick: (e)=>onScreenClick(e, screenIdx, screenshot.filename),
                                            style: {
                                                width: `${CARD_WIDTH}px`,
                                                height: `${CARD_HEIGHT}px`,
                                                borderRadius: '6px',
                                                overflow: 'hidden',
                                                cursor: 'pointer',
                                                border: `3px solid ${branch.color}`,
                                                position: 'relative'
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("img", {
                                                    src: getThumbnailUrl(screenshot.filename),
                                                    alt: screenshot.filename,
                                                    style: {
                                                        width: '100%',
                                                        height: '100%',
                                                        objectFit: 'cover'
                                                    }
                                                }, void 0, false, {
                                                    fileName: "[project]/src/app/flow-lab/page.tsx",
                                                    lineNumber: 1271,
                                                    columnNumber: 23
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        position: 'absolute',
                                                        top: '2px',
                                                        left: '2px',
                                                        fontSize: '10px',
                                                        background: branch.color,
                                                        color: '#fff',
                                                        padding: '1px 4px',
                                                        borderRadius: '3px'
                                                    },
                                                    children: screenIdx + 1
                                                }, void 0, false, {
                                                    fileName: "[project]/src/app/flow-lab/page.tsx",
                                                    lineNumber: 1280,
                                                    columnNumber: 23
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/src/app/flow-lab/page.tsx",
                                            lineNumber: 1259,
                                            columnNumber: 21
                                        }, this),
                                        i < filteredScreens.length - 1 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                padding: '0 4px',
                                                color: branch.color,
                                                fontSize: '14px',
                                                flexShrink: 0
                                            },
                                            children: "→"
                                        }, void 0, false, {
                                            fileName: "[project]/src/app/flow-lab/page.tsx",
                                            lineNumber: 1296,
                                            columnNumber: 23
                                        }, this)
                                    ]
                                }, screenIdx, true, {
                                    fileName: "[project]/src/app/flow-lab/page.tsx",
                                    lineNumber: 1253,
                                    columnNumber: 19
                                }, this);
                            })
                        ]
                    }, branch.id, true, {
                        fileName: "[project]/src/app/flow-lab/page.tsx",
                        lineNumber: 1171,
                        columnNumber: 13
                    }, this);
                }),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        position: 'fixed',
                        bottom: '24px',
                        right: '340px',
                        display: 'flex',
                        gap: '16px',
                        background: 'var(--bg-card)',
                        padding: '8px 16px',
                        borderRadius: '8px',
                        fontSize: '12px',
                        color: 'var(--text-muted)',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px'
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        width: '12px',
                                        height: '12px',
                                        background: '#ef4444',
                                        borderRadius: '50%'
                                    }
                                }, void 0, false, {
                                    fileName: "[project]/src/app/flow-lab/page.tsx",
                                    lineNumber: 1327,
                                    columnNumber: 13
                                }, this),
                                "分支点"
                            ]
                        }, void 0, true, {
                            fileName: "[project]/src/app/flow-lab/page.tsx",
                            lineNumber: 1326,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px'
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        width: '12px',
                                        height: '12px',
                                        background: '#8b5cf6',
                                        borderRadius: '50%'
                                    }
                                }, void 0, false, {
                                    fileName: "[project]/src/app/flow-lab/page.tsx",
                                    lineNumber: 1331,
                                    columnNumber: 13
                                }, this),
                                "汇合点"
                            ]
                        }, void 0, true, {
                            fileName: "[project]/src/app/flow-lab/page.tsx",
                            lineNumber: 1330,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px'
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        width: '12px',
                                        height: '12px',
                                        background: '#22c55e',
                                        borderRadius: '2px'
                                    }
                                }, void 0, false, {
                                    fileName: "[project]/src/app/flow-lab/page.tsx",
                                    lineNumber: 1335,
                                    columnNumber: 13
                                }, this),
                                "待选截图"
                            ]
                        }, void 0, true, {
                            fileName: "[project]/src/app/flow-lab/page.tsx",
                            lineNumber: 1334,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/src/app/flow-lab/page.tsx",
                    lineNumber: 1313,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/src/app/flow-lab/page.tsx",
            lineNumber: 1013,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/src/app/flow-lab/page.tsx",
        lineNumber: 1007,
        columnNumber: 5
    }, this);
}
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__b22cdf74._.js.map