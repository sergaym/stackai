import { NextRequest, NextResponse } from 'next/server'
import { api } from '@/lib/logger'

const BACKEND_URL = process.env.STACKAI_BACKEND_URL!

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const connectionId = searchParams.get('connectionId')
    const parentResourceId = searchParams.get('parentResourceId')
    const accessToken = request.headers.get('x-access-token')

    // Validate required environment variables
    if (!BACKEND_URL) {
      api.error('Missing STACKAI_BACKEND_URL environment variable')
      return NextResponse.json(
        { error: 'Server configuration error: Missing backend URL' },
        { status: 500 }
      )
    }

    if (!accessToken) {
      return NextResponse.json({ error: 'Access token required' }, { status: 401 })
    }

    if (!connectionId) {
      return NextResponse.json({ error: 'Connection ID required' }, { status: 400 })
    }

    // Build the Stack AI API URL
    let url = `${BACKEND_URL}/connections/${connectionId}/resources/children`
    
    if (parentResourceId && parentResourceId !== 'root') {
      url += `?resource_id=${parentResourceId}`
    }

    api.debug('Fetching files from API', { url, connectionId, parentResourceId })

    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const errorText = await response.text()
      api.error('Files fetch failed', { error: errorText, status: response.status })
      return NextResponse.json(
        { error: `Failed to fetch files: ${response.statusText}` },
        { status: response.status }
      )
    }

    const data = await response.json()
    api.info('Fetched files', { count: data.data?.length || 0 })

    return NextResponse.json(data)

  } catch (error) {
    api.error('Files fetch error', { error })
    return NextResponse.json(
      { error: 'Internal server error while fetching files' },
      { status: 500 }
    )
  }
} 