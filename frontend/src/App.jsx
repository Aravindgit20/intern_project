import { useEffect, useState } from 'react'
import './App.css'
import AgentDashboard from './AgentDashboard'
import ScrapDashboard from './ScrapDashboard'


function App() {

    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')


    useEffect(() => {

        const getCurrentUser = async () => {

            try {

                const response = await fetch(
                    '/api/current-user/',
                    {
                        credentials: 'include',
                    }
                )


                let data = null

                try {

                    data = await response.json()

                } catch {

                    data = null

                }


                if (!response.ok) {

                    setError(
                        'Please login first.'
                    )

                    setLoading(false)

                    return
                }


                setUser(data)


            } catch (error) {

                setError(
                    'Unable to connect to Django.'
                )

            } finally {

                setLoading(false)

            }

        }


        getCurrentUser()

    }, [])


    /* =====================================================
       LOADING
    ===================================================== */

    if (loading) {

        return (

            <div className="loading-screen">

                Loading...

            </div>

        )

    }


    /* =====================================================
       ERROR
    ===================================================== */

    if (error) {

        return (

            <div className="loading-screen">

                {error}

            </div>

        )

    }


    /* =====================================================
       NO USER
    ===================================================== */

    if (!user) {

        return null

    }


    /* =====================================================
       AGENT DASHBOARD
    ===================================================== */

    if (user.role === 'agent') {

        return (

            <AgentDashboard
                username={user.username}
            />

        )

    }


    /* =====================================================
       SCRAP TEAM DASHBOARD
    ===================================================== */

    if (user.role === 'scrap_team') {

        return (

            <ScrapDashboard
                username={user.username}
            />

        )

    }


    /* =====================================================
       OTHER ROLES
    ===================================================== */

    return (

        <div className="loading-screen">

            <h2>
                Access Denied
            </h2>

            <p>
                You do not have permission to access this dashboard.
            </p>

        </div>

    )

}


export default App