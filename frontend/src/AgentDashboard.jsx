
import { useCallback, useEffect, useState } from 'react'
import './AgentDashboard.css'

function getCookie(name) {
    const cookies = document.cookie.split(';')

    for (let cookie of cookies) {
        cookie = cookie.trim()

        if (cookie.startsWith(name + '=')) {
            return decodeURIComponent(
                cookie.substring(name.length + 1)
            )
        }
    }

    return null
}

/* =========================================================
   API ERROR HELPER
========================================================= */

async function readResponse(response) {
    const contentType =
        response.headers.get('content-type') || ''

    if (!contentType.includes('application/json')) {
        throw new Error(
            `Server returned an unexpected response (HTTP ${response.status}).`
        )
    }

    const data = await response.json()

    if (!response.ok) {
        throw new Error(
            data.error ||
            data.message ||
            data.detail ||
            `Request failed (HTTP ${response.status}).`
        )
    }

    return data
}

/* =========================================================
   SUBMIT MATERIAL FORM
========================================================= */

function SubmitMaterialForm({ onSubmitted }) {
    const [materialType, setMaterialType] =
        useState('bauxite')

    const [quantity, setQuantity] = useState('')
    const [message, setMessage] = useState('')
    const [error, setError] = useState('')
    const [submitting, setSubmitting] = useState(false)

    const submitMaterial = async (event) => {
        event.preventDefault()

        setMessage('')
        setError('')

        const numericQuantity = Number(quantity)

        if (
            !quantity.trim() ||
            !Number.isFinite(numericQuantity) ||
            numericQuantity <= 0
        ) {
            setError('Enter a quantity greater than zero.')
            return
        }

        setSubmitting(true)

        try {
            const response = await fetch(
                '/api/submit-material/',
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken') || '',
                    },
                    credentials: 'include',
                    body: JSON.stringify({
                        material_type: materialType,
                        quantity: numericQuantity,
                    }),
                }
            )

            const data = await readResponse(response)

            setMessage(
                data.message ||
                'Material submitted successfully.'
            )

            setQuantity('')

            if (onSubmitted) {
                await onSubmitted()
            }
        } catch (error) {
            console.error('Submit material error:', error)

            setError(
                error.message ||
                'Unable to submit material. Please try again.'
            )
        } finally {
            setSubmitting(false)
        }
    }

    return (
        <section className="form-card">
            <h2>Submit Raw Material</h2>

            <p>
                Enter the raw material details for processing.
            </p>

            <form onSubmit={submitMaterial}>
                <div className="form-row">
                    <div className="form-group">
                        <label>Material Type</label>

                        <select
                            value={materialType}
                            onChange={(event) =>
                                setMaterialType(event.target.value)
                            }
                            disabled={submitting}
                        >
                            <option value="bauxite">
                                Bauxite
                            </option>

                            <option value="scrap_aluminum">
                                Scrap Aluminum
                            </option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Quantity (kg)</label>

                        <input
                            type="text"
                            inputMode="decimal"
                            value={quantity}
                            onChange={(event) => {
                                const value = event.target.value

                                if (/^\d*\.?\d*$/.test(value)) {
                                    setQuantity(value)
                                }
                            }}
                            placeholder="Enter quantity in kg"
                            required
                            disabled={submitting}
                        />
                    </div>
                </div>

                <button
                    type="submit"
                    className="submit-button"
                    disabled={submitting}
                >
                    {submitting
                        ? 'Submitting...'
                        : 'Submit Material'}
                </button>
            </form>

            {message && (
                <div className="message success" role="status">
                    {message}
                </div>
            )}

            {error && (
                <div className="message error" role="alert">
                    {error}
                </div>
            )}
        </section>
    )
}

/* =========================================================
   GET BY-PRODUCTS
========================================================= */

function getByProducts(item) {
    if (!item) {
        return []
    }

    if (Array.isArray(item.byproducts)) {
        return item.byproducts
    }

    if (Array.isArray(item.by_products)) {
        return item.by_products
    }

    if (item.byproduct) {
        return [item.byproduct]
    }

    if (item.by_product) {
        return [item.by_product]
    }

    return []
}

/* =========================================================
   RESULT TABLE
========================================================= */

function ResultTable({ item }) {
    if (!item) {
        return null
    }

    const byProducts = getByProducts(item)

    const displayValue = (value) =>
        value !== null && value !== undefined && value !== ''
            ? value
            : '-'

    return (
        <div className="result-section">
            <div className="result-heading">
                <h3>Processing Result</h3>

                <p>
                    Complete processing information for Product ID{' '}
                    {item.product_id}.
                </p>
            </div>

            <div className="result-table-wrapper">
                <table className="result-table">
                    <thead>
                        <tr>
                            <th>Product ID</th>
                            <th>Material</th>
                            <th>Input Quantity</th>
                            <th>Lower Yield</th>
                            <th>Expected Yield</th>
                            <th>Upper Yield</th>
                            <th>Actual Yield</th>
                            <th>Waste</th>
                            <th>Process Stage</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr>
                            <td>{displayValue(item.product_id)}</td>

                            <td>
                                {item.material_type_display ||
                                    item.material_type ||
                                    '-'}
                            </td>

                            <td>
                                {displayValue(item.quantity)} kg
                            </td>

                            <td>
                                {displayValue(item.lower_yield)} kg
                            </td>

                            <td className="expected-value">
                                {displayValue(item.predicted_yield)} kg
                            </td>

                            <td>
                                {displayValue(item.upper_yield)} kg
                            </td>

                            <td>
                                {item.actual_yield !== null &&
                                item.actual_yield !== undefined
                                    ? `${item.actual_yield} kg`
                                    : '-'}
                            </td>

                            <td>
                                {item.waste_quantity !== null &&
                                item.waste_quantity !== undefined
                                    ? `${item.waste_quantity} kg`
                                    : '-'}
                            </td>

                            <td>
                                {displayValue(item.process_stage)}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div className="yield-summary">
                <div className="yield-item">
                    <span>Lower Yield</span>
                    <strong>
                        {displayValue(item.lower_yield)} kg
                    </strong>
                </div>

                <div className="yield-item expected">
                    <span>Expected Yield</span>
                    <strong>
                        {displayValue(item.predicted_yield)} kg
                    </strong>
                </div>

                <div className="yield-item">
                    <span>Upper Yield</span>
                    <strong>
                        {displayValue(item.upper_yield)} kg
                    </strong>
                </div>

                <div className="yield-item">
                    <span>Actual Yield</span>
                    <strong>
                        {item.actual_yield !== null &&
                        item.actual_yield !== undefined
                            ? `${item.actual_yield} kg`
                            : '-'}
                    </strong>
                </div>

                <div className="yield-item">
                    <span>Waste</span>
                    <strong>
                        {item.waste_quantity !== null &&
                        item.waste_quantity !== undefined
                            ? `${item.waste_quantity} kg`
                            : '-'}
                    </strong>
                </div>
            </div>

            <div className="byproduct-section">
                <div className="byproduct-heading">
                    <div>
                        <h3>Produced By-Products</h3>

                        <p>
                            By-products generated during the recovery process.
                        </p>
                    </div>
                </div>

                {byProducts.length === 0 ? (
                    <div className="no-byproduct">
                        No by-product information available.
                    </div>
                ) : (
                    <div className="result-table-wrapper">
                        <table className="result-table byproduct-table">
                            <thead>
                                <tr>
                                    <th>By-Product</th>
                                    <th>Quantity</th>
                                    <th>Status</th>
                                </tr>
                            </thead>

                            <tbody>
                                {byProducts.map((byProduct, index) => (
                                    <tr
                                        key={
                                            byProduct.id ??
                                            `${byProduct.byproduct_type || 'byproduct'}-${index}`
                                        }
                                    >
                                        <td>
                                            {byProduct.byproduct_type_display ||
                                                byProduct.by_product_type_display ||
                                                byProduct.byproduct_type ||
                                                byProduct.by_product_type ||
                                                byProduct.type ||
                                                '-'}
                                        </td>

                                        <td>
                                            {byProduct.quantity !== null &&
                                            byProduct.quantity !== undefined
                                                ? `${byProduct.quantity} kg`
                                                : '-'}
                                        </td>

                                        <td>
                                            <span
                                                className={`status-badge ${
                                                    byProduct.status
                                                        ? byProduct.status.toLowerCase()
                                                        : ''
                                                }`}
                                            >
                                                {byProduct.status || '-'}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    )
}

/* =========================================================
   SUBMISSIONS TABLE
========================================================= */

function SubmissionsTable({
    submissions,
    loading,
    error,
    onRetry,
}) {
    const [viewingResult, setViewingResult] = useState(null)

    const toggleResult = (item) => {
        if (!item.processing_completed) {
            return
        }

        setViewingResult((current) =>
            current === item.id ? null : item.id
        )
    }

    const selectedItem = submissions.find(
        (item) => item.id === viewingResult
    )

    return (
        <>
            <section className="table-card">
                <div className="table-heading">
                    <div>
                        <h2>My Submissions</h2>

                        <p>
                            Submitted raw materials and predicted yield.
                        </p>
                    </div>

                    <button
                        type="button"
                        className="view-result-button"
                        onClick={onRetry}
                        disabled={loading}
                    >
                        {loading ? 'Refreshing...' : 'Refresh'}
                    </button>
                </div>

                {error && (
                    <div className="message error" role="alert">
                        {error}
                    </div>
                )}

                {loading && submissions.length === 0 ? (
                    <div className="empty-state">
                        Loading submissions...
                    </div>
                ) : submissions.length === 0 ? (
                    <div className="empty-state">
                        {error
                            ? 'Unable to load submissions. Please try again.'
                            : 'No submissions found.'}
                    </div>
                ) : (
                    <div className="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Product ID</th>
                                    <th>Material</th>
                                    <th>Quantity</th>
                                    <th>Lower Yield</th>
                                    <th>Expected Yield</th>
                                    <th>Upper Yield</th>
                                    <th>Process Stage</th>
                                    <th>Result</th>
                                </tr>
                            </thead>

                            <tbody>
                                {submissions.map((item) => (
                                    <tr key={item.id}>
                                        <td>{item.product_id}</td>

                                        <td>
                                            {item.material_type_display ||
                                                item.material_type}
                                        </td>

                                        <td>{item.quantity} kg</td>

                                        <td>{item.lower_yield} kg</td>

                                        <td>
                                            <strong>
                                                {item.predicted_yield} kg
                                            </strong>
                                        </td>

                                        <td>{item.upper_yield} kg</td>

                                        <td>{item.process_stage}</td>

                                        <td>
                                            {item.processing_completed ? (
                                                <button
                                                    type="button"
                                                    className="view-result-button"
                                                    onClick={() =>
                                                        toggleResult(item)
                                                    }
                                                >
                                                    {viewingResult === item.id
                                                        ? 'Hide Result'
                                                        : 'View Result'}
                                                </button>
                                            ) : (
                                                <button
                                                    type="button"
                                                    className="view-result-button"
                                                    disabled
                                                >
                                                    Processing Pending
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </section>

            {viewingResult !== null && selectedItem && (
                <section className="result-card">
                    <ResultTable item={selectedItem} />
                </section>
            )}
        </>
    )
}

/* =========================================================
   AGENT DASHBOARD
========================================================= */

function AgentDashboard({ username }) {
    const [submissions, setSubmissions] = useState([])
    const [submissionsLoading, setSubmissionsLoading] = useState(true)
    const [submissionsError, setSubmissionsError] = useState('')

    const loadSubmissions = useCallback(async (showLoading = false) => {
        if (showLoading) {
            setSubmissionsLoading(true)
        }

        try {
            const response = await fetch(
                '/api/my-submissions/',
                {
                    credentials: 'include',
                    headers: {
                        Accept: 'application/json',
                    },
                }
            )

            const data = await readResponse(response)

            // Support APIs returning either a list or { results: [...] }.
            const items = Array.isArray(data)
                ? data
                : Array.isArray(data.results)
                    ? data.results
                    : null

            if (!items) {
                throw new Error(
                    'The submissions API did not return a list of submissions.'
                )
            }

            setSubmissions(items)
            setSubmissionsError('')
        } catch (error) {
            console.error('Load submissions error:', error)

            setSubmissionsError(
                error.message ||
                'Unable to load submissions. Please try again.'
            )
        } finally {
            setSubmissionsLoading(false)
        }
    }, [])

    useEffect(() => {
        loadSubmissions(true)

        // Check for processing updates every 10 seconds.
        const intervalId = setInterval(() => {
            loadSubmissions(false)
        }, 10000)

        return () => {
            clearInterval(intervalId)
        }
    }, [loadSubmissions])

    return (
        <div className="app">
            <nav className="navbar">
                <div className="welcome">
                    Welcome, {username}!

                    <span className="separator">•</span>

                    Agent Dashboard
                </div>

                <div className="nav-links">
                    <a href="/">Home</a>
                    <a href="/login/">Login</a>
                    <a href="/register/">Register</a>
                    <a href="/logout/">Logout</a>
                </div>
            </nav>

            <main className="dashboard-content">
                <div className="dashboard-heading">
                    <h1>Raw Material Processing</h1>

                    <p>
                        Submit raw materials and monitor predicted recovery.
                    </p>
                </div>

                <SubmitMaterialForm
                    onSubmitted={() => loadSubmissions(false)}
                />

                <SubmissionsTable
                    submissions={submissions}
                    loading={submissionsLoading}
                    error={submissionsError}
                    onRetry={() => loadSubmissions(true)}
                />
            </main>
        </div>
    )
}

export default AgentDashboard
