const exports = {}
"use strict";
/**
 * Copyright (c) Microsoft Corporation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.endAriaCaches = exports.beginAriaCaches = exports.getAriaDisabled = exports.kAriaDisabledRoles = exports.getAriaLevel = exports.kAriaLevelRoles = exports.getAriaExpanded = exports.kAriaExpandedRoles = exports.getAriaPressed = exports.kAriaPressedRoles = exports.getChecked = exports.getAriaChecked = exports.kAriaCheckedRoles = exports.getAriaSelected = exports.kAriaSelectedRoles = exports.getElementAccessibleDescription = exports.getElementAccessibleName = exports.getAriaLabelledByElements = exports.isElementHiddenForAria = exports.getAriaRole = exports.elementSafeTagName = exports.isVisibleTextNode = exports.isElementVisible = exports.isElementStyleVisibilityVisible = exports.getElementComputedStyle = exports.closestCrossShadow = exports.enclosingShadowRootOrDocument = exports.parentElementOrShadowHost = exports.enclosingElement = exports.isInsideScope = exports.setBrowserName = void 0;
let browserNameForWorkarounds = '';
function setBrowserName(name) {
    browserNameForWorkarounds = name;
}
exports.setBrowserName = setBrowserName;
function isInsideScope(scope, element) {
    while (element) {
        if (scope.contains(element))
            return true;
        element = enclosingShadowHost(element);
    }
    return false;
}
exports.isInsideScope = isInsideScope;
function enclosingElement(node) {
    var _a;
    if (node.nodeType === 1 /* Node.ELEMENT_NODE */)
        return node;
    return (_a = node.parentElement) !== null && _a !== void 0 ? _a : undefined;
}
exports.enclosingElement = enclosingElement;
function parentElementOrShadowHost(element) {
    if (element.parentElement)
        return element.parentElement;
    if (!element.parentNode)
        return;
    if (element.parentNode.nodeType === 11 /* Node.DOCUMENT_FRAGMENT_NODE */ && element.parentNode.host)
        return element.parentNode.host;
}
exports.parentElementOrShadowHost = parentElementOrShadowHost;
function enclosingShadowRootOrDocument(element) {
    let node = element;
    while (node.parentNode)
        node = node.parentNode;
    if (node.nodeType === 11 /* Node.DOCUMENT_FRAGMENT_NODE */ || node.nodeType === 9 /* Node.DOCUMENT_NODE */)
        return node;
}
exports.enclosingShadowRootOrDocument = enclosingShadowRootOrDocument;
function enclosingShadowHost(element) {
    while (element.parentElement)
        element = element.parentElement;
    return parentElementOrShadowHost(element);
}
// Assumption: if scope is provided, element must be inside scope's subtree.
function closestCrossShadow(element, css, scope) {
    while (element) {
        const closest = element.closest(css);
        if (scope && closest !== scope && (closest === null || closest === void 0 ? void 0 : closest.contains(scope)))
            return;
        if (closest)
            return closest;
        element = enclosingShadowHost(element);
    }
}
exports.closestCrossShadow = closestCrossShadow;
function getElementComputedStyle(element, pseudo) {
    return element.ownerDocument && element.ownerDocument.defaultView ? element.ownerDocument.defaultView.getComputedStyle(element, pseudo) : undefined;
}
exports.getElementComputedStyle = getElementComputedStyle;
function isElementStyleVisibilityVisible(element, style) {
    style = style !== null && style !== void 0 ? style : getElementComputedStyle(element);
    if (!style)
        return true;
    // Element.checkVisibility checks for content-visibility and also looks at
    // styles up the flat tree including user-agent ShadowRoots, such as the
    // details element for example.
    // All the browser implement it, but WebKit has a bug which prevents us from using it:
    // https://bugs.webkit.org/show_bug.cgi?id=264733
    // @ts-ignore
    if (Element.prototype.checkVisibility && browserNameForWorkarounds !== 'webkit') {
        // @ts-ignore
        if (!element.checkVisibility())
            return false;
    }
    else {
        // Manual workaround for WebKit that does not have checkVisibility.
        const detailsOrSummary = element.closest('details,summary');
        if (detailsOrSummary !== element && (detailsOrSummary === null || detailsOrSummary === void 0 ? void 0 : detailsOrSummary.nodeName) === 'DETAILS' && !detailsOrSummary.open)
            return false;
    }
    if (style.visibility !== 'visible')
        return false;
    return true;
}
exports.isElementStyleVisibilityVisible = isElementStyleVisibilityVisible;
function isElementVisible(element) {
    // Note: this logic should be similar to waitForDisplayedAtStablePosition() to avoid surprises.
    const style = getElementComputedStyle(element);
    if (!style)
        return true;
    if (style.display === 'contents') {
        // display:contents is not rendered itself, but its child nodes are.
        for (let child = element.firstChild; child; child = child.nextSibling) {
            if (child.nodeType === 1 /* Node.ELEMENT_NODE */ && isElementVisible(child))
                return true;
            if (child.nodeType === 3 /* Node.TEXT_NODE */ && isVisibleTextNode(child))
                return true;
        }
        return false;
    }
    if (!isElementStyleVisibilityVisible(element, style))
        return false;
    const rect = element.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
}
exports.isElementVisible = isElementVisible;
function isVisibleTextNode(node) {
    // https://stackoverflow.com/questions/1461059/is-there-an-equivalent-to-getboundingclientrect-for-text-nodes
    const range = node.ownerDocument.createRange();
    range.selectNode(node);
    const rect = range.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
}
exports.isVisibleTextNode = isVisibleTextNode;
function elementSafeTagName(element) {
    // Named inputs, e.g. <input name=tagName>, will be exposed as fields on the parent <form>
    // and override its properties.
    if (element instanceof HTMLFormElement)
        return 'FORM';
    // Elements from the svg namespace do not have uppercase tagName right away.
    return element.tagName.toUpperCase();
}
exports.elementSafeTagName = elementSafeTagName;
/**
 * Copyright (c) Microsoft Corporation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
function hasExplicitAccessibleName(e) {
    return e.hasAttribute('aria-label') || e.hasAttribute('aria-labelledby');
}
// https://www.w3.org/TR/wai-aria-practices/examples/landmarks/HTML5.html
const kAncestorPreventingLandmark = 'article:not([role]), aside:not([role]), main:not([role]), nav:not([role]), section:not([role]), [role=article], [role=complementary], [role=main], [role=navigation], [role=region]';
// https://www.w3.org/TR/wai-aria-1.2/#global_states
const kGlobalAriaAttributes = new Map([
    ['aria-atomic', undefined],
    ['aria-busy', undefined],
    ['aria-controls', undefined],
    ['aria-current', undefined],
    ['aria-describedby', undefined],
    ['aria-details', undefined],
    // Global use deprecated in ARIA 1.2
    // ['aria-disabled', undefined],
    ['aria-dropeffect', undefined],
    // Global use deprecated in ARIA 1.2
    // ['aria-errormessage', undefined],
    ['aria-flowto', undefined],
    ['aria-grabbed', undefined],
    // Global use deprecated in ARIA 1.2
    // ['aria-haspopup', undefined],
    ['aria-hidden', undefined],
    // Global use deprecated in ARIA 1.2
    // ['aria-invalid', undefined],
    ['aria-keyshortcuts', undefined],
    ['aria-label', new Set(['caption', 'code', 'deletion', 'emphasis', 'generic', 'insertion', 'paragraph', 'presentation', 'strong', 'subscript', 'superscript'])],
    ['aria-labelledby', new Set(['caption', 'code', 'deletion', 'emphasis', 'generic', 'insertion', 'paragraph', 'presentation', 'strong', 'subscript', 'superscript'])],
    ['aria-live', undefined],
    ['aria-owns', undefined],
    ['aria-relevant', undefined],
    ['aria-roledescription', new Set(['generic'])],
]);
function hasGlobalAriaAttribute(element, forRole) {
    return [...kGlobalAriaAttributes].some(([attr, prohibited]) => {
        return !(prohibited === null || prohibited === void 0 ? void 0 : prohibited.has(forRole || '')) && element.hasAttribute(attr);
    });
}
function hasTabIndex(element) {
    return !Number.isNaN(Number(String(element.getAttribute('tabindex'))));
}
function isFocusable(element) {
    // TODO:
    // - "inert" attribute makes the whole substree not focusable
    // - when dialog is open on the page - everything but the dialog is not focusable
    return !isNativelyDisabled(element) && (isNativelyFocusable(element) || hasTabIndex(element));
}
function isNativelyFocusable(element) {
    const tagName = elementSafeTagName(element);
    if (['BUTTON', 'DETAILS', 'SELECT', 'TEXTAREA'].includes(tagName))
        return true;
    if (tagName === 'A' || tagName === 'AREA')
        return element.hasAttribute('href');
    if (tagName === 'INPUT')
        return !element.hidden;
    return false;
}
// https://w3c.github.io/html-aam/#html-element-role-mappings
// https://www.w3.org/TR/html-aria/#docconformance
const kImplicitRoleByTagName = {
    'A': (e) => {
        return e.hasAttribute('href') ? 'link' : null;
    },
    'AREA': (e) => {
        return e.hasAttribute('href') ? 'link' : null;
    },
    'ARTICLE': () => 'article',
    'ASIDE': () => 'complementary',
    'BLOCKQUOTE': () => 'blockquote',
    'BUTTON': () => 'button',
    'CAPTION': () => 'caption',
    'CODE': () => 'code',
    'DATALIST': () => 'listbox',
    'DD': () => 'definition',
    'DEL': () => 'deletion',
    'DETAILS': () => 'group',
    'DFN': () => 'term',
    'DIALOG': () => 'dialog',
    'DT': () => 'term',
    'EM': () => 'emphasis',
    'FIELDSET': () => 'group',
    'FIGURE': () => 'figure',
    'FOOTER': (e) => closestCrossShadow(e, kAncestorPreventingLandmark) ? null : 'contentinfo',
    'FORM': (e) => hasExplicitAccessibleName(e) ? 'form' : null,
    'H1': () => 'heading',
    'H2': () => 'heading',
    'H3': () => 'heading',
    'H4': () => 'heading',
    'H5': () => 'heading',
    'H6': () => 'heading',
    'HEADER': (e) => closestCrossShadow(e, kAncestorPreventingLandmark) ? null : 'banner',
    'HR': () => 'separator',
    'HTML': () => 'document',
    'IMG': (e) => (e.getAttribute('alt') === '') && !e.getAttribute('title') && !hasGlobalAriaAttribute(e) && !hasTabIndex(e) ? 'presentation' : 'img',
    'INPUT': (e) => {
        const type = e.type.toLowerCase();
        if (type === 'search')
            return e.hasAttribute('list') ? 'combobox' : 'searchbox';
        if (['email', 'tel', 'text', 'url', ''].includes(type)) {
            // https://html.spec.whatwg.org/multipage/input.html#concept-input-list
            const list = getIdRefs(e, e.getAttribute('list'))[0];
            return (list && elementSafeTagName(list) === 'DATALIST') ? 'combobox' : 'textbox';
        }
        if (type === 'hidden')
            return '';
        return {
            'button': 'button',
            'checkbox': 'checkbox',
            'image': 'button',
            'number': 'spinbutton',
            'radio': 'radio',
            'range': 'slider',
            'reset': 'button',
            'submit': 'button',
        }[type] || 'textbox';
    },
    'INS': () => 'insertion',
    'LI': () => 'listitem',
    'MAIN': () => 'main',
    'MARK': () => 'mark',
    'MATH': () => 'math',
    'MENU': () => 'list',
    'METER': () => 'meter',
    'NAV': () => 'navigation',
    'OL': () => 'list',
    'OPTGROUP': () => 'group',
    'OPTION': () => 'option',
    'OUTPUT': () => 'status',
    'P': () => 'paragraph',
    'PROGRESS': () => 'progressbar',
    'SECTION': (e) => hasExplicitAccessibleName(e) ? 'region' : null,
    'SELECT': (e) => e.hasAttribute('multiple') || e.size > 1 ? 'listbox' : 'combobox',
    'STRONG': () => 'strong',
    'SUB': () => 'subscript',
    'SUP': () => 'superscript',
    // For <svg> we default to Chrome behavior:
    // - Chrome reports 'img'.
    // - Firefox reports 'diagram' that is not in official ARIA spec yet.
    // - Safari reports 'no role', but still computes accessible name.
    'SVG': () => 'img',
    'TABLE': () => 'table',
    'TBODY': () => 'rowgroup',
    'TD': (e) => {
        const table = closestCrossShadow(e, 'table');
        const role = table ? getExplicitAriaRole(table) : '';
        return (role === 'grid' || role === 'treegrid') ? 'gridcell' : 'cell';
    },
    'TEXTAREA': () => 'textbox',
    'TFOOT': () => 'rowgroup',
    'TH': (e) => {
        if (e.getAttribute('scope') === 'col')
            return 'columnheader';
        if (e.getAttribute('scope') === 'row')
            return 'rowheader';
        const table = closestCrossShadow(e, 'table');
        const role = table ? getExplicitAriaRole(table) : '';
        return (role === 'grid' || role === 'treegrid') ? 'gridcell' : 'cell';
    },
    'THEAD': () => 'rowgroup',
    'TIME': () => 'time',
    'TR': () => 'row',
    'UL': () => 'list',
};
const kPresentationInheritanceParents = {
    'DD': ['DL', 'DIV'],
    'DIV': ['DL'],
    'DT': ['DL', 'DIV'],
    'LI': ['OL', 'UL'],
    'TBODY': ['TABLE'],
    'TD': ['TR'],
    'TFOOT': ['TABLE'],
    'TH': ['TR'],
    'THEAD': ['TABLE'],
    'TR': ['THEAD', 'TBODY', 'TFOOT', 'TABLE'],
};
function getImplicitAriaRole(element) {
    var _a;
    const implicitRole = ((_a = kImplicitRoleByTagName[elementSafeTagName(element)]) === null || _a === void 0 ? void 0 : _a.call(kImplicitRoleByTagName, element)) || '';
    if (!implicitRole)
        return null;
    // Inherit presentation role when required.
    // https://www.w3.org/TR/wai-aria-1.2/#conflict_resolution_presentation_none
    let ancestor = element;
    while (ancestor) {
        const parent = parentElementOrShadowHost(ancestor);
        const parents = kPresentationInheritanceParents[elementSafeTagName(ancestor)];
        if (!parents || !parent || !parents.includes(elementSafeTagName(parent)))
            break;
        const parentExplicitRole = getExplicitAriaRole(parent);
        if ((parentExplicitRole === 'none' || parentExplicitRole === 'presentation') && !hasPresentationConflictResolution(parent, parentExplicitRole))
            return parentExplicitRole;
        ancestor = parent;
    }
    return implicitRole;
}
// https://www.w3.org/TR/wai-aria-1.2/#role_definitions
const allRoles = [
    'alert', 'alertdialog', 'application', 'article', 'banner', 'blockquote', 'button', 'caption', 'cell', 'checkbox', 'code', 'columnheader', 'combobox', 'command',
    'complementary', 'composite', 'contentinfo', 'definition', 'deletion', 'dialog', 'directory', 'document', 'emphasis', 'feed', 'figure', 'form', 'generic', 'grid',
    'gridcell', 'group', 'heading', 'img', 'input', 'insertion', 'landmark', 'link', 'list', 'listbox', 'listitem', 'log', 'main', 'marquee', 'math', 'meter', 'menu',
    'menubar', 'menuitem', 'menuitemcheckbox', 'menuitemradio', 'navigation', 'none', 'note', 'option', 'paragraph', 'presentation', 'progressbar', 'radio', 'radiogroup',
    'range', 'region', 'roletype', 'row', 'rowgroup', 'rowheader', 'scrollbar', 'search', 'searchbox', 'section', 'sectionhead', 'select', 'separator', 'slider',
    'spinbutton', 'status', 'strong', 'structure', 'subscript', 'superscript', 'switch', 'tab', 'table', 'tablist', 'tabpanel', 'term', 'textbox', 'time', 'timer',
    'toolbar', 'tooltip', 'tree', 'treegrid', 'treeitem', 'widget', 'window'
];
// https://www.w3.org/TR/wai-aria-1.2/#abstract_roles
const abstractRoles = ['command', 'composite', 'input', 'landmark', 'range', 'roletype', 'section', 'sectionhead', 'select', 'structure', 'widget', 'window'];
const validRoles = allRoles.filter(role => !abstractRoles.includes(role));
function getExplicitAriaRole(element) {
    // https://www.w3.org/TR/wai-aria-1.2/#document-handling_author-errors_roles
    const roles = (element.getAttribute('role') || '').split(' ').map(role => role.trim());
    return roles.find(role => validRoles.includes(role)) || null;
}
function hasPresentationConflictResolution(element, role) {
    // https://www.w3.org/TR/wai-aria-1.2/#conflict_resolution_presentation_none
    return hasGlobalAriaAttribute(element, role) || isFocusable(element);
}
function getAriaRole(element) {
    const explicitRole = getExplicitAriaRole(element);
    if (!explicitRole)
        return getImplicitAriaRole(element);
    if (explicitRole === 'none' || explicitRole === 'presentation') {
        const implicitRole = getImplicitAriaRole(element);
        if (hasPresentationConflictResolution(element, implicitRole))
            return implicitRole;
    }
    return explicitRole;
}
exports.getAriaRole = getAriaRole;
function getAriaBoolean(attr) {
    return attr === null ? undefined : attr.toLowerCase() === 'true';
}
function isElementIgnoredForAria(element) {
    return ['STYLE', 'SCRIPT', 'NOSCRIPT', 'TEMPLATE'].includes(elementSafeTagName(element));
}
// https://www.w3.org/TR/wai-aria-1.2/#tree_exclusion, but including "none" and "presentation" roles
// Not implemented:
//   `Any descendants of elements that have the characteristic "Children Presentational: True"`
// https://www.w3.org/TR/wai-aria-1.2/#aria-hidden
function isElementHiddenForAria(element) {
    if (isElementIgnoredForAria(element))
        return true;
    const style = getElementComputedStyle(element);
    const isSlot = element.nodeName === 'SLOT';
    if ((style === null || style === void 0 ? void 0 : style.display) === 'contents' && !isSlot) {
        // display:contents is not rendered itself, but its child nodes are.
        for (let child = element.firstChild; child; child = child.nextSibling) {
            if (child.nodeType === 1 /* Node.ELEMENT_NODE */ && !isElementHiddenForAria(child))
                return false;
            if (child.nodeType === 3 /* Node.TEXT_NODE */ && isVisibleTextNode(child))
                return false;
        }
        return true;
    }
    // Note: <option> inside <select> are not affected by visibility or content-visibility.
    // Same goes for <slot>.
    const isOptionInsideSelect = element.nodeName === 'OPTION' && !!element.closest('select');
    if (!isOptionInsideSelect && !isSlot && !isElementStyleVisibilityVisible(element, style))
        return true;
    return belongsToDisplayNoneOrAriaHiddenOrNonSlotted(element);
}
exports.isElementHiddenForAria = isElementHiddenForAria;
function belongsToDisplayNoneOrAriaHiddenOrNonSlotted(element) {
    let hidden = cacheIsHidden === null || cacheIsHidden === void 0 ? void 0 : cacheIsHidden.get(element);
    if (hidden === undefined) {
        hidden = false;
        // When parent has a shadow root, all light dom children must be assigned to a slot,
        // otherwise they are not rendered and considered hidden for aria.
        // Note: we can remove this logic once WebKit supports `Element.checkVisibility`.
        if (element.parentElement && element.parentElement.shadowRoot && !element.assignedSlot)
            hidden = true;
        // display:none and aria-hidden=true are considered hidden for aria.
        if (!hidden) {
            const style = getElementComputedStyle(element);
            hidden = !style || style.display === 'none' || getAriaBoolean(element.getAttribute('aria-hidden')) === true;
        }
        // Check recursively.
        if (!hidden) {
            const parent = parentElementOrShadowHost(element);
            if (parent)
                hidden = belongsToDisplayNoneOrAriaHiddenOrNonSlotted(parent);
        }
        cacheIsHidden === null || cacheIsHidden === void 0 ? void 0 : cacheIsHidden.set(element, hidden);
    }
    return hidden;
}
function getIdRefs(element, ref) {
    if (!ref)
        return [];
    const root = enclosingShadowRootOrDocument(element);
    if (!root)
        return [];
    try {
        const ids = ref.split(' ').filter(id => !!id);
        const set = new Set();
        for (const id of ids) {
            // https://www.w3.org/TR/wai-aria-1.2/#mapping_additional_relations_error_processing
            // "If more than one element has the same ID, the user agent SHOULD use the first element found with the given ID"
            const firstElement = root.querySelector('#' + CSS.escape(id));
            if (firstElement)
                set.add(firstElement);
        }
        return [...set];
    }
    catch (e) {
        return [];
    }
}
function trimFlatString(s) {
    // "Flat string" at https://w3c.github.io/accname/#terminology
    return s.trim();
}
function asFlatString(s) {
    // "Flat string" at https://w3c.github.io/accname/#terminology
    // Note that non-breaking spaces are preserved.
    return s.split('\u00A0').map(chunk => chunk.replace(/\r\n/g, '\n').replace(/\s\s*/g, ' ')).join('\u00A0').trim();
}
function queryInAriaOwned(element, selector) {
    const result = [...element.querySelectorAll(selector)];
    for (const owned of getIdRefs(element, element.getAttribute('aria-owns'))) {
        if (owned.matches(selector))
            result.push(owned);
        result.push(...owned.querySelectorAll(selector));
    }
    return result;
}
function getPseudoContent(element, pseudo) {
    const cache = pseudo === '::before' ? cachePseudoContentBefore : cachePseudoContentAfter;
    if (cache === null || cache === void 0 ? void 0 : cache.has(element))
        return (cache === null || cache === void 0 ? void 0 : cache.get(element)) || '';
    const pseudoStyle = getElementComputedStyle(element, pseudo);
    const content = getPseudoContentImpl(pseudoStyle);
    if (cache)
        cache.set(element, content);
    return content;
}
function getPseudoContentImpl(pseudoStyle) {
    // Note: all browsers ignore display:none and visibility:hidden pseudos.
    if (!pseudoStyle || pseudoStyle.display === 'none' || pseudoStyle.visibility === 'hidden')
        return '';
    const content = pseudoStyle.content;
    if ((content[0] === '\'' && content[content.length - 1] === '\'') ||
        (content[0] === '"' && content[content.length - 1] === '"')) {
        const unquoted = content.substring(1, content.length - 1);
        // SPEC DIFFERENCE.
        // Spec says "CSS textual content, without a space", but we account for display
        // to pass "name_file-label-inline-block-styles-manual.html"
        const display = pseudoStyle.display || 'inline';
        if (display !== 'inline')
            return ' ' + unquoted + ' ';
        return unquoted;
    }
    return '';
}
function getAriaLabelledByElements(element) {
    const ref = element.getAttribute('aria-labelledby');
    if (ref === null)
        return null;
    return getIdRefs(element, ref);
}
exports.getAriaLabelledByElements = getAriaLabelledByElements;
function allowsNameFromContent(role, targetDescendant) {
    // SPEC: https://w3c.github.io/aria/#namefromcontent
    //
    // Note: there is a spec proposal https://github.com/w3c/aria/issues/1821 that
    // is roughly aligned with what Chrome/Firefox do, and we follow that.
    //
    // See chromium implementation here:
    // https://source.chromium.org/chromium/chromium/src/+/main:third_party/blink/renderer/modules/accessibility/ax_object.cc;l=6338;drc=3decef66bc4c08b142a19db9628e9efe68973e64;bpv=0;bpt=1
    const alwaysAllowsNameFromContent = ['button', 'cell', 'checkbox', 'columnheader', 'gridcell', 'heading', 'link', 'menuitem', 'menuitemcheckbox', 'menuitemradio', 'option', 'radio', 'row', 'rowheader', 'switch', 'tab', 'tooltip', 'treeitem'].includes(role);
    const descendantAllowsNameFromContent = targetDescendant && ['', 'caption', 'code', 'contentinfo', 'definition', 'deletion', 'emphasis', 'insertion', 'list', 'listitem', 'mark', 'none', 'paragraph', 'presentation', 'region', 'row', 'rowgroup', 'section', 'strong', 'subscript', 'superscript', 'table', 'term', 'time'].includes(role);
    return alwaysAllowsNameFromContent || descendantAllowsNameFromContent;
}
function getElementAccessibleName(element, includeHidden) {
    const cache = (includeHidden ? cacheAccessibleNameHidden : cacheAccessibleName);
    let accessibleName = cache === null || cache === void 0 ? void 0 : cache.get(element);
    if (accessibleName === undefined) {
        // https://w3c.github.io/accname/#computation-steps
        accessibleName = '';
        // step 1.
        // https://w3c.github.io/aria/#namefromprohibited
        const elementProhibitsNaming = ['caption', 'code', 'definition', 'deletion', 'emphasis', 'generic', 'insertion', 'mark', 'paragraph', 'presentation', 'strong', 'subscript', 'suggestion', 'superscript', 'term', 'time'].includes(getAriaRole(element) || '');
        if (!elementProhibitsNaming) {
            // step 2.
            accessibleName = asFlatString(getTextAlternativeInternal(element, {
                includeHidden,
                visitedElements: new Set(),
                embeddedInDescribedBy: undefined,
                embeddedInLabelledBy: undefined,
                embeddedInLabel: undefined,
                embeddedInNativeTextAlternative: undefined,
                embeddedInTargetElement: 'self',
            }));
        }
        cache === null || cache === void 0 ? void 0 : cache.set(element, accessibleName);
    }
    return accessibleName;
}
exports.getElementAccessibleName = getElementAccessibleName;
function getElementAccessibleDescription(element, includeHidden) {
    const cache = (includeHidden ? cacheAccessibleDescriptionHidden : cacheAccessibleDescription);
    let accessibleDescription = cache === null || cache === void 0 ? void 0 : cache.get(element);
    if (accessibleDescription === undefined) {
        // https://w3c.github.io/accname/#mapping_additional_nd_description
        // https://www.w3.org/TR/html-aam-1.0/#accdesc-computation
        accessibleDescription = '';
        if (element.hasAttribute('aria-describedby')) {
            // precedence 1
            const describedBy = getIdRefs(element, element.getAttribute('aria-describedby'));
            accessibleDescription = asFlatString(describedBy.map(ref => getTextAlternativeInternal(ref, {
                includeHidden,
                visitedElements: new Set(),
                embeddedInLabelledBy: undefined,
                embeddedInLabel: undefined,
                embeddedInNativeTextAlternative: undefined,
                embeddedInTargetElement: 'none',
                embeddedInDescribedBy: { element: ref, hidden: isElementHiddenForAria(ref) },
            })).join(' '));
        }
        else if (element.hasAttribute('aria-description')) {
            // precedence 2
            accessibleDescription = asFlatString(element.getAttribute('aria-description') || '');
        }
        else {
            // TODO: handle precedence 3 - html-aam-specific cases like table>caption.
            // https://www.w3.org/TR/html-aam-1.0/#accdesc-computation
            // precedence 4
            accessibleDescription = asFlatString(element.getAttribute('title') || '');
        }
        cache === null || cache === void 0 ? void 0 : cache.set(element, accessibleDescription);
    }
    return accessibleDescription;
}
exports.getElementAccessibleDescription = getElementAccessibleDescription;
function getTextAlternativeInternal(element, options) {
    var _a, _b, _c, _d;
    if (options.visitedElements.has(element))
        return '';
    const childOptions = Object.assign(Object.assign({}, options), { embeddedInTargetElement: options.embeddedInTargetElement === 'self' ? 'descendant' : options.embeddedInTargetElement });
    // step 2a. Hidden Not Referenced: If the current node is hidden and is:
    // Not part of an aria-labelledby or aria-describedby traversal, where the node directly referenced by that relation was hidden.
    // Nor part of a native host language text alternative element (e.g. label in HTML) or attribute traversal, where the root of that traversal was hidden.
    if (!options.includeHidden) {
        const isEmbeddedInHiddenReferenceTraversal = !!((_a = options.embeddedInLabelledBy) === null || _a === void 0 ? void 0 : _a.hidden) ||
            !!((_b = options.embeddedInDescribedBy) === null || _b === void 0 ? void 0 : _b.hidden) ||
            !!((_c = options.embeddedInNativeTextAlternative) === null || _c === void 0 ? void 0 : _c.hidden) ||
            !!((_d = options.embeddedInLabel) === null || _d === void 0 ? void 0 : _d.hidden);
        if (isElementIgnoredForAria(element) ||
            (!isEmbeddedInHiddenReferenceTraversal && isElementHiddenForAria(element))) {
            options.visitedElements.add(element);
            return '';
        }
    }
    const labelledBy = getAriaLabelledByElements(element);
    // step 2b. LabelledBy:
    // Otherwise, if the current node has an aria-labelledby attribute that contains
    // at least one valid IDREF, and the current node is not already part of an ongoing
    // aria-labelledby or aria-describedby traversal, process its IDREFs in the order they occur...
    if (!options.embeddedInLabelledBy) {
        const accessibleName = (labelledBy || []).map(ref => getTextAlternativeInternal(ref, Object.assign(Object.assign({}, options), { embeddedInLabelledBy: { element: ref, hidden: isElementHiddenForAria(ref) }, embeddedInDescribedBy: undefined, embeddedInTargetElement: 'none', embeddedInLabel: undefined, embeddedInNativeTextAlternative: undefined }))).join(' ');
        if (accessibleName)
            return accessibleName;
    }
    const role = getAriaRole(element) || '';
    const tagName = elementSafeTagName(element);
    // step 2c:
    //   if the current node is a control embedded within the label (e.g. any element directly referenced by aria-labelledby) for another widget...
    //
    // also step 2d "skip to rule Embedded Control" section:
    //   If traversal of the current node is due to recursion and the current node is an embedded control...
    // Note this is not strictly by the spec, because spec only applies this logic when "aria-label" is present.
    // However, browsers and and wpt test name_heading-combobox-focusable-alternative-manual.html follow this behavior,
    // and there is an issue filed for this: https://github.com/w3c/accname/issues/64
    if (!!options.embeddedInLabel || !!options.embeddedInLabelledBy || options.embeddedInTargetElement === 'descendant') {
        const isOwnLabel = [...element.labels || []].includes(element);
        const isOwnLabelledBy = (labelledBy || []).includes(element);
        if (!isOwnLabel && !isOwnLabelledBy) {
            if (role === 'textbox') {
                options.visitedElements.add(element);
                if (tagName === 'INPUT' || tagName === 'TEXTAREA')
                    return element.value;
                return element.textContent || '';
            }
            if (['combobox', 'listbox'].includes(role)) {
                options.visitedElements.add(element);
                let selectedOptions;
                if (tagName === 'SELECT') {
                    selectedOptions = [...element.selectedOptions];
                    if (!selectedOptions.length && element.options.length)
                        selectedOptions.push(element.options[0]);
                }
                else {
                    const listbox = role === 'combobox' ? queryInAriaOwned(element, '*').find(e => getAriaRole(e) === 'listbox') : element;
                    selectedOptions = listbox ? queryInAriaOwned(listbox, '[aria-selected="true"]').filter(e => getAriaRole(e) === 'option') : [];
                }
                if (!selectedOptions.length && tagName === 'INPUT') {
                    // SPEC DIFFERENCE:
                    // This fallback is not explicitly mentioned in the spec, but all browsers and
                    // wpt test name_heading-combobox-focusable-alternative-manual.html do this.
                    return element.value;
                }
                return selectedOptions.map(option => getTextAlternativeInternal(option, childOptions)).join(' ');
            }
            if (['progressbar', 'scrollbar', 'slider', 'spinbutton', 'meter'].includes(role)) {
                options.visitedElements.add(element);
                if (element.hasAttribute('aria-valuetext'))
                    return element.getAttribute('aria-valuetext') || '';
                if (element.hasAttribute('aria-valuenow'))
                    return element.getAttribute('aria-valuenow') || '';
                return element.getAttribute('value') || '';
            }
            if (['menu'].includes(role)) {
                // https://github.com/w3c/accname/issues/67#issuecomment-553196887
                options.visitedElements.add(element);
                return '';
            }
        }
    }
    // step 2d.
    const ariaLabel = element.getAttribute('aria-label') || '';
    if (trimFlatString(ariaLabel)) {
        options.visitedElements.add(element);
        return ariaLabel;
    }
    // step 2e.
    if (!['presentation', 'none'].includes(role)) {
        // https://w3c.github.io/html-aam/#input-type-button-input-type-submit-and-input-type-reset-accessible-name-computation
        //
        // SPEC DIFFERENCE.
        // Spec says to ignore this when aria-labelledby is defined.
        // WebKit follows the spec, while Chromium and Firefox do not.
        // We align with Chromium and Firefox here.
        if (tagName === 'INPUT' && ['button', 'submit', 'reset'].includes(element.type)) {
            options.visitedElements.add(element);
            const value = element.value || '';
            if (trimFlatString(value))
                return value;
            if (element.type === 'submit')
                return 'Submit';
            if (element.type === 'reset')
                return 'Reset';
            const title = element.getAttribute('title') || '';
            return title;
        }
        // https://w3c.github.io/html-aam/#input-type-image-accessible-name-computation
        //
        // SPEC DIFFERENCE.
        // Spec says to ignore this when aria-labelledby is defined, but all browsers take it into account.
        if (tagName === 'INPUT' && element.type === 'image') {
            options.visitedElements.add(element);
            const labels = element.labels || [];
            if (labels.length && !options.embeddedInLabelledBy)
                return getAccessibleNameFromAssociatedLabels(labels, options);
            const alt = element.getAttribute('alt') || '';
            if (trimFlatString(alt))
                return alt;
            const title = element.getAttribute('title') || '';
            if (trimFlatString(title))
                return title;
            // SPEC DIFFERENCE.
            // Spec says return localized "Submit Query", but browsers and axe-core insist on "Submit".
            return 'Submit';
        }
        // https://w3c.github.io/html-aam/#button-element-accessible-name-computation
        if (!labelledBy && tagName === 'BUTTON') {
            options.visitedElements.add(element);
            const labels = element.labels || [];
            if (labels.length)
                return getAccessibleNameFromAssociatedLabels(labels, options);
            // From here, fallthrough to step 2f.
        }
        // https://w3c.github.io/html-aam/#output-element-accessible-name-computation
        if (!labelledBy && tagName === 'OUTPUT') {
            options.visitedElements.add(element);
            const labels = element.labels || [];
            if (labels.length)
                return getAccessibleNameFromAssociatedLabels(labels, options);
            return element.getAttribute('title') || '';
        }
        // https://w3c.github.io/html-aam/#input-type-text-input-type-password-input-type-number-input-type-search-input-type-tel-input-type-email-input-type-url-and-textarea-element-accessible-name-computation
        // https://w3c.github.io/html-aam/#other-form-elements-accessible-name-computation
        // For "other form elements", we count select and any other input.
        //
        // Note: WebKit does not follow the spec and uses placeholder when aria-labelledby is present.
        if (!labelledBy && (tagName === 'TEXTAREA' || tagName === 'SELECT' || tagName === 'INPUT')) {
            options.visitedElements.add(element);
            const labels = element.labels || [];
            if (labels.length)
                return getAccessibleNameFromAssociatedLabels(labels, options);
            const usePlaceholder = (tagName === 'INPUT' && ['text', 'password', 'search', 'tel', 'email', 'url'].includes(element.type)) || tagName === 'TEXTAREA';
            const placeholder = element.getAttribute('placeholder') || '';
            const title = element.getAttribute('title') || '';
            if (!usePlaceholder || title)
                return title;
            return placeholder;
        }
        // https://w3c.github.io/html-aam/#fieldset-and-legend-elements
        if (!labelledBy && tagName === 'FIELDSET') {
            options.visitedElements.add(element);
            for (let child = element.firstElementChild; child; child = child.nextElementSibling) {
                if (elementSafeTagName(child) === 'LEGEND') {
                    return getTextAlternativeInternal(child, Object.assign(Object.assign({}, childOptions), { embeddedInNativeTextAlternative: { element: child, hidden: isElementHiddenForAria(child) } }));
                }
            }
            const title = element.getAttribute('title') || '';
            return title;
        }
        // https://w3c.github.io/html-aam/#figure-and-figcaption-elements
        if (!labelledBy && tagName === 'FIGURE') {
            options.visitedElements.add(element);
            for (let child = element.firstElementChild; child; child = child.nextElementSibling) {
                if (elementSafeTagName(child) === 'FIGCAPTION') {
                    return getTextAlternativeInternal(child, Object.assign(Object.assign({}, childOptions), { embeddedInNativeTextAlternative: { element: child, hidden: isElementHiddenForAria(child) } }));
                }
            }
            const title = element.getAttribute('title') || '';
            return title;
        }
        // https://w3c.github.io/html-aam/#img-element
        //
        // SPEC DIFFERENCE.
        // Spec says to ignore this when aria-labelledby is defined, but all browsers take it into account.
        if (tagName === 'IMG') {
            options.visitedElements.add(element);
            const alt = element.getAttribute('alt') || '';
            if (trimFlatString(alt))
                return alt;
            const title = element.getAttribute('title') || '';
            return title;
        }
        // https://w3c.github.io/html-aam/#table-element
        if (tagName === 'TABLE') {
            options.visitedElements.add(element);
            for (let child = element.firstElementChild; child; child = child.nextElementSibling) {
                if (elementSafeTagName(child) === 'CAPTION') {
                    return getTextAlternativeInternal(child, Object.assign(Object.assign({}, childOptions), { embeddedInNativeTextAlternative: { element: child, hidden: isElementHiddenForAria(child) } }));
                }
            }
            // SPEC DIFFERENCE.
            // Spec does not say a word about <table summary="...">, but all browsers actually support it.
            const summary = element.getAttribute('summary') || '';
            if (summary)
                return summary;
            // SPEC DIFFERENCE.
            // Spec says "if the table element has a title attribute, then use that attribute".
            // We ignore title to pass "name_from_content-manual.html".
        }
        // https://w3c.github.io/html-aam/#area-element
        if (tagName === 'AREA') {
            options.visitedElements.add(element);
            const alt = element.getAttribute('alt') || '';
            if (trimFlatString(alt))
                return alt;
            const title = element.getAttribute('title') || '';
            return title;
        }
        // https://www.w3.org/TR/svg-aam-1.0/#mapping_additional_nd
        if (tagName === 'SVG' || element.ownerSVGElement) {
            options.visitedElements.add(element);
            for (let child = element.firstElementChild; child; child = child.nextElementSibling) {
                if (elementSafeTagName(child) === 'TITLE' && child.ownerSVGElement) {
                    return getTextAlternativeInternal(child, Object.assign(Object.assign({}, childOptions), { embeddedInLabelledBy: { element: child, hidden: isElementHiddenForAria(child) } }));
                }
            }
        }
        if (element.ownerSVGElement && tagName === 'A') {
            const title = element.getAttribute('xlink:title') || '';
            if (trimFlatString(title)) {
                options.visitedElements.add(element);
                return title;
            }
        }
    }
    // See https://w3c.github.io/html-aam/#summary-element-accessible-name-computation for "summary"-specific check.
    const shouldNameFromContentForSummary = tagName === 'SUMMARY' && !['presentation', 'none'].includes(role);
    // step 2f + step 2h.
    if (allowsNameFromContent(role, options.embeddedInTargetElement === 'descendant') ||
        shouldNameFromContentForSummary ||
        !!options.embeddedInLabelledBy || !!options.embeddedInDescribedBy ||
        !!options.embeddedInLabel || !!options.embeddedInNativeTextAlternative) {
        options.visitedElements.add(element);
        const tokens = [];
        const visit = (node, skipSlotted) => {
            var _a;
            if (skipSlotted && node.assignedSlot)
                return;
            if (node.nodeType === 1 /* Node.ELEMENT_NODE */) {
                const display = ((_a = getElementComputedStyle(node)) === null || _a === void 0 ? void 0 : _a.display) || 'inline';
                let token = getTextAlternativeInternal(node, childOptions);
                // SPEC DIFFERENCE.
                // Spec says "append the result to the accumulated text", assuming "with space".
                // However, multiple tests insist that inline elements do not add a space.
                // Additionally, <br> insists on a space anyway, see "name_file-label-inline-block-elements-manual.html"
                if (display !== 'inline' || node.nodeName === 'BR')
                    token = ' ' + token + ' ';
                tokens.push(token);
            }
            else if (node.nodeType === 3 /* Node.TEXT_NODE */) {
                // step 2g.
                tokens.push(node.textContent || '');
            }
        };
        tokens.push(getPseudoContent(element, '::before'));
        const assignedNodes = element.nodeName === 'SLOT' ? element.assignedNodes() : [];
        if (assignedNodes.length) {
            for (const child of assignedNodes)
                visit(child, false);
        }
        else {
            for (let child = element.firstChild; child; child = child.nextSibling)
                visit(child, true);
            if (element.shadowRoot) {
                for (let child = element.shadowRoot.firstChild; child; child = child.nextSibling)
                    visit(child, true);
            }
            for (const owned of getIdRefs(element, element.getAttribute('aria-owns')))
                visit(owned, true);
        }
        tokens.push(getPseudoContent(element, '::after'));
        const accessibleName = tokens.join('');
        // Spec says "Return the accumulated text if it is not the empty string". However, that is not really
        // compatible with the real browser behavior and wpt tests, where an element with empty contents will fallback to the title.
        // So we follow the spec everywhere except for the target element itself. This can probably be improved.
        const maybeTrimmedAccessibleName = options.embeddedInTargetElement === 'self' ? trimFlatString(accessibleName) : accessibleName;
        if (maybeTrimmedAccessibleName)
            return accessibleName;
    }
    // step 2i.
    if (!['presentation', 'none'].includes(role) || tagName === 'IFRAME') {
        options.visitedElements.add(element);
        const title = element.getAttribute('title') || '';
        if (trimFlatString(title))
            return title;
    }
    options.visitedElements.add(element);
    return '';
}
exports.kAriaSelectedRoles = ['gridcell', 'option', 'row', 'tab', 'rowheader', 'columnheader', 'treeitem'];
function getAriaSelected(element) {
    // https://www.w3.org/TR/wai-aria-1.2/#aria-selected
    // https://www.w3.org/TR/html-aam-1.0/#html-attribute-state-and-property-mappings
    if (elementSafeTagName(element) === 'OPTION')
        return element.selected;
    if (exports.kAriaSelectedRoles.includes(getAriaRole(element) || ''))
        return getAriaBoolean(element.getAttribute('aria-selected')) === true;
    return null;
}
exports.getAriaSelected = getAriaSelected;
exports.kAriaCheckedRoles = ['checkbox', 'menuitemcheckbox', 'option', 'radio', 'switch', 'menuitemradio', 'treeitem'];
function getAriaChecked(element) {
    const result = getChecked(element, true);
    return result === 'error' ? null : result;
}
exports.getAriaChecked = getAriaChecked;
function getChecked(element, allowMixed) {
    const tagName = elementSafeTagName(element);
    // https://www.w3.org/TR/wai-aria-1.2/#aria-checked
    // https://www.w3.org/TR/html-aam-1.0/#html-attribute-state-and-property-mappings
    if (allowMixed && tagName === 'INPUT' && element.indeterminate)
        return 'mixed';
    if (tagName === 'INPUT' && ['checkbox', 'radio'].includes(element.type))
        return element.checked;
    if (exports.kAriaCheckedRoles.includes(getAriaRole(element) || '')) {
        const checked = element.getAttribute('aria-checked');
        if (checked === 'true')
            return true;
        if (allowMixed && checked === 'mixed')
            return 'mixed';
        return false;
    }
    return 'error';
}
exports.getChecked = getChecked;
exports.kAriaPressedRoles = ['button'];
function getAriaPressed(element) {
    // https://www.w3.org/TR/wai-aria-1.2/#aria-pressed
    if (exports.kAriaPressedRoles.includes(getAriaRole(element) || '')) {
        const pressed = element.getAttribute('aria-pressed');
        if (pressed === 'true')
            return true;
        if (pressed === 'mixed')
            return 'mixed';
    }
    return null;
}
exports.getAriaPressed = getAriaPressed;
exports.kAriaExpandedRoles = ['application', 'button', 'checkbox', 'combobox', 'gridcell', 'link', 'listbox', 'menuitem', 'row', 'rowheader', 'tab', 'treeitem', 'columnheader', 'menuitemcheckbox', 'menuitemradio', 'rowheader', 'switch'];
function getAriaExpanded(element) {
    // https://www.w3.org/TR/wai-aria-1.2/#aria-expanded
    // https://www.w3.org/TR/html-aam-1.0/#html-attribute-state-and-property-mappings
    if (elementSafeTagName(element) === 'DETAILS')
        return element.open;
    if (exports.kAriaExpandedRoles.includes(getAriaRole(element) || '')) {
        const expanded = element.getAttribute('aria-expanded');
        if (expanded === null)
            return null; // 'none';
        if (expanded === 'true')
            return true;
        return false;
    }
    return null; // 'none';
}
exports.getAriaExpanded = getAriaExpanded;
exports.kAriaLevelRoles = ['heading', 'listitem', 'row', 'treeitem'];
function getAriaLevel(element) {
    // https://www.w3.org/TR/wai-aria-1.2/#aria-level
    // https://www.w3.org/TR/html-aam-1.0/#html-attribute-state-and-property-mappings
    const native = { 'H1': 1, 'H2': 2, 'H3': 3, 'H4': 4, 'H5': 5, 'H6': 6 }[elementSafeTagName(element)];
    if (native)
        return native;
    if (exports.kAriaLevelRoles.includes(getAriaRole(element) || '')) {
        const attr = element.getAttribute('aria-level');
        const value = attr === null ? Number.NaN : Number(attr);
        if (Number.isInteger(value) && value >= 1)
            return value;
    }
    return null;
}
exports.getAriaLevel = getAriaLevel;
exports.kAriaDisabledRoles = ['application', 'button', 'composite', 'gridcell', 'group', 'input', 'link', 'menuitem', 'scrollbar', 'separator', 'tab', 'checkbox', 'columnheader', 'combobox', 'grid', 'listbox', 'menu', 'menubar', 'menuitemcheckbox', 'menuitemradio', 'option', 'radio', 'radiogroup', 'row', 'rowheader', 'searchbox', 'select', 'slider', 'spinbutton', 'switch', 'tablist', 'textbox', 'toolbar', 'tree', 'treegrid', 'treeitem'];
function getAriaDisabled(element) {
    // https://www.w3.org/TR/wai-aria-1.2/#aria-disabled
    // Note that aria-disabled applies to all descendants, so we look up the hierarchy.
    const a = isNativelyDisabled(element);
    const b = hasExplicitAriaDisabled(element);
    if (a === null && b === null) {
        return null;
    }
    return a || b;
}
exports.getAriaDisabled = getAriaDisabled;
function isNativelyDisabled(element) {
    // https://www.w3.org/TR/html-aam-1.0/#html-attribute-state-and-property-mappings
    const isNativeFormControl = ['BUTTON', 'INPUT', 'SELECT', 'TEXTAREA', 'OPTION', 'OPTGROUP'].includes(element.tagName);
    if (isNativeFormControl) {
        return (element.hasAttribute('disabled') || belongsToDisabledFieldSet(element));
    }
    return null;
}
function belongsToDisabledFieldSet(element) {
    if (!element)
        return null;
    //   return false;
    if (elementSafeTagName(element) === 'FIELDSET' && element.hasAttribute('disabled'))
        return true;
    // fieldset does not work across shadow boundaries.
    return belongsToDisabledFieldSet(element.parentElement);
}
function hasExplicitAriaDisabled(element) {
    if (!element)
        return null;
    // return false;
    if (exports.kAriaDisabledRoles.includes(getAriaRole(element) || '')) {
        const attribute = (element.getAttribute('aria-disabled') || '').toLowerCase();
        if (attribute === 'true')
            return true;
        if (attribute === 'false')
            return false;
    }
    // aria-disabled works across shadow boundaries.
    return hasExplicitAriaDisabled(parentElementOrShadowHost(element));
}
function getAccessibleNameFromAssociatedLabels(labels, options) {
    return [...labels].map(label => getTextAlternativeInternal(label, Object.assign(Object.assign({}, options), { embeddedInLabel: { element: label, hidden: isElementHiddenForAria(label) }, embeddedInNativeTextAlternative: undefined, embeddedInLabelledBy: undefined, embeddedInDescribedBy: undefined, embeddedInTargetElement: 'none' }))).filter(accessibleName => !!accessibleName).join(' ');
}
let cacheAccessibleName;
let cacheAccessibleNameHidden;
let cacheAccessibleDescription;
let cacheAccessibleDescriptionHidden;
let cacheIsHidden;
let cachePseudoContentBefore;
let cachePseudoContentAfter;
let cachesCounter = 0;
function beginAriaCaches() {
    ++cachesCounter;
    cacheAccessibleName !== null && cacheAccessibleName !== void 0 ? cacheAccessibleName : (cacheAccessibleName = new Map());
    cacheAccessibleNameHidden !== null && cacheAccessibleNameHidden !== void 0 ? cacheAccessibleNameHidden : (cacheAccessibleNameHidden = new Map());
    cacheAccessibleDescription !== null && cacheAccessibleDescription !== void 0 ? cacheAccessibleDescription : (cacheAccessibleDescription = new Map());
    cacheAccessibleDescriptionHidden !== null && cacheAccessibleDescriptionHidden !== void 0 ? cacheAccessibleDescriptionHidden : (cacheAccessibleDescriptionHidden = new Map());
    cacheIsHidden !== null && cacheIsHidden !== void 0 ? cacheIsHidden : (cacheIsHidden = new Map());
    cachePseudoContentBefore !== null && cachePseudoContentBefore !== void 0 ? cachePseudoContentBefore : (cachePseudoContentBefore = new Map());
    cachePseudoContentAfter !== null && cachePseudoContentAfter !== void 0 ? cachePseudoContentAfter : (cachePseudoContentAfter = new Map());
}
exports.beginAriaCaches = beginAriaCaches;
function endAriaCaches() {
    if (!--cachesCounter) {
        cacheAccessibleName = undefined;
        cacheAccessibleNameHidden = undefined;
        cacheAccessibleDescription = undefined;
        cacheAccessibleDescriptionHidden = undefined;
        cacheIsHidden = undefined;
        cachePseudoContentBefore = undefined;
        cachePseudoContentAfter = undefined;
    }
}
exports.endAriaCaches = endAriaCaches;
function getElementInfo(element, includeHidden) {
    const clientRect = element.getBoundingClientRect();
    const result = {
        role: getAriaRole(element),
        // .replace is from normalizeWhiteSpace in utils/isomorphic/stringUtils.ts
        name: getElementAccessibleName(element, includeHidden).replace(/\u200b/g, '').trim().replace(/\s+/g, ' '),
        properties: {
            selected: getAriaSelected(element),
            checked: getAriaChecked(element),
            pressed: getAriaPressed(element),
            expanded: getAriaExpanded(element),
            level: getAriaLevel(element),
            disabled: getAriaDisabled(element),
            // url: null as string | null,
        },
        // bounding_box: [clientRect.x, clientRect.y, clientRect.width, clientRect.height], // camel_case for Python.
        bounding_box: {
            x: clientRect.x, y: clientRect.y, width: clientRect.width, height: clientRect.height
        },
        tag_name: element.tagName.toLowerCase(),
    };
    if (element.hasAttribute("href")) {
        // @ts-ignore
        result.properties.url = element.getAttribute("href");
    }
    // Remove the `null` properties.
    for (const key in result.properties) {
        if (result.properties[key] === null) {
            delete result.properties[key];
        }
    }
    if (element.tagName == 'IFRAME') {
        result.role = 'iframe';
        // @ts-ignore
        result.properties.name = element.name;
        // @ts-ignore
        result.properties.url = element.src;
    }
    return result;
}
;
function _populateLocatorParts(axtree, locatorParts) {
    // Done in this way because the correct locator can only be known from the parent element.
    axtree.locator_parts = locatorParts;
    const { children } = axtree;
    for (let childIndex = 0; childIndex < children.length; childIndex++) {
        // Attempt to generate a child locator.
        // Test candidate locators.
        // 1. Count number of role & name substring match
        // 2. Count number of role & name exact match
        // We will attempt 1 and 2, and if 2 doesn't work, we use an nth selector on 2.
        const child = children[childIndex];
        let matchingNameSubstrings = 0;
        let matchingNameExacts = 0;
        let matchingNameSubstringsIndex = -1;
        let matchingNameExactsIndex = -1;
        for (let siblingIndex = 0; siblingIndex < children.length; siblingIndex++) {
            const sibling = children[siblingIndex];
            if (childIndex == siblingIndex) {
                matchingNameExactsIndex = matchingNameExacts;
                matchingNameSubstringsIndex = matchingNameSubstrings;
            }
            // if (childRoles[siblingIndex] == childRoles[childIndex]) {
            if (sibling.role == child.role) {
                if (sibling.name.toLowerCase().includes(child.name.toLowerCase())) {
                    matchingNameSubstrings += 1;
                }
                // Whitespace is already handled by Playwright's Accessibility Tree algorithm.
                if (sibling.name == child.name) {
                    matchingNameExacts += 1;
                }
            }
        }
        const newLocatorsForChild = [];
        // If the substring match is unique, use it.
        if (matchingNameSubstrings === 1) {
            newLocatorsForChild.push({
                selector: "get_by_role",
                parameters: { role: child.role, name: child.name }
            });
        }
        else if (matchingNameExacts === 1) {
            newLocatorsForChild.push({
                selector: "get_by_role",
                parameters: { role: child.role, name: child.name, exact: true }
            });
        }
        else {
            newLocatorsForChild.push({
                selector: "get_by_role",
                parameters: { role: child.role, name: child.name, exact: true }
            });
            newLocatorsForChild.push({
                selector: "nth",
                parameters: { index: matchingNameExactsIndex },
            });
        }
        _populateLocatorParts(child, newLocatorsForChild);
    }
}
function _getAccessibilityTree(element, includeHidden, idCounter) {
    let children = [...element.children];
    const id = idCounter;
    idCounter += 1;
    const childrenResults = [];
    for (const child of children) {
        // to do potentially: add text nodes
        const axtree = _getAccessibilityTree(child, includeHidden, idCounter);
        idCounter += 1;
        if (Array.isArray(axtree)) {
            childrenResults.push(...axtree);
        }
        else {
            childrenResults.push(axtree);
        }
    }
    if (element === document.body) {
        return Object.assign(Object.assign({}, getElementInfo(element, includeHidden)), { id, role: "document", name: document.title, children: childrenResults, locator_parts: [] });
    }
    const role = getAriaRole(element);
    const name = getElementAccessibleName(element, includeHidden);
    const skipNode = (role === null ||
        (!includeHidden && isElementHiddenForAria(element)) ||
        (name.length === 0) && ((Object.keys(getElementInfo(element, includeHidden).properties).length === 0 && [
            "generic",
            "img",
            "list",
            "strong",
            "paragraph",
            "banner",
            "navigation",
            "Section",
            "LabelText",
            "Legend",
            "none",
            "emphasis",
            "superscript",
            "separator",
        ].includes(role)) || role == 'listitem'));
    if (skipNode && !(element.tagName.toLowerCase() == 'iframe')) {
        return childrenResults;
    }
    else {
        return Object.assign(Object.assign({}, getElementInfo(element, includeHidden)), { id, children: childrenResults, locator_parts: [] });
    }
}
function getAccessibilityTree() {
    let idCounter = 0;
    const tree = _getAccessibilityTree(document.body, false, idCounter);
    if (Array.isArray(tree)) {
        throw new Error("Expected a single tree, but got multiple trees.");
    }
    _populateLocatorParts(tree, [
        { selector: "get_by_role", parameters: { role: "document" } }
    ]);
    return tree;
}
// @ts-ignore
window.__webAgentDomInterface = {
    getElementInfo,
    getAccessibilityTree
};
