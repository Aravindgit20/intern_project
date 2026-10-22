
import { useEffect, useState, useRef } from "react";
import "./scrap_dashboard.css";

function ScrapDashboard() {
    const [byproducts, setByproducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [loadError, setLoadError] = useState("");
    const [updatingId, setUpdatingId] = useState(null);
    const [completionItem, setCompletionItem] = useState(null);
    const [username, setUsername] = useState("Scrap Team");

    const scrollPosition = useRef(0);

    // =========================================================
    // CSRF
    // =========================================================

    const getCookie = (name) => {
        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {
            cookie = cookie.trim();

            if (cookie.startsWith(name + "=")) {
                return decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
            }
        }

        return null;
    };

    // =========================================================
    // Load Username
    // =========================================================

    useEffect(() => {
        const loadUsername = async () => {
            try {
                const response = await fetch(
                    "/api/current-user/",
                    {
                        credentials: "include"
                    }
                );

                if (!response.ok) {
                    return;
                }

                const data = await response.json();

                const currentUser =
                    data.user ||
                    data.current_user ||
                    data;

                const name =
                    (typeof currentUser === "string"
                        ? currentUser
                        : currentUser?.username ||
                          currentUser?.name) ||
                    data.username ||
                    data.name;

                if (name) {
                    setUsername(name);
                }
            } catch (error) {
                console.error(
                    "Error loading username:",
                    error
                );
            }
        };

        loadUsername();
    }, []);

    // =========================================================
    // Load By-products
    // =========================================================

    const loadByproducts = async () => {
        try {
            setLoadError("");

            const response = await fetch(
                "/api/scrap-byproducts/",
                {
                    credentials: "include"
                }
            );

            const contentType =
                response.headers.get("content-type") || "";

            let data;

            if (contentType.includes("application/json")) {
                data = await response.json();
            } else {
                const responseText = await response.text();

                throw new Error(
                    `Expected JSON but received a non-JSON response. ` +
                    `HTTP ${response.status}. ` +
                    responseText.slice(0, 150)
                );
            }

            if (!response.ok) {
                throw new Error(
                    data.error ||
                    data.detail ||
                    `API request failed with status ${response.status}`
                );
            }

            const records = Array.isArray(data)
                ? data
                : Array.isArray(data.results)
                    ? data.results
                    : Array.isArray(data.byproducts)
                        ? data.byproducts
                        : null;

            if (!records) {
                console.error(
                    "Unexpected Scrap API response:",
                    data
                );

                throw new Error(
                    "The API response does not contain a list of records. " +
                    "Check the browser console."
                );
            }

            console.log("Scrap API response:", records);

            setByproducts(records);
        } catch (error) {
            console.error(
                "Error loading Scrap Dashboard:",
                error
            );

            setLoadError(error.message);
            setByproducts([]);
        } finally {
            setLoading(false);
        }
    };

    // =========================================================
    // Initial Load
    // =========================================================

    useEffect(() => {
        loadByproducts();
    }, []);

    // =========================================================
    // Start Newly Submitted Material
    // =========================================================

    const startMaterialProcessing = async (materialId) => {
        if (!materialId) {
            return;
        }

        scrollPosition.current = window.scrollY;

        try {
            setUpdatingId(`material-${materialId}`);

            const csrfToken = getCookie("csrftoken");

            const response = await fetch(
                "/api/update-byproduct/",
                {
                    method: "POST",
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken || ""
                    },
                    body: JSON.stringify({
                        material_id: materialId,
                        status: "in_progress"
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error ||
                    data.detail ||
                    "Failed to start processing"
                );
            }

            await loadByproducts();

            window.scrollTo({
                top: scrollPosition.current,
                behavior: "instant"
            });
        } catch (error) {
            console.error(
                "Error starting processing:",
                error
            );

            alert(
                error.message ||
                "Unable to start processing."
            );
        } finally {
            setUpdatingId(null);
        }
    };

    // =========================================================
    // Update Existing By-product Status
    // =========================================================

    const updateStatus = async (byproductId, status) => {
        if (!byproductId || !status) {
            return;
        }

        scrollPosition.current = window.scrollY;

        try {
            setUpdatingId(byproductId);

            const csrfToken = getCookie("csrftoken");

            const response = await fetch(
                "/api/update-byproduct/",
                {
                    method: "POST",
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken || ""
                    },
                    body: JSON.stringify({
                        byproduct_id: byproductId,
                        status
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error ||
                    data.detail ||
                    "Failed to update status"
                );
            }

            await loadByproducts();

            window.scrollTo({
                top: scrollPosition.current,
                behavior: "instant"
            });
        } catch (error) {
            console.error(
                "Error updating status:",
                error
            );

            alert(
                error.message ||
                "Unable to update processing status."
            );
        } finally {
            setUpdatingId(null);
        }
    };

    // =========================================================
    // Completion Confirmation
    // =========================================================

    const openCompletionForm = (item) => {
        setCompletionItem(item);
    };

    const cancelCompletion = () => {
        if (updatingId !== null) {
            return;
        }

        setCompletionItem(null);
    };

    // =========================================================
    // Complete Processing
    // =========================================================

    const completeProcessing = async (byproductId) => {
        if (!byproductId) {
            return;
        }

        scrollPosition.current = window.scrollY;

        try {
            setUpdatingId(byproductId);

            const csrfToken = getCookie("csrftoken");

            const response = await fetch(
                "/api/update-byproduct/",
                {
                    method: "POST",
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken || ""
                    },
                    body: JSON.stringify({
                        byproduct_id: byproductId,
                        status: "completed"
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error ||
                    data.detail ||
                    "Failed to complete processing"
                );
            }

            setCompletionItem(null);

            await loadByproducts();

            window.scrollTo({
                top: scrollPosition.current,
                behavior: "instant"
            });
        } catch (error) {
            console.error(
                "Error completing processing:",
                error
            );

            alert(
                error.message ||
                "Unable to complete processing."
            );
        } finally {
            setUpdatingId(null);
        }
    };

    // =========================================================
    // Status Helpers
    // =========================================================

    const getStatusLabel = (status) => {
        if (status === "pending") {
            return "Pending";
        }

        if (status === "in_progress") {
            return "In Progress";
        }

        if (status === "completed") {
            return "Completed";
        }

        return status || "-";
    };

    const getStatusClass = (status) => {
        if (status === "pending") {
            return "status-pending";
        }

        if (status === "in_progress") {
            return "status-progress";
        }

        if (status === "completed") {
            return "status-completed";
        }

        return "";
    };

    const getNextStatus = (status) => {
        if (status === "pending") {
            return "in_progress";
        }

        return null;
    };

    // =========================================================
    // Normalize API Material Names
    // =========================================================

    const normalizeMaterial = (value) => {
        const material = String(value ?? "")
            .trim()
            .toLowerCase()
            .replaceAll("_", " ")
            .replaceAll("-", " ")
            .replace(/\s+/g, " ");

        if (material === "bauxite") {
            return "bauxite";
        }

        if (
            material === "scrap aluminum" ||
            material === "scrap aluminium"
        ) {
            return "scrap aluminum";
        }

        return material;
    };

    // =========================================================
    // Stage 1 Completed
    // =========================================================

    const isStageOneCompleted = (materialId) => {
        return byproducts.some(
            item =>
                Number(item.material_id) === Number(materialId) &&
                item.byproduct_type ===
                    "Aluminum Dross / Residue" &&
                item.status === "completed"
        );
    };

    // =========================================================
    // Filter Sections
    // =========================================================

    const bauxiteByproducts = byproducts.filter(
        item =>
            normalizeMaterial(item.raw_material) === "bauxite"
    );

    const scrapByproducts = byproducts.filter(
        item =>
            normalizeMaterial(item.raw_material) ===
            "scrap aluminum"
    );

    // =========================================================
    // Scrap Aluminum Stages
    // =========================================================

    const stageOneByproducts = scrapByproducts.filter(
        item =>
            item.byproduct_type ===
            "Aluminum Dross / Residue"
    );

    const stageTwoByproducts = scrapByproducts.filter(
        item =>
            item.byproduct_type === "Manganese Alloy"
    );

    // =========================================================
    // Applications
    // =========================================================

    const renderApplications = (item) => {
        if (
            !item ||
            item.status !== "completed" ||
            !Array.isArray(item.potential_applications) ||
            item.potential_applications.length === 0
        ) {
            return null;
        }

        return (
            <div className="applications-box">
                <h4>Potential Applications</h4>

                <div className="applications-list">
                    {item.potential_applications.map(
                        (application, index) => (
                            <div
                                className="application-item"
                                key={`${item.id}-${index}`}
                            >
                                <span className="application-dot">
                                    ✓
                                </span>

                                <span>{application}</span>
                            </div>
                        )
                    )}
                </div>
            </div>
        );
    };

    const getCompletedApplicationItem = (items) => {
        return items.find(
            item =>
                item.status === "completed" &&
                Array.isArray(item.potential_applications) &&
                item.potential_applications.length > 0
        );
    };

    // =========================================================
    // Render Action
    // =========================================================

    const renderAction = (item) => {
        if (item.status === "completed") {
            if (
                item.byproduct_type ===
                "Aluminum Dross / Residue"
            ) {
                return (
                    <span className="completed-text">
                        Stage 1 Completed
                    </span>
                );
            }

            return (
                <span className="completed-text">
                    Processing Completed
                </span>
            );
        }

        if (
            item.byproduct_type === "Manganese Alloy" &&
            !isStageOneCompleted(item.material_id)
        ) {
            return (
                <span className="locked-text">
                    Complete Stage 1 First
                </span>
            );
        }

        if (item.status === "in_progress") {
            if (
                item.raw_material === "Bauxite" ||
                normalizeMaterial(item.raw_material) === "bauxite" ||
                item.byproduct_type === "Manganese Alloy"
            ) {
                return (
                    <button
                        type="button"
                        className="update-btn"
                        disabled={updatingId === item.id}
                        onClick={() => openCompletionForm(item)}
                    >
                        {updatingId === item.id
                            ? "Updating..."
                            : "Complete Processing"}
                    </button>
                );
            }

            return (
                <button
                    type="button"
                    className="update-btn"
                    disabled={updatingId === item.id}
                    onClick={() => completeProcessing(item.id)}
                >
                    {updatingId === item.id
                        ? "Completing..."
                        : "Complete Processing"}
                </button>
            );
        }

        const nextStatus = getNextStatus(item.status);

        if (!nextStatus) {
            return null;
        }

        if (!item.id && item.material_id) {
            const loadingId = `material-${item.material_id}`;

            return (
                <button
                    type="button"
                    className="update-btn"
                    disabled={updatingId === loadingId}
                    onClick={() =>
                        startMaterialProcessing(item.material_id)
                    }
                >
                    {updatingId === loadingId
                        ? "Starting..."
                        : "Start Processing"}
                </button>
            );
        }

        return (
            <button
                type="button"
                className="update-btn"
                disabled={updatingId === item.id}
                onClick={() => updateStatus(item.id, nextStatus)}
            >
                {updatingId === item.id
                    ? "Updating..."
                    : "Start Processing"}
            </button>
        );
    };

    // =========================================================
    // Render Table
    // =========================================================

    const renderTable = (items) => {
        if (items.length === 0) {
            return (
                <div className="empty-state">
                    No by-products available.
                </div>
            );
        }

        return (
            <div className="table-wrapper">
                <table className="scrap-table">
                    <thead>
                        <tr>
                            <th>Product ID</th>
                            <th>By-product</th>
                            <th>Quantity</th>
                            <th>Lower Yield</th>
                            <th>Expected Yield</th>
                            <th>Upper Yield</th>
                            <th>Process Stage</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>

                    <tbody>
                        {items.map(item => (
                            <tr
                                key={
                                    item.id
                                        ? `byproduct-${item.id}`
                                        : `material-${item.material_id}`
                                }
                            >
                                <td>
                                    <span className="product-id">
                                        {item.product_id ?? "-"}
                                    </span>
                                </td>

                                <td>
                                    <div className="byproduct-name">
                                        {item.byproduct_type || "-"}
                                    </div>
                                </td>

                                <td>
                                    {item.quantity !== null &&
                                    item.quantity !== undefined
                                        ? `${item.quantity} kg`
                                        : "-"}
                                </td>

                                <td>{item.lower_yield ?? "-"}</td>

                                <td>
                                    <strong>
                                        {item.predicted_yield ?? "-"}
                                    </strong>
                                </td>

                                <td>{item.upper_yield ?? "-"}</td>

                                <td>{item.stage || "-"}</td>

                                <td>
                                    <span
                                        className={`status-badge ${getStatusClass(
                                            item.status
                                        )}`}
                                    >
                                        {getStatusLabel(item.status)}
                                    </span>
                                </td>

                                <td>{renderAction(item)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );
    };

    // =========================================================
    // Loading
    // =========================================================

    if (loading) {
        return (
            <div className="scrap-dashboard">
                <nav className="scrap-navbar">
                    <div className="navbar-title">
                        ♻ Aluminum Recovery
                    </div>
                </nav>

                <main className="scrap-main">
                    <div className="loading-state">
                        Loading by-products...
                    </div>
                </main>
            </div>
        );
    }

    // =========================================================
    // Completed Applications
    // =========================================================

    const completedBauxite =
        getCompletedApplicationItem(bauxiteByproducts);

    const completedStageOne =
        getCompletedApplicationItem(stageOneByproducts);

    const completedStageTwo =
        getCompletedApplicationItem(stageTwoByproducts);

    // =========================================================
    // Main Dashboard
    // =========================================================

    return (
        <div className="scrap-dashboard">
            <nav className="scrap-navbar">
                <div className="navbar-title">
                    ♻ Aluminum Recovery
                </div>

                <span className="welcome-text">
                    Welcome to scrap Team, {username}
                </span>

                <div className="navbar-right">
                    <a href="/" className="nav-link">
                        Home
                    </a>

                    <a href="/logout/" className="logout-link">
                        Logout
                    </a>
                </div>
            </nav>

            <main className="scrap-main">
                <div className="page-heading">
                    <div>
                        <h1>Scrap Team Dashboard</h1>

                        <p>
                            Manage by-product processing
                            and recovery operations.
                        </p>
                    </div>
                </div>

                {loadError && (
                    <div
                        role="alert"
                        style={{
                            padding: "12px 16px",
                            marginBottom: "16px",
                            color: "#991b1b",
                            background: "#fef2f2",
                            border: "1px solid #fecaca",
                            borderRadius: "8px",
                            overflowWrap: "anywhere"
                        }}
                    >
                        <strong>
                            Unable to load Scrap Dashboard:
                        </strong>{" "}
                        {loadError}

                        <button
                            type="button"
                            className="update-btn"
                            style={{ marginLeft: "12px" }}
                            onClick={loadByproducts}
                        >
                            Retry
                        </button>
                    </div>
                )}

                {/* BAUXITE */}

                <section className="dashboard-section">
                    <div className="section-header">
                        <div>
                            <h2>Bauxite Processing</h2>
                        </div>
                    </div>

                    {renderTable(bauxiteByproducts)}

                    {completedBauxite &&
                        renderApplications(completedBauxite)}
                </section>

                {/* SCRAP ALUMINUM */}

                <div className="scrap-aluminum-section">
                    <div className="section-header">
                        <div>
                            <h2>Scrap Aluminum Processing</h2>
                        </div>
                    </div>

                    {/* STAGE 1 */}

                    <div className="processing-stage">
                        <div className="stage-header">
                            <div>
                                <span className="stage-label">
                                    Stage 1
                                </span>

                                <h3>
                                    Aluminum Dross / Residue
                                </h3>
                            </div>
                        </div>

                        <div className="stage-table">
                            {renderTable(stageOneByproducts)}
                        </div>

                        {completedStageOne &&
                            renderApplications(completedStageOne)}
                    </div>

                    {/* STAGE 2 */}

                    <div className="processing-stage">
                        <div className="stage-header">
                            <div>
                                <span className="stage-label">
                                    Stage 2
                                </span>

                                <h3>Manganese Alloy</h3>
                            </div>
                        </div>

                        <div className="stage-table">
                            {renderTable(stageTwoByproducts)}
                        </div>

                        {completedStageTwo &&
                            renderApplications(completedStageTwo)}
                    </div>
                </div>
            </main>

            {/* COMPLETION MODAL */}

            {completionItem &&
                (
                    normalizeMaterial(completionItem.raw_material) ===
                        "bauxite" ||
                    completionItem.byproduct_type === "Manganese Alloy"
                ) && (
                    <div
                        className="completion-modal-overlay"
                        onClick={event => {
                            if (
                                event.target === event.currentTarget
                            ) {
                                cancelCompletion();
                            }
                        }}
                    >
                        <div className="completion-modal">
                            <div className="completion-modal-icon">
                                ✓
                            </div>

                            <h2>Complete Processing</h2>

                            <p>
                                The system will automatically calculate
                                the simulated actual yield and waste
                                for this processing operation.
                            </p>

                            <div className="completion-modal-actions">
                                <button
                                    type="button"
                                    className="cancel-btn"
                                    disabled={
                                        updatingId === completionItem.id
                                    }
                                    onClick={cancelCompletion}
                                >
                                    Cancel
                                </button>

                                <button
                                    type="button"
                                    className="update-btn"
                                    disabled={
                                        updatingId === completionItem.id
                                    }
                                    onClick={() =>
                                        completeProcessing(
                                            completionItem.id
                                        )
                                    }
                                >
                                    {updatingId === completionItem.id
                                        ? "Completing..."
                                        : "Complete Processing"}
                                </button>
                            </div>
                        </div>
                    </div>
                )}
        </div>
    );
}

export default ScrapDashboard;
