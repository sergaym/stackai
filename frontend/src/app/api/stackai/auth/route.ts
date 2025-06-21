import { NextRequest, NextResponse } from 'next/server'
import { auth, api } from '@/lib/logger'

const SUPABASE_AUTH_URL = process.env.STACKAI_SUPABASE_AUTH_URL!
const ANON_KEY = process.env.STACKAI_ANON_KEY!
const BACKEND_URL = process.env.STACKAI_BACKEND_URL!

// For security, we can override credentials via env vars or use the defaults from the task
const DEFAULT_EMAIL = process.env.STACKAI_EMAIL!
const DEFAULT_PASSWORD = process.env.STACKAI_PASSWORD!

export async function POST(request: NextRequest) {
  try {
    // Allow override of credentials via request body, but fallback to env vars
    const body = await request.json().catch(() => ({}))
    const email = body.email || DEFAULT_EMAIL
    const password = body.password || DEFAULT_PASSWORD

    auth.info('Starting Stack AI authentication', { email })

    // Validate required environment variables
    if (!SUPABASE_AUTH_URL || !ANON_KEY || !BACKEND_URL) {
      auth.error('Missing required environment variables')
      return NextResponse.json(
        { error: 'Server configuration error: Missing required environment variables' },
        { status: 500 }
      )
    }

    if (!email || !password) {
      auth.error('Missing credentials')
      return NextResponse.json(
        { error: 'Email and password are required' },
        { status: 400 }
      )
    }

    // Authenticate with Supabase
    const authResponse = await fetch(`${SUPABASE_AUTH_URL}/auth/v1/token?grant_type=password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Apikey': ANON_KEY,
      },
      body: JSON.stringify({
        email,
        password,
        gotrue_meta_security: {},
      }),
    })

    if (!authResponse.ok) {
      const errorText = await authResponse.text()
      auth.error('Auth failed', { error: errorText, status: authResponse.status })
      return NextResponse.json(
        { error: `Authentication failed: ${authResponse.statusText}` },
        { status: authResponse.status }
      )
    }

    const authData = await authResponse.json()
    const accessToken = authData.access_token

    auth.debug('Got access token')

    // Get organization ID
    const orgResponse = await fetch(`${BACKEND_URL}/organizations/me/current`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
    })

    if (!orgResponse.ok) {
      const errorText = await orgResponse.text()
      auth.error('Org fetch failed', { error: errorText, status: orgResponse.status })
      return NextResponse.json(
        { error: `Failed to get organization: ${orgResponse.statusText}` },
        { status: orgResponse.status }
      )
    }

    const orgData = await orgResponse.json()
    auth.info('Got org data', { orgId: orgData.org_id })

    // Get connections
    const connectionsResponse = await fetch(`${BACKEND_URL}/connections?connection_provider=gdrive&limit=1`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
    })

    if (!connectionsResponse.ok) {
      const errorText = await connectionsResponse.text()
      auth.error('Connections fetch failed', { error: errorText, status: connectionsResponse.status })
      return NextResponse.json(
        { error: `Failed to get connections: ${connectionsResponse.statusText}` },
        { status: connectionsResponse.status }
      )
    }

    const connections = await connectionsResponse.json()
    auth.info('Got connections', { count: connections.length })

    return NextResponse.json({
      success: true,
      accessToken,
      orgId: orgData.org_id,
      connections,
      userEmail: email
    })

  } catch (error) {
    auth.error('Authentication error', { error })
    return NextResponse.json(
      { error: 'Internal server error during authentication' },
      { status: 500 }
    )
  }
} 