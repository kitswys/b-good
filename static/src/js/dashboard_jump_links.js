/** @odoo-module **/

const ACTION_BUTTONS = {
    action_open_assessments: 'button[name="action_open_assessments"]',
    action_open_missing_evidence_lines: 'button[name="action_open_missing_evidence_lines"]',
    action_open_high_risk_suppliers: 'button[name="action_open_high_risk_suppliers"]',
    action_open_recalculate_scorecard: 'button[name="action_open_recalculate_scorecard"]',
    action_open_generate_evidence: 'button[name="action_open_generate_evidence"]',
    action_open_supplier_profiles: 'button[name="action_open_supplier_profiles"]',
    action_open_chart_spend_classification: 'button[name="action_open_chart_spend_classification"]',
    action_open_chart_evidence_status: 'button[name="action_open_chart_evidence_status"]',
    action_open_chart_certificate_status: 'button[name="action_open_chart_certificate_status"]',
    action_open_chart_assessment_trend: 'button[name="action_open_chart_assessment_trend"]',
    action_open_info_executive_snapshot: 'button[name="action_open_info_executive_snapshot"]',
    action_open_info_business_impact: 'button[name="action_open_info_business_impact"]',
    action_open_info_fastest_improvement_path: 'button[name="action_open_info_fastest_improvement_path"]',
    action_open_info_in_scope_spend: 'button[name="action_open_info_in_scope_spend"]',
    action_open_info_verification_ready_spend: 'button[name="action_open_info_verification_ready_spend"]',
    action_open_info_current_period_score: 'button[name="action_open_info_current_period_score"]',
    action_open_info_supplier_compliance_health: 'button[name="action_open_info_supplier_compliance_health"]',
    action_open_info_spend_at_risk: 'button[name="action_open_info_spend_at_risk"]',
    action_open_info_bee_level: 'button[name="action_open_info_bee_level"]',
};

const INFO_PANELS = {
    executive_snapshot: {
        title: "Executive Snapshot",
        body: "Your officially recognized B-BBEE level calculated based on current recognized spend recognition.",
        action: "action_open_info_executive_snapshot",
    },
    business_impact: {
        title: "Business Impact",
        body: "Critical operational risk levels based on missing compliance items and exposure metrics.",
        action: "action_open_info_business_impact",
    },
    fastest_improvement_path: {
        title: "Fastest Improvement Path",
        body: "Actionable strategic checklist steps to unlock your next target compliance level.",
        action: "action_open_info_fastest_improvement_path",
    },
    in_scope_spend: {
        title: "In-Scope Spend",
        body: "Total procurement financial spend pulled from posted vendor bills within this active evaluation period.",
        action: "action_open_info_in_scope_spend",
    },
    verification_ready_spend: {
        title: "Verification-Ready Spend",
        body: "The total portion of your spend that is fully supported by valid compliance documents and will count on a scorecard.",
        action: "action_open_info_verification_ready_spend",
    },
    current_period_score: {
        title: "Current Period Score",
        body: "Your current calculated procurement point progress matched directly against your corporate target threshold.",
        action: "action_open_info_current_period_score",
    },
    supplier_compliance_health: {
        title: "Supplier Compliance Health",
        body: "The percentage of active suppliers in your system who have valid, unexpired certificates or affidavits loaded.",
        action: "action_open_info_supplier_compliance_health",
    },
    spend_at_risk: {
        title: "Spend At Risk",
        body: "Procurement spend tied to suppliers with expired, missing, or unverified documentation. This spend is highly vulnerable to auditor rejection.",
        action: "action_open_info_spend_at_risk",
    },
    bee_level: {
        title: "B-BBEE Level",
        body: "Your current B-BBEE level is the headline compliance grade for the selected period. Level 1 is the strongest result and Level 8 is the weakest. Lower numbers mean better procurement recognition, stronger audit confidence, and less operational risk.",
        action: "action_open_info_bee_level",
    },
};

let activeInfoOverlay = null;
let activeInfoAnchor = null;

function closeInfoOverlay() {
    if (activeInfoOverlay) {
        activeInfoOverlay.remove();
        activeInfoOverlay = null;
        activeInfoAnchor = null;
    }
}

function openInfoOverlay(infoKey, anchorEl) {
    const info = INFO_PANELS[infoKey];
    if (!info) {
        return;
    }
    closeInfoOverlay();

    const overlay = document.createElement("div");
    overlay.className = "bbbbee-info-overlay";
    overlay.style.cssText = [
        "position:fixed",
        "inset:0",
        "background:transparent",
        "z-index:1200",
    ].join(";");

    const panel = document.createElement("div");
    panel.style.cssText = [
        "position:fixed",
        "width:min(380px, calc(100vw - 24px))",
        "border:1px solid #dbe2ee",
        "border-radius:12px",
        "background:#fff",
        "box-shadow:0 18px 45px rgba(15,23,42,0.16)",
        "padding:14px",
    ].join(";");

    panel.innerHTML = `
        <div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:10px;">
            <div>
                <div style="font-size:11px;font-weight:800;letter-spacing:0.03em;text-transform:uppercase;color:#2f5be3;margin-bottom:6px;">Info</div>
                <div style="font-size:16px;font-weight:800;color:#1f2d3d;">${info.title}</div>
            </div>
            <button type="button" class="bbbbee-info-close" style="border:0;background:transparent;font-size:18px;line-height:1;color:#64748b;cursor:pointer;">&times;</button>
        </div>
        <div style="font-size:13px;line-height:1.65;color:#52627c;margin-bottom:12px;">${info.body}</div>
        <div style="display:flex;justify-content:flex-end;gap:10px;">
            <button type="button" class="bbbbee-info-close" style="border:1px solid #dbe2ee;background:#fff;color:#1f2d3d;border-radius:8px;padding:7px 11px;">Close</button>
            <button type="button" class="bbbbee-info-read-more" style="border:1px solid #2f5be3;background:#2f5be3;color:#fff;border-radius:8px;padding:7px 11px;font-weight:700;">Read more</button>
        </div>
    `;

    overlay.appendChild(panel);
    document.body.appendChild(overlay);
    activeInfoOverlay = overlay;
    activeInfoAnchor = anchorEl || null;

    const anchorRect = anchorEl ? anchorEl.getBoundingClientRect() : null;
    const panelWidth = 380;
    let top = 16;
    let left = 16;
    if (anchorRect) {
        top = Math.max(12, Math.min(window.innerHeight - 24, anchorRect.bottom + 10));
        left = Math.max(12, Math.min(window.innerWidth - panelWidth - 12, anchorRect.left - 12));
        if (left + panelWidth > window.innerWidth - 12) {
            left = Math.max(12, window.innerWidth - panelWidth - 12);
        }
        if (top + 260 > window.innerHeight) {
            top = Math.max(12, anchorRect.top - 270);
        }
    }
    panel.style.top = `${top}px`;
    panel.style.left = `${left}px`;

    overlay.addEventListener("click", (ev) => {
        if (ev.target === overlay) {
            closeInfoOverlay();
        }
    });

    panel.querySelectorAll(".bbbbee-info-close").forEach((button) => {
        button.addEventListener("click", closeInfoOverlay);
    });

    panel.querySelector(".bbbbee-info-read-more").addEventListener("click", () => {
        closeInfoOverlay();
        triggerDashboardAction(info.action);
    });

    window.addEventListener("resize", closeInfoOverlay, { once: true });
}

function triggerDashboardAction(targetName) {
    const selector = ACTION_BUTTONS[targetName] || `button[name="${targetName}"]`;
    const button = document.querySelector(selector);
    if (button) {
        button.click();
        return true;
    }
    return false;
}

function handleClick(ev) {
    const infoTrigger = ev.target.closest(".bbbbee-info-trigger[data-info-key]");
    if (infoTrigger) {
        ev.preventDefault();
        ev.stopPropagation();
        openInfoOverlay(infoTrigger.dataset.infoKey, infoTrigger);
        return;
    }

    const link = ev.target.closest(".bbbbee-dashboard-jump[data-target-button]");
    if (!link) {
        return;
    }
    const targetName = link.dataset.targetButton;
    if (!targetName) {
        return;
    }
    ev.preventDefault();
    ev.stopPropagation();
    triggerDashboardAction(targetName);
}

function handleDocumentationSearchInput(ev) {
    const q = ev.target.value.toLowerCase().trim();
    const cards = document.querySelectorAll(".doc-section-card");
    cards.forEach((card) => {
        const originalHtml = card.dataset.originalHtml || card.innerHTML;
        if (!card.dataset.originalHtml) {
            card.dataset.originalHtml = originalHtml;
        }

        if (q === "") {
            card.style.display = "";
            card.innerHTML = originalHtml;
            return;
        }

        const content = `${card.getAttribute("data-keywords") || ""} ${card.innerText || ""}`.toLowerCase();
        if (content.indexOf(q) > -1) {
            card.style.display = "";
            card.innerHTML = originalHtml;
            const regex = new RegExp("(" + q.replace(/[-\/\\^$*+?.()|[\]{}]/g, "\\$&") + ")", "gi");
            card.innerHTML = card.innerHTML.replace(regex, '<mark class="bg-warning p-0">$1</mark>');
        } else {
            card.style.display = "none";
            card.innerHTML = originalHtml;
        }
    });
}

if (!window.__bbbbeeDashboardJumpLinksBound) {
    window.__bbbbeeDashboardJumpLinksBound = true;
    document.addEventListener("click", handleClick, true);
    document.addEventListener("input", (ev) => {
        if (ev.target && ev.target.id === "wikiSearchInput") {
            handleDocumentationSearchInput(ev);
        }
    }, true);
    document.addEventListener("keydown", (ev) => {
        if (ev.key === "Escape") {
            closeInfoOverlay();
        }
    });
}
